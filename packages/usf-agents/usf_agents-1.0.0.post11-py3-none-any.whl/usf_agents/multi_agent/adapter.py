import json
from typing import Dict, Any, Optional, List, TYPE_CHECKING

from ..types import Tool, ToolCall, Message, RunOptions
from ..types.multi_agent import (
    ContextMode,
    TaskPayload,
    ToolCallExecutionResult,
)

if TYPE_CHECKING:
    from .base import SubAgent  # for type hints only


def build_schema_from_subagent(sub_agent: 'SubAgent') -> Dict[str, Any]:
    """
    Auto-generate a public JSON schema for invoking a SubAgent as a tool.
    - Always includes a required 'task' parameter (string).
    - 'task' description pulled from sub_agent.task_placeholder when available.
    - Adds 'context' (string) based on sub_agent.context_mode:
        * NONE: omitted
        * OPTIONAL: present but optional
        * REQUIRED: present and required
    """
    desc = getattr(sub_agent, 'description', '') or ''
    if not desc.strip():
        raise ValueError(f"SubAgent '{getattr(sub_agent, 'id', '')}' must define a description for tool selection.")

    params: Dict[str, Any] = {
        'type': 'object',
        'properties': {
            'task': {
                'type': 'string',
                'description': getattr(sub_agent, 'task_placeholder', None) or 'Task for the agent'
            }
        },
        'required': ['task']
    }

    mode = getattr(sub_agent, 'context_mode', 'NONE')
    ctx_desc = "Additional context for this subtask. Include relevant background, constraints, instructions, or guidelines."
    if mode == 'REQUIRED':
        (params['properties'])['context'] = {'type': 'string', 'description': ctx_desc}
        params['required'] = list(set(params.get('required', []) + ['context']))
    elif mode == 'OPTIONAL':
        (params['properties'])['context'] = {'type': 'string', 'description': ctx_desc}

    return {
        'description': desc,
        'parameters': params
    }


def make_agent_tool(sub_agent: 'SubAgent', alias: Optional[str] = None) -> Tool:
    """
    Generate an OpenAI-compatible tool definition that invokes a SubAgent.
    The tool does not expose the sub-agent's internal tools or memory.
    """
    tool_name = alias or f"agent_{sub_agent.id}"
    schema = build_schema_from_subagent(sub_agent)
    return {
        'type': 'function',
        'function': {
            'name': tool_name,
            'description': schema.get('description'),
            'parameters': schema.get('parameters')
        },
        # metadata to distinguish agent tools at runtime (ignored by OpenAI schema)
        'x_kind': 'agent',
        'x_agent_id': getattr(sub_agent, 'id', None),
        'x_alias': alias,
        'x_exec': getattr(sub_agent, '_execute_as_tool', None)
    }


async def handle_agent_tool_call(
    sub_agent: 'SubAgent',
    tool_call: ToolCall,
    history_messages: Optional[List[Message]],
    mode: ContextMode,
    context_param: Optional[Dict[str, Any]] = None,
    options: Optional[RunOptions] = None
) -> ToolCallExecutionResult:
    """
    Execute a SubAgent when invoked via tool-calls coming from a manager agent.
    This handles argument parsing, context shaping, and returns a normalized result.
    """
    try:
        func = tool_call.get('function') or {}
        tool_name = func.get('name') or f"agent_{sub_agent.id}"
        raw_args = func.get('arguments') or '{}'
        try:
            args = json.loads(raw_args)
        except Exception:
            args = {'task': str(raw_args)}

        # Enforce string-only task/context for subagent shaping
        task_str = str(args.get('task') or 'task')

        # Allow explicit context override at call-time (mapped from 'context' in public schema)
        call_context = context_param if context_param is not None else args.get('context')
        if call_context is not None and not isinstance(call_context, str):
            raise TypeError("context must be a string when provided.")

        # Temporarily override policy if mode is provided explicitly
        # We do not mutate sub_agent.context_mode, only use for this call.
        from .context import _shape_context_for_mode
        # Build history according to the sub-agent's policy (no implicit sanitization)
        hist = list(history_messages or [])
        if getattr(sub_agent, 'trim_last_user', False) and len(hist) > 0 and (hist[-1] or {}).get('role') == 'user':
            hist = hist[:-1]

        shaped_messages = _shape_context_for_mode(
            mode,
            task_str,
            history_messages=hist,
            context=call_context,
            introduction=getattr(sub_agent.usf, 'introduction', '') or '',
            knowledge_cutoff=getattr(sub_agent.usf, 'knowledge_cutoff', '') or '',
            backstory=getattr(sub_agent, 'backstory', '') or '',
            goal=getattr(sub_agent, 'goal', '') or '',
            history=bool(getattr(sub_agent, 'history', False)),
            trim_last_user=bool(getattr(sub_agent, 'trim_last_user', False))
        )

        # Use the underlying USFAgent to run with shaped messages
        from .base import _acollect_final_answer
        collected = await _acollect_final_answer(sub_agent.usf, shaped_messages, options)

        if collected['status'] == 'final':
            return {
                'success': True,
                'content': collected.get('content') or '',
                'error': None,
                'tool_name': tool_name,
                'raw': collected
            }
        if collected['status'] == 'tool_calls':
            return {
                'success': False,
                'content': '',
                'error': 'Sub-agent requested tool_calls; external execution required.',
                'tool_name': tool_name,
                'raw': collected
            }
        return {
            'success': False,
            'content': '',
            'error': 'Sub-agent returned no final content.',
            'tool_name': tool_name,
            'raw': collected
        }
    except Exception as e:
        return {
            'success': False,
            'content': '',
            'error': f'handle_agent_tool_call error: {e}',
            'tool_name': tool_call.get('function', {}).get('name', f"agent_{sub_agent.id}"),
            'raw': None
        }
