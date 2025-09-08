import sys
import types
import pytest

from usf_agents.runtime.docstring_schema import parse_docstring_to_schema, json_type_from_str

try:
    import yaml  # type: ignore
    HAS_YAML = True
except Exception:
    HAS_YAML = False


def test_google_style_parsing_success():
    def fn(a, b: int, c: bool = False):
        """
        Test function.

        Args:
            a (str): first arg
            b (int): second arg
            c (bool, optional): third arg
        """
        return None

    schema = parse_docstring_to_schema(fn)
    assert isinstance(schema, dict)
    assert schema.get("description", "").startswith("Test function")
    params = schema.get("parameters") or {}
    props = params.get("properties") or {}
    req = params.get("required") or []
    assert set(props.keys()) == {"a", "b", "c"}
    # required should include 'a' and 'b' (c is optional)
    assert set(req) == {"a", "b"}
    assert props["b"]["type"] == "number"
    assert props["c"]["type"] == "boolean"




@pytest.mark.skipif(not HAS_YAML, reason="PyYAML not installed")
def test_yaml_block_parsing_success():
    def fn(numbers):
        """
        Calculate.

        ```yaml
        description: Sum tool
        parameters:
          type: object
          properties:
            numbers:
              type: array
              description: values
          required: [numbers]
        ```
        """
        return sum(numbers)

    schema = parse_docstring_to_schema(fn)
    assert isinstance(schema, dict)
    assert schema.get("description") == "Sum tool"
    params = schema.get("parameters") or {}
    props = params.get("properties") or {}
    req = params.get("required") or []
    assert set(props.keys()) == {"numbers"}
    assert req == ["numbers"]
    assert props["numbers"]["type"] == "array"


def test_missing_docstring_returns_none():
    def fn(a):  # no docstring
        return a
    assert parse_docstring_to_schema(fn) is None


def test_type_mapping_unknown_defaults_to_string():
    assert json_type_from_str("CustomType") == "string"
    assert json_type_from_str("LIST[int]") == "array"
    assert json_type_from_str("DICT[str, Any]") == "object"
