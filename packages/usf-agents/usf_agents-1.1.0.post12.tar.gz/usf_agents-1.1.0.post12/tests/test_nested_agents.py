import json
import pytest

from usf_agents.multi_agent.base import SubAgent, ManagerAgent
from usf_agents.multi_agent.base import _acollect_final_answer as real_collect


@pytest.mark.asyncio
async def test_any_agent_can_add_sub_agent_and_list_tools():
    # Any agent (including SubAgent) can aggregate other agents as sub-agents (agent-as-tool)
    parent = SubAgent({
        'name': 'parent',
        'context_mode': 'NONE',
        'description': 'Parent agent',
        'usf_config': {'api_key': 'DUMMY', 'model': 'usf-mini'}
    })
    child = SubAgent({
        'name': 'child',
        'context_mode': 'NONE',
        'description': 'Child tool',
        'usf_config': {'api_key': 'DUMMY', 'model': 'usf-mini'}
    })

    # Attach child as sub-agent tool to parent
    parent.add_sub_agent(child)

    tools = parent.list_tools()
    assert isinstance(tools, list) and len(tools) >= 1
    # Should include a tool with default name agent_child
    names = []
    for t in tools:
        fn = (t.get('function') or {}).get('name')
        if fn:
            names.append(fn)
    assert 'agent_child' in names


@pytest.mark.asyncio
async def test_subagent_exec_passes_its_composed_tools(monkeypatch):
    # B has sub-agent C. When executing B as a tool, B should pass its composed tools (including C) to run_until_final.
    b = SubAgent({
        'name': 'b',
        'context_mode': 'OPTIONAL',
        'description': 'B tool',
        'usf_config': {'api_key': 'DUMMY', 'model': 'usf-mini'}
    })
    c = SubAgent({
        'name': 'c',
        'context_mode': 'NONE',
        'description': 'C tool',
        'usf_config': {'api_key': 'DUMMY', 'model': 'usf-mini'}
    })
    b.add_sub_agent(c)

    captured = {}

    async def fake_run_until_final(agent, shaped_messages, tools, router, max_loops=20):
        captured['tools'] = tools or []
        return 'ok'

    monkeypatch.setattr('usf_agents.runtime.safe_seq.run_until_final', fake_run_until_final)

    tool_call = {
        'id': '1',
        'type': 'function',
        'function': {
            'name': 'agent_b',
            'arguments': '{"task":"run"}'
        }
    }

    res = await b._execute_as_tool_until_final(tool_call, history_messages=[])
    assert res['success'] is True
    tools = captured.get('tools') or []
    assert isinstance(tools, list) and len(tools) >= 1

    names = []
    for t in tools:
        fn = (t.get('function') or {}).get('name')
        if fn:
            names.append(fn)
    assert 'agent_c' in names
