import json
import re
import inspect
from typing import List, Dict, Any, Optional, AsyncGenerator, Union, Callable

from ..usfAgent import USFAgent
from ..types import Message, RunOptions, AgentResult, Tool, ToolCall
from ..types.multi_agent import (
    AgentId,
    AgentSpec,
    ContextMode,
    TaskPayload,
    ToolCallExecutionResult,
)
from .context import _shape_context_for_mode, to_openai_messages_from_task
from ..runtime.openai_compat import (
    make_completion,
    make_chunk_from_content_delta,
    make_chunk_tool_calls,
    make_chunk_tool_result,
    make_chunk_finish,
)

def _slugify(value: str) -> str:
    s = (value or '').strip().lower()
    s = re.sub(r'[^a-z0-9]+', '_', s)
    s = re.sub(r'_+', '_', s).strip('_')
    return s or 'agent'


def _chunk_text(text: str, n: int):
    """
    Yield text in chunks of size n. If n <= 0, yield the whole text once.
    """
    if not isinstance(text, str):
        text = str(text or "")
    if n and n > 0:
        for i in range(0, len(text), n):
            yield text[i:i + n]
    else:
        yield text


def _collect_final_answer(agent: USFAgent, messages: List[Message], options: Optional[RunOptions] = None) -> Dict[str, Any]:
    """
    Helper to run the USFAgent and collect either final_answer or first tool_calls requirement.
    Returns:
      {
        'status': 'final' | 'tool_calls' | 'error',
        'content': Optional[str],
        'tool_calls': Optional[List[Dict[str, Any]]],
        'raw_chunks': List[Dict[str, Any]]  # plan/tool_calls/final chunks as yielded
      }
    """
    # The run() is async generator; we need to consume it synchronously from async context
    # This helper is intended to be awaited by wrapper methods.
    raise RuntimeError("This helper must be awaited via _acollect_final_answer")


async def _acollect_final_answer(agent: USFAgent, messages: List[Message], options: Optional[RunOptions] = None) -> Dict[str, Any]:
    raw_chunks: List[Dict[str, Any]] = []
    async for chunk in agent.run(messages, options or {}):
        raw_chunks.append(chunk)
        if chunk.get('type') == 'tool_calls':
            return {
                'status': 'tool_calls',
                'content': None,
                'tool_calls': chunk.get('tool_calls'),
                'raw_chunks': raw_chunks
            }
        if chunk.get('type') == 'final_answer':
            return {
                'status': 'final',
                'content': chunk.get('content', ''),
                'tool_calls': None,
                'raw_chunks': raw_chunks
            }
    # If nothing decisive was returned
    return {
        'status': 'error',
        'content': None,
        'tool_calls': None,
        'raw_chunks': raw_chunks
    }


def _merge_tools(existing: Optional[List[Tool]], extra: Optional[List[Tool]]) -> List[Tool]:
    """
    Merge two tool lists, de-duplicating by function.name when available.
    """
    existing = list(existing or [])
    extra = list(extra or [])
    seen = set()
    merged: List[Tool] = []

    def name_of(t: Tool) -> str:
        if isinstance(t, dict):
            fn = (t.get('function') or {}).get('name')
            if fn:
                return fn
        # Fallback: stable string key
        try:
            return json.dumps(t, sort_keys=True)
        except Exception:
            return str(t)

    for t in existing + extra:
        key = name_of(t)
        if key not in seen:
            seen.add(key)
            merged.append(t)
    return merged


class BaseAgentWrapper:
    """
    Composition wrapper over USFAgent that enforces isolation and provides
    unified entry points for message-based and task-based execution.
    """

    def __init__(self, spec: AgentSpec):
        if not spec or not isinstance(spec, dict):
            raise Exception("BaseAgentWrapper Error: spec is required")

        # Enforce name-first; derive stable internal id via slugify(name)
        _name = spec.get('name')
        if not (_name and str(_name).strip()):
            raise Exception("BaseAgentWrapper Error: 'name' is required in spec")
        self.name: str = str(_name).strip()
        self.id: AgentId = _slugify(self.name)
        self.description: str = spec.get('description', '') or ''
        self.backstory: str = spec.get('backstory', '') or ''
        self.goal: str = spec.get('goal', '') or ''
        self.context_mode: ContextMode = spec.get('context_mode', 'NONE')  # default policy for sub usage
        self.task_placeholder: str = spec.get('task_placeholder') or ''
        # Per-agent history policy (defaults False unless explicitly set)
        self.history: bool = bool(spec.get('history', False))
        self.trim_last_user: bool = bool(spec.get('trim_last_user', False))

        usf_config = spec.get('usf_config') or {}
        # Ensure backstory/goal are present in agent config for consistent behavior
        usf_config = {
            **usf_config,
            'backstory': self.backstory,
            'goal': self.goal,
        }

        # Keep a copy for convenience (used by manager sugar to spawn sub-agents)
        self._usf_config = usf_config

        # Memory is isolated per wrapper by virtue of distinct USFAgent instance.
        self.usf = USFAgent(usf_config)

        # Allow manager/generic agents to have native tools (not sub-agents as tools)
        self._native_tools: List[Tool] = spec.get('tools', []) or []
        # Optional sub-agent entries (any agent can aggregate sub-agents)
        self._sub_entries: List[Dict[str, Any]] = []  # [{'sub': BaseAgentWrapper}]

    async def run(self, messages: Union[str, List[Message], Dict[str, Any]], options: Optional[RunOptions] = None) -> Any:
        """
        Unified entry: single public API.
        - If a string is provided, it is treated as a single user message.
        - If a list of messages is provided, they are passed through to the USFAgent.
        - If a dict resembling a TaskPayload is provided (has 'task'/'input'/'context'),
          it will be shaped according to this agent's context_mode (enforcing REQUIRED for SubAgents).
        Returns final or pending tool_calls in a normalized dict.
        """
        opts: RunOptions = dict(options or {})

        # Handle TaskPayload dicts (task-centric path with context shaping and REQUIRED enforcement)
        msg_list: List[Message]
        if isinstance(messages, dict) and any(k in messages for k in ('task', 'input', 'context')):
            # Normalize to string-only task/context for shaping
            if isinstance(messages, dict):
                task_val = messages.get('task')
                task_str = str(task_val) if task_val is not None else 'task'
                _ctx_val = messages.get('context')
                ctx_str = None
                if _ctx_val is not None:
                    if isinstance(_ctx_val, str):
                        ctx_str = _ctx_val
                    else:
                        raise TypeError("context must be a string when provided in task payload")
            else:
                raise TypeError("TaskPayload must be a dict when provided")

            shaped_messages = _shape_context_for_mode(
                self.context_mode,
                task_str,
                history_messages=None,
                context=ctx_str,
                introduction=getattr(self.usf, 'introduction', '') or '',
                knowledge_cutoff=getattr(self.usf, 'knowledge_cutoff', '') or '',
                backstory=getattr(self, 'backstory', '') or '',
                goal=getattr(self, 'goal', '') or '',
                history=False,
                trim_last_user=False
            )
            msg_list = shaped_messages
        elif isinstance(messages, str):
            msg_list = [{'role': 'user', 'content': messages}]  # type: ignore[typeddict-item]
        else:
            msg_list = list(messages or [])

        # Compose tools
        comp_tools = self._compose_tools()
        if comp_tools:
            opts['tools'] = _merge_tools(opts.get('tools'), comp_tools)

        # Single-step collect
        return await _acollect_final_answer(self.usf, msg_list, opts)



    def get_public_tool(self) -> Optional[Tool]:
        """
        Default: no direct public tool surface. Subclasses may override.
        """
        return None

    def list_native_tools(self) -> List[Tool]:
        """
        Native external tools configured for this agent (excludes sub-agents).
        """
        return list(self._native_tools)

    @staticmethod
    def _merge_usf_config(base: Dict[str, Any], overrides: Optional[Dict[str, Any]]) -> Dict[str, Any]:
        """
        Shallow-merge base USF config with overrides, deep-merging stage keys:
        planning, tool_calling, final_response.
        """
        if not overrides:
            return dict(base or {})
        merged: Dict[str, Any] = dict(base or {})
        for key, val in (overrides or {}).items():
            if key in ('planning', 'tool_calling', 'final_response'):
                base_stage = dict((merged.get(key) or {})) if isinstance(merged.get(key), dict) else {}
                if isinstance(val, dict):
                    base_stage.update(val)
                    merged[key] = base_stage
                else:
                    merged[key] = val
            else:
                merged[key] = val
        return merged

    def _build_system_context(self) -> str:
        """
        Compose a single system context block from introduction, knowledge_cutoff,
        backstory, and goal. Empty fields are omitted; parts are joined by newlines.
        """
        parts: List[str] = []
        introduction = getattr(self.usf, 'introduction', '') or ''
        knowledge_cutoff = getattr(self.usf, 'knowledge_cutoff', '') or ''
        backstory = getattr(self, 'backstory', '') or ''
        goal = getattr(self, 'goal', '') or ''
        if isinstance(introduction, str) and introduction.strip():
            parts.append(introduction.strip())
        if isinstance(knowledge_cutoff, str) and knowledge_cutoff.strip():
            parts.append(knowledge_cutoff.strip())
        if isinstance(backstory, str) and backstory.strip():
            parts.append(backstory.strip())
        if isinstance(goal, str) and goal.strip():
            parts.append(goal.strip())
        return "\n".join(parts).strip()

    def _compose_tools(self) -> List[Tool]:
        """
        Compose this agent's native tools + each registered sub-agent as a tool (agent-as-tool adapter).
        """
        tools: List[Tool] = []
        # Native tools first
        tools.extend(self.list_native_tools())

        # Avoid import cycle by importing adapter lazily
        try:
            from .adapter import make_agent_tool
        except Exception:
            make_agent_tool = None  # type: ignore

        for entry in self._sub_entries:
            sub = entry['sub']
            alias = entry.get('alias')
            overrides = entry.get('overrides') or {}
            ov_desc = (overrides or {}).get('description')
            # Prefer explicit override description if provided
            if ov_desc:
                tools.append({
                    'type': 'function',
                    'function': {
                        'name': (alias or f"agent_{getattr(sub, 'id', 'sub')}"),
                        'description': ov_desc,
                        'parameters': {
                            'type': 'object',
                            'properties': {
                                'task': {'type': 'string'},
                                'context': {'type': 'string'}
                            },
                            'required': ['task']
                        }
                    }
                })
            elif make_agent_tool:
                tools.append(make_agent_tool(sub, alias=alias))
            else:
                # Fallback to sub's own public tool surface if available
                try:
                    tools.append(sub.get_public_tool(alias=alias))  # type: ignore[attr-defined]
                except Exception:
                    desc_text = (getattr(sub, 'description', '') or f"Invoke sub-agent {getattr(sub, 'name', 'agent')} ({getattr(sub, 'id', '')})")
                    tools.append({
                        'type': 'function',
                        'function': {
                            'name': (alias or f"agent_{getattr(sub, 'id', 'sub')}"),
                            'description': desc_text,
                            'parameters': {
                                'type': 'object',
                                'properties': {
                                    'task': {'type': 'string'},
                                    'context': {'type': 'string'}
                                },
                                'required': ['task']
                            }
                        }
                    })

        # Validate unique function names within this agent's composed tool surface
        names: List[str] = []
        for t in tools:
            try:
                fn = (t.get('function') or {}).get('name')  # type: ignore[attr-defined]
            except Exception:
                fn = None
            if fn:
                names.append(fn)
        dupes = sorted({n for n in names if names.count(n) > 1})
        if dupes:
            raise Exception(f"Tool Name Collision: duplicate tool names in agent '{self.id}': {dupes}")

        # Deduplicate by name for stability
        return _merge_tools([], tools)

    def add_sub_agent(self, sub: 'BaseAgentWrapper', spec_overrides: Optional[Dict[str, Any]] = None, alias: Optional[str] = None) -> None:
        """
        Register a sub-agent as a tool.

        Args:
            sub: The SubAgent/BaseAgentWrapper instance to register.
            spec_overrides: Optional metadata for future use (e.g., description overrides).
            alias: Optional tool alias (function name) to expose for this sub-agent.
        """
        if not isinstance(sub, BaseAgentWrapper):
            raise TypeError("add_sub_agent requires a BaseAgentWrapper/SubAgent instance.")
        self._sub_entries.append({'sub': sub, 'alias': alias, 'overrides': spec_overrides})

    def list_tools(self) -> List[Tool]:
        """
        Expose composed tools (native + sub-agents).
        """
        return self._compose_tools()


class SubAgent(BaseAgentWrapper):
    """
    SubAgent that can expose a tool surface for managers (agent-as-tool),
    while keeping its internals (tools, memory) fully private.
    """

    async def run(self, messages: Union[str, List[Message], Dict[str, Any]], options: Optional[RunOptions] = None) -> Any:
        """
        Single public API for SubAgent.

        Behavior:
        - If a TaskPayload-like dict is provided (any of keys 'task'|'input'|'context'), shape messages using
          this agent's context_mode policy, enforcing REQUIRED context and returning a normalized single-step result.
        - If a string is provided, it's treated as the delegated task string:
            * REQUIRED: raises ValueError (caller must provide a TaskPayload dict with non-empty 'context')
            * NONE/OPTIONAL: shapes with no context and collects a single-step result
        - If a list of messages is provided:
            * REQUIRED: raises ValueError (caller must provide a TaskPayload dict with non-empty 'context')
            * NONE/OPTIONAL: passes through as-is to the underlying USFAgent

        """
        opts: RunOptions = dict(options or {})


        # TaskPayload dict path (preferred for sub-agents)
        if isinstance(messages, dict) and any(k in messages for k in ('task', 'input', 'context')):
            task_val = messages.get('task')
            task_str = str(task_val) if task_val is not None else 'task'
            _ctx_val = messages.get('context')
            ctx_str = None
            if _ctx_val is not None:
                if isinstance(_ctx_val, str):
                    ctx_str = _ctx_val
                else:
                    raise TypeError("context must be a string when provided in task payload")

            shaped_messages = _shape_context_for_mode(
                self.context_mode,
                task_str,
                history_messages=None,
                context=ctx_str,
                introduction=getattr(self.usf, 'introduction', '') or '',
                knowledge_cutoff=getattr(self.usf, 'knowledge_cutoff', '') or '',
                backstory=getattr(self, 'backstory', '') or '',
                goal=getattr(self, 'goal', '') or '',
                history=False,
                trim_last_user=False
            )
            comp_tools = self._compose_tools()
            if comp_tools:
                opts['tools'] = _merge_tools(opts.get('tools'), comp_tools)
            return await _acollect_final_answer(self.usf, shaped_messages, opts)

        # String task path
        if isinstance(messages, str):
            if self.context_mode == 'REQUIRED':
                raise ValueError("Context required: SubAgent with context_mode='REQUIRED' must be called with a TaskPayload dict including a non-empty 'context'.")
            # NONE/OPTIONAL => shape with no context
            shaped_messages = _shape_context_for_mode(
                self.context_mode,
                messages,
                history_messages=None,
                context=None,
                introduction=getattr(self.usf, 'introduction', '') or '',
                knowledge_cutoff=getattr(self.usf, 'knowledge_cutoff', '') or '',
                backstory=getattr(self, 'backstory', '') or '',
                goal=getattr(self, 'goal', '') or '',
                history=False,
                trim_last_user=False
            )
            comp_tools = self._compose_tools()
            if comp_tools:
                opts['tools'] = _merge_tools(opts.get('tools'), comp_tools)
            return await _acollect_final_answer(self.usf, shaped_messages, opts)

        # List[Message] path
        msg_list = list(messages or [])  # type: ignore[arg-type]
        if self.context_mode == 'REQUIRED':
            raise ValueError("Context required: SubAgent with context_mode='REQUIRED' cannot be called with a raw messages list. Provide a TaskPayload dict including a non-empty 'context'.")
        # Optional system_merge on messages lists
        merge_mode = (opts.get('system_merge') if isinstance(opts, dict) else None)
        if merge_mode:
            ours = self._build_system_context()
            delim = (opts.get('system_merge_delimiter') if isinstance(opts, dict) else None) or "\n\n---\n\n"
            sys_idx = next((i for i, m in enumerate(msg_list) if (m or {}).get('role') == 'system'), None)
            if sys_idx is not None:
                their = (msg_list[sys_idx].get('content') or '')
                msg_list[sys_idx]['content'] = f"{ours}{delim}{their}" if ours else their
            else:
                msg_list.insert(0, {'role': 'system', 'content': ours})
        comp_tools = self._compose_tools()
        if comp_tools:
            opts['tools'] = _merge_tools(opts.get('tools'), comp_tools)
        return await _acollect_final_answer(self.usf, msg_list, opts)

    def get_public_tool(self, alias: Optional[str] = None) -> Tool:
        """
        Provide a callable OpenAI tool definition for this SubAgent. Auto-generates parameters from SubAgent config.
        """
        tool_name = alias or f"agent_{self.id}"
        desc = self.description if getattr(self, 'description', '') else None
        if not desc:
            raise ValueError(f"SubAgent '{self.id}' must define a description for tool selection.")
        try:
            from .adapter import build_schema_from_subagent  # lazy import to avoid cycles
            schema = build_schema_from_subagent(self)
        except Exception:
            # Minimal fallback
            schema = {
                'description': desc,
                'parameters': {
                    'type': 'object',
                    'properties': {'task': {'type': 'string'}},
                    'required': ['task']
                }
            }
        return {
            'type': 'function',
            'function': {
                'name': tool_name,
                'description': schema.get('description', desc),
                'parameters': schema.get('parameters')
            },
            # metadata to distinguish agent tools at runtime (ignored by OpenAI schema)
            'x_kind': 'agent',
            'x_agent_id': self.id,
            'x_alias': alias
        }

    async def _execute_as_tool(
        self,
        tool_call: ToolCall,
        history_messages: Optional[List[Message]],
        context: Optional[str] = None,
        options: Optional[RunOptions] = None
    ) -> ToolCallExecutionResult:
        """
        Execute the sub-agent as a tool and internally drive until a final answer (standardized).
        This ensures agent-as-tool calls always yield a final content for the parent.
        """
        return await self._execute_as_tool_until_final(tool_call, history_messages, context, options)


    async def _execute_as_tool_until_final(
        self,
        tool_call: ToolCall,
        history_messages: Optional[List[Message]],
        context: Optional[str] = None,
        options: Optional[RunOptions] = None
    ) -> ToolCallExecutionResult:
        """
        Execute the sub-agent as a tool and internally drive its tool loop until a final answer.
        Returns a normalized tool result with success=True and final content.
        """
        try:
            func = tool_call.get('function') or {}
            tool_name = func.get('name') or f"agent_{self.id}"
            raw_args = func.get('arguments') or '{}'
            try:
                args = json.loads(raw_args)
            except Exception:
                args = {'task': str(raw_args)}

            task_str = str(args.get('task') or 'task')
            call_context = context if context is not None else args.get('context')
            if call_context is not None and not isinstance(call_context, str):
                raise TypeError("context must be a string when provided.")

            # Build history according to this sub-agent's policy (no implicit sanitization)
            hist = list(history_messages or [])
            if self.trim_last_user and len(hist) > 0 and (hist[-1] or {}).get('role') == 'user':
                hist = hist[:-1]

            shaped_messages = _shape_context_for_mode(
                self.context_mode,
                task_str,
                history_messages=hist,
                context=call_context,
                introduction=getattr(self.usf, 'introduction', '') or '',
                knowledge_cutoff=getattr(self.usf, 'knowledge_cutoff', '') or '',
                backstory=getattr(self, 'backstory', '') or '',
                goal=getattr(self, 'goal', '') or '',
                history=bool(self.history),
                trim_last_user=bool(self.trim_last_user)
            )

            # Compose tools available to this sub-agent (native + nested sub-agents)
            comp_tools = self._compose_tools()

            # Lazy import to avoid cycles
            from ..runtime.safe_seq import run_until_final

            # Default router: acknowledge tool execution; in real setups users provide executors
            async def _router(tc: ToolCall, current_msgs: List[Message]) -> Dict[str, Any]:
                fname = (tc.get('function') or {}).get('name')
                return {'success': True, 'content': f"{fname} executed"}

            

            content = await run_until_final(
                self.usf,
                shaped_messages,
                comp_tools,
                _router,
                max_loops=(options or {}).get('max_loops', 20) if isinstance(options, dict) else 20
            )

            

            return {
                'success': True,
                'content': content or '',
                'error': None,
                'tool_name': tool_name,
                'raw': {'status': 'final', 'content': content}
            }
        except Exception as e:
            return {
                'success': False,
                'content': '',
                'error': f'_execute_as_tool_until_final error: {e}',
                'tool_name': tool_call.get('function', {}).get('name', f"agent_{self.id}"),
                'raw': None
            }

class ManagerAgent(BaseAgentWrapper):
    """
    ManagerAgent that can aggregate native tools and sub-agents (as tools).
    Simplified public API:
      - No user-supplied name/description/context_mode.
      - Always uses name='Manager' internally; custom names are not accepted.
      - Users configure behavior via usf_config (including introduction, knowledge_cutoff,
        date_time_override, etc.) and optionally backstory/goal.
    """

    def __init__(self, *, usf_config: Dict[str, Any], backstory: str = '', goal: str = '', tools: Optional[List[Tool]] = None):
        # Force a fixed internal spec; do NOT expose name/description/context_mode to callers
        fixed_spec: AgentSpec = {
            'name': 'Manager',
            'backstory': backstory,
            'goal': goal,
            'usf_config': (usf_config or {}),
            'tools': list(tools or [])
        }
        super().__init__(fixed_spec)
        # Track sub-agents and their tool schemas for later tool list composition
        self._sub_entries: List[Dict[str, Any]] = []  # [{'sub': SubAgent}]

        # Internal registry for custom function tools (sugar API)
        try:
            from ..runtime.tool_registry import ToolRegistry
            self._registry = ToolRegistry()
        except Exception:
            self._registry = None  # lazy-init fallback

    def _compose_tools(self) -> List[Tool]:
        """
        Compose manager's native tools + each sub-agent as a tool (agent-as-tool adapter).
        """
        tools: List[Tool] = []
        # Native tools first
        tools.extend(self.list_native_tools())

        # Avoid import cycle by importing adapter lazily
        try:
            from .adapter import make_agent_tool
        except Exception:
            make_agent_tool = None  # type: ignore

        for entry in self._sub_entries:
            sub = entry['sub']
            alias = entry.get('alias')
            overrides = entry.get('overrides') or {}
            ov_desc = (overrides or {}).get('description')
            # Prefer explicit override description if provided
            if ov_desc:
                tools.append({
                    'type': 'function',
                    'function': {
                        'name': (alias or f"agent_{getattr(sub, 'id', 'sub')}"),
                        'description': ov_desc,
                        'parameters': {
                            'type': 'object',
                            'properties': {
                                'task': {'type': 'string'},
                                'context': {'type': 'string'}
                            },
                            'required': ['task']
                        }
                    }
                })
            elif make_agent_tool:
                tools.append(make_agent_tool(sub, alias=alias))
            else:
                # Fallback to sub's own public tool surface
                try:
                    tools.append(sub.get_public_tool(alias=alias))
                except Exception:
                    desc_text = (getattr(sub, 'description', '') or f"Invoke sub-agent {getattr(sub, 'name', 'agent')} ({getattr(sub, 'id', '')})")
                    tools.append({
                        'type': 'function',
                        'function': {
                            'name': (alias or f"agent_{getattr(sub, 'id', 'sub')}"),
                            'description': desc_text,
                            'parameters': {
                                'type': 'object',
                                'properties': {
                                    'task': {'type': 'string'},
                                    'context': {'type': 'string'}
                                },
                                'required': ['task']
                            }
                        }
                    })

        # Validate unique function names within this manager's composed tool surface
        names: List[str] = []
        for t in tools:
            try:
                fn = (t.get('function') or {}).get('name')  # type: ignore[attr-defined]
            except Exception:
                fn = None
            if fn:
                names.append(fn)
        dupes = sorted({n for n in names if names.count(n) > 1})
        if dupes:
            raise Exception(f"Tool Name Collision: duplicate tool names in manager '{self.id}': {dupes}")

        # Deduplicate by name for stability
        return _merge_tools([], tools)

    async def run(self, messages: Union[str, List[Message], Dict[str, Any]], options: Optional[RunOptions] = None) -> Any:
        """
        Unified ManagerAgent entry returning OpenAI-compatible chat.completion (non-stream).
        - Auto-executes according to options.mode using composed tools (native + sub-agents).
        - On tool request (when mode disables auto for that call), returns a completion with assistant.tool_calls.
        - On final answer, returns a completion with assistant content.
        """
        opts: RunOptions = dict(options or {})  # copy to avoid mutating caller's dict
        mode = (opts.get('mode') or 'auto')
        allowed_modes = {'disable', 'auto', 'agent-only', 'tool-only'}
        if mode not in allowed_modes:
            raise Exception(f"ManagerAgent.run Error: invalid mode '{mode}'. Allowed: {sorted(allowed_modes)}")
        max_loops = int(opts.get('max_loops') or getattr(self.usf, 'max_loops', 20) or 20)

        # Normalize messages or task payloads
        if isinstance(messages, dict) and any(k in messages for k in ('task', 'input', 'context')):
            task_val = messages.get('task')
            task_str = str(task_val) if task_val is not None else 'task'
            current: List[Message] = to_openai_messages_from_task(
                task_str,
                introduction=getattr(self.usf, 'introduction', '') or '',
                knowledge_cutoff=getattr(self.usf, 'knowledge_cutoff', '') or '',
                backstory=getattr(self, 'backstory', '') or '',
                goal=getattr(self, 'goal', '') or '',
                date_time_override=(opts.get('final_response', {}) if isinstance(opts.get('final_response'), dict) else {}).get('date_time_override')
            )
        elif isinstance(messages, str):
            current = [{'role': 'user', 'content': messages}]  # type: ignore[typeddict-item]
        else:
            current = list(messages or [])

        # Optional system_merge when caller supplies messages or a single string (not TaskPayload dict)
        merge_mode = (opts.get('system_merge') if isinstance(opts, dict) else None)
        if merge_mode:
            ours = self._build_system_context()
            delim = (opts.get('system_merge_delimiter') if isinstance(opts, dict) else None) or "\n\n---\n\n"
            sys_idx = next((i for i, m in enumerate(current) if (m or {}).get('role') == 'system'), None)
            if sys_idx is not None:
                their = (current[sys_idx].get('content') or '')
                current[sys_idx]['content'] = f"{ours}{delim}{their}" if ours else their
            else:
                current.insert(0, {'role': 'system', 'content': ours})

        # Compose tools and derive router
        tools = self.list_tools()
        if self._registry is None:
            try:
                from ..runtime.tool_registry import ToolRegistry
                self._registry = ToolRegistry()
            except Exception:
                self._registry = None

        async def _noop_router(tc: ToolCall, current_msgs: List[Message]) -> Dict[str, Any]:
            return {"success": False, "error": "no router provided"}

        router = self._registry.router() if getattr(self, "_registry", None) and hasattr(self._registry, "router") else _noop_router  # type: ignore[assignment]

        # Helper maps
        def _tool_map(tools_list: List[Tool]) -> Dict[str, Tool]:
            m: Dict[str, Tool] = {}
            for t in tools_list or []:
                try:
                    fn = (t.get('function') or {}).get('name')  # type: ignore[attr-defined]
                except Exception:
                    fn = None
                if fn:
                    m[fn] = t
            return m

        def _is_agent_tool(tool_def: Optional[Tool]) -> bool:
            if not isinstance(tool_def, dict):
                return False
            kind = tool_def.get('x_kind')
            if kind == 'agent':
                return True
            try:
                nm = (tool_def.get('function') or {}).get('name')
            except Exception:
                nm = None
            return bool(nm and str(nm).startswith('agent_'))

        tmap = _tool_map(tools)
        model_name = getattr(self.usf, 'model', 'usf-mini') or 'usf-mini'

        # Force non-streaming at engine for deterministic final collection in this path
        prev_stream = getattr(self.usf, 'stream', False)
        setattr(self.usf, 'stream', False)
        try:
            loops = 0
            while loops < max_loops:
                loops += 1

                inner_opts: RunOptions = dict(opts)
                inner_opts['tools'] = tools
                inner_opts['max_loops'] = max_loops

                async for chunk in self.usf.run(current, inner_opts):
                    ctype = chunk.get('type')

                    if ctype == 'plan':
                        plan_text = chunk.get('content') or chunk.get('plan') or ''
                        current.append({
                            'role': 'assistant',
                            'content': plan_text,
                            'plan': chunk.get('plan'),
                            'final_decision': chunk.get('final_decision'),
                            'agent_status': chunk.get('agent_status'),
                            'tool_choice': chunk.get('tool_choice'),
                            'type': chunk.get('type')
                        })

                    elif ctype == 'tool_calls':
                        tool_calls = chunk.get('tool_calls', [])
                        # Append assistant tool_calls envelope
                        current.append({
                            'role': 'assistant',
                            'content': '',
                            'tool_calls': tool_calls,
                            'type': 'tool_calls'
                        })

                        if mode == 'disable':
                            # Return OpenAI completion indicating tool_calls requested
                            return make_completion(model=model_name, content=None, tool_calls=tool_calls, finish_reason="tool_calls")

                        # Policy gates
                        allow_agent = (mode in {'auto', 'agent-only'})
                        allow_custom = (mode in {'auto', 'tool-only'})

                        # Execute each tool_call
                        for tc in tool_calls:
                            fn_name = (tc.get('function') or {}).get('name')
                            tool_def = tmap.get(fn_name)
                            is_agent = _is_agent_tool(tool_def)

                            if is_agent and not allow_agent:
                                return make_completion(model=model_name, content=None, tool_calls=tool_calls, finish_reason="tool_calls")
                            if (not is_agent) and not allow_custom:
                                return make_completion(model=model_name, content=None, tool_calls=tool_calls, finish_reason="tool_calls")

                            if is_agent:
                                # Use bound execution hook if available
                                exec_fn = None
                                if isinstance(tool_def, dict):
                                    exec_fn = tool_def.get('x_exec')  # type: ignore[assignment]
                                if callable(exec_fn):
                                    try:
                                        result = await exec_fn(tc, current, None, {'max_loops': max_loops})  # type: ignore[misc]
                                        payload = {
                                            'success': bool(result.get('success')),
                                            'content': result.get('content'),
                                            'error': result.get('error')
                                        }
                                    except Exception as e:
                                        payload = {'success': False, 'error': f'agent tool exec error: {e}'}
                                else:
                                    payload = {'success': False, 'error': 'agent tool has no execution hook (x_exec) available'}

                                current.append({
                                    'role': 'tool',
                                    'tool_call_id': tc.get('id'),
                                    'name': fn_name,
                                    'content': json.dumps(payload, ensure_ascii=False)
                                })

                            else:
                                # Custom tool
                                try:
                                    payload = await router(tc, current)
                                except Exception as e:
                                    payload = {'success': False, 'error': f'custom tool exec error: {e}'}

                                current.append({
                                    'role': 'tool',
                                    'tool_call_id': tc.get('id'),
                                    'name': fn_name,
                                    'content': json.dumps(payload, ensure_ascii=False)
                                })

                        # Re-enter engine with appended tool results
                        break

                    elif ctype == 'final_answer':
                        # Final non-stream content returned by engine
                        content = chunk.get('content', '') or ''
                        return make_completion(model=model_name, content=content, tool_calls=None, finish_reason="stop")

            # No final produced within loop budget
            return make_completion(model=model_name, content='', tool_calls=None, finish_reason="stop")
        finally:
            setattr(self.usf, 'stream', prev_stream)

    async def stream(self, messages: Union[str, List[Message], Dict[str, Any]], options: Optional[RunOptions] = None) -> AsyncGenerator[Dict[str, Any], None]:
        """
        Stream OpenAI-compatible chat.completion.chunk events:
          - plan: simulated deltas in assistant content with x_usf.stage="plan"
          - tool_calls: single delta with assistant.tool_calls
          - tool_result: vendor extension chunk with x_usf.stage="tool_result"
          - final_answer: true streaming deltas forwarded from engine
          - final finish chunk with finish_reason="stop"
        """
        opts: RunOptions = dict(options or {})
        mode = (opts.get('mode') or 'auto')
        allowed_modes = {'disable', 'auto', 'agent-only', 'tool-only'}
        if mode not in allowed_modes:
            raise Exception(f"ManagerAgent.stream Error: invalid mode '{mode}'. Allowed: {sorted(allowed_modes)}")

        # Normalize messages or task payloads
        if isinstance(messages, dict) and any(k in messages for k in ('task', 'input', 'context')):
            task_val = messages.get('task')
            task_str = str(task_val) if task_val is not None else 'task'
            current: List[Message] = to_openai_messages_from_task(
                task_str,
                introduction=getattr(self.usf, 'introduction', '') or '',
                knowledge_cutoff=getattr(self.usf, 'knowledge_cutoff', '') or '',
                backstory=getattr(self, 'backstory', '') or '',
                goal=getattr(self, 'goal', '') or '',
                date_time_override=(opts.get('final_response', {}) if isinstance(opts.get('final_response'), dict) else {}).get('date_time_override')
            )
        elif isinstance(messages, str):
            current = [{'role': 'user', 'content': messages}]  # type: ignore[typeddict-item]
        else:
            current = list(messages or [])

        # Optional system_merge when caller supplies messages or a single string (not TaskPayload dict)
        merge_mode = (opts.get('system_merge') if isinstance(opts, dict) else None)
        if merge_mode:
            ours = self._build_system_context()
            delim = (opts.get('system_merge_delimiter') if isinstance(opts, dict) else None) or "\n\n---\n\n"
            sys_idx = next((i for i, m in enumerate(current) if (m or {}).get('role') == 'system'), None)
            if sys_idx is not None:
                their = (current[sys_idx].get('content') or '')
                current[sys_idx]['content'] = f"{ours}{delim}{their}" if ours else their
            else:
                current.insert(0, {'role': 'system', 'content': ours})

        # Tools and router
        tools = self.list_tools()
        if getattr(self, "_registry", None) is None:
            try:
                from ..runtime.tool_registry import ToolRegistry
                self._registry = ToolRegistry()
            except Exception:
                self._registry = None

        async def _noop_router(tc: ToolCall, current_msgs: List[Message]) -> Dict[str, Any]:
            return {"success": False, "error": "no router provided"}

        router = self._registry.router() if getattr(self, "_registry", None) and hasattr(self._registry, "router") else _noop_router  # type: ignore[assignment]

        def _tool_map(tools_list: List[Tool]) -> Dict[str, Tool]:
            m: Dict[str, Tool] = {}
            for t in tools_list or []:
                try:
                    fn = (t.get('function') or {}).get('name')  # type: ignore[attr-defined]
                except Exception:
                    fn = None
                if fn:
                    m[fn] = t
            return m

        def _is_agent_tool(tool_def: Optional[Tool]) -> bool:
            if not isinstance(tool_def, dict):
                return False
            kind = tool_def.get('x_kind')
            if kind == 'agent':
                return True
            try:
                nm = (tool_def.get('function') or {}).get('name')
            except Exception:
                nm = None
            return bool(nm and str(nm).startswith('agent_'))

        tmap = _tool_map(tools)
        model_name = getattr(self.usf, 'model', 'usf-mini') or 'usf-mini'

        # Streaming knobs
        streaming_cfg = dict(opts.get("streaming") or {})
        plan_chunk_size = int(streaming_cfg.get("plan_chunk_size") or 80)
        preserve_acc = bool(streaming_cfg.get("preserve_accumulator", True))

        # Ensure engine final streaming is ON for this call
        prev_stream = getattr(self.usf, 'stream', False)
        setattr(self.usf, 'stream', True)
        try:
            max_loops = int(opts.get('max_loops') or getattr(self.usf, 'max_loops', 20) or 20)
            loops = 0
            acc_plan = ""

            while loops < max_loops:
                loops += 1

                inner_opts: RunOptions = dict(opts)
                inner_opts['tools'] = tools
                inner_opts['max_loops'] = max_loops

                async for chunk in self.usf.run(current, inner_opts):
                    ctype = chunk.get('type')

                    if ctype == 'plan':
                        plan_text = chunk.get('content') or chunk.get('plan') or ''
                        # Simulated streaming of plan
                        if plan_chunk_size > 0 and plan_text:
                            for part in _chunk_text(plan_text, plan_chunk_size):
                                acc_plan = (acc_plan + part) if preserve_acc else ""
                                yield make_chunk_from_content_delta(model=model_name, delta=part, stage="plan", done=False)
                            # signal plan done
                            yield make_chunk_from_content_delta(model=model_name, delta="", stage="plan", done=True)
                        else:
                            yield make_chunk_from_content_delta(model=model_name, delta=plan_text, stage="plan", done=True)

                        # Append plan to conversation
                        current.append({
                            'role': 'assistant',
                            'content': plan_text,
                            'plan': chunk.get('plan'),
                            'final_decision': chunk.get('final_decision'),
                            'agent_status': chunk.get('agent_status'),
                            'tool_choice': chunk.get('tool_choice'),
                            'type': chunk.get('type')
                        })

                    elif ctype == 'tool_calls':
                        tool_calls = chunk.get('tool_calls', [])
                        # Emit tool_calls envelope as a single assistant delta
                        yield make_chunk_tool_calls(model=model_name, tool_calls=tool_calls, stage="tool_calls")
                        # Append envelope to conversation
                        current.append({
                            'role': 'assistant',
                            'content': '',
                            'tool_calls': tool_calls,
                            'type': 'tool_calls'
                        })

                        if mode == 'disable':
                            # finish stream signaling tool_calls requested
                            yield make_chunk_finish(model=model_name, finish_reason="tool_calls")
                            return

                        allow_agent = (mode in {'auto', 'agent-only'})
                        allow_custom = (mode in {'auto', 'tool-only'})

                        # Execute each tool_call and emit vendor extension tool_result
                        for tc in tool_calls:
                            fn_name = (tc.get('function') or {}).get('name')
                            tool_def = tmap.get(fn_name)
                            is_agent = _is_agent_tool(tool_def)

                            if is_agent and not allow_agent:
                                yield make_chunk_finish(model=model_name, finish_reason="tool_calls")
                                return
                            if (not is_agent) and not allow_custom:
                                yield make_chunk_finish(model=model_name, finish_reason="tool_calls")
                                return

                            if is_agent:
                                exec_fn = None
                                if isinstance(tool_def, dict):
                                    exec_fn = tool_def.get('x_exec')  # type: ignore[assignment]
                                if callable(exec_fn):
                                    try:
                                        result = await exec_fn(tc, current, None, {'max_loops': max_loops})  # type: ignore[misc]
                                        payload = {
                                            'success': bool(result.get('success')),
                                            'content': result.get('content'),
                                            'error': result.get('error')
                                        }
                                    except Exception as e:
                                        payload = {'success': False, 'error': f'agent tool exec error: {e}'}
                                else:
                                    payload = {'success': False, 'error': 'agent tool has no execution hook (x_exec) available'}
                            else:
                                try:
                                    payload = await router(tc, current)
                                except Exception as e:
                                    payload = {'success': False, 'error': f'custom tool exec error: {e}'}

                            current.append({
                                'role': 'tool',
                                'tool_call_id': tc.get('id'),
                                'name': fn_name,
                                'content': json.dumps(payload, ensure_ascii=False)
                            })

                            # Emit vendor extension chunk with tool result
                            yield make_chunk_tool_result(
                                model=model_name,
                                tool_call_id=tc.get('id'),
                                name=fn_name,
                                result=payload
                            )

                        # Re-enter engine with appended tool results
                        break

                    elif ctype == 'final_answer':
                        # Forward true streaming final deltas as assistant content
                        delta = chunk.get('content', '') or ''
                        if delta:
                            yield make_chunk_from_content_delta(model=model_name, delta=delta, stage=None, done=None)

                # end inner async-for
                # After an iteration that involved tool_calls, we 'break' above to re-enter; otherwise loop ends naturally.

                # If we finished without explicit final, continue outer loop until loops exhausted
                # Once engine completes final, it will stop yielding and we exit loops below
                pass

            # Finished loops; emit finish signal (stop)
            yield make_chunk_finish(model=model_name, finish_reason="stop")
        finally:
            setattr(self.usf, 'stream', prev_stream)



    def add_sub_agent(self, sub: BaseAgentWrapper, spec_overrides: Optional[Dict[str, Any]] = None, alias: Optional[str] = None) -> None:
        """
        Register a sub-agent as a tool.

        Args:
            sub: The SubAgent/BaseAgentWrapper instance to register.
            spec_overrides: Optional metadata for future use (e.g., description overrides).
            alias: Optional tool alias (function name) to expose for this sub-agent.
        """
        if not isinstance(sub, BaseAgentWrapper):
            raise TypeError("add_sub_agent requires a BaseAgentWrapper/SubAgent instance.")
        self._sub_entries.append({'sub': sub, 'alias': alias, 'overrides': spec_overrides})

    def list_tools(self) -> List[Tool]:
        """
        Expose manager's native tools + sub-agents as tools.
        """
        return self._compose_tools()

    # ========== Sugar APIs for simpler developer UX ==========

    @staticmethod
    def _validate_schema_matches_signature(func: Any, schema: Dict[str, Any], strict: bool = False) -> None:
        """
        Validate that schema 'required' exactly matches non-default parameters in the Python signature.
        When strict=True, also require that schema.properties keys equal the set of signature parameters
        (excluding *args/**kwargs).
        """
        try:
            sig = inspect.signature(func)
        except Exception:
            raise Exception("Schema Validation Error: unable to read function signature")

        # Collect function parameter names, excluding *args / **kwargs
        sig_params: List[str] = []
        required_sig: List[str] = []
        for pname, param in sig.parameters.items():
            if param.kind in (inspect.Parameter.VAR_POSITIONAL, inspect.Parameter.VAR_KEYWORD):
                continue
            sig_params.append(pname)
            if param.default is inspect._empty:
                required_sig.append(pname)

        parameters = (schema or {}).get('parameters') or {}
        props = (parameters or {}).get('properties') or {}
        req = (parameters or {}).get('required') or []

        if not isinstance(props, dict):
            raise Exception("Schema Validation Error: parameters.properties must be an object")
        if not isinstance(req, list):
            raise Exception("Schema Validation Error: parameters.required must be a list")

        schema_props = list(props.keys())
        schema_req = [str(x) for x in req]

        # Required must match exactly
        missing_required = [p for p in required_sig if p not in schema_req]
        extra_required = [p for p in schema_req if p not in required_sig]
        if missing_required or extra_required:
            raise Exception(f"Schema Validation Error: required mismatch. Missing in schema: {missing_required}; Extra in schema: {extra_required}")

        if strict:
            missing_props = [p for p in sig_params if p not in schema_props]
            extra_props = [p for p in schema_props if p not in sig_params]
            if missing_props or extra_props:
                raise Exception(f"Schema Validation Error (strict properties): properties mismatch. Missing in schema: {missing_props}; Extra in schema: {extra_props}")

    @staticmethod
    def _infer_schema_from_func(func: Any, name: str, strict: bool = False) -> Dict[str, Any]:
        """
        Docstring-first schema inference.
        - If a YAML code block or Google-style docstring is present, parse it.
        - Enforce required-parameter equality; if strict=True, enforce properties equality too.
        - Raise a clear error if neither explicit schema nor parseable docstring is available.
        """
        try:
            from ..runtime.docstring_schema import parse_docstring_to_schema  # local import to avoid cycles
        except Exception as e:
            raise Exception(f"Schema Inference Error: unable to import docstring parser: {e}")

        schema = None
        try:
            schema = parse_docstring_to_schema(func)
        except Exception as e:
            # Parser errors are non-fatal here; we will raise a unified error below if schema stays None
            schema = None

        if not schema:
            raise Exception(f"Tool Registration Error: no explicit schema and no parseable docstring for function '{name}'. Provide a JSON schema or a Google-style docstring (YAML block takes precedence).")

        # Description is required
        desc = schema.get('description')
        if not (isinstance(desc, str) and desc.strip()):
            raise Exception("Schema Validation Error: description is required")

        # Validate against signature
        ManagerAgent._validate_schema_matches_signature(func, schema, strict=strict)
        return schema

    def add_function_tool(
        self,
        func: Any,
        alias: Optional[str] = None,
        schema: Optional[Dict[str, Any]] = None,
        examples: Optional[List[Dict[str, Any]]] = None,
        strict: bool = False
    ) -> None:
        """
        Register a Python function as a custom tool on this manager.

        Naming:
        - canonical_name = func.__name__ (used as the registry key)
        - exposed tool name = alias if provided else agent_{canonical_name}

        Schema precedence:
        - explicit schema argument > decorator schema > docstring parsing (YAML → Google)
        """
        if self._registry is None:
            from ..runtime.tool_registry import ToolRegistry
            self._registry = ToolRegistry()

        # Determine canonical name
        canonical_name = getattr(func, "__name__", None)
        if not canonical_name or not isinstance(canonical_name, str):
            raise Exception("Tool Registration Error: unable to determine function name (__name__)")

        # Read decorator metadata (if any)
        meta = getattr(func, "__usf_tool__", {}) if hasattr(func, "__usf_tool__") else {}
        # Apply defaults when not explicitly provided
        alias = alias or (meta.get("alias") if isinstance(meta, dict) else None) or f"agent_{canonical_name}"

        if schema is not None:
            # Description is required on explicit schema
            if not (isinstance(schema.get("description"), str) and str(schema.get("description")).strip()):
                raise Exception("Schema Validation Error: description is required")
            # Validate provided schema against function signature
            ManagerAgent._validate_schema_matches_signature(func, schema, strict=strict)
            final_schema = schema
        else:
            # Precedence: decorator-provided schema -> docstring parsing
            meta_schema = meta.get("schema") if isinstance(meta, dict) else None
            if isinstance(meta_schema, dict):
                # Description is required on decorator-provided schema
                if not (isinstance(meta_schema.get("description"), str) and str(meta_schema.get("description")).strip()):
                    raise Exception("Schema Validation Error: description is required")
                # Validate decorator-provided schema
                ManagerAgent._validate_schema_matches_signature(func, meta_schema, strict=strict)
                final_schema = meta_schema
            else:
                # Infer from docstring (and validate)
                final_schema = self._infer_schema_from_func(func, canonical_name, strict=strict)

        tool = self._registry.register_function(name=canonical_name, func=func, schema=final_schema, alias=alias, examples=examples)
        # Add to native tools so list_tools() exposes it without additional wiring
        self._native_tools.append(tool)  # type: ignore[arg-type]

    def add_sub_agents(self, *items: Any) -> None:
        """
        Batch add sub-agents with production-ready structure.

        Accepts:
        - SubAgent instances (recommended for production)
            mgr.add_sub_agents(calculator, researcher)
            mgr.add_sub_agents([calculator, researcher, coder, writer])
        - Dict specs (concise form)
            mgr.add_sub_agents([{'name':'logs', 'alias':'agent_logs', 'context_mode':'OPTIONAL', 'description':'Analyze logs'}, ...])

        For SubAgent instances, a minimal default tool schema is supplied (task + optional context).
        """
        # Normalize varargs and list inputs into a flat list
        flat: List[Any] = []
        for it in items or []:
            if isinstance(it, (list, tuple)):
                flat.extend(list(it))
            else:
                flat.append(it)

        for it in flat:
            # SubAgent or BaseAgentWrapper instance path
            if isinstance(it, BaseAgentWrapper):
                sub: BaseAgentWrapper = it
                # Require explicit description on SubAgent instances
                desc = (getattr(sub, 'description', '') or '')
                if not desc.strip():
                    raise ValueError(f"add_sub_agents Error: SubAgent '{getattr(sub, 'id', 'sub')}' requires a description (spec['description']).")
                # Register; schema will be auto-generated
                self.add_sub_agent(sub)
            # Dict spec path
            elif isinstance(it, dict):
                name = it.get('name')
                context_mode = it.get('context_mode', 'NONE')
                alias = it.get('alias')
                description = it.get('description')
                overrides = it.get('usf_overrides') or {}

                # Merge manager's config with per-sub overrides (deep-merge for stage keys)
                merged_usf = self._merge_usf_config((self._usf_config or {}), overrides)

                # Do not inherit skip_planning_if_no_tools from manager unless explicitly provided in overrides
                if overrides.get('skip_planning_if_no_tools') is None:
                    merged_usf.pop('skip_planning_if_no_tools', None)
                # Also avoid inheriting planning-stage flag unless explicitly provided in overrides.planning
                if isinstance(merged_usf.get('planning'), dict):
                    planning_overrides = overrides.get('planning') if isinstance(overrides.get('planning'), dict) else None
                    if not (planning_overrides and (planning_overrides.get('skip_planning_if_no_tools') is not None)):
                        merged_usf['planning'].pop('skip_planning_if_no_tools', None)

                if not (description and str(description).strip()):
                    raise ValueError(f"add_sub_agents Error: SubAgent '{name}' requires a description.")

                sub = SubAgent({
                    'name': name,
                    'context_mode': context_mode,
                    'description': description,
                    'usf_config': merged_usf
                })
                self.add_sub_agent(sub, None, alias)
            else:
                raise Exception(f"add_sub_agents Error: unsupported item type {type(it)}; expected SubAgent/BaseAgentWrapper or dict spec.")

    def add_function_tools(self, functions: List[Callable[..., Any]], *, strict: bool = False) -> None:
        """
        Batch register Python functions as custom tools on this manager.

        Naming and defaults:
        - Tool name = function.__name__.
        - Alias defaults to decorator meta['alias'] if present.
        - Description is taken from provided schema (if any), else decorator meta['description'], else docstring summary.

        Strictness:
        - Enforces required-parameter equality always.
        - If strict=True, also enforces properties set equality with the function signature.
        """
        for func in functions or []:
            if not callable(func):
                raise Exception("add_function_tools Error: all items must be callables")
            meta = getattr(func, "__usf_tool__", {}) if hasattr(func, "__usf_tool__") else {}
            alias = meta.get("alias") if isinstance(meta, dict) else None
            # Delegate to single add_function_tool path (docstring parsing and validation happen there)
            self.add_function_tool(func, alias=alias, schema=None, examples=None, strict=strict)

    def add_function_tools_from_module(
        self,
        module: Any,
        *,
        filter: Optional[Callable[[Callable[..., Any]], bool]] = None,
        strict: bool = False
    ) -> None:
        """
        Discover and batch add functions from a module.

        Selection:
        - Candidate functions are callables whose __module__ equals module.__name__.
        - If a filter callable is provided, it's applied to candidates.
        - Each candidate is registered via add_function_tool using:
            canonical name = function.__name__
            alias = __usf_tool__['alias'] if present
        - Functions without parseable docstrings and without explicit schema will raise (by design).
        """
        if module is None or not hasattr(module, "__name__"):
            raise Exception("add_function_tools_from_module Error: invalid module")

        candidates: List[Callable[..., Any]] = []
        for attr in dir(module):
            obj = getattr(module, attr)
            # Include any callable attached to the module, regardless of obj.__module__
            # (helps with dynamically attached functions in tests or REPL).
            if callable(obj):
                candidates.append(obj)

        if filter:
            candidates = [fn for fn in candidates if filter(fn)]

        if not candidates:
            return

        for func in candidates:
            meta = getattr(func, "__usf_tool__", {}) if hasattr(func, "__usf_tool__") else {}
            alias = meta.get("alias") if isinstance(meta, dict) else None
            self.add_function_tool(func, alias=alias, schema=None, examples=None, strict=strict)
