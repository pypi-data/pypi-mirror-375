import time
import uuid
from typing import Any, Dict, List, Optional


def _now_ts() -> int:
    try:
        return int(time.time())
    except Exception:
        return 0


def _new_id(prefix: str = "cmpl") -> str:
    try:
        return f"{prefix}-{uuid.uuid4().hex}"
    except Exception:
        return f"{prefix}-00000000000000000000000000000000"


def make_completion(
    *,
    model: str,
    content: Optional[str],
    tool_calls: Optional[List[Dict[str, Any]]] = None,
    finish_reason: Optional[str] = "stop",
    usage: Optional[Dict[str, int]] = None,
    x_usf: Optional[Dict[str, Any]] = None,
    id_prefix: str = "cmpl",
) -> Dict[str, Any]:
    """
    Build an OpenAI-compatible non-stream chat.completion response with a single choice.
    """
    message: Dict[str, Any] = {"role": "assistant"}
    if tool_calls:
        # OpenAI-compatible assistant tool_calls message
        message["tool_calls"] = tool_calls
        # When returning tool_calls (no final content), content should be None
        message["content"] = None
        if finish_reason is None:
            finish_reason = "tool_calls"
    else:
        # Final assistant content
        message["content"] = content or ""
        if finish_reason is None:
            finish_reason = "stop"

    resp: Dict[str, Any] = {
        "id": _new_id(id_prefix),
        "object": "chat.completion",
        "created": _now_ts(),
        "model": model,
        "choices": [
            {
                "index": 0,
                "message": message,
                "finish_reason": finish_reason,
            }
        ],
        "usage": usage if isinstance(usage, dict) else {
            "prompt_tokens": None,
            "completion_tokens": None,
            "total_tokens": None,
        },
    }
    if x_usf:
        resp["x_usf"] = x_usf
    return resp


def make_chunk_base(model: str, id_prefix: str = "cmpl") -> Dict[str, Any]:
    """
    Base shape for an OpenAI streaming chunk.
    """
    return {
        "id": _new_id(id_prefix),
        "object": "chat.completion.chunk",
        "created": _now_ts(),
        "model": model,
        "choices": [
            {
                "index": 0,
                "delta": {},
                "finish_reason": None,
            }
        ],
    }


def make_chunk_from_content_delta(
    *,
    model: str,
    delta: str,
    stage: Optional[str] = None,
    done: Optional[bool] = None,
    id_prefix: str = "cmpl",
) -> Dict[str, Any]:
    """
    Create a chunk carrying assistant content delta (used for both plan simulation and final streaming).
    """
    chunk = make_chunk_base(model, id_prefix=id_prefix)
    chunk["choices"][0]["delta"] = {
        "role": "assistant",
        "content": delta,
    }
    if stage or done is not None:
        chunk["x_usf"] = {"stage": stage}
        if done is not None:
            chunk["x_usf"]["done"] = bool(done)
    return chunk


def make_chunk_tool_calls(
    *,
    model: str,
    tool_calls: List[Dict[str, Any]],
    stage: Optional[str] = "tool_calls",
    id_prefix: str = "cmpl",
) -> Dict[str, Any]:
    """
    Create a chunk that carries a complete assistant tool_calls delta (single emission).
    """
    chunk = make_chunk_base(model, id_prefix=id_prefix)
    chunk["choices"][0]["delta"] = {
        "role": "assistant",
        "tool_calls": tool_calls,
    }
    if stage:
        chunk["x_usf"] = {"stage": stage}
    return chunk


def make_chunk_tool_result(
    *,
    model: str,
    tool_call_id: str,
    name: Optional[str],
    result: Dict[str, Any],
    id_prefix: str = "cmpl",
) -> Dict[str, Any]:
    """
    Emit a vendor-extension-only chunk for tool execution result.
    Keep OpenAI core fields empty to maintain compatibility.
    """
    chunk = make_chunk_base(model, id_prefix=id_prefix)
    # Leave delta empty; populate vendor extension
    chunk["x_usf"] = {
        "stage": "tool_result",
        "tool_call_id": tool_call_id,
        "name": name,
        "result": result,
    }
    return chunk


def make_chunk_finish(
    *,
    model: str,
    finish_reason: str = "stop",
    id_prefix: str = "cmpl",
) -> Dict[str, Any]:
    """
    Final chunk signalling end of streaming, with finish_reason.
    """
    chunk = make_chunk_base(model, id_prefix=id_prefix)
    chunk["choices"][0]["delta"] = {}
    chunk["choices"][0]["finish_reason"] = finish_reason
    return chunk