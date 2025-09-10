from typing import List, Dict, Any, Optional

from ..types import Message  # OpenAI-format message type
from ..types import RunOptions  # For completeness if needed by callers
from ..types import Tool  # Type reference (not used here directly)

from ..types.multi_agent import (
    ContextMode,
)


def _task_to_user_content(task: str) -> str:
    """
    Accepts a string task and returns it.
    Enforces string-only tasks for sub-agents.
    """
    if not isinstance(task, str):
        raise TypeError("task must be a string")
    return task


def to_openai_messages_from_task(
    task: str,
    introduction: str = '',
    knowledge_cutoff: str = '',
    backstory: str = '',
    goal: str = '',
    date_time_override: Optional[Dict[str, Any]] = None
) -> List[Message]:
    """
    Construct minimal OpenAI-format messages from a string task for an agent acting
    as a main entry point (message-based flow). The final response stage will add
    system/date context. For planning/tool-calling we just need user intent.
    """
    content = _task_to_user_content(task)
    return [
        {'role': 'user', 'content': content}
    ]


def _shape_context_for_mode(
    mode: ContextMode,
    task: str,
    history_messages: Optional[List[Message]] = None,
    *,
    context: Optional[str] = None,
    introduction: str = '',
    knowledge_cutoff: str = '',
    backstory: str = '',
    goal: str = '',
    history: bool = False,
    trim_last_user: bool = False
) -> List[Message]:
    """
    INTERNAL: Build OpenAI-format messages for sub-agent execution using ContextMode policy
    and history flags. Not part of the public API (subject to change).

    Contract (strict):
    - task: required string
    - context: string when provided

    Modes:
    - NONE: context must be None. Do not include parent history.
    - OPTIONAL: context may be provided (string). Parent history included only when history=True.
    - REQUIRED: context must be a non-empty string. Parent history included only when history=True.

    History handling:
    - When history=True, append history_messages as-is. If trim_last_user=True and the last
      message role is 'user', drop that last user message before appending. When history=False,
      parent messages are not included.

    System prompt:
    - Constructed from any non-empty of introduction, knowledge_cutoff, backstory, goal joined by newlines.
    - If a context string is provided (non-empty), append:
        "### Additional Context for this current task\n" + context
      to the same system message.
    - If none of the system fields nor context are provided, no system message is added.

    Final message order:
      [system?] + [history?] + [{'role':'user','content': task}]
    """
    # Validate task/context types
    if not isinstance(task, str):
        raise TypeError("task must be a string")
    if context is not None and not isinstance(context, str):
        raise TypeError("context must be a string when provided")

    # Validate mode/context invariant
    if mode == 'NONE':
        context = None  # ensure ignored
    elif mode == 'REQUIRED':
        if not (isinstance(context, str) and context.strip()):
            # Enforce REQUIRED invariant; raise to make violations visible to callers
            raise ValueError("Context required: 'REQUIRED' mode expects a non-empty context string.")

    messages: List[Message] = []

    # Build system content
    sys_parts: List[str] = []
    if introduction and isinstance(introduction, str) and introduction.strip():
        sys_parts.append(introduction.strip())
    if knowledge_cutoff and isinstance(knowledge_cutoff, str) and knowledge_cutoff.strip():
        sys_parts.append(knowledge_cutoff.strip())
    if backstory and isinstance(backstory, str) and backstory.strip():
        sys_parts.append(backstory.strip())
    if goal and isinstance(goal, str) and goal.strip():
        sys_parts.append(goal.strip())

    system_prompt = "\n".join(sys_parts).strip()

    sys_content_parts: List[str] = []
    if system_prompt:
        sys_content_parts.append(system_prompt)
    if context and isinstance(context, str) and context.strip():
        sys_content_parts.append("### Additional Context for this current task")
        sys_content_parts.append(context.strip())

    if sys_content_parts:
        messages.append({'role': 'system', 'content': "\n".join(sys_content_parts)})

    # History handling
    if history and history_messages:
        base_hist = list(history_messages or [])
        if trim_last_user and len(base_hist) > 0 and (base_hist[-1] or {}).get('role') == 'user':
            base_hist = base_hist[:-1]
        messages.extend(base_hist)

    # Always append the delegated task as the final user instruction
    messages.append({'role': 'user', 'content': _task_to_user_content(task)})

    return messages


def build_messages_for_final(
    messages: List[Message],
    introduction: str,
    knowledge_cutoff: str,
    backstory: str,
    goal: str,
    date_time_override: Optional[Dict[str, Any]]
) -> List[Message]:
    """
    Wrapper for final-response message shaping that leverages the existing
    process_messages_for_final_response pipeline to ensure consistency
    (introduction, knowledge cutoff, and timestamp injection).
    """
    from ..usfMessageHandler import process_messages_for_final_response  # Local import to avoid cycles
    return process_messages_for_final_response(
        messages=messages,
        date_time_override=date_time_override,
        backstory=backstory or '',
        goal=goal or '',
        introduction=introduction or '',
        knowledge_cutoff=knowledge_cutoff or ''
    )
