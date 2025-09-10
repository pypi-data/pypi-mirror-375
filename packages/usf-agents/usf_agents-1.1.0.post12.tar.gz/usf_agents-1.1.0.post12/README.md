# USF Agents — Simplify the Complex, Amplify the Intelligent for Enterprise

Orchestrate multiple agents with ease: register agents, integrate tools, define custom instructions, and leverage multiple models.  
Enterprise-grade and production-ready, with full control, deep customization, strong defaults, clear boundaries, and developer-focused APIs.

---

# USF Agents

This is the official documentation for the **USF Agents Python SDK**.

Important: Responses are now OpenAI-compatible by default
- Non-streaming methods return OpenAI chat.completion dicts: object="chat.completion"
- Streaming methods yield OpenAI chat.completion.chunk dicts: object="chat.completion.chunk"
- USF-only stages are indicated via vendor extension x_usf, e.g. {"stage":"plan"} or {"stage":"tool_result"}

📖 **Docs:** [Quickstart](https://agents-docs.us.inc/docs/quickstart) | [Installation](https://agents-docs.us.inc/docs/start/installation) | [Configuration](https://agents-docs.us.inc/docs/start/configuration) | [Troubleshooting / FAQ](https://agents-docs.us.inc/docs/troubleshooting-faq)

---

## Installation & Requirements

### Requirements
- Python **3.9+**
- USF API key (set as an environment variable)

### Install the SDK

```bash
pip install usf-agents
````

Other package managers:

```bash
# uv
uv add usf-agents

# poetry
poetry add usf-agents

# pdm
pdm add usf-agents
```

### Set Your API Key

```bash
# macOS/Linux
export USF_API_KEY=YOUR_KEY

# Windows PowerShell
$env:USF_API_KEY="YOUR_KEY"

# Windows CMD
set USF_API_KEY=YOUR_KEY
```

### (Optional) Virtual Environment

```bash
python -m venv .venv

# macOS/Linux
source .venv/bin/activate

# Windows PowerShell
.venv\Scripts\Activate.ps1
```

### Verify Installation

```bash
pip show usf-agents
```

Minimal import check:

```bash
python - <<'PY'
try:
    import usf_agents
    print("usf_agents import: OK")
except Exception as e:
    print("Import failed:", e)
PY
```

---

## Quick Sanity Run

Requires your `USF_API_KEY` to be set.

Non-streaming (OpenAI chat.completion):

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
            "model": "usf-mini",
        }
    )
    completion = await mgr.run("Say 'hello world'", {"mode": "auto"})
    # completion is OpenAI-compatible: object="chat.completion"
    choice = (completion.get("choices") or [{}])[0] or {}
    message = choice.get("message") or {}
    if message.get("tool_calls"):
        print("Tool Calls (finish_reason=tool_calls):", message.get("tool_calls"))
    else:
        print("Final:", (message.get("content") or ""))

if __name__ == "__main__":
    asyncio.run(main())
```

Streaming (OpenAI chat.completion.chunk):

```python
# stream_sanity.py
import os
import asyncio
import nest_asyncio
from usf_agents import ManagerAgent

nest_asyncio.apply()

async def main():
    mgr = ManagerAgent(
        usf_config={
            "api_key": os.getenv("USF_API_KEY"),
            "model": "usf-mini",
        }
    )
    async for chunk in mgr.stream(
        "Briefly introduce yourself.",
        {"mode": "auto", "streaming": {"plan_chunk_size": 80}}
    ):
        # chunk is OpenAI-compatible: object="chat.completion.chunk"
        delta = ((chunk.get("choices") or [{}])[0] or {}).get("delta") or {}
        x_usf = chunk.get("x_usf") or {}
        stage = x_usf.get("stage")
        if "tool_calls" in delta:
            print("stream tool_calls:", delta["tool_calls"])
        elif "content" in delta and delta["content"]:
            if stage == "plan":
                print("stream plan delta:", delta["content"])
            else:
                print("stream final delta:", delta["content"])
        elif stage == "tool_result":
            print("stream tool_result:", x_usf)
        finish = ((chunk.get("choices") or [{}])[0] or {}).get("finish_reason")
        if finish:
            print("stream finished with reason:", finish)

if __name__ == "__main__":
    asyncio.run(main())
```

Run it:

```bash
python sanity.py
python stream_sanity.py
```

---

## Migration Note

This release adopts OpenAI-compatible response formats by default:
- ManagerAgent.run(...) returns an OpenAI chat.completion dict.
- ManagerAgent.stream(...) yields OpenAI chat.completion.chunk dicts.
- Ephemeral helpers (run_ephemeral, run_ephemeral_final, run_many_parallel) now produce OpenAI shapes as well.

Breaking changes:
- Legacy shapes like {'status': 'final' | 'tool_calls', 'content': ..., 'tool_calls': [...]} are removed.
- Update integrations to read choices[0].message.* for non-stream, and choices[0].delta.* for streaming.

---

## Documentation

### Getting Started

* [Quickstart](https://agents-docs.us.inc/docs/quickstart)
* [Installation](https://agents-docs.us.inc/docs/start/installation)
* [Configuration](https://agents-docs.us.inc/docs/start/configuration)
* [Troubleshooting / FAQ](https://agents-docs.us.inc/docs/troubleshooting-faq)

### Tools

* [Overview](https://agents-docs.us.inc/docs/tools/overview)
* [Docstrings](https://agents-docs.us.inc/docs/tools/docstrings)
* [Decorator](https://agents-docs.us.inc/docs/tools/decorator)
* [Explicit Schema](https://agents-docs.us.inc/docs/tools/explicit-schema)
* [Type Mapping](https://agents-docs.us.inc/docs/tools/type-mapping)
* [Registry & Batching](https://agents-docs.us.inc/docs/tools/registry-and-batch-tool-registration)

### Multi-Agent

* [Overview](https://agents-docs.us.inc/docs/multi-agent/overview)
* [Execution Modes](https://agents-docs.us.inc/docs/multi-agent/auto-execution-modes)
* [Context Modes](https://agents-docs.us.inc/docs/multi-agent/context-modes)
* [Manager-driven Delegation](https://agents-docs.us.inc/docs/multi-agent/manager-driven-delegation)
* [Skip Planning (No Tools)](https://agents-docs.us.inc/docs/multi-agent/skip-planning-no-tools)
* [Custom Instruction](https://agents-docs.us.inc/docs/multi-agent/custom-instruction)

### Jupyter Notebook Guides

* [Email Drafting Assistant](https://agents-docs.us.inc/docs/jupyter-notebooks/email-drafting-assistant)
* [Customer Support Triage](https://agents-docs.us.inc/docs/jupyter-notebooks/customer-support-triage)
* [Planner-Worker Delegation](https://agents-docs.us.inc/docs/jupyter-notebooks/planner-worker-delegation)
* [Strict JSON Output](https://agents-docs.us.inc/docs/jupyter-notebooks/strict-json-output)
* [Currency Converter](https://agents-docs.us.inc/docs/jupyter-notebooks/currency-converter)

### FastAPI Apps

* [Email Drafting Assistant](https://agents-docs.us.inc/docs/fastapi-apps/email-drafting-assistant/README)
* [Customer Support Triage](https://agents-docs.us.inc/docs/fastapi-apps/customer-support-triage/README)
* [Planner-Worker Delegation](https://agents-docs.us.inc/docs/fastapi-apps/planner-worker-delegation/README)
* [Strict JSON Output](https://agents-docs.us.inc/docs/fastapi-apps/strict-json-output/README)
* [Currency Converter](https://agents-docs.us.inc/docs/fastapi-apps/currency-converter/README)

---

## License

See [LICENSE](https://agents-docs.us.inc/license).