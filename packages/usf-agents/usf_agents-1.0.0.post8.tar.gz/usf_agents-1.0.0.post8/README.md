# USF Agents (Python SDK)

USF Agents — Simplify the Complex, Amplify the Intelligent for Enterprise

Production-grade Python SDK to design, orchestrate, and safely execute multi-agent systems with OpenAI-compatible APIs. Built for developers who need control, visibility, and reliability for simple to complex use cases.

- Homepage: https://us.inc
- Docs: https://us.inc/docs
- PyPI: https://pypi.org/project/usf-agents/

---

## Overview

USF Agents is a lightweight multi-agent orchestration SDK that streamlines:

- Planning → tool execution → final answers with predictable policies
- Docstring/YAML-driven tool schemas (no verbose JSON required)
- Sub-agent composition (manager + sub‑agents) in a few lines
- OpenAI-compatible runtime and types

Designed for:

- Developers needing a simple, controllable agent runtime with OpenAI-compatible APIs

---

## Key Features

- Docstring/YAML-driven tool schemas with validation
- `@tool` decorator for defaults or explicit schema
- Batch tool registration and module discovery
- Auto Execution Modes: `disable` | `auto` | `agent-only` | `tool-only`
- Multi-agent orchestration (manager + sub-agents)

Learn more:

- Tools overview: https://us.inc/docs/tools/overview
- Decorator: https://us.inc/docs/tools/decorator
- Docstrings: https://us.inc/docs/tools/docstrings
- Explicit schema: https://us.inc/docs/tools/explicit-schema
- Type mapping: https://us.inc/docs/tools/type-mapping
- Registry & Batching: https://us.inc/docs/tools/registry-and-batch-tool-registration
- Multi-agent overview: https://us.inc/docs/multi-agent/overview
- Execution Modes: https://us.inc/docs/multi-agent/auto-execution-modes
- Context Modes: https://us.inc/docs/multi-agent/context-modes
- Manager-driven Delegation: https://us.inc/docs/multi-agent/manager-driven-delegation
- Skip planning when no tools: https://us.inc/docs/multi-agent/skip-planning-no-tools
- Custom Instruction: https://us.inc/docs/multi-agent/custom-instruction

---

## ManagerAgent API rules

- Constructor: `ManagerAgent(usf_config: dict, backstory: str = '', goal: str = '', tools: list | None = None)`
  - Only `usf_config` is required at construction time.
  - Does not accept `name`, `description`, or `context_mode`. The internal name is always "Manager" (id "manager").
- Configure system context via `usf_config.introduction` and `usf_config.knowledge_cutoff`, plus optional constructor `backstory`/`goal`.
- When calling `await ManagerAgent.run(...)` with a TaskPayload-like dict, only the `"task"` field is used; `"context"` is ignored (Manager shapes its own context).
- Modes allowed: `'disable' | 'auto' | 'agent-only' | 'tool-only'`.

---

## Advantages

- Developer-friendly: fewer lines, strong defaults, and explicit controls
- Compatibility: OpenAI-compatible APIs and multiple providers
- Extensibility: simple tool creation, sub-agent orchestration, registry flows
- Operational simplicity: minimal setup, predictable behavior

---

## Installation & Requirements

Requirements

- Python 3.8+
- USF API key (set as environment variable `USF_API_KEY`)

Install the SDK

- pip (recommended):
```bash
pip install usf-agents
```

- uv:
```bash
uv add usf-agents
```

- poetry:
```bash
poetry add usf-agents
```

- pdm:
```bash
pdm add usf-agents
```

Set your API key

- macOS/Linux:
```bash
export USF_API_KEY=YOUR_KEY
```

- Windows PowerShell:
```powershell
$env:USF_API_KEY="YOUR_KEY"
```

- Windows cmd:
```bat
set USF_API_KEY=YOUR_KEY
```

Optional: Virtual environment

```bash
python -m venv .venv
# macOS/Linux
source .venv/bin/activate
# Windows PowerShell
.venv\Scripts\Activate.ps1
```

---

## Examples

Below are minimal, copy/paste runnable examples. For comprehensive guides and advanced patterns, see the documentation links.

Example 1 — Minimal agent (hello world) using ManagerAgent

```python
import os
import asyncio
from usf_agents import ManagerAgent

async def main():
    mgr = ManagerAgent(usf_config={'api_key': os.getenv('USF_API_KEY'), 'model': 'usf-mini'})
    result = await mgr.run("Say 'hello world'")
    # result is a dict like {'status': 'final', 'content': '...'}
    print("Final:", result.get("content"))

asyncio.run(main())
```

Example 2 — Minimal tool with @tool decorator

```python
import os
import asyncio
from usf_agents import ManagerAgent
from usf_agents.runtime.decorators import tool

@tool(schema={
    "description": "Calculate the sum of a list of integers.",
    "parameters": {
      "type": "object",
      "properties": {
        "numbers": {
          "type": "array",
          "items": {"type": "integer"},
          "description": "List of integers to sum."
        }
      },
      "required": ["numbers"]
    }
})
def calc_sum(numbers: list[int]) -> int:
    return sum(numbers)

async def main():
    mgr = ManagerAgent(usf_config={'api_key': os.getenv('USF_API_KEY'), 'model': 'usf-mini'})
    mgr.add_function_tool(calc_sum)  # optional alias via @tool or add_function_tool(alias="...")
    result = await mgr.run([{"role": "user", "content": "Use calc_sum for 10,20,30"}], {"mode": "auto"})
    print("Final:", result.get("content"))

asyncio.run(main())
```

Example 3 — Compose a sub-agent as a tool and call it

```python
import os
import asyncio
from usf_agents import ManagerAgent, SubAgent

async def main():
    api_key = os.getenv("USF_API_KEY")
    mgr = ManagerAgent(usf_config={'api_key': api_key, 'model': 'usf-mini'})

    # Create a sub-agent with a clear description (required)
    writer = SubAgent({
        "name": "writer",
        "context_mode": "NONE",
        "description": "Draft short outputs",
        "usf_config": {"api_key": api_key, "model": "usf-mini"},
    })
    # Expose sub-agent as a tool on the manager. Optionally alias the tool name.
    mgr.add_sub_agent(writer, alias="agent_writer")

    # Ask the manager; it can choose to call the sub-agent tool based on the task
    result = await mgr.run([{"role": "user", "content": "Ask agent_writer to write a haiku"}], {"mode": "auto"})
    print("Final:", result.get("content"))

asyncio.run(main())
```

---

## Complete Documentation

Start here

- Quickstart: https://us.inc/docs/quickstart
- Installation: https://us.inc/docs/start/installation
- Configuration: https://us.inc/docs/start/configuration
- Troubleshooting / FAQ: https://us.inc/docs/troubleshooting-faq

Tools

- Overview: https://us.inc/docs/tools/overview
- Docstrings: https://us.inc/docs/tools/docstrings
- Decorator: https://us.inc/docs/tools/decorator
- Explicit schema: https://us.inc/docs/tools/explicit-schema
- Type mapping: https://us.inc/docs/tools/type-mapping
- Registry & Batching: https://us.inc/docs/tools/registry-and-batch-tool-registration

Multi-Agent

- Overview: https://us.inc/docs/multi-agent/overview
- Execution Modes: https://us.inc/docs/multi-agent/auto-execution-modes
- Context Modes: https://us.inc/docs/multi-agent/context-modes
- Manager-driven Delegation: https://us.inc/docs/multi-agent/manager-driven-delegation
- Skip Planning (No Tools): https://us.inc/docs/multi-agent/skip-planning-no-tools
- Custom Instruction: https://us.inc/docs/multi-agent/custom-instruction

Jupyter notebook guides

- Email Drafting Assistant: https://us.inc/docs/jupyter-notebooks/email-drafting-assistant
- Customer Support Triage: https://us.inc/docs/jupyter-notebooks/customer-support-triage
- Planner-Worker Delegation: https://us.inc/docs/jupyter-notebooks/planner-worker-delegation
- Strict JSON Output: https://us.inc/docs/jupyter-notebooks/strict-json-output
- Currency Converter: https://us.inc/docs/jupyter-notebooks/currency-converter

FastAPI apps

- Email Drafting Assistant: https://us.inc/docs/fastapi-apps/email-drafting-assistant/README
- Customer Support Triage: https://us.inc/docs/fastapi-apps/customer-support-triage/README
- Planner-Worker Delegation: https://us.inc/docs/fastapi-apps/planner-worker-delegation/README
- Strict JSON Output: https://us.inc/docs/fastapi-apps/strict-json-output/README
- Currency Converter: https://us.inc/docs/fastapi-apps/currency-converter/README

---

## License

License: USF Agents SDK License  
See: ./LICENSE

Summary

- Permitted Use: anyone may use this software for any purpose.
- Restricted Activities: no modification of the code; no commercial use; no creation of competitive products.
- Attribution: retain this license notice and attribute UltraSafe AI Team.

---

© 2025 UltraSafe AI Team
