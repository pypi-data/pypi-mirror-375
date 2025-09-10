from .multi_agent.base import BaseAgentWrapper, SubAgent, ManagerAgent
from .multi_agent.registry import AgentRegistry
from .types import (
    ExecutionMode,
    RunOptions,
    Message,
    Tool,
    ToolCall,
)

# Flow A — Per-request ephemeral agent utilities
from .runtime.ephemeral import (
    build_ephemeral_config,
    create_ephemeral_agent,
    run_ephemeral,
    run_ephemeral_final,
    run_many_parallel,
)

__all__ = [
    # Public API
    'SubAgent',
    'ManagerAgent',
    'AgentRegistry',
    # Flow A — Per-request ephemeral agent utilities
    'build_ephemeral_config',
    'create_ephemeral_agent',
    'run_ephemeral',
    'run_ephemeral_final',
    'run_many_parallel',
    # Types
    'ExecutionMode',
    'RunOptions',
    'Message',
    'Tool',
    'ToolCall',
]

__version__ = '1.1.0.post12'
