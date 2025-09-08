from typing import TypedDict, Literal, Optional, List, Dict, Any, Union

# Basic aliases
AgentId = str

# Context passing/inheritance policy for sub-agents
ContextMode = Literal['NONE', 'OPTIONAL', 'REQUIRED']


class TaskPayload(TypedDict, total=False):
    """
    High-level payload for invoking a sub-agent as a tool (task-first pattern).
    """
    task: str  # Task name/description/instruction
    context: Optional[str]  # Additional context passed when context_mode is OPTIONAL/REQUIRED
    metadata: Optional[Dict[str, Any]]  # Correlation IDs, run IDs, custom info


class AgentSpec(TypedDict, total=False):
    """
    Public specification for registering an agent in the registry/orchestrator.
    """
    id: AgentId
    name: str
    backstory: Optional[str]
    goal: Optional[str]
    context_mode: ContextMode  # Default policy for this agent when acting as sub-agent
    # Per-agent history policy (defaults False if not provided)
    history: bool
    trim_last_user: bool
    usf_config: 'USFAgentConfig'  # Reuse existing config typing from types package
    tools: Optional[List['Tool']]  # Native external tools (manager/generic agents only)


class RouteMessage(TypedDict, total=False):
    """
    Routing envelope for direct or parent-mediated communication between agents.
    """
    from_agent: AgentId
    to_agent: AgentId
    payload: Union['TaskPayload', List['Message']]  # Either a task payload or OpenAI-format messages
    route_via: Literal['direct', 'parent']  # Explicit route choice
    parent_id: Optional[AgentId]  # Applicable when route_via='parent'


class ToolCallExecutionResult(TypedDict, total=False):
    """
    Normalized result for sub-agent-as-tool execution.
    """
    success: bool
    content: str  # Summarized result or response text intended for inclusion in conversation
    error: Optional[str]
    tool_name: str
    raw: Any  # Raw tool/sub-agent response (kept internal and private)


__all__ = [
    'AgentId',
    'ContextMode',
    'TaskPayload',
    'AgentSpec',
    'RouteMessage',
    'ToolCallExecutionResult',
]
