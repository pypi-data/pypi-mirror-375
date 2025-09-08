from typing import Any, Callable, Optional, Dict


def tool(
    alias: Optional[str] = None,
    schema: Optional[Dict[str, Any]] = None
) -> Callable[[Callable[..., Any]], Callable[..., Any]]:
    """
    Lightweight decorator to attach USF tool metadata to a function.

    BREAKING CHANGES:
    - Only 'alias' and 'schema' are supported. 'name' and 'description' are removed.

    Defaults:
    - Display tool name = alias if provided, else 'agent_{function_name}' (applied during registration).

    Schema precedence on registration (ManagerAgent.add_function_tool):
        1) Explicit schema passed to add_function_tool(..., schema=...) takes priority.
        2) Decorator-provided schema (this decorator's 'schema' argument), if present.
        3) Docstring parsing (YAML → Google).

    Usage:

        # A) No metadata; schema will be inferred from the docstring.
        @tool
        def calc_sum(numbers: list[int]) -> int:
            '''
            Calculate the sum of a list of integers.

            Args:
                numbers (list[int]): A list of integers to add together.
            '''
            return sum(numbers)

        # B) Provide an alias (display name for the LLM)
        @tool(alias="sum_tool")
        def calc_sum(numbers: list[int]) -> int:
            return sum(numbers)

        # C) Provide an explicit OpenAI-compatible schema in the decorator
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

    Notes:
    - This decorator does NOT register the function as a tool. Use ManagerAgent.add_function_tool(...)
      or batch sugar APIs to register.
    """
    meta: Dict[str, Any] = {}
    if alias is not None:
        meta["alias"] = alias
    if schema is not None:
        meta["schema"] = schema

    def _wrap(func: Callable[..., Any]) -> Callable[..., Any]:
        # Attach metadata without altering the callable behavior
        setattr(func, "__usf_tool__", meta)
        return func

    return _wrap
