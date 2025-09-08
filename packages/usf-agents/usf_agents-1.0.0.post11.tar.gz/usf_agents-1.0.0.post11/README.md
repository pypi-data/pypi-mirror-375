# USF Agents — Simplify the Complex, Amplify the Intelligent for Enterprise

Orchestrate multiple agents with ease: register agents, integrate tools, define custom instructions, and leverage multiple models.  
Enterprise-grade and production-ready, with full control, deep customization, strong defaults, clear boundaries, and developer-focused APIs.

---

# USF Agents

This is the official documentation for the **USF Agents Python SDK**.

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