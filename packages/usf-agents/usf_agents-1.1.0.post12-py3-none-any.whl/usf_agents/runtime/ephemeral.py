import asyncio
import uuid
import json
from typing import Any, AsyncGenerator, Dict, Iterable, List, Optional, Tuple, Type, Union

from ..usfAgent import USFAgent
from .openai_compat import (
    make_chunk_from_content_delta,
    make_chunk_tool_calls,
    make_chunk_tool_result,
    make_chunk_finish,
    make_completion,
)

Message = Dict[str, Any]
Messages = Union[str, List[Message]]


def build_ephemeral_config(
    base_config: Dict[str, Any],
    *,
    memory: bool = False,
    max_queue_size: int = 10,
    default_timeout: float = 60.0,
    stream: Optional[bool] = None,
) -> Dict[str, Any]:
    """
    Build an ephemeral USFAgent configuration for per-request usage.

    Goals:
      - Isolation: defaults to memory disabled (no cross-request leakage)
      - Performance: keep per-instance queue small and timeouts strict (misuse detection)
      - Backward compatibility: shallowly inherit caller's base_config

    Args:
      base_config: Caller-provided config template (api_key, model, provider, etc.)
      memory: Enable in-process memory for this ephemeral agent (default False)
      max_queue_size: Per-instance queue capacity (guardrail only; not for throughput)
      default_timeout: Per-instance queue timeout (guardrail for stuck runs)
      stream: Optional override for streaming final response

    Returns:
      A new dict suitable for initializing a USFAgent
    """
    cfg = dict(base_config or {})

    # Make memory policy explicit; disabled by default for strict isolation
    temp_mem_cfg = dict((cfg.get("temp_memory") or {}))
    temp_mem_cfg["enabled"] = bool(memory)
    # Keep caller's max_length/auto_trim if provided
    if "max_length" not in temp_mem_cfg:
        temp_mem_cfg["max_length"] = 10
    if "auto_trim" not in temp_mem_cfg:
        temp_mem_cfg["auto_trim"] = True
    cfg["temp_memory"] = temp_mem_cfg

    # Per-instance concurrency guardrails (not a global throttle)
    conc_cfg = dict((cfg.get("concurrency") or {}))
    conc_cfg["max_queue_size"] = int(max_queue_size)
    conc_cfg["default_timeout"] = float(default_timeout)
    cfg["concurrency"] = conc_cfg

    # Optional streaming override (default to caller's base_config or False)
    if stream is not None:
        cfg["stream"] = bool(stream)

    return cfg


def create_ephemeral_agent(
    base_config: Dict[str, Any],
    *,
    memory: bool = False,
    max_queue_size: int = 10,
    default_timeout: float = 60.0,
    stream: Optional[bool] = None,
    agent_cls: Type[USFAgent] = USFAgent,
) -> USFAgent:
    """
    Construct a fresh USFAgent instance for a single request.

    - Memory is disabled by default (enable per-session if needed)
    - Queue and timeout are kept tight so misuse is detected quickly
    - Agent instances are meant to be thrown away after use

    Args:
      base_config: Caller config template
      memory: Whether to enable in-process memory (default False)
      max_queue_size: Per-instance queue capacity
      default_timeout: Per-instance queue timeout
      stream: Optional streaming override
      agent_cls: Override for testing (e.g., a mock subclass)

    Returns:
      New USFAgent instance
    """
    cfg = build_ephemeral_config(
        base_config,
        memory=memory,
        max_queue_size=max_queue_size,
        default_timeout=default_timeout,
        stream=stream,
    )
    return agent_cls(cfg)


async def run_ephemeral(
    messages: Messages,
    *,
    base_config: Dict[str, Any],
    options: Optional[Dict[str, Any]] = None,
    memory: bool = False,
    agent_cls: Type[USFAgent] = USFAgent,
) -> AsyncGenerator[Dict[str, Any], None]:
    """
    Stream OpenAI-compatible chat.completion.chunk events from a per-request ephemeral agent.

    Behavior:
    - plan: simulated assistant content deltas with x_usf.stage="plan" and final done chunk
    - tool_calls: single assistant delta with tool_calls, then finish chunk with finish_reason="tool_calls"
    - final_answer: true streaming deltas forwarded from engine, then final finish chunk with finish_reason="stop"

    Notes:
    - This helper does not auto-execute tools. On tool_calls it will emit finish_reason="tool_calls".
    """
    agent = create_ephemeral_agent(base_config, memory=memory, agent_cls=agent_cls)

    # Streaming knobs
    opts = dict(options or {})
    streaming_cfg = dict(opts.get("streaming") or {})
    plan_chunk_size = int(streaming_cfg.get("plan_chunk_size") or 80)

    # Ensure engine final streaming is ON for this call
    prev_stream = getattr(agent, "stream", False)
    setattr(agent, "stream", True)
    model_name = getattr(agent, "model", "usf-mini") or "usf-mini"
    try:
        async for chunk in agent.run(messages, opts):
            ctype = chunk.get("type")

            if ctype == "plan":
                plan_text = chunk.get("content") or chunk.get("plan") or ""
                if plan_chunk_size > 0 and plan_text:
                    for i in range(0, len(plan_text), plan_chunk_size):
                        part = plan_text[i : i + plan_chunk_size]
                        if part:
                            yield make_chunk_from_content_delta(model=model_name, delta=part, stage="plan", done=False)
                    # signal plan done
                    yield make_chunk_from_content_delta(model=model_name, delta="", stage="plan", done=True)
                else:
                    yield make_chunk_from_content_delta(model=model_name, delta=plan_text, stage="plan", done=True)

            elif ctype == "tool_calls":
                tool_calls = chunk.get("tool_calls", [])
                # Emit tool_calls envelope as a single assistant delta, then finish with reason "tool_calls"
                yield make_chunk_tool_calls(model=model_name, tool_calls=tool_calls, stage="tool_calls")
                yield make_chunk_finish(model=model_name, finish_reason="tool_calls")
                return

            elif ctype == "final_answer":
                # Forward true streaming final deltas as assistant content
                delta = chunk.get("content", "") or ""
                if delta:
                    yield make_chunk_from_content_delta(model=model_name, delta=delta, stage=None, done=None)

        # engine finished; emit stop chunk
        yield make_chunk_finish(model=model_name, finish_reason="stop")
    finally:
        setattr(agent, "stream", prev_stream)


async def run_ephemeral_final(
    messages: Messages,
    *,
    base_config: Dict[str, Any],
    options: Optional[Dict[str, Any]] = None,
    memory: bool = False,
    agent_cls: Type[USFAgent] = USFAgent,
) -> Dict[str, Any]:
    """
    Run a per-request ephemeral agent and return an OpenAI-compatible chat.completion (non-stream).
    - On tool_calls: returns assistant.tool_calls with finish_reason="tool_calls".
    - On final answer: returns assistant content with finish_reason="stop".
    """
    agent = create_ephemeral_agent(base_config, memory=memory, agent_cls=agent_cls)

    # Force non-streaming at engine for deterministic final collection
    prev_stream = getattr(agent, "stream", False)
    setattr(agent, "stream", False)
    model_name = getattr(agent, "model", "usf-mini") or "usf-mini"

    try:
        async for chunk in agent.run(messages, options or {}):
            ctype = chunk.get("type")
            if ctype == "tool_calls":
                tool_calls = chunk.get("tool_calls", [])
                return make_completion(model=model_name, content=None, tool_calls=tool_calls, finish_reason="tool_calls")
            if ctype == "final_answer":
                content = chunk.get("content", "") or ""
                return make_completion(model=model_name, content=content, tool_calls=None, finish_reason="stop")

        # No decisive event produced
        return make_completion(model=model_name, content="", tool_calls=None, finish_reason="stop")
    finally:
        setattr(agent, "stream", prev_stream)


async def run_many_parallel(
    tasks: Iterable[Tuple[Messages, Optional[Dict[str, Any]]]],
    *,
    base_config: Dict[str, Any],
    per_request_memory: bool = False,
    concurrency_limit: Optional[int] = None,
    agent_cls: Type[USFAgent] = USFAgent,
) -> List[Dict[str, Any]]:
    """
    Execute many per-request ephemeral agents in parallel.

    - Each task gets its own agent instance (full isolation).
    - Optional semaphore to bound CPU/FDs while preserving high parallelism.
    - Returns a list of results with OpenAI-compatible completion and the raw streamed chunks.
    """
    sem = asyncio.Semaphore(concurrency_limit) if concurrency_limit else None

    async def _one(messages: Messages, options: Optional[Dict[str, Any]]) -> Dict[str, Any]:
        rid = str(uuid.uuid4())
        try:
            if sem:
                async with sem:
                    return await _run_collect(rid, messages, options)
            else:
                return await _run_collect(rid, messages, options)
        except Exception as e:
            return {"run_id": rid, "success": False, "completion": None, "raw_chunks": [], "error": str(e)}

    async def _run_collect(run_id: str, messages: Messages, options: Optional[Dict[str, Any]]) -> Dict[str, Any]:
        raw_chunks: List[Dict[str, Any]] = []
        final_text = ""
        last_tool_calls: Optional[List[Dict[str, Any]]] = None
        finish_reason: Optional[str] = None
        model_name = (base_config or {}).get("model") or "usf-mini"

        async for chunk in run_ephemeral(
            messages,
            base_config=base_config,
            options=(options or {}),
            memory=per_request_memory,
            agent_cls=agent_cls,
        ):
            raw_chunks.append(chunk)
            # Accumulate final content deltas
            try:
                delta = ((chunk.get("choices") or [{}])[0] or {}).get("delta") or {}
            except Exception:
                delta = {}
            if isinstance(delta, dict):
                text = delta.get("content")
                if isinstance(text, str):
                    final_text += text
                tc = delta.get("tool_calls")
                if isinstance(tc, list) and tc:
                    last_tool_calls = tc
            # Observe finish reason
            try:
                fr = ((chunk.get("choices") or [{}])[0] or {}).get("finish_reason")
            except Exception:
                fr = None
            if fr:
                finish_reason = fr

        # Build completion from accumulated data
        if finish_reason == "tool_calls" and last_tool_calls:
            completion = make_completion(model=model_name, content=None, tool_calls=last_tool_calls, finish_reason="tool_calls")
        else:
            completion = make_completion(model=model_name, content=final_text, tool_calls=None, finish_reason="stop")

        return {"run_id": run_id, "success": True, "completion": completion, "raw_chunks": raw_chunks, "error": None}

    coros = [_one(m, o) for (m, o) in tasks]
    return list(await asyncio.gather(*coros, return_exceptions=False))