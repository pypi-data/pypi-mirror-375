"""
Tests for the FunctionNode and from_function functionality.

This module tests the ability to create nodes from functions with various parameter types:
- Simple primitive types (int, str)
- Pydantic models
- Complex types (Tuple, List, Dict)
"""

import asyncio
import time
from typing import Dict, List, Union

import pytest
import railtracks as rt
from pydantic import BaseModel
from railtracks import function_node
from railtracks.exceptions import NodeCreationError
from railtracks.nodes.nodes import Node


class PydanticModel(BaseModel):
    """A simple Pydantic model for testing."""

    name: str
    value: int


simple_test_inputs = [
    ("5", type("5")),
    (5, type(5)),
    (5.0, type(5.0)),
    (True, type(True)),
    ((1, 2, 3), type((1, 2, 3))),
    (None, type(None)),
    ([5, 4, 3, 2, 1], type([5, 4, 3, 2, 1])),
    ({"key": "value"}, type({"key": "value"})),
]

arg_test_inputs = [
    (("5", 5, 5.0), [type("5"), type(5), type(5.0)]),
    (
        (["5", "5"], {"key": "value"}, (1, 2, 3)),
        [type(["5", "5"]), type({"key": "value"}), type((1, 2, 3))],
    ),
]

kwarg_test_inputs = [
    (
        {"zeroth": None, "first": "5", "second": 5, "third": 5.0},
        [type(None), type("5"), type(5), type(5.0)],
    ),
    (
        {
            "zeroth": [None],
            "first": ["5", "5"],
            "second": {"key": "value"},
            "third": (1, 2, 3),
        },
        [type([None]), type(["5", "5"]), type({"key": "value"}), type((1, 2, 3))],
    ),
]


def func_type(arg):
    return type(arg)


def func_multiple_types(*args):
    return [type(arg) for arg in args]


async def func_multiple_ktypes_coroutine(
    zeroth=None,
    first: int = 5,
    second: PydanticModel = PydanticModel,
    third=[1, 2],
    **kwargs,
):
    await asyncio.sleep(1)
    return [type(zeroth), type(first), type(second), type(third)] + [
        type(kwargs[kwarg]) for kwarg in kwargs
    ]


def func_kwarg_auto(
    zeroth=None,
    first: int = 5,
    second: PydanticModel = PydanticModel,
    third: List[int] = [1, 2],
    fourth: List = [1, 2],
):
    return [zeroth, first, second, third, fourth]


def func_kwarg_error_dict(dict: Dict[str, int] = {"first": 5}):
    return


def func_kwarg_error_pydantic(
    pydantic_model: PydanticModel = PydanticModel(name="name", value=5),
):
    return


def func_buggy():
    async def corout():
        asyncio.sleep(1)
        return "This is a coroutine function."

    return corout()


# ===== Unit Tests =====
def test_to_node():
    """Test that to_node decorator works correctly."""

    @rt.function_node
    def secret_phrase() -> str:
        """
        Function that returns a secret phrase.

        Returns:
            str: The secret phrase.
        """
        return "Constantinople"

    assert issubclass(secret_phrase.node_type, Node)
    assert secret_phrase.node_type.name() == "secret_phrase"


# ===== Test Classes =====
class TestPrimitiveInputTypes:
    def test_empty_function(self):
        """Test that a function with no parameters works correctly."""

        def empty_function() -> str:
            """
            Returns:
                str: A simple string indicating the function was called.
            """
            return "This is an empty function."

        test_node = function_node(empty_function)

        async def top_level():
            with rt.Session():
                result = await rt.call(test_node)
            return result

        result = asyncio.run(top_level())
        assert "This is an empty function." == result

    @pytest.mark.parametrize("input, expected_output", simple_test_inputs)
    def test_single_int_input(self, input, expected_output):
        """Test that a function with a single int parameter works correctly."""
        test_node = function_node(func_type)

        async def top_level():
            with rt.Session():
                result = await rt.call(test_node, input)
            return result

        result = asyncio.run(top_level())
        assert result == expected_output


class TestSequenceInputTypes:
    @pytest.mark.parametrize("input, expected_output", arg_test_inputs)
    def test_multi_arg_input(self, input, expected_output):
        """Test that a function with multiple arg parameters works correctly."""
        test_node = function_node(func_multiple_types)

        async def top_level():
            with rt.Session():
                result = await rt.call(test_node, *input)

            return result

        result = asyncio.run(top_level())
        assert result == expected_output

    @pytest.mark.parametrize("input, expected_output", kwarg_test_inputs)
    def test_multi_kwarg_input(self, input, expected_output):
        """Test that a function with multiple kwarg parameters works correctly."""
        test_node = function_node(func_multiple_ktypes_coroutine)

        async def top_level():
            with rt.Session():
                result = await rt.call(test_node, **input)
            return result

        result = asyncio.run(top_level())
        assert result == expected_output


class TestfunctionMethods:
    def test_prepare_tools(self):
        """Test that tools are prepared properly when called."""
        test_nodea = function_node(func_kwarg_auto).node_type
        test_nodeb = function_node(func_kwarg_auto).node_type
        test_parent_node = function_node(func_multiple_types).node_type
        child_toola = test_nodea.prepare_tool(
            {
                "zeroth": None,
                "first": 5,
                "second": {"name": "name", "value": 5},
                "third": [1, 2, 3],
            }
        )
        child_toolb = test_nodea.prepare_tool(
            {"third": (1, 2, 3, 4), "fourth": "[1,2]"}
        )
        child_toolc = test_nodea.prepare_tool({"third": "1,2,3,4"})
        parent_tool = test_parent_node.prepare_tool(
            {
                "nodeA": test_nodea,
                "nodeB": test_nodeb,
                "first": 5,
                "second": {"name": "name", "value": 5},
                "third": 5.0,
                "fourth": None,
            }
        )
        assert child_toola.kwargs == {
            "zeroth": None,
            "first": 5,
            "second": PydanticModel(name="name", value=5),
            "third": [1, 2, 3],
        }
        assert child_toolb.kwargs == {"third": [1, 2, 3, 4], "fourth": ["[1,2]"]}
        assert child_toolc.kwargs == {"third": ["1,2,3,4"]}
        assert parent_tool.kwargs == {}


class TestRaiseErrors:
    DICT_ERROR_FROM_FUNCTION_MSG = (
        r"Parameter '.*' contains a dictionary type at .*, which is not allowed\."
    )

    def test_builtin_function_raises_error(self):
        """Test that a builtin function raises error"""
        with pytest.raises(RuntimeError):
            test_node = function_node(time.sleep)
            test_node.node_type.prepare_tool({"seconds": 5})

    def test_nested_async_func_raises_error(self):
        """Test edge case where a function that returns a coroutine raises an error."""
        test_node = function_node(func_buggy)
        with pytest.raises(NodeCreationError):

            async def top_level():
                with rt.Session():
                    await rt.call(test_node)

            asyncio.run(top_level())

    def test_dict_parameter(self):
        """Test that a function with a dict parameter raises an error."""

        def secret_function(fruits: dict[str, str]) -> str:
            return fruits.get("secret", "")

        with pytest.raises(NodeCreationError, match=self.DICT_ERROR_FROM_FUNCTION_MSG):
            _ = rt.function_node(secret_function)

    def test_nested_dict_parameter(self):
        """Test that a function with a nested dict parameter raises an error."""
        with pytest.raises(NodeCreationError, match=self.DICT_ERROR_FROM_FUNCTION_MSG):

            @rt.function_node
            def secret_function(fruits: list[Union[str, list[dict[str, str]]]]) -> str:
                return "test"

    def test_bmodel_with_dict_param(self):
        """Test that a BaseModel with a dict field raises an error when used as a function parameter."""

        class MyModel(BaseModel):
            name: str
            age: int
            data: dict[str, str]

        def secret_function(model: MyModel) -> str:
            pass

        with pytest.raises(NodeCreationError, match=self.DICT_ERROR_FROM_FUNCTION_MSG):
            _ = rt.function_node(secret_function)

    def test_bmodel_with_nested_dict_param(self):
        """Test that a BaseModel with a nested dict field raises an error when used as a function parameter."""

        class InnerModel(BaseModel):
            info: dict

        class OuterModel(BaseModel):
            inner: InnerModel

        with pytest.raises(NodeCreationError, match=self.DICT_ERROR_FROM_FUNCTION_MSG):

            @rt.function_node
            def secret_function(model: OuterModel) -> str:
                pass

    def test_pydantic_for_kwarg_raises_error(self):
        """Test that passing a dict for a kwarg raises an error since we don't support dicts as kwargs yet"""
        with pytest.raises(RuntimeError):
            test_node = function_node(func_kwarg_error_pydantic).node_type
            test_node.prepare_tool({"pydantic_model": ("name", 5)})
