import asyncio
import json
import types
import pytest

from usf_agents.multi_agent.base import ManagerAgent, SubAgent
from usf_agents.runtime.decorators import tool


@pytest.mark.asyncio
async def test_decorator_schema_used_when_no_explicit_schema(monkeypatch):
    @tool(
        alias="sum_tool",
        schema={
            "description": "Sum integers",
            "parameters": {
                "type": "object",
                "properties": {
                    "numbers": {"type": "array", "description": "List of ints"}
                },
                "required": ["numbers"]
            }
        }
    )
    def calc_sum(numbers: list[int]) -> int:
        return sum(numbers)

    mgr = ManagerAgent(
        usf_config={"api_key": "DUMMY", "model": "usf-mini"}
    )
    mgr = ManagerAgent(
        usf_config={"api_key": "DUMMY", "model": "usf-mini"}
    )
    # No explicit schema passed here; decorator-provided schema must be used
    mgr.add_function_tool(calc_sum)

    tools = mgr.list_tools()
    names = [(t.get("function") or {}).get("name") for t in tools]
    # Function name in OpenAI tool equals alias (display name)
    assert "sum_tool" in names

    # Stub USFAgent.run to simulate planning -> tool call -> final
    async def fake_run(messages, options=None):
        has_tool_results = any(m.get("role") == "tool" for m in messages)
        if not has_tool_results:
            yield {"type": "plan", "content": "plan", "agent_status": "running", "tool_choice": {"type": "function"}}
            yield {"type": "tool_calls", "tool_calls": [{"id": "1", "type": "function", "function": {"name": "sum_tool", "arguments": json.dumps({"numbers": [1, 2, 3]})}}]}
        else:
            yield {"type": "final_answer", "content": "done"}

    monkeypatch.setattr(mgr.usf, "run", fake_run)

    result = await mgr.run([{"role": "user", "content": "sum"}], {"mode": "auto"})
    assert isinstance(result, dict) and result.get("status") == "final" and result.get("content") == "done"


@pytest.mark.asyncio
async def test_explicit_schema_overrides_decorator(monkeypatch):
    @tool(
        alias="echo_alias",
        schema={
            "description": "Echo from decorator",
            "parameters": {"type": "object", "properties": {"text": {"type": "string"}}, "required": ["text"]},
        }
    )
    def echo(text: str) -> str:
        return text

    mgr = ManagerAgent(usf_config={"api_key": "DUMMY", "model": "usf-mini"})
    # Provide explicit schema; must take precedence
    mgr.add_function_tool(
        echo,
        alias=None,  # keep decorator alias
        schema={
            "description": "Explicit schema desc",
            "parameters": {"type": "object", "properties": {"text": {"type": "string"}}, "required": ["text"]},
        },
    )

    tools = mgr.list_tools()
    # alias should still apply as final display name
    assert any((t.get("function") or {}).get("name") == "echo_alias" for t in tools)

    async def fake_run(messages, options=None):
        has_tool_results = any(m.get("role") == "tool" for m in messages)
        if not has_tool_results:
            yield {"type": "plan", "content": "plan", "agent_status": "running", "tool_choice": {"type": "function"}}
            yield {"type": "tool_calls", "tool_calls": [{"id": "1", "type": "function", "function": {"name": "echo_alias", "arguments": json.dumps({"text": "hi"})}}]}
        else:
            yield {"type": "final_answer", "content": "done"}

    monkeypatch.setattr(mgr.usf, "run", fake_run)
    result = await mgr.run([{"role": "user", "content": "echo"}], {"mode": "auto"})
    assert isinstance(result, dict) and result.get("status") == "final" and result.get("content") == "done"


def _mk_schema(props, required):
    return {"description": "x", "parameters": {"type": "object", "properties": props, "required": required}}


@pytest.mark.asyncio
async def test_strict_properties_mismatch_raises():
    @tool()
    def f(a: int, b: int = 1) -> int:
        "Doc"
        return a + b

    mgr = ManagerAgent(usf_config={"api_key": "DUMMY", "model": "usf-mini"})
    # properties only includes 'a' so strict=True should raise
    with pytest.raises(Exception) as ei:
        mgr.add_function_tool(f, schema=_mk_schema({"a": {"type": "number"}}, ["a"]), strict=True)
    assert "properties mismatch" in str(ei.value) or "Schema Validation Error" in str(ei.value)
