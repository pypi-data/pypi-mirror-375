USF Agents — Simplify the Complex, Amplify the Intelligent for Enterprise

Orchestrate multiple agents with ease: register agents, integrate tools, define custom instructions, and leverage multiple models. Enterprise-grade and production-ready, with full control, deep customization, strong defaults, clear boundaries, and developer-focused APIs.


---

# USF Agents

This website contains the documentation for the USF Agents Python SDK.

To get started, please visit the [documentation](docs/quickstart).


---

---
slug: /start/installation
title: Installation & Requirements
sidebar_position: 2
description: Install USF Agents SDK (Python) and set up required environment variables on macOS, Linux, or Windows.
---

import Tabs from '@theme/Tabs';
import TabItem from '@theme/TabItem';

:::note Requirements
- Python 3.9+
- USF API key (set as an environment variable)
:::

### Install the SDK

<Tabs>
<TabItem value="pip" label="pip (recommended)">

```bash
pip install usf-agents
```

</TabItem>
<TabItem value="uv" label="uv">

```bash
uv add usf-agents
```

</TabItem>
<TabItem value="poetry" label="poetry">

```bash
poetry add usf-agents
```

</TabItem>
<TabItem value="pdm" label="pdm">

```bash
pdm add usf-agents
```

</TabItem>
</Tabs>

### Set Your API Key

<Tabs>
<TabItem value="macos" label="macOS/Linux">

```bash
export USF_API_KEY=YOUR_KEY
```

</TabItem>
<TabItem value="powershell" label="Windows PowerShell">

```powershell
$env:USF_API_KEY="YOUR_KEY"
```

</TabItem>
<TabItem value="cmd" label="Windows cmd">

```bat
set USF_API_KEY=YOUR_KEY
```

</TabItem>
</Tabs>

### Optional: Virtual Environment

```bash
python -m venv .venv
```
<Tabs>
<TabItem value="macos" label="macOS/Linux">

```bash
source .venv/bin/activate
```

</TabItem>
<TabItem value="windows" label="Windows PowerShell">

```powershell
.venv\Scripts\Activate.ps1
```

</TabItem>
</Tabs>


### Verify Installation

Check if the package is installed:
```bash
pip show usf-agents
```

Perform a minimal import check:
```bash
python - <<'PY'
try:
    import usf_agents
    print("usf_agents import: OK")
except Exception as e:
    print("Import failed:", e)
PY
```

### Quick Sanity Run

This requires your `USF_API_KEY` to be set.

```python
# sanity.py
import os
import asyncio
import nest_asyncio
from usf_agents import ManagerAgent

nest_asyncio.apply()

async def main():
    mgr = ManagerAgent(
        usf_config={
            "api_key": os.getenv("USF_API_KEY"),
            "model": "usf-mini"
        }
    )

    # Unified run API (auto-exec by default with mode="auto")
    result = await mgr.run("Say 'hello world'", {"mode": "auto"})
    if result.get("status") == "final":
        print("Final:", result.get("content"))
    else:
        print("Pending tool calls:", result.get("tool_calls"))

if __name__ == "__main__":
    asyncio.run(main())
```

Run it:
```bash
python sanity.py
```

:::info Troubleshooting
- If an import fails, ensure your virtual environment is activated and that `pip show usf-agents` lists the package in the same interpreter.
- If you encounter runtime errors related to a missing API key, confirm that `USF_API_KEY` is set in the same shell session that is running Python.
:::


---

---
slug: /start/configuration
title: Configuration
sidebar_position: 3
description: Configure ManagerAgent/SubAgent globally and per stage, override per run, control providers, and set execution limits and behaviors.
---

### Overview

This guide explains how to configure agents and stages in the SDK. It covers:
- Global configuration on `ManagerAgent` (and `SubAgent`)
- Stage-level overrides for `planning` / `tool_calling` / `final_response`
- Per-run overrides via `RunOptions` on `run(...)`

### Execution Model: Sequential by Design

:::note
usf-agent executes agent and tool calls strictly in sequence; parallel execution is not supported by design. This is a deliberate choice—not a limitation—to prioritize determinism, traceability, and output quality.
:::

- Sequential flow simplifies state management and reduces race conditions.
- When parallelism is required, orchestrate at a higher level (e.g., multiple processes/tasks or external job runners) while keeping the agent’s internal flow sequential for quality.

### Running in Colab

To run this notebook in Google Colab:

```bash
!pip install usf-agents
```

### Global Configuration (ManagerAgent / SubAgent)

:::note Global Agent Settings (inside `usf_config`)
- `api_key`: string (required) — Your USF API key
- `model`: string (default `"usf-mini"`) — Default model
- `provider`: Optional[string] — Provider for planning/tool-calling (`openrouter`, `openai`, `claude`, `huggingface-inference`, `groq`)
- `introduction`: string — High-level system introduction
- `knowledge_cutoff`: string — Knowledge cutoff date
- `max_loops`: int (default `20`, range `1..100`) — Upper bound on internal loops
- `backstory`: string — Agent backstory
- `goal`: string — Primary agent goal
- `temp_memory`:
  - `enabled`: bool (default `False`)
  - `max_length`: int (default `10`)
  - `auto_trim`: bool (default `True`)
- `debug`: bool (default `False`)
- `skip_planning_if_no_tools`: bool (default `False`) — See “Skip planning when no tools”
- Stage-specific overrides:
  - `planning`: Stage config
  - `tool_calling`: Stage config
  - `final_response`: Stage config
:::

#### StageConfig (applies to `planning`, `tool_calling`, `final_response`)
- `api_key`, `provider`, `model`, `introduction`, `knowledge_cutoff`
- `temperature`, `stop`
- `date_time_override` (only where relevant)
- `debug`
- Additional OpenAI‑compatible parameters (e.g., `max_tokens`, `top_p`, etc. on `final_response`)

#### Example: Global Config and Stage Overrides

```python
import os
import asyncio
import nest_asyncio
from usf_agents import ManagerAgent

nest_asyncio.apply()

USF_API_KEY = os.getenv("USF_API_KEY") or "YOUR_API_KEY_HERE"

async def main():
    mgr = ManagerAgent(
        usf_config={
            "api_key": USF_API_KEY,
            "model": "usf-mini",
            "temp_memory": {
                "enabled": True,
                "max_length": 5,
                "auto_trim": True
            },
            "max_loops": 10,
            "planning": {
                "model": "usf-mini",
                "introduction": "You are planning the steps to solve the task.",
                "knowledge_cutoff": "15 January 2025",
                "debug": True
            },
            "tool_calling": {
                "provider": "",
                "model": "usf-mini",
                "debug": True
            },
            "final_response": {
                "model": "usf-mini",
                "temperature": 0.5,
                "max_tokens": 512,
                "top_p": 1.0
            }
        },
        backstory="Power user of the system.",
        goal="Concise, accurate answers."
    )

    result = await mgr.run("Say hello world", {"mode": "auto"})
    print(result)

if __name__ == '__main__':
    asyncio.run(main())
```

### Stage-Level Configuration

You can override global settings at each stage: `planning`, `tool_calling`, and `final_response`.

:::info Supported Keys
- **Common**: `api_key`, `provider`, `model`, `introduction`, `knowledge_cutoff`, `temperature`, `stop`, `debug`.
- **`final_response`**: Additional OpenAI-compatible parameters such as `response_format`, `max_tokens`, `top_p`, `presence_penalty`, `frequency_penalty`, `logit_bias`, `seed`, `user`, `stream_options`, etc.
- Note: `final_response` does not execute tools.
:::

### Per-Run Overrides (RunOptions)

Override any configuration on a per-run basis by passing a `RunOptions` dict to `mgr.run(...)`.

`RunOptions` (selected keys):
- `mode`: `"auto" | "disable" | "agent-only" | "tool-only"`
- `max_loops`: int
- `tools`: Optional[List[Tool]] (usually auto-composed for a manager)
- `planning`, `tool_calling`, `final_response`: StageConfig
- `temperature`, `stop`
- `skip_planning_if_no_tools`: bool
- `date_time_override`

#### Example: Per-Run Override

```python
import os
import asyncio
import nest_asyncio
from usf_agents import ManagerAgent

nest_asyncio.apply()

USF_API_KEY = os.getenv("USF_API_KEY") or "YOUR_API_KEY_HERE"

async def main():
    mgr = ManagerAgent(
        usf_config={"api_key": USF_API_KEY, "model": "usf-mini"}
    )

    opts = {
      "mode": "auto",
      "temperature": 0.2,
      "max_loops": 5,
      "final_response": {
        "date_time_override": {
          "enabled": True,
          "date": "08/31/2025",
          "time": "07:00:00 AM",
          "timezone": "UTC"
        }
      }
    }

    result = await mgr.run(
        "Reply with the current date/time string from system context.",
        opts
    )
    print(result)

if __name__ == '__main__':
    asyncio.run(main())
```

### Notes

- Use `{"mode":"disable"}` to avoid auto-exec and receive `{"status":"tool_calls", ...}` for manual tool routing.
- Prefer configuring common defaults in `usf_config`, and use per-run overrides to adjust behavior as needed for specific calls.
- See “Skip planning when no tools” for fast, tool-less responses.


---

---
id: decorator
title: "@tool Decorator"
description: "Provide optional alias and/or a full schema directly on the decorator."
sidebar_position: 3
---

## Overview

The `@tool` decorator lets you attach metadata and an optional full schema directly to a function so it can be registered as an agent tool. This keeps definitions close to the code and provides a concise path to production-grade schemas when needed.

:::note What You Can Set
- Alias: optional display name for the tool (LLM-facing).
- Full Schema: Provide an OpenAI function-calling compatible schema under `schema=...`.
- If no explicit schema is provided, the docstring will be parsed for the schema.
- Default display name when alias is not provided: `agent_(function_name)`.
:::

## How it Works

- Decorate a Python function with `@tool(...)` to optionally provide an alias and/or a full schema.
- When registering the function with `add_function_tool(...)`:
  - An explicit `schema=...` passed at registration time overrides any decorator or docstring schema.
  - If no explicit schema is passed, but the decorator has `schema=...`, that schema is used.
  - Otherwise, the SDK attempts to infer the schema from the function docstring (YAML → Google Args).
- Validation on registration:
  - `required` must match the function parameters without default values.
  - With `strict=True`, the schema’s `parameters.properties` must exactly equal the function signature (no missing or extra keys).
- Naming:
  - Tool names must be unique per agent; use an `alias` to disambiguate exposed names for the LLM while keeping Python function names simple.

:::info Validation Rules
- `schema.parameters.required` must equal the function’s parameters that have no default values.
- With `strict=True`, the schema’s `properties` must exactly match the function’s parameters.
- Tool names must be unique per agent; use an `alias` to disambiguate.
:::

## Running in Colab

You can run these examples directly in Google Colab.

- Install the SDK:
```bash
!pip install -q usf-agents
```

- Set your API key:
```python
import os
os.environ["USF_API_KEY"] = "YOUR_API_KEY"
```

- Copy a snippet from the Code section below into a new cell and run it.

## Code

### A) Decorator with Defaults

The schema is inferred from the docstring.

```python
import os
import asyncio
import nest_asyncio
from usf_agents import ManagerAgent
from usf_agents.runtime.decorators import tool

nest_asyncio.apply()

@tool(alias="sum_tool")
def calc_sum(numbers: list[int]) -> int:
    """
    Sum integers.
    Args:
      numbers (list[int]): Values to add up.
    """
    return sum(numbers)

async def main():
    mgr = ManagerAgent(
        usf_config={"api_key": os.getenv("USF_API_KEY"), "model": "usf-mini"}
    )
    mgr.add_function_tool(calc_sum)

    result = await mgr.run("Use sum_tool to sum 10,20,30", {"mode": "auto"})
    print(result)

if __name__ == "__main__":
    asyncio.run(main())
```

### B) Decorator with an Explicit Schema

This schema takes precedence over the docstring when no explicit schema is passed at registration time.

```python
import os
import asyncio
import nest_asyncio
from usf_agents import ManagerAgent
from usf_agents.runtime.decorators import tool

nest_asyncio.apply()

@tool(
    alias="sum_tool",
    schema={
        "description": "Sum integers",
        "parameters": {
            "type": "object",
            "properties": {"numbers": {"type": "array", "description": "List of ints"}},
            "required": ["numbers"]
        }
    }
)
def calc_sum(numbers: list[int]) -> int:
    return sum(numbers)

async def main():
    mgr = ManagerAgent(
        usf_config={"api_key": os.getenv("USF_API_KEY"), "model": "usf-mini"}
    )
    mgr.add_function_tool(calc_sum)

    result = await mgr.run("Use sum_tool to sum 1, 2, 3, 4, 5", {"mode": "auto"})
    print(result)

if __name__ == "__main__":
    asyncio.run(main())
```

:::tip When to Use the Decorator
- Use decorator **defaults** to keep tool definitions concise and co-located with your code.
- Use a decorator **schema** if you want strong control without passing a schema at registration time.
- Prefer an **explicit schema** (via registration) with `strict=True` for maximum validation when developing critical tools.
:::


---

---
id: docstrings
title: Docstring Schemas
description: Infer tool schemas from function docstrings with precedence YAML → Google Args.
sidebar_position: 2
---

## Overview

You can define tool schemas without writing JSON by using function docstrings. The SDK parses a YAML block (if present), and falls back to Google-style `Args:`.

:::info Precedence
1. **YAML block** inside the docstring.
2. **Google-style** `Args:` section.
:::

## How it Works

- When you register a function as a tool without an explicit `schema=...` and without a `@tool(..., schema=...)`, the SDK attempts to infer the schema from the function’s docstring.
- The parser tries the formats in a strict order (YAML → Google). The first successfully parsed format wins.
- The inferred schema will:
  - Build the JSON Schema under `parameters` including `type`, `properties`, and (when determinable) `required`.
  - Align `required` with function parameters that have no default values.
- Tips for writing parseable docstrings:
  - Google: Use an `Args:` section with one entry per parameter, and a short type hint in parentheses or description.
  - YAML: Provide a commented YAML block that mirrors OpenAI function-calling style under `parameters`.
- If you need strict property-name control or complex shapes, prefer passing an explicit schema (or a decorator schema) rather than relying on docstrings.
- PyYAML is installed by default with `usf-agents`, so fenced YAML blocks support nested objects/arrays out of the box. If PyYAML is not present in your environment, a flat-only fallback is used.

## Running in Colab

You can run these examples directly in Google Colab.

- Install the SDK:
```bash
!pip install -q usf-agents
```

- Set your API key:
```python
import os
os.environ["USF_API_KEY"] = "YOUR_API_KEY"
```

- Copy a snippet from the Code section below into a new cell and run it.

## Code

### A) Google-Style Docstring

```python
import os
import asyncio
import nest_asyncio
from usf_agents import ManagerAgent

nest_asyncio.apply()

def calc(expression: str) -> int:
    """
    Evaluate a simple expression.
    Args:
      expression (str): A Python expression to evaluate.
    """
    return eval(expression)  # demo only

async def main():
    mgr = ManagerAgent(
        usf_config={"api_key": os.getenv("USF_API_KEY"), "model": "usf-mini"}
    )
    mgr.add_function_tool(calc, alias="math_calc")

    result = await mgr.run("Use math_calc to compute 25*4", {"mode": "auto"})
    print(result)

if __name__ == "__main__":
    asyncio.run(main())
```

:::note Limitations (Google-style)
- Nested schemas are not supported in Google-style docstrings (Args:).

If a YAML block is present, it overrides Google parsing.

```python
import os
import asyncio
import nest_asyncio
from usf_agents import ManagerAgent

nest_asyncio.apply()

def http_get(url: str) -> dict:
    """
    Perform GET.
    ˋˋˋyaml
    description: Simple HTTP GET (demo)
    parameters:
      type: object
      properties:
        url:
          type: string
          description: URL to fetch
      required: [url]
    ˋˋˋ
    """
    return {"status": 200, "body": "ok"}

async def main():
    mgr = ManagerAgent(
        usf_config={"api_key": os.getenv("USF_API_KEY"), "model": "usf-mini"}
    )
    mgr.add_function_tool(http_get)

    result = await mgr.run("Call http_get with https://example.com", {"mode": "auto"})
    print(result)

if __name__ == "__main__":
    asyncio.run(main())
```

### Nested Parameters (YAML)

Nested shapes are supported when PyYAML is available (installed by default with `usf-agents`).

Cheat‑sheet (object vs array):
```yaml
# object (map/dict)
options:
  type: object
  properties:
    timeout:
      type: number
    headers:
      type: object

# array of scalars
tags:
  type: array
  items:
    type: string

# array of objects
items:
  type: array
  items:
    type: object
    properties:
      id: { type: string }
      qty: { type: number }
    required: [id, qty]
```

Example: nested object
```python
def http_fetch(url: str, options: dict | None = None) -> dict:
    """
    Fetch with options.

    ˋˋˋyaml
    description: Fetch with options
    parameters:
      type: object
      properties:
        url:
          type: string
          description: URL to fetch
        options:
          type: object
          description: Request options
          properties:
            timeout:
              type: number
              description: Timeout in seconds
            headers:
              type: object
              description: HTTP headers map
      required: [url]
    ˋˋˋ
    """
    return {"status": 200, "body": "ok"}
```

Example: array of objects
```python
def submit_items(items: list[dict]) -> dict:
    """
    Submit items.

    ˋˋˋyaml
    description: Submit item list
    parameters:
      type: object
      properties:
        items:
          type: array
          items:
            type: object
            properties:
              id:
                type: string
              qty:
                type: number
            required: [id, qty]
      required: [items]
    ˋˋˋ
    """
    return {"ok": True}
```

:::danger Gotchas
- Description is required:
  - YAML: the fenced YAML block must include a non-empty `description:` field.
  - Google: the first non-empty line of the docstring is used as the description; if the docstring has no summary line, registration will error.
- If you see "no explicit schema and no parseable docstring," ensure your docstring uses one of the supported formats.
- If you see "required mismatch," align the schema’s `required` field with the function parameters that have no defaults.
- Use aliases to avoid tool name collisions.
:::

:::tip When to Use Docstrings vs. Explicit Schemas
- **Docstrings**: Fastest way to get started; great for simple tools.
- **Explicit/Decorator Schemas**: Use when you need strict typing, complex shapes, or exact property names.
:::


---

---
id: explicit-schema
title: Explicit Schema (+ strict mode)
description: Pass a full OpenAI function-calling compatible schema to add_function_tool and optionally enforce strict property equality.
sidebar_position: 4
---

## Overview

You can pass an explicit JSON schema when registering a function as a tool. This gives you exact control over parameter names, types, and required fields, and it overrides any decorator or docstring-derived schema. Combine with `strict=True` to enforce exact property equality to the function signature.

## How it Works

- Precedence: An explicit `schema=...` passed to `add_function_tool(...)` overrides decorator and docstring schemas.
- Validation (always on):
  - `required` must match the function parameters that have no default values.
- `strict=True` (optional additional checks):
  - `parameters.properties` must exactly match the function signature (no extra or missing keys).
- When to use:
  - You need precise property names and types.
  - You want robust validation in CI/CD or production, without relying on docstring parsing.

## Running in Colab

You can run these examples directly in Google Colab.

- Install the SDK:
```bash
!pip install -q usf-agents
```

- Set your API key and (optionally) enable nested asyncio:
```python
import os, nest_asyncio
os.environ["USF_API_KEY"] = "YOUR_API_KEY"
nest_asyncio.apply()
```

- Copy a snippet from the Code section below into a new cell and run it.

## Code

### A) Minimal Explicit Schema

```python
import os
import asyncio
import nest_asyncio
from usf_agents import ManagerAgent

nest_asyncio.apply()

def calc(expression: str) -> int:
    return eval(expression)

async def main():
    mgr = ManagerAgent(
        usf_config={
            "api_key": os.getenv("USF_API_KEY"),
            "model": "usf-mini",
        }
    )
    mgr.add_function_tool(
        calc,
        alias="math_calc",
        schema={
            "description": "Evaluate math expression",
            "parameters": {
                "type": "object",
                "properties": {
                    "expression": {
                        "type": "string"
                    }
                },
                "required": ["expression"],
            },
        },
    )
    result = await mgr.run(
        [
            {
                "role": "user",
                "content": "Use math_calc to compute 9*9"
            }
        ],
        {"mode": "auto"}
    )
    if isinstance(result, dict) and result.get("status") == "final":
        print("Final:", result.get("content"))
    else:
        print("Pending tool calls:", result)

if __name__ == "__main__":
    asyncio.run(main())
```

### B) Strict Mode

With `strict=True`, the keys in `parameters.properties` must exactly match the function parameters.

```python
import os
import asyncio
import nest_asyncio
from usf_agents import ManagerAgent

nest_asyncio.apply()

def demo(a: str, n: int, flag: bool) -> dict:
    return {"ok": True}

async def main():
    mgr = ManagerAgent(
        usf_config={
            "api_key": os.getenv("USF_API_KEY"),
            "model": "usf-mini",
        }
    )
    mgr.add_function_tool(
        demo,
        schema={
            "description": "Type demo",
            "parameters": {
                "type": "object",
                "properties": {
                    "a": {
                        "type": "string"
                    },
                    "n": {
                        "type": "number"
                    },
                    "flag": {
                        "type": "boolean"
                    },
                },
                "required": ["a", "n", "flag"],
            },
        },
        strict=True,
    )
    result = await mgr.run(
        [
            {
                "role": "user",
                "content": "Call demo with a='x', n=1, flag=true"
            }
        ],
        {"mode": "auto"}
    )
    if isinstance(result, dict) and result.get("status") == "final":
        print("Final:", result.get("content"))
    else:
        print("Pending tool calls:", result)

if __name__ == "__main__":
    asyncio.run(main())
```

### C) Strict Failure Example

```python
import os
import asyncio
import nest_asyncio
from usf_agents import ManagerAgent

nest_asyncio.apply()

def demo(a: str, n: int, flag: bool) -> dict:
    return {"ok": True}

async def main():
    mgr = ManagerAgent(
        usf_config={
            "api_key": os.getenv("USF_API_KEY"),
            "model": "usf-mini",
        }
    )
    try:
        mgr.add_function_tool(
            demo,
            schema={
                "description": "Invalid strict example",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "a": {
                            "type": "string"
                        },
                        "n": {
                            "type": "number"
                        },
                        "extra": {
                            "type": "string"
                        },
                    },
                    "required": ["a", "n"],
                },
            },
            strict=True,
        )
    except Exception as e:
        print("Expected strict error:\n", e)

asyncio.run(main())
```

:::danger Common Errors
-   "required mismatch": Align `required` with function parameters that have no default values.
-   "properties mismatch" (when `strict=True`): Ensure `parameters.properties` keys exactly match the function parameter names.
:::

:::tip When to Use Explicit Schema
-   You need precise property names and types.
-   You want to enable `strict=True` for robust validation.
-   You don’t want to rely on docstring parsing in CI/CD or production environments.
:::


---

---
id: overview
title: Tools Overview
description: Define and register tools with schema precedence and strong validation.
sidebar_position: 1
---

## Overview

Tools let agents call your Python functions using OpenAI function-calling compatible schemas. The SDK supports multiple ways to define schemas with clear precedence and validation guarantees.

:::info Overview
- Tools let agents call your Python functions using OpenAI function-calling compatible schemas.
- **Schema Precedence**:
  1. Explicit schema passed to `add_function_tool(..., schema=...)`.
  2. Schema provided in the `@tool` decorator.
  3. Docstring parsing (YAML → Google).
- **Validation**:
  - `required` must match the function parameters that have no default values.
  - Optional `strict` mode enforces that properties match the function signature.
:::

## How it Works

- You register normal Python functions as tools on an agent (e.g., a `ManagerAgent`). Each tool exposes:
  - a function `name` (and optional `alias` used by the LLM),
  - a `description`,
  - a JSON schema under `parameters` that defines arguments.
- When a tool call is selected by the planner, the arguments returned by the model are validated against the schema:
  - `required` must exactly equal the set of function parameters without defaults.
  - Set `strict=True` to additionally enforce that `parameters.properties` exactly matches the function signature (no extra or missing keys).
- Schema resolution order:
  1) If you pass an explicit `schema=...` at registration time, it overrides everything.
  2) Otherwise, if the function has a `@tool(..., schema=...)` decorator, its schema is used.
  3) Otherwise, the SDK tries to infer a schema from the docstring (YAML block → Google `Args:`).

This precedence model gives you a fast path to get started (docstrings), a convenient in-code option (`@tool`), and an explicit/strict option for production.

## Running in Colab

You can run these examples directly in Google Colab.

- Install the SDK:
```bash
!pip install -q usf-agents
```

- Set your API key:
```python
import os
os.environ["USF_API_KEY"] = "YOUR_API_KEY"
```

- Copy a snippet from the Code section below into a new cell and run it.

## Code

### Tool Format

```python
tool = {
  "type": "function",
  "function": {
    "name": "http_get",
    "description": "Fetch a URL",
    "parameters": {
      "type": "object",
      "properties": {"url": {"type": "string"}},
      "required": ["url"]
    }
  }
}
```

### Register a Function Tool

Schema is inferred from the docstring in this example.

```python
from usf_agents import ManagerAgent

def calc(expression: str) -> int:
    """
    Evaluates a simple expression.
    Args:
      expression (str): A Python expression.
    """
    return eval(expression)

mgr = ManagerAgent(
    usf_config={"api_key": "...", "model": "usf-mini"}
)
mgr.add_function_tool(
    calc,
    alias="math_calc"
)
```

### Run End-to-End

```python
result = await mgr.run("Use math_calc to compute 25*4", {"mode": "auto"})
if result.get("status") == "final":
    print("Final:", result.get("content"))
else:
    print("Pending tool calls:", result.get("tool_calls"))
```

### Strict Mode

Set `strict=True` when passing an explicit schema to enforce an exact match between schema properties and function parameters.

#### Passing Example (`strict=True`)

```python
import os
import asyncio
import nest_asyncio
from usf_agents import ManagerAgent

nest_asyncio.apply()

def demo(a: str, n: int, flag: bool) -> dict:
    """Return a simple dict."""
    return {"ok": True}

async def main():
    mgr = ManagerAgent(
        usf_config={"api_key": os.getenv("USF_API_KEY"), "model": "usf-mini"}
    )
    mgr.add_function_tool(
        demo,
        schema={
            "description": "Type demo",
            "parameters": {
                "type": "object",
                "properties": {
                    "a": {"type": "string"},
                    "n": {"type": "number"},
                    "flag": {"type": "boolean"},
                },
                "required": ["a", "n", "flag"]
            }
        },
        strict=True,
    )
    result = await mgr.run("Call demo with a='x', n=1, flag=true", {"mode": "auto"})
    print(result)

asyncio.run(main())
```

#### Failing Example (`strict=True`)

```python
import os
import asyncio
import nest_asyncio
from usf_agents import ManagerAgent

nest_asyncio.apply()

def demo(a: str, n: int, flag: bool) -> dict:
    """Return a simple dict."""
    return {"ok": True}

async def main():
    mgr = ManagerAgent(
        usf_config={"api_key": os.getenv("USF_API_KEY"), "model": "usf-mini"}
    )
    try:
        mgr.add_function_tool(
            demo,
            schema={
                "description": "Invalid strict example",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "a": {"type": "string"},
                        "n": {"type": "number"},
                        "extra": {"type": "string"}
                    },
                    "required": ["a", "n"]
                }
            },
            strict=True,
        )
    except Exception as e:
        print("Expected strict error:\n", e)

asyncio.run(main())
```

:::danger Common Errors
- **"no explicit schema and no parseable docstring"**: Provide a docstring or a schema.
- **"required mismatch"**: Align `required` with function parameters that have no default values.
- **"properties mismatch" (`strict=True`)**: Align `parameters.properties` with the function parameters.
:::


---

---
id: registry-and-batch-tool-registration
title: Registry & Batch Tool Registration
description: Register single or multiple tools, auto-discover from modules; covers schema inference/validation, aliases, and collisions. For execution flow, see Auto Execution Modes.
sidebar_position: 6
slug: /tools/registry-and-batch-tool-registration
---

## Overview

You can register a single function as a tool, batch register many, or auto-discover tools from a module. This keeps your setup concise and consistent, and encourages clear aliasing and docstring-based schema inference by default. This page focuses on registration patterns; for execution flow and normalized return shapes, see [Auto Execution Modes](/docs/multi-agent/auto-execution-modes).

- Single tool registration with `add_function_tool(func, alias="...", schema=...)`:
  - Registers one function on a `ManagerAgent`.
  - Aliases via the `@tool` decorator (optional) are respected.
- Batch register a list of functions with `add_function_tools([func_a, func_b, ...], strict=False)`:
  - Pass Python callables directly.
  - If no explicit schema is provided, the SDK infers it from docstrings (precedence: YAML code block → Google-style `Args:`).
  - Aliases provided via the `@tool` decorator (optional) are respected.
  - Validation rules:
    - `required` must match the function parameters that have no default values.
    - With `strict=True`, `parameters.properties` must exactly match the function signature.
- Auto-discover from a Python module with `add_function_tools_from_module(module, filter=None, strict=False)`:
  - Scans the module for callables.
  - Optionally provide a `filter(fn)` to restrict which functions are registered.
  - Aliases from the `@tool` decorator are respected if present.

:::tip Guidelines
- Keep function names stable and use the `@tool` decorator for human-friendly aliases.
- Use clear docstrings (YAML or Google style) for schema inference when you don’t provide an explicit schema.
- For critical tools, prefer explicit schemas or use `strict=True` to catch mismatches early.
:::

## How it Works

### Registration APIs
- Single tool: `add_function_tool(func, alias="...", schema=...)`
  - Best for one-off utilities or when you want an explicit alias/schema.
- Batch list: `add_function_tools([func_a, func_b, ...], strict=False)`
  - Register many functions in one call; mixes decorator metadata + docstring inference.
- From module: `add_function_tools_from_module(module, filter=None, strict=False)`
  - Auto-discovers callables from a Python module. Use `filter(fn)` to select a subset.

### Schema inference and validation
- If `schema` isn’t provided:
  - Inference precedence: YAML code block → Google-style `Args:` → (fallbacks).
- Validation rules:
  - `required` must equal parameters with no defaults.
  - With `strict=True`, `parameters.properties` must exactly match the function signature.

### Nested parameters
- YAML docstrings:
  - Nested objects and arrays are supported when PyYAML is available (import yaml succeeds).
  - If PyYAML is not available, the fallback parser only supports flat properties; nested shapes will not be inferred. In that case, use `@tool(schema=...)` or install PyYAML.
  - Example YAML to place inside a function docstring:
    ```yaml
    description: Create a user
    parameters:
      type: object
      properties:
        user:
          type: object
          description: User payload
          properties:
            name:
              type: string
            address:
              type: object
              properties:
                city:
                  type: string
                zip:
                  type: string
            roles:
              type: array
              items:
                type: object
                properties:
                  name:
                    type: string
                  level:
                    type: number
      required: ["user"]
    ```

- Google-style Args:
  - Not supported for nested structures; only flat `name (type): description` items are parsed.
  - For nested parameters, use YAML or an explicit schema with `@tool(schema=...)`.

- Explicit schema via `@tool` (recommended for complex nesting):
  ```python
  from usf_agents.runtime.decorators import tool

  @tool(
      schema={
          "description": "Create a user",
          "parameters": {
              "type": "object",
              "properties": {
                  "user": {
                      "type": "object",
                      "properties": {
                          "name": {"type": "string"},
                          "address": {
                              "type": "object",
                              "properties": {
                                  "city": {"type": "string"},
                                  "zip": {"type": "string"},
                              },
                              "required": ["city", "zip"],
                          },
                          "roles": {
                              "type": "array",
                              "items": {
                                  "type": "object",
                                  "properties": {
                                      "name": {"type": "string"},
                                      "level": {"type": "number"},
                                  },
                                  "required": ["name"],
                              },
                          },
                      },
                      "required": ["name"],
                  }
              },
              "required": ["user"],
          },
      },
  )
  def create_user(user: dict) -> str:
      return "ok"
  ```

See also: [Explicit Schema (+ strict mode)](/docs/tools/explicit-schema) • [Auto Execution Modes](/docs/multi-agent/auto-execution-modes) • [Custom Instruction](/docs/multi-agent/custom-instruction)

### Names, aliases, and collisions
- Default display tool name is agent_(function_name).
- Use `alias` for human-friendly names and to avoid collisions.
- Names must be unique per manager.


### When to use what
- Use single registration for a small number of tools or when providing explicit schemas.
- Use batch list for a curated set of functions within one file.
- Use module discovery for larger libraries; narrow with `filter` to keep surface area clean.

## Running in Colab

You can run these examples directly in Google Colab.

- Install the SDK:
```bash
!pip install -q usf-agents
```

- Set your API key and (optionally) enable nested asyncio:
```python
import os, nest_asyncio
os.environ["USF_API_KEY"] = "YOUR_API_KEY"
nest_asyncio.apply()
```

- Copy a snippet from the Code section below into a new cell and run it.

## Code

### Single Tool Registration

```python
import os
import asyncio
import nest_asyncio
from usf_agents import ManagerAgent

nest_asyncio.apply()

def calc(expression: str) -> int:
    """
    Evaluate a simple expression.
    Args:
      expression (str): A Python expression to evaluate.
    """
    return eval(expression)  # demo only; use a safe evaluator in production

async def main():
    api_key = os.getenv("USF_API_KEY") or "YOUR_API_KEY_HERE"

    mgr = ManagerAgent(
        usf_config={"api_key": api_key, "model": "usf-mini"}
    )

    # Register the function as a tool (docstring schema inferred automatically)
    mgr.add_function_tool(calc, alias="math_calc")

    # End-to-end auto execution: plan -> tool_calls -> final
    result = await mgr.run("Use math_calc to compute 25*4", {"mode": "auto"})
    print(result)

if __name__ == "__main__":
    asyncio.run(main())
```

### Batch Register a List

```python
import os
import asyncio
import nest_asyncio
from usf_agents import ManagerAgent
# Optional: use decorator to supply alias/schema metadata
from usf_agents.runtime.decorators import tool

nest_asyncio.apply()

@tool(alias="hello")
def greet(name: str) -> str:
    """
    Greets.
    Args:
        name (str): Person to greet
    """
    return f"Hello {name}!"

def calc(expression: str) -> int:
    """
    Evaluates a simple expression.
    Args:
        expression (str): Python expression (demo only)
    """
    return eval(expression)  # demo only

async def main():
    mgr = ManagerAgent(
        usf_config={
            "api_key": os.getenv("USF_API_KEY"),
            "model": "usf-mini",
        }
    )

    # Register both via batch (decorator metadata on greet, docstring parsing on calc)
    mgr.add_function_tools([greet, calc])

    result = await mgr.run(
        [
            {
                "role": "user",
                "content": "Use hello for 'USF' then calc for 6*7",
            }
        ],
        {"mode": "auto"}
    )

    if isinstance(result, dict) and result.get("status") == "final":
        print("Final:", result.get("content"))
    else:
        print("Pending tool calls:", result)

if __name__ == "__main__":
    asyncio.run(main())
```


## Notes

- Schemas:
  - You can pass an explicit JSON schema in `add_function_tool(..., schema=...)`.
  - Otherwise a decorator or docstring can be parsed to infer one.
- Collisions:
  - Tool names must be unique within a manager. Use `alias=` to disambiguate.
- Modes: See [Auto Execution Modes](/docs/multi-agent/auto-execution-modes).

### Discover from a Module

Collect utility functions in a single module and register them with an optional filter.

```python
# Example tools module (tools_mod.py)
def add(a: int, b: int) -> int:
    """
    Adds two numbers.
    Args:
        a (int): First operand
        b (int): Second operand
    """
    return a + b

def echo(text: str) -> str:
    """
    Echoes text.
    Args:
        text (str): Text to echo
    """
    return text
```

```python
import os
import asyncio
import nest_asyncio
import importlib
from usf_agents import ManagerAgent

nest_asyncio.apply()

async def main():
    tools_mod = importlib.import_module("tools_mod")
    mgr = ManagerAgent(
        usf_config={
            "api_key": os.getenv("USF_API_KEY"),
            "model": "usf-mini",
        }
    )

    # Filter only the functions we want to expose
    def only_named(fn):
        return getattr(fn, "__name__", "") in {"add", "echo"}

    mgr.add_function_tools_from_module(tools_mod, filter=only_named)

    result = await mgr.run(
        [
            {
                "role": "user",
                "content": "Use add for 10 and 20; then echo 'done'",
            }
        ],
        {"mode": "auto"}
    )

    if isinstance(result, dict) and result.get("status") == "final":
        print("Final:", result.get("content"))
    else:
        print("Pending tool calls:", result)

if __name__ == "__main__":
    asyncio.run(main())


---

---
id: type-mapping
title: Type Mapping & Examples
description: Map Python types to JSON Schema for tools, with examples using the unified run API.
sidebar_position: 5
---

## Overview

When registering Python functions as tools, the SDK maps Python type hints to JSON Schema. This page shows examples of common type mappings and how to execute tools end‑to‑end via the unified `ManagerAgent.run(...)` API.

:::info Summary
- Use `add_function_tool(func, alias=?, schema=?, strict=?)` to register.
- Type hints inform docstring/schema inference when no explicit schema is provided.
- Execute with `ManagerAgent.run(messages_or_string, {"mode":"auto"})`.
:::

## Running in Colab

```bash
!pip install usf-agents
```

## Code

### Basic types

```python
import os
import asyncio
import nest_asyncio
from usf_agents import ManagerAgent

nest_asyncio.apply()

def echo(text: str) -> str:
    """Return the same text."""
    return text

async def main():
    mgr = ManagerAgent(
        usf_config={"api_key": os.getenv("USF_API_KEY"), "model": "usf-mini"}
    )
    mgr.add_function_tool(echo)

    result = await mgr.run("Use echo with text='hi'", {"mode": "auto"})
    print(result)

asyncio.run(main())
```

### Numbers, arrays, and objects

```python
import os
import asyncio
import nest_asyncio
from typing import List, Dict, Any
from usf_agents import ManagerAgent

nest_asyncio.apply()

def stats(values: List[float]) -> Dict[str, float]:
    """Return basic stats for a list of floats."""
    if not values:
        return {"min": 0, "max": 0, "avg": 0}
    mn, mx = min(values), max(values)
    avg = sum(values) / len(values)
    return {"min": mn, "max": mx, "avg": round(avg, 4)}

def describe_user(user: Dict[str, Any]) -> str:
    """Return a human-readable summary of a user dict."""
    return f"User: {user.get('name','?')} ({user.get('role','?')})"

async def main():
    mgr = ManagerAgent(
        usf_config={"api_key": os.getenv("USF_API_KEY"), "model": "usf-mini"}
    )
    mgr.add_function_tool(stats)
    mgr.add_function_tool(describe_user)

    result = await mgr.run("Call stats with values=[1.5,2.5,3.5] then summarize.", {"mode": "auto"})
    print(result)

asyncio.run(main())
```

### Enums & strict schemas

For more constrained inputs, provide an explicit schema (optionally with `strict=True` to enforce exact properties).

```python
import os
import asyncio
import nest_asyncio
from usf_agents import ManagerAgent

nest_asyncio.apply()

def priority_label(level: str) -> str:
    """Return a label for a priority level."""
    return {"p0":"CRITICAL","p1":"HIGH","p2":"MEDIUM","p3":"LOW"}.get(level, "UNKNOWN")

async def main():
    mgr = ManagerAgent(
        usf_config={"api_key": os.getenv("USF_API_KEY"), "model": "usf-mini"}
    )
    mgr.add_function_tool(
        priority_label,
        schema={
            "description": "Return a label for a priority level.",
            "parameters": {
                "type": "object",
                "properties": {
                    "level": {"type": "string", "enum": ["p0","p1","p2","p3"]}
                },
                "required": ["level"]
            }
        },
        strict=True
    )

    result = await mgr.run("Use priority_label with level='p1'", {"mode": "auto"})
    print(result)

asyncio.run(main())
```

:::tip Notes
- When relying on docstrings, ensure your docstrings are parseable (see Docstring Schemas).
- Use `strict=True` with explicit schemas to ensure exact property sets in production-sensitive tools.
:::


---

---
id: auto-execution-modes
title: Auto Execution Modes
sidebar_position: 4
slug: /multi-agent/auto-execution-modes
description: Control how agents auto-run tools and sub-agents to reach a final answer — disable | auto | agent-only | tool-only.
---

### Overview

This guide explains how to control the auto-execution of tools and sub-agents using a single, unified API:
- Call `ManagerAgent.run(messages_or_string, options={"mode": ...})`
- Choose an execution mode that fits your workflow.

### Execution Modes

Set `options.mode` to select behavior:

- **`"disable"`**: Do not auto-run tools. Returns the assistant’s first `tool_calls` payload to the caller for manual handling.
- **`"auto"`** (default): Auto-run both agent tools (sub-agents) and custom tools until a final answer is reached (or `max_loops` is exceeded).
- **`"agent-only"`**: Auto-run only agent tools (sub-agents). If a custom tool is requested, pending `tool_calls` are returned.
- **`"tool-only"`**: Auto-run only custom tools. If an agent tool is requested, pending `tool_calls` are returned.

### Running in Colab

To run this notebook in Google Colab, install the package in a code cell:

```bash
!pip install usf-agents
```

### Code

```python
import os
import asyncio
import nest_asyncio
from usf_agents import ManagerAgent, SubAgent

nest_asyncio.apply()

USF_API_KEY = os.getenv("USF_API_KEY") or "YOUR_API_KEY_HERE"

async def main():
    api_key = USF_API_KEY

    # Manager orchestrates tools and sub-agents
    mgr = ManagerAgent(
        usf_config={
            "api_key": api_key,
            "model": "usf-mini"
        }
    )

    # Simple sub-agent exposed as a tool
    writer = SubAgent({
        "name": "writer",
        "description": "Write short outputs.",
        "context_mode": "NONE",
        "usf_config": {
            "api_key": api_key,
            "model": "usf-mini"
        }
    })
    mgr.add_sub_agent(writer)  # exposed as tool: agent_writer

    # --- Auto (default) ---
    result = await mgr.run(
        "Ask agent_writer to write a 1-line poem about ocean.",
        {"mode": "auto"}
    )
    print("Auto mode result:", result)

    # --- Disable (never auto-run; return tool_calls) ---
    messages = [
        {"role": "user", "content": "Call any tool but do not auto-execute it."}
    ]
    payload = await mgr.run(messages, {"mode": "disable"})
    print("Disable mode payload:", payload)  # expect {'status':'tool_calls', ...}

    # --- Agent-only (only sub-agents auto-execute) ---
    agent_only = await mgr.run(
        "Ask agent_writer to write a motto about focus.",
        {"mode": "agent-only"}
    )
    print("Agent-only mode:", agent_only)

    # For completeness, tool-only mode is symmetric:
    # - If a custom tool is requested -> executes automatically
    # - If an agent tool is requested -> returns {'status':'tool_calls', ...}

if __name__ == '__main__':
    asyncio.run(main())
```

### Notes

- `ManagerAgent.run(...)` always returns a normalized result:
  - `{"status": "final", "content": "..."}`
  - or `{"status": "tool_calls", "tool_calls": [...]}`
- Use `{"mode": "disable"}` when you need full manual control over tool execution (e.g., to run tools in your own environment and append their results).
- `max_loops` can be controlled via `options.max_loops` when you want to bound retries/iterations.


---

---
id: context-modes
title: Context Modes
description: Control how much context a SubAgent receives — NONE | OPTIONAL | REQUIRED. Plus history and trim_last_user flags.
sidebar_position: 2
---

## Overview

Each `SubAgent` declares a `context_mode` that determines what the sub-agent receives when invoked as a tool by the manager, along with two flags that control whether parent history is included, and if the last user message should be trimmed.

:::info Note
`context_mode` applies to `SubAgent` only. `ManagerAgent` does not accept `context_mode` and ignores `TaskPayload.context`. Provide history to the manager as a list of messages and set system context via `usf_config.introduction`/`knowledge_cutoff` and optional `backstory`/`goal`.
:::

:::note Available Modes
- **NONE**: No parent conversation is provided; `context` must be omitted.
- **OPTIONAL**: `context` is a free-form string and may be omitted; parent history is included only when `history=True`.
- **REQUIRED**: `context` is a required non-empty string; parent history is included only when `history=True`.
:::

### History Flags

- `history` (bool, default `False`): When `True`, append the parent history as-is before the final user task.
- `trim_last_user` (bool, default `False`): When `True` and the last history message has `role: "user"`, drop that last user message before appending (useful when the task restates the last user’s request).

Defaults
- history: False
- trim_last_user: False

These are per-agent policy flags and default to False unless set on the agent spec.

### System Prompt Composition

Meanings of the fields and how to author them:

- **introduction**
  - What it is: A short statement of the assistant’s identity, role, and tone.
  - Use it for: Voice, audience, and scope boundaries.
  - Keep it: Short and declarative.
  - Example: "You are a concise, senior Python engineer who explains trade-offs clearly."

- **knowledge_cutoff**
  - What it is: The date after which information may be incomplete.
  - Use it for: Setting expectations about data freshness; prompting verification for newer facts.
  - Format: ISO-like date (e.g., "2024-10").
  - Example: "Knowledge cutoff: 2024-10."

- **backstory**
  - What it is: Stable persona and guiding principles that shape judgment across tasks.
  - Use it for: Domain strengths, values, constraints, safety posture, communication style.
  - Keep it: Timeless, not task-specific; avoid step-by-step instructions.
  - Example: "Ex-Google infra engineer focused on correctness and reproducibility; favors evidence-based recommendations; secure-by-design."

- **goal**
  - What it is: Clear outcomes the assistant aims to achieve for users.
  - Use it for: Objectives, scope, and success criteria that guide responses.
  - Keep it: Outcome-oriented, not procedural; avoid ephemeral details.
  - Example: "Help users design, debug, and optimize production-grade Python services while minimizing operational risk."

- **context**
  - What it is: Task-specific facts, constraints, inputs, and preferences for the current request.
  - Use it for: Environment details, versions, links, dataset snippets, acceptance criteria.
  - Keep it: Concrete, time-bound, minimal but sufficient.
  - Example: "Troubleshooting a Flask app on Python 3.12; CPU spikes under load test. Target P95 latency < 120 ms; no dependency upgrades."

**Writing Tips**
- Avoid contradictions across fields; if in doubt, prefer the context of the current task.
- Separate identity (backstory), outcomes (goal), and situational facts (context).
- Be succinct; avoid meta or implementation details.

## How it Works

- Use `context_mode` to precisely control what the sub-agent sees.
- Prefer tighter context for deterministic tools, and broader (or explicit) context for summarizers/writers that depend on history.
- If you include history, you can optionally trim the last user message via `trim_last_user=True` so the final task acts as the latest instruction.


## Running in Colab

You can run these examples directly in Google Colab.

- Install the SDK:
```bash
!pip install -q usf-agents
```

- Set your API key:
```python
import os
os.environ["USF_API_KEY"] = "YOUR_API_KEY"
```

- Copy a snippet from the Code section below into a new cell and run it.

## Code

### `NONE` (No Parent Context)

```python
from usf_agents import SubAgent

writer = SubAgent({
    "name": "writer",
    "context_mode": "NONE",
    "description": "Writes concise, polished short-form text.",
    "task_placeholder": "Describe the writing task",
    "usf_config": {"api_key": "...", "model": "usf-mini"}
})
```

### `OPTIONAL` (Context Optional)

```python
from usf_agents import SubAgent

researcher = SubAgent({
    "name": "researcher",
    "context_mode": "OPTIONAL",
    "description": "Looks up and synthesizes current knowledge.",
    "task_placeholder": "Describe the research request",
    "usf_config": {"api_key": "...", "model": "usf-mini"}
})
```

### `REQUIRED` (Context Required)

```python
from usf_agents import SubAgent

coder = SubAgent({
    "name": "coder",
    "context_mode": "REQUIRED",
    "description": "Generates or refactors code from natural-language specifications.",
    "task_placeholder": "Describe the coding task",
    "usf_config": {"api_key": "...", "model": "usf-mini"}
})
```

### Per-Agent History Policy (creation time)

You can set history and trim_last_user on each SubAgent at creation.

**REQUIRED (Context Required; History Opt-in)**
```python
from usf_agents import SubAgent

coder = SubAgent({
    "name": "coder",
    "context_mode": "REQUIRED",
    "description": "Generates/refactors code.",
    "usf_config": {"api_key": "...", "model": "usf-mini"},
    # History policy (defaults are False)
    "history": True,
    "trim_last_user": True
})
```

**OPTIONAL (Context Optional; History Opt-in)**
```python
from usf_agents import SubAgent

researcher = SubAgent({
    "name": "researcher",
    "context_mode": "OPTIONAL",
    "description": "Research and synthesis.",
    "usf_config": {"api_key": "...", "model": "usf-mini"},
    "history": False,
    "trim_last_user": False
})
```

### Manager-driven selection (with context and history)

```python
from usf_agents import ManagerAgent, SubAgent

mgr = ManagerAgent(
    usf_config={"api_key": "...", "model": "usf-mini"}
)
coder = SubAgent({
    "name": "coder",
    "context_mode": "OPTIONAL",
    "description": "Generates or refactors code from natural-language specifications.",
    "task_placeholder": "Describe the coding task",
    "usf_config": {"api_key": "...", "model": "usf-mini"}
})
mgr.add_sub_agent(coder)

# Ask the manager to call the appropriate sub-agent tool.
# The manager applies the sub-agent's history policy:
#   - history (default False unless set on SubAgent spec)
#   - trim_last_user (default False unless set on SubAgent spec)
prompt = "Ask agent_coder to add 3 into 4. Context: 2+2 is 4."
result = await mgr.run(prompt, {"mode": "auto"})
print(result)
```


:::note Context Rules
- NONE: `context` must be omitted.
- OPTIONAL: `context` may be omitted (string when provided).
- REQUIRED: `context` is required and must be a non-empty string.
- History is included only when `history=True`; when `trim_last_user=True` and the last history message is a user message, it is dropped before appending.
:::

:::tip Guidelines
- Prefer **NONE** for deterministic sub-agents that don’t need prior chat.
- Use **OPTIONAL** when you sometimes have extra context to pass or want to optionally include history.
- Use **REQUIRED** when you want explicit context provided for every delegation.
- Use `trim_last_user=True` to avoid repeating the latest user message if the task already restates it.
:::

## Enforcement and API behavior

Single public API: `.run(...)`.

- SubAgent.run:
  - Accepts a TaskPayload-like dict: `{"task": "...", "context": "..."}`.
    - Messages are shaped using `context_mode`, `introduction`, `knowledge_cutoff`, `backstory`, and `goal`.
    - Enforces REQUIRED context. If `context_mode="REQUIRED"` and no non-empty `context` is provided, a `ValueError` is raised.
  - Accepts a raw `str` (treated as the task) or `List[Message]`:
    - With `context_mode="REQUIRED"`, calling with a raw string or a messages list raises `ValueError` (provide a dict with a non-empty `context` instead).
- ManagerAgent.run:
  - Accepts `str`, `List[Message]`, or a TaskPayload-like dict.
  - When provided a dict, the manager uses only `{'task': ...}` and ignores `'context'`. System context comes from `usf_config.introduction`/`knowledge_cutoff` and optional `backstory`/`goal`.

### Examples

REQUIRED enforcement via SubAgent.run with dict:
```python
from usf_agents import SubAgent

sub_required = SubAgent({
    "name": "Analyst",
    "description": "Analyze logs with required context.",
    "context_mode": "REQUIRED",
    "usf_config": {"api_key": "...", "model": "usf-mini"},
})

# OK: provides context
out = await sub_required.run({"task": "Assess error spikes", "context": "Logset ID: prod-2025w01"})

# Raises ValueError if raw string without context
try:
    await sub_required.run("Assess error spikes")
except ValueError as e:
    print("Expected:", e)
```

Direct call with `.run(...)` in OPTIONAL/NONE modes:
```python
sub_optional = SubAgent({
    "name": "Summarizer",
    "description": "Summarize content succinctly.",
    "context_mode": "OPTIONAL",
    "usf_config": {"api_key": "...", "model": "usf-mini"}
})

# OK with raw string (OPTIONAL mode)
out = await sub_optional.run("Summarize: We shipped v2 yesterday; highlight the key changes.")
```

### Related APIs

- `ManagerAgent.run(messages_or_string_or_task_dict, options={"mode":"auto"})`: Manager-driven planning + tool execution loop until final when allowed.


---

---
id: custom-instruction
title: Custom Instruction
description: Set a custom final-response instruction text (overwrite) for managers and sub-agents.
sidebar_position: 5
slug: /multi-agent/custom-instruction
---

## Overview

Sub-agents can use the same final-response instruction controls as top-level agents. By default, a sub-agent inherits the manager’s config, but you can override this behavior per sub-agent.

This page focuses on setting a custom final-response instruction (overwrite) per agent. For execution flow and other modes, see [Auto Execution Modes](/docs/multi-agent/auto-execution-modes).

:::note Ways to Override
- Explicit `SubAgent` with its own `usf_config`.
- `ManagerAgent.add_sub_agents([...{"usf_overrides": {...}}...])`
:::

## How it Works

- A sub-agent inherits the manager’s `final_response` instruction behavior unless you provide overrides.
- You can replace the final-response instruction entirely with your own custom text (overwrite).
- Merge semantics:
  - Shallow merge overall with targeted deep merges for `planning`, `tool_calling`, and `final_response`.
  - You can override just `final_response` without copying the entire config.


## Running in Colab

You can run these examples directly in Google Colab.

- Install the SDK:
```bash
!pip install -q usf-agents
```

- Set your API key:
```python
import os
os.environ["USF_API_KEY"] = "YOUR_API_KEY"
```

- Copy a snippet from the Code section below into a new cell and run it.

## Code

### Manager-level Custom Instruction (overwrite)

```python
import os
from usf_agents import ManagerAgent

api_key = os.getenv("USF_API_KEY")

mgr_overwrite = ManagerAgent(
    usf_config={
        "api_key": api_key,
        "model": "usf-mini",
        "final_response": {
            "final_instruction_mode": "overwrite",
            "final_instruction_text": "<IMPORTANT>\nProvide a concise, complete answer without calling any services.\n</IMPORTANT>"
        }
    }
)
```

### A) Explicit SubAgent with `usf_config`

```python
import os
from usf_agents import ManagerAgent, SubAgent

api_key = os.getenv("USF_API_KEY")

mgr = ManagerAgent(
    usf_config={"api_key": api_key, "model": "usf-mini"}
)

writer = SubAgent({
    "name": "writer",
    "description": "Writes concise, polished text.",
    "task_placeholder": "Describe the writing task",
    "context_mode": "NONE",
    "usf_config": {
        "api_key": api_key,
        "model": "usf-mini",
        "final_response": {
            "final_instruction_mode": "overwrite",
            "final_instruction_text": "<IMPORTANT>\nProvide concise answers with a short summary.\n</IMPORTANT>"
        }
    }
})

mgr.add_sub_agent(writer)
```


### B) `add_sub_agents` with Dictionary Spec

```python
import os
from usf_agents import ManagerAgent

api_key = os.getenv("USF_API_KEY")

mgr = ManagerAgent(
    usf_config={"api_key": api_key, "model": "usf-mini"}
)

mgr.add_sub_agents(
    [
        {
            "name": "writer",
            "description": "Writes concise, polished text.",
            "usf_overrides": {
                "final_response": {
                    "final_instruction_mode": "overwrite",
                    "final_instruction_text": "<IMPORTANT>\nProvide concise answers with a short summary.\n</IMPORTANT>"
                }
            }
        }
    ]
)
```

:::note Notes on Merging
- `usf_overrides` are shallow-merged onto the manager’s base config with a targeted deep-merge for `planning`, `tool_calling`, and `final_response`.
- You can override `final_response` without copying the entire config.
:::


---

---
id: manager-driven-delegation
title: Manager-driven Delegation
description: SubAgents are exposed as tools. The Manager LLM selects and invokes them via tool calls. No manual delegate API.
sidebar_position: 3
slug: /multi-agent/manager-driven-delegation
---

## Overview

USF Agents uses a manager-driven delegation model: a `ManagerAgent` exposes its `SubAgent`s as tools, and the Manager's LLM plans, selects, and invokes those SubAgent tools via tool calls during a normal run. There is no manual delegate API anymore.

This page explains how the manager-driven approach works, how to run it in Colab, and provides ready-to-run code snippets.

## How it Works

- Compose SubAgents into a Manager:
  - Add SubAgents with `add_sub_agent(...)` or `add_sub_agents(...)`.
  - A tool function named `agent_{slug(name)}` is auto-generated by default (you can override with `alias=...`).
- Manager-driven orchestration:
  - Call `ManagerAgent.run(...)` to let the LLM plan and select tools/SubAgents.
  - When the LLM picks a SubAgent, it is invoked as a tool under the hood.
- Context policy:
  - The public "context" argument is included per each SubAgent's `context_mode`:
    - `NONE`: omitted.
    - `OPTIONAL`: included when provided.
    - `REQUIRED`: must be provided and non-empty.
- History shaping (simple and explicit):
  - Controlled by per-agent flags set at creation time:
    - `history`: include parent conversation history when invoking the SubAgent (default `False`).
    - `trim_last_user`: when including history, optionally drop the last user message (default `False`).
  - The manager applies these flags when shaping messages. No sanitize helper is used.

## Direct SubAgent calls (optional)

While the recommended pattern is manager-driven delegation, you can also invoke a SubAgent directly via a single public API.

- `sub.run(..., options=None)`
  - Accepts a TaskPayload-like dict: `{"task": "...", "context": "..."}`.
    - Shapes messages using the sub-agent’s policy:
      - `context_mode` (NONE | OPTIONAL | REQUIRED)
      - `backstory`, `goal`
      - `introduction`, `knowledge_cutoff` (from the sub-agent’s USF config)
    - Enforces REQUIRED context (raises `ValueError` if missing).
  - Also accepts a raw `str` (treated as a task) or a list of OpenAI-format messages:
    - With `context_mode="REQUIRED"`, calling with raw string/messages raises `ValueError` (provide a dict with a non-empty `context` instead).
  - Returns either `{'status':'final','content':...}` or `{'status':'tool_calls','tool_calls':[...]}`.

Examples:

```python
from usf_agents import SubAgent

sub = SubAgent({
    "name": "Summarizer",
    "description": "Summarize content succinctly.",
    "context_mode": "OPTIONAL",
    "usf_config": {"api_key": "...", "model": "usf-mini"}
})

# Direct call (raw string) — OK for OPTIONAL/NONE
out = await sub.run("Summarize: Large Language Models are ...")

# Context-shaped task (dict) — REQUIRED enforcement when context_mode="REQUIRED"
out2 = await sub.run({"task": "Summarize the article", "context": "Internal blog v2"})
```

Note on REQUIRED:
- For `context_mode: "REQUIRED"`, `sub.run(...)` raises `ValueError` unless you pass a dict including a non-empty `"context"`.
- For OPTIONAL/NONE, you may pass a raw string or message list, or use a dict with optional `"context"`.

## Running in Colab

You can run these examples directly in Google Colab.

- Install the SDK:
```bash
!pip install -q usf-agents
```

- Set your API key:
```python
import os
os.environ["USF_API_KEY"] = "YOUR_API_KEY"
```

- Copy a snippet from the Code section below into a new cell and run it.

For a full notebook walkthrough of manager/sub-agent delegation, see:
- Planner-Worker Delegation notebook: [../jupyter-notebooks/planner-worker-delegation.md](../jupyter-notebooks/planner-worker-delegation.md)

## Code

### Manager-driven selection (basic)

```python
import os
import asyncio
import nest_asyncio
from usf_agents import ManagerAgent, SubAgent

nest_asyncio.apply()

async def main():
    api_key = os.getenv("USF_API_KEY")

    mgr = ManagerAgent(
        usf_config={"api_key": api_key, "model": "usf-mini"}
    )

    writer = SubAgent({
        "name": "writer",
        "description": "Draft short outputs.",
        "task_placeholder": "Describe the writing task",
        "context_mode": "OPTIONAL",
        "usf_config": {"api_key": api_key, "model": "usf-mini"}
    })

    # Expose as tool (default name agent_writer)
    mgr.add_sub_agent(writer)

    # Inspect available tools
    tools = [t["function"]["name"] for t in mgr.list_tools()]
    print("Tools:", tools)  # e.g., ["agent_writer", ...]

    # Manager-driven orchestration (LLM chooses tools)
    result = await mgr.run("Ask agent_writer to draft a 1-line tip about testing.", {"mode": "auto"})
    print(result)  # {'status':'final','content':'...'} or {'status':'tool_calls',...}

asyncio.run(main())
```

### Context policy and history example

```python
import os
import asyncio
import nest_asyncio
from usf_agents import ManagerAgent, SubAgent

nest_asyncio.apply()

async def main():
    api_key = os.getenv("USF_API_KEY")

    mgr = ManagerAgent(
        usf_config={"api_key": api_key, "model": "usf-mini"}
    )

    writer = SubAgent({
        "name": "writer",
        "description": "Draft short outputs.",
        "task_placeholder": "Describe the writing task",
        "context_mode": "OPTIONAL",
        "history": True,          # include parent conversation history
        "trim_last_user": True,   # optional: drop last user message when including history
        "usf_config": {"api_key": api_key, "model": "usf-mini"}
    })

    mgr.add_sub_agent(writer)

    result = await mgr.run(
        "Ask agent_writer to summarize the previous discussion in one sentence.",
        {"mode": "auto"}
    )
    print(result)

asyncio.run(main())
```

### Nested Delegation (Sub-agents of Sub-agents)

Any agent, including a SubAgent, can aggregate its own sub-agents. This enables nested delegation such as Manager → B → C. The Manager exposes B as a tool; when B runs (as a tool), it can itself select and invoke C (also as a tool) under the hood.

```python
import os
import asyncio
import nest_asyncio
from usf_agents import ManagerAgent, SubAgent

nest_asyncio.apply()

async def main():
    api_key = os.getenv("USF_API_KEY")

    # Top-level manager
    mgr = ManagerAgent(
        usf_config={"api_key": api_key, "model": "usf-mini"}
    )

    # Sub-agent B (has its own sub-agent)
    b = SubAgent({
        "name": "b",
        "description": "Intermediate specialist that can further delegate",
        "task_placeholder": "Describe B's task",
        "context_mode": "OPTIONAL",  # allow passing context down when provided
        "usf_config": {"api_key": api_key, "model": "usf-mini"}
    })

    # Sub-agent C (child of B)
    c = SubAgent({
        "name": "c",
        "description": "Leaf specialist (e.g., transformation or formatting)",
        "task_placeholder": "Describe C's task",
        "context_mode": "NONE",
        "usf_config": {"api_key": api_key, "model": "usf-mini"}
    })

    # Wire C under B, then B under manager
    b.add_sub_agent(c)
    mgr.add_sub_agent(b)

    # The manager will pick agent_b; when B runs, it can select agent_c internally
    result = await mgr.run(
        "Ask agent_b to use agent_c to uppercase the word 'testing', then return the result.",
        {"mode": "auto"}
    )
    print(result)  # {'status':'final','content':'TESTING'} (shape depends on model/config)

asyncio.run(main())
```

Notes:
- B’s execution (as a tool) receives its own composed tools (including C). This is what enables nested selection and execution.
- Each agent’s description should be clear and scoped to assist the LLM in selecting the right tool/agent.

### Combining Tools and Sub-agents

A Manager can expose both:
- Custom Python function tools (registered on the manager), and
- Sub-agents (exposed as tools)

```python
import os
import asyncio
import nest_asyncio
from usf_agents import ManagerAgent, SubAgent

nest_asyncio.apply()

# A simple custom tool
def calc_sum(a: int, b: int) -> int:
    """Add two integers and return the result."""
    return int(a) + int(b)

async def main():
    api_key = os.getenv("USF_API_KEY")

    mgr = ManagerAgent(
        usf_config={"api_key": api_key, "model": "usf-mini"}
    )

    # Register the custom function tool with an explicit schema
    mgr.add_function_tool(
        calc_sum,
        schema={
            "description": "Add two integers",
            "parameters": {
                "type": "object",
                "properties": {
                    "a": {"type": "integer", "description": "First addend"},
                    "b": {"type": "integer", "description": "Second addend"}
                },
                "required": ["a", "b"]
            }
        }
    )

    # Also compose a writing sub-agent
    writer = SubAgent({
        "name": "writer",
        "description": "Writes concise summaries.",
        "task_placeholder": "Describe the writing task",
        "context_mode": "OPTIONAL",
        "usf_config": {"api_key": api_key, "model": "usf-mini"}
    })
    mgr.add_sub_agent(writer)

    # The manager can choose to call calc_sum (custom tool) and agent_writer (sub-agent) in one run
    result = await mgr.run(
        "Use calc_sum to add 12 and 7, then ask agent_writer to summarize the result in 1 sentence.",
        {"mode": "auto"}
    )
    print(result)

asyncio.run(main())
```

Tips:
- Keep tool and sub-agent descriptions distinct to avoid selection ambiguity.
- You can pass decorator metadata or docstring-based schemas instead of explicit schemas; see the Tools docs for details.

## Tips

- Provide clear, distinct `description` values on each SubAgent to help the LLM select the right one.
- Ensure unique tool names; defaults are `agent_{slug(name)}`.
- Control automatic tool execution with `options.mode`: `"auto"` | `"disable"` | `"agent-only"` | `"tool-only"`.


---

---
id: overview
title: Multi-Agent Overview
description: Compose Manager and SubAgents, expose sub-agents as tools, and orchestrate end-to-end runs with a unified run API.
sidebar_position: 1
---

## Overview

USF Agents provides a simple way to compose multi-agent systems by combining a `ManagerAgent` with one or more `SubAgent` instances.

:::note Key Ideas
- ManagerAgent: Orchestrates a set of sub-agents and custom tools.
- ManagerAgent constructor only supports `usf_config` and does not accept `name`, `description`, or `context_mode`.
- SubAgent: A specialized capability, exposed as a tool to the manager.
- Each sub-agent can have its own context policy (`context_mode`) and USF config.
- Single public API: `run(...)` for both managers and sub-agents.
:::


## How it Works

:::note API rule
- `add_sub_agent(sub, spec_overrides=None, alias=None)`:
  - `alias` sets the tool function name for the sub-agent (defaults to `agent_{slug(name)}` when not provided).
  - `spec_overrides` can provide a `description` override for the composed tool surface. If neither the sub-agent nor overrides define a description, composition will raise.
:::

- Define a `ManagerAgent` that coordinates work.
- Create one or more `SubAgent` instances, each focused on a distinct responsibility (e.g., writing, coding, calculation).
- Expose each `SubAgent` to the manager as a tool using `add_sub_agent(sub)`. The tool name defaults to `agent_{slug(name)}` (e.g., `agent_writer`).
- Schemas are auto-generated from the SubAgent configuration. `task` is always required (its description can be customized via `task_placeholder`). A `context` string is included based on `context_mode`: omitted for `NONE`, optional for `OPTIONAL`, required for `REQUIRED`.
- Drive the end-to-end flow:
  - Use `ManagerAgent.run("...", {"mode":"auto"})` to plan, select tools/sub-agents, call them, and produce a final answer.
- Sub-agents can operate with different `context_mode` settings and independent `usf_config` to fine-tune behavior.

## Running in Colab

You can run these examples directly in Google Colab.

- Install the SDK:
```bash
!pip install -q usf-agents
```

- Set your API key:
```python
import os
os.environ["USF_API_KEY"] = "YOUR_API_KEY"
```

- Copy a snippet from the Code section below into a new cell and run it.

For a full notebook walkthrough of manager/sub-agent delegation, see:
- Planner-Worker Delegation notebook: [../jupyter-notebooks/planner-worker-delegation.md](../jupyter-notebooks/planner-worker-delegation.md)

## Code

### Register SubAgent (explicit)

```python
import os
import asyncio
import nest_asyncio
from usf_agents import ManagerAgent, SubAgent

nest_asyncio.apply()

async def main():
    api_key = os.getenv("USF_API_KEY")

    mgr = ManagerAgent(
        usf_config={"api_key": api_key, "model": "usf-mini"}
    )

    writer = SubAgent({
        "name": "writer",
        "context_mode": "NONE",
        "description": "Writes concise, polished short-form text.",
        "task_placeholder": "Describe the writing task",
        "usf_config": {"api_key": api_key, "model": "usf-mini"}
    })
    mgr.add_sub_agent(writer)

    result = await mgr.run(
        "Ask agent_writer to write a haiku about teamwork.",
        {"mode": "auto"}
    )
    if result.get("status") == "final":
        print("Final:", result.get("content"))
    else:
        print("Pending tool calls:", result.get("tool_calls"))

if __name__ == "__main__":
    asyncio.run(main())
```

### Minimal Composition

```python
import os
import asyncio
import nest_asyncio
from usf_agents import ManagerAgent, SubAgent

nest_asyncio.apply()

async def main():
    api_key = os.getenv("USF_API_KEY")

    mgr = ManagerAgent(
        usf_config={"api_key": api_key, "model": "usf-mini"}
    )

    writer = SubAgent({
        "name": "writer",
        "context_mode": "NONE",
        "description": "Writes concise, polished short-form text.",
        "task_placeholder": "Describe the writing task",
        "usf_config": {"api_key": api_key, "model": "usf-mini"}
    })

    mgr.add_sub_agent(writer)

    result = await mgr.run(
        "Ask agent_writer to write a haiku about teamwork.",
        {"mode": "auto"}
    )
    if result.get("status") == "final":
        print("Final:", result.get("content"))
    else:
        print("Pending tool calls:", result.get("tool_calls"))

if __name__ == "__main__":
    asyncio.run(main())
```

### Multiple Sub-Agents

```python
import os
import asyncio
import nest_asyncio
from usf_agents import ManagerAgent, SubAgent

nest_asyncio.apply()

async def main():
    api_key = os.getenv("USF_API_KEY")

    mgr = ManagerAgent(
        usf_config={"api_key": api_key, "model": "usf-mini"}
    )

    calc = SubAgent({
        "name": "calc",
        "description": "Performs numeric computations.",
        "task_placeholder": "Describe the calculation",
        "context_mode": "NONE",
        "usf_config": {"api_key": api_key, "model": "usf-mini"}
    })
    coder = SubAgent({
        "name": "coder",
        "description": "Generates or refactors code.",
        "task_placeholder": "Describe the coding task",
        "context_mode": "NONE",
        "usf_config": {"api_key": api_key, "model": "usf-mini"}
    })
    writer = SubAgent({
        "name": "writer",
        "description": "Writes concise, polished text.",
        "task_placeholder": "Describe the writing task",
        "context_mode": "NONE",
        "usf_config": {"api_key": api_key, "model": "usf-mini"}
    })

    mgr.add_sub_agent(calc)
    mgr.add_sub_agent(coder)
    mgr.add_sub_agent(writer)

    result = await mgr.run(
        "Compute 12*7, then write a 1-line summary.",
        {"mode": "auto"}
    )
    if result.get("status") == "final":
        print("Final:", result.get("content"))
    else:
        print("Pending tool calls:", result.get("tool_calls"))

if __name__ == "__main__":
    asyncio.run(main())
```

### Advanced Patterns

- Nested Delegation (Sub-agents of Sub-agents)
  - Any agent, including a SubAgent, can aggregate its own sub-agents, enabling Manager → B → C style delegation. See the full example:
    - [Nested Delegation (Sub-agents of Sub-agents)](./manager-driven-delegation.md#nested-delegation-sub-agents-of-sub-agents)

- Combining Tools and Sub-agents
  - A manager can expose both custom Python function tools and sub-agents in the same run.

```python
import os
import asyncio
import nest_asyncio
from usf_agents import ManagerAgent, SubAgent

nest_asyncio.apply()

def calc_sum(a: int, b: int) -> int:
    """
    Add two integers.

    Args:
        a (int): First addend.
        b (int): Second addend.
    """
    return int(a) + int(b)

async def main():
    api_key = os.getenv("USF_API_KEY")

    mgr = ManagerAgent(
        usf_config={"api_key": api_key, "model": "usf-mini"}
    )

    # Register custom function tool (schema inferred from docstring)
    mgr.add_function_tool(calc_sum)

    # Compose a writing sub-agent
    writer = SubAgent({
        "name": "writer",
        "description": "Writes concise summaries.",
        "task_placeholder": "Describe the writing task",
        "context_mode": "OPTIONAL",
        "usf_config": {"api_key": api_key, "model": "usf-mini"}
    })
    mgr.add_sub_agent(writer)

    # The manager can call both calc_sum (custom tool) and agent_writer (sub-agent) in one flow
    result = await mgr.run(
        "Use calc_sum to add 3 and 4, then ask agent_writer to summarize the result in 1 sentence.",
        {"mode": "auto"}
    )
    print(result)

if __name__ == "__main__":
    asyncio.run(main())
```

:::tip Best Practices
- Provide a clear, scoped `description` for every `SubAgent`.
- Use distinct, non-overlapping responsibilities across sub-agents to keep selection unambiguous.
- Tool names default to `agent_<slug(name)>` (e.g., `agent_writer`). Ensure uniqueness to prevent collisions.
:::

---

## Single-step API: run

USF Agents exposes a single public entry point on wrappers.

- SubAgent.run(...):
  - Accepts a TaskPayload-like dict: `{"task": "...", "context": "..."}`.
    - Shapes messages using the sub-agent’s policy:
      - `context_mode` (NONE | OPTIONAL | REQUIRED)
      - `backstory`, `goal`
      - `introduction`, `knowledge_cutoff` (from the agent’s USF config)
    - Enforces REQUIRED context (raises `ValueError` if missing).
  - Also accepts a `str` (treated as a task) or a list of OpenAI-format messages:
    - With `context_mode="REQUIRED"`, calling with raw string/messages raises `ValueError` (provide a dict with a non-empty `context` instead).
  - Returns either `{'status':'final','content':...}` or `{'status':'tool_calls','tool_calls':[...]}`.

- ManagerAgent.run(messages_or_string_or_task_dict, options):
  - Can auto-orchestrate plan → tool_calls → tool execution → re-entry loops until final when `options.mode` allows (e.g., `"auto"`).
  - Accepts:
    - `str`: a single user message
    - `List[Message]`: a pre-shaped conversation
    - `TaskPayload-like dict`: `{'task': ...}`. ManagerAgent ignores `'context'` and constructs messages from the task (system context comes from `usf_config.introduction`/`knowledge_cutoff`).


---

---
id: skip-planning-no-tools
title: Skip Planning When No Tools
description: Opt-in to bypass the planning stage when an agent has no tools.
sidebar_position: 4
---

## Overview

Planning is enabled by default for all agents. If an agent has no tools, you can opt in to skip the planning phase and directly produce a final response.

:::info
Managers with sub-agents will not skip planning, because sub-agents are exposed as tools.
:::

## How it Works

- Per-Agent setting: Enable `skip_planning_if_no_tools` on an agent to bypass planning whenever it has zero tools.
- Per-Run override: Even if the agent doesn’t have the flag set, you can opt in for a single `run` call.
- Sub-agent explicit opt-in: Sub-agents do not inherit the manager’s setting; enable it on each sub-agent that should skip planning when tool-less.
- When to use: For lightweight responders with no tools where planning adds latency but no value; for deterministic utility sub-agents that simply transform input.

## Running in Colab

You can run these examples directly in Google Colab.

- Install the SDK:
```bash
!pip install -q usf-agents
```

- Set your API key:
```python
import os
os.environ["USF_API_KEY"] = "YOUR_API_KEY"
```

- Copy a snippet from the Code section below into a new cell and run it.

## Code

### Per-Agent Opt-In (Manager with no tools)

```python
from usf_agents import ManagerAgent

mgr = ManagerAgent(
    usf_config={
        "api_key": "...",
        "model": "usf-mini",
        "skip_planning_if_no_tools": True
    }
)

# Because no tools are registered and skip_planning_if_no_tools=True,
# the manager produces a direct final response.
result = await mgr.run("Explain circuit breakers in 2 lines", {"mode": "auto"})
print(result)  # {'status':'final','content':'...'}
```

### Per-Run Override (without changing config)

```python
from usf_agents import ManagerAgent

mgr = ManagerAgent(
    usf_config={
        "api_key": "...",
        "model": "usf-mini"
    }
)

# Per-call override: skip planning only for this run when there are zero tools
result = await mgr.run(
    "Explain Kafka in two lines",
    {"mode": "auto", "skip_planning_if_no_tools": True}
)
print(result)  # {'status':'final','content':'...'}
```

### Sub-Agent Explicit Opt-In

Sub-agents do not inherit `skip_planning_if_no_tools` from the manager and must opt in explicitly.

```python
from usf_agents import ManagerAgent, SubAgent

api_key = "..."

mgr = ManagerAgent(
    usf_config={"api_key": api_key, "model": "usf-mini"}
)

writer = SubAgent({
    "name": "writer",
    "description": "Writes concise, polished text.",
    "task_placeholder": "Describe the writing task",
    "context_mode": "NONE",
    "usf_config": {
        "api_key": api_key,
        "model": "usf-mini",
        "skip_planning_if_no_tools": True
    }
})
mgr.add_sub_agent(writer)
```

:::tip When to Use
- For lightweight responders with no tools, where planning adds latency but no value.
- For deterministic utility sub-agents that simply transform input without tool selection.
:::


---

## License

See: https://agents-docs.us.inc/license
