import json
import pytest
from usf_agents.multi_agent.context import _shape_context_for_mode as shape_context_for_mode
from usf_agents.types.multi_agent import TaskPayload


def _mk_msgs(n=2):
    return (
        [{'role': 'user', 'content': f'user-{i}'} for i in range(n)]
        + [{'role': 'assistant', 'content': f'assistant-{i}'} for i in range(n)]
    )


def test_context_mode_none_history_false_minimal():
    task = 'do'
    calling = _mk_msgs()
    msgs = shape_context_for_mode('NONE', task, history_messages=calling)
    assert isinstance(msgs, list)
    # Should only contain a single user message with the delegated task content
    assert len(msgs) == 1
    assert msgs[0]['role'] == 'user'
    assert msgs[0]['content'] == 'do'
    # Ensure no calling transcript leaked
    assert 'user-0' not in msgs[0]['content']
    assert 'assistant-0' not in msgs[0]['content']


def test_context_mode_optional_with_history_and_context():
    task = 'do'
    calling = _mk_msgs()
    ctx_text = "2+2 is 4, now add 3 into 4."
    msgs = shape_context_for_mode(
        'OPTIONAL',
        task,
        history_messages=calling,
        context=ctx_text,
        history=True
    )
    # Should include a system message with Additional Context, then history, then final user task
    assert len(msgs) >= len(calling) + 1  # +1 for final user task; system is optional but expected here
    assert msgs[0]['role'] == 'system'
    assert 'Additional Context for this current task' in msgs[0]['content']
    assert ctx_text in msgs[0]['content']
    # Transcript preserved
    assert any(m.get('content') == 'user-0' for m in msgs)
    # Final user message with the task
    assert msgs[-1]['role'] == 'user'
    assert msgs[-1]['content'] == 'do'


def test_context_mode_required_raises_when_missing_context():
    task = 'do'
    with pytest.raises(ValueError):
        _ = shape_context_for_mode('REQUIRED', task, history_messages=None)


def test_history_trim_last_user_drops_trailing_user_message():
    # Create a history that ends with a user message
    calling = [
        {'role': 'user', 'content': 'u1'},
        {'role': 'assistant', 'content': 'a1'},
        {'role': 'user', 'content': 'u2'}  # last is user
    ]
    task = 'do'
    msgs = shape_context_for_mode(
        'OPTIONAL',
        task,
        history_messages=calling,
        context="ctx",
        history=True,
        trim_last_user=True
    )
    # Ensure 'u2' (last user) was trimmed
    contents = [m.get('content') for m in msgs if 'content' in m]
    assert 'u2' not in contents
    assert 'u1' in contents and 'a1' in contents
    # Final task still appended
    assert contents[-1] == 'do'
