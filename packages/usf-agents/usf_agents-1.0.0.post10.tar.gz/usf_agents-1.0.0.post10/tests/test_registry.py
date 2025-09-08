import asyncio
import pytest

from usf_agents.multi_agent.registry import AgentRegistry
from usf_agents.multi_agent.base import SubAgent, ManagerAgent


def make_agent(name: str, is_manager: bool = False):
    base_usf = {
        'api_key': 'DUMMY_KEY',  # Replace with real key for integration tests
        'model': 'usf-mini'
    }
    if is_manager:
        return ManagerAgent(usf_config=base_usf)
    spec = {
        'name': name,
        'context_mode': 'NONE',
        'usf_config': base_usf
    }
    return SubAgent(spec)


def test_registry_add_and_get():
    reg = AgentRegistry()
    a = make_agent('a')
    b = make_agent('b', is_manager=True)

    reg.add_agent(a)
    reg.add_agent(b)

    assert reg.has('a')
    assert reg.has('manager')

    assert reg.get('a').id == 'a'
    assert reg.get('manager').id == 'manager'

    with pytest.raises(KeyError):
        reg.get('C')


def test_relations_non_exclusive():
    reg = AgentRegistry()
    a = make_agent('a', is_manager=True)
    b = make_agent('b')
    c = make_agent('c')

    reg.add_agent(a)
    reg.add_agent(b)
    reg.add_agent(c)

    reg.add_relation('manager', 'b')
    reg.add_relation('manager', 'c')
    # c is also child of b (non-exclusive)
    reg.add_relation('b', 'c')

    assert set(reg.get_children('manager')) == {'b', 'c'}
    assert set(reg.get_children('b')) == {'c'}
    assert set(reg.get_parents('c')) == {'manager', 'b'}
    assert reg.get_parents('b') == ['manager'] or set(reg.get_parents('b')) == {'manager'}


def test_all_agents():
    reg = AgentRegistry()
    for i in range(3):
        reg.add_agent(make_agent(f'x{i}'))
    assert set(reg.all_agents()) == {'x0', 'x1', 'x2'}
