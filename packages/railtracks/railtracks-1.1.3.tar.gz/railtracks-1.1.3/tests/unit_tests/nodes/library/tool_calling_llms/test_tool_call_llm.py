import pytest
import railtracks as rt
from railtracks.built_nodes.concrete.response import LLMResponse
from railtracks.nodes.nodes import Node
from railtracks.built_nodes.easy_usage_wrappers.helpers import tool_call_llm
from railtracks.built_nodes.concrete import ToolCallLLM
from railtracks import agent_node
from railtracks.built_nodes.concrete import OutputLessToolCallLLM
from railtracks.exceptions import LLMError, NodeCreationError, NodeInvocationError
from railtracks.llm import MessageHistory, ToolMessage, SystemMessage, UserMessage, AssistantMessage, ToolCall, ToolResponse, Tool
# ---- ToolCallLLM tests ----

def test_tool_call_llm_return_output_returns_last_message_content(mock_llm, mock_tool):
    class DummyToolCallLLM(ToolCallLLM):
        @classmethod
        def name(cls):
            return "Dummy"
        
        def tool_nodes(self):
            return {mock_tool}
        
    mh = MessageHistory([SystemMessage("sys"), UserMessage("hi"), AssistantMessage("final answer")])
    node = DummyToolCallLLM(mh, mock_llm())
    assert node.return_output().content == "final answer"

# ---- OutputLessToolCallLLM tests ----

def test_outputless_tool_call_llm_create_node_success(mock_llm, mock_tool):
    class DummyLLM(OutputLessToolCallLLM):
        @classmethod
        def name(cls):
            return "Dummy"
        def tool_nodes(self):
            return {mock_tool}
        def return_output(self):
            return None
    mh = MessageHistory([SystemMessage("sys"), UserMessage("hi")])
    node = DummyLLM(mh, mock_llm())
    tool_name = mock_tool.tool_info().name
    result = node.create_node(tool_name, {"foo": "bar"})
    assert result is not None

def test_outputless_tool_call_llm_create_node_no_match(mock_llm, mock_tool):
    class DummyLLM(OutputLessToolCallLLM):
        @classmethod
        def name(cls):
            return "Dummy"
        def tool_nodes(self):
            return {mock_tool}
        def return_output(self):
            return None
    mh = MessageHistory([SystemMessage("sys"), UserMessage("hi")])
    node = DummyLLM(mh, mock_llm())
    with pytest.raises(LLMError, match="doesn't match any of the tool names"):
        node.create_node("nonexistent_tool", {})

def test_outputless_tool_call_llm_create_node_multiple_match(mock_llm, mock_tool):
    tool1 = Tool(name="duplicate", detail="duplicate does something", parameters=None)
    tool2 = Tool(name="duplicate", detail="duplicate does something else", parameters=None)
    class node1(Node):
        @classmethod
        def name(cls):
            return "name1"
        @classmethod
        def tool_info(cls):
            return tool1
    class node2(Node):
        @classmethod
        def name(cls):
            return "name2"
        @classmethod
        def tool_info(cls):
            return tool2
    class DummyLLM(OutputLessToolCallLLM):
        @classmethod
        def name(cls):
            return "Dummy"
        def tool_nodes(self):
            return {node1, node2}
        def return_output(self):
            return None
    mh = MessageHistory([SystemMessage("sys"), UserMessage("hi")])
    node = DummyLLM(mh, mock_llm())
    with pytest.raises(NodeCreationError, match="multiple nodes"):
        node.create_node("duplicate", {})

# ---- Max Tool Calls tests ----
def test_unlimited_tool_call_gives_warning_on_creation(mock_llm, mock_tool, caplog):
    with caplog.at_level("WARNING"):
        _ = tool_call_llm(
            tool_nodes={mock_tool},
            name="Test ToolCallLLM",
            llm=mock_llm(),
            max_tool_calls=None,    # None means unlimited
            system_message=SystemMessage("system prompt")
        )

@pytest.mark.skip("TODO: check if depracated because of node_builder")
async def test_unlimited_tool_call_gives_warning_at_runtime(mock_llm, mock_tool):
    class MockLimitedToolCallLLM(ToolCallLLM):
        @classmethod
        def name(cls):
            return "Mock Limited Tool Call LLM"
        
        def tool_nodes(self):
            return {mock_tool}
    mh = MessageHistory([SystemMessage("system prompt"), UserMessage("hello")])
    mock_model = mock_llm()
    with pytest.warns(RuntimeWarning, match="unlimited tool calls"):    # param injection at runtime
        resp = await rt.call(MockLimitedToolCallLLM, user_input=mh, model=mock_model, max_tool_calls=None)

@pytest.mark.skip("TODO: check if depracated because of node_builder")
def test_limited_tool_call_llm_return_output(mock_tool, mock_llm):
    class MockLimitedToolCallLLM(ToolCallLLM):
       @classmethod
       def name(cls):
           return "Mock Limited Tool Call LLM"
       
       def tool_nodes(self):
           return {mock_tool}
    
    mh = MessageHistory([SystemMessage("system prompt"), UserMessage("hello")])
    node = MockLimitedToolCallLLM(mh, mock_llm())
    node.message_hist.append(AssistantMessage(content="The answer"))
    assert node.return_output().content == "The answer"

@pytest.mark.skip("TODO: check if depracated because of node_builder")
@pytest.mark.asyncio
async def test_tool_call_llm_on_max_tool_calls_exceeded_appends_final_answer(mock_tool, mock_llm):
    class MockLimitedToolCallLLM(ToolCallLLM):
       @classmethod
       def name(cls):
           return "Mock Limited Tool Call LLM"
       
       def tool_nodes(self):
           return {mock_tool}
    
    mh = MessageHistory([SystemMessage("system prompt"), 
                         UserMessage("hello"),
                         AssistantMessage([ToolCall(identifier="test", name="last tool call", arguments={})]),  # mock model expects the tool call name
                         ToolMessage(ToolResponse(identifier="test", name="last tool call", result="The answer"))
                        ])
    # if tool response has name "last tool call", then the mock model will return "Final answer after tool calls exhausted."
    node = MockLimitedToolCallLLM(mh, mock_llm())
    await node._on_max_tool_calls_exceeded()
    assert isinstance(node.message_hist[-1], AssistantMessage)
    assert node.message_hist[-1].content == "Final answer after tool calls exhausted."

def test_tool_call_llm_init_appends_system_message(mock_llm, mock_tool):
    ToolCallLLM = tool_call_llm(
        tool_nodes={mock_tool},
        name="Test ToolCallLLM",
        llm=mock_llm(),
        max_tool_calls=2,
        system_message="system prompt"
    )
    mh = MessageHistory([UserMessage("hello")])
    node = ToolCallLLM(mh)
    assert "system prompt" in node.message_hist[0].content

def test_tool_call_llm_return_output_last_message(mock_llm, mock_tool):
    ToolCallLLM = tool_call_llm(
        tool_nodes={mock_tool},
        name="Test ToolCallLLM",
        llm=mock_llm(),
    )
    mh = MessageHistory([SystemMessage("system prompt"), UserMessage("hello")])
    node = ToolCallLLM(mh)
    node.message_hist.append(AssistantMessage(content="The answer"))
    assert node.return_output().content == "The answer"

def test_tool_call_llm_connected_nodes(mock_llm, mock_tool):
    ToolCallLLM = tool_call_llm(
        tool_nodes={mock_tool},
        name="Test ToolCallLLM",
        llm=mock_llm()
    )
    mh = MessageHistory([SystemMessage("system prompt"), UserMessage("hello")])
    node = ToolCallLLM(mh)
    assert mock_tool in node.tool_nodes()

def test_tool_call_llm_pretty_name_default(mock_llm, mock_tool):
    ToolCallLLM = tool_call_llm(
        tool_nodes={mock_tool},
        llm=mock_llm()
    )
    assert "Tool Call LLM" == ToolCallLLM.name()

def test_tool_call_llm_instantiate_with_string(mock_llm, mock_tool):
    """Test that ToolCallLLM can be instantiated with a string input."""
    class MockToolCallLLM(ToolCallLLM):
        @classmethod
        def name(cls):
            return "Mock Tool Call LLM"

        @classmethod
        def system_message(cls):
            return "system prompt"

        @classmethod
        def tool_nodes(cls):
            return {mock_tool}

    node = MockToolCallLLM(user_input="hello", llm=mock_llm())
    # Verify that the string was converted to a MessageHistory with a UserMessage
    assert len(node.message_hist) == 2  # System message + UserMessage
    assert node.message_hist[0].role == "system"
    assert node.message_hist[0].content == "system prompt"
    assert node.message_hist[1].role == "user"
    assert node.message_hist[1].content == "hello"

def test_tool_call_llm_instantiate_with_user_message(mock_llm, mock_tool):
    """Test that ToolCallLLM can be instantiated with a UserMessage input."""
    class MockToolCallLLM(ToolCallLLM):
        @classmethod
        def name(cls):
            return "Mock Tool Call LLM"

        @classmethod
        def system_message(cls):
            return "system prompt"

        @classmethod
        def tool_nodes(cls):
            return {mock_tool}

    user_msg = UserMessage("hello")
    node = MockToolCallLLM(user_input=user_msg, llm=mock_llm())
    # Verify that the UserMessage was converted to a MessageHistory
    assert len(node.message_hist) == 2  # System message + UserMessage
    assert node.message_hist[0].role == "system"
    assert node.message_hist[0].content == "system prompt"
    assert node.message_hist[1].role == "user"
    assert node.message_hist[1].content == "hello"

def test_tool_call_llm_easy_usage_with_string(mock_llm, mock_tool):
    """Test that the easy usage wrapper can be instantiated with a string input."""
    ToolCallLLM = tool_call_llm(
        tool_nodes={mock_tool},
        name="Test ToolCallLLM",
        system_message="system prompt",
        llm=mock_llm(),
    )

    node = ToolCallLLM(user_input="hello")
    # Verify that the string was converted to a MessageHistory with a UserMessage
    assert len(node.message_hist) == 2  # System message + UserMessage
    assert node.message_hist[0].role == "system"
    assert node.message_hist[0].content == "system prompt"
    assert node.message_hist[1].role == "user"
    assert node.message_hist[1].content == "hello"

def test_tool_call_llm_easy_usage_with_user_message(mock_llm, mock_tool):
    """Test that the easy usage wrapper can be instantiated with a UserMessage input."""
    ToolCallLLM = tool_call_llm(
        tool_nodes={mock_tool},
        name="Test ToolCallLLM",
        system_message="system prompt",
        llm=mock_llm(),
    )

    user_msg = UserMessage("hello")
    node = ToolCallLLM(user_input=user_msg)
    # Verify that the UserMessage was converted to a MessageHistory
    assert len(node.message_hist) == 2  # System message + UserMessage
    assert node.message_hist[0].role == "system"
    assert node.message_hist[0].content == "system prompt"
    assert node.message_hist[1].role == "user"
    assert node.message_hist[1].content == "hello"

def test_tool_call_llm_with_output_type_message_history(mock_llm, mock_tool):
    ToolCallLLM = agent_node(
        tool_nodes={mock_tool},
        name="Test ToolCallLLM",
        llm=mock_llm(),
    )
    mh = MessageHistory([SystemMessage("system prompt"), UserMessage("hello")])
    node = ToolCallLLM(mh)
    assert isinstance(node.return_output(), LLMResponse)
    assert all(not isinstance(x.role, SystemMessage) for x in node.return_output().message_history)
    assert node.return_output().content == "hello"

    assert ToolCallLLM.name() == "Test ToolCallLLM"

@pytest.mark.asyncio
@pytest.mark.parametrize("class_based", [True, False], ids=["class_based", "easy_usage_wrapper"])
async def test_negative_tool_calls_raises(class_based, mock_llm, mock_tool):
    neg_max_tool_calls = -1
    if not class_based:
        with pytest.raises(NodeCreationError, match="max_tool_calls must be a non-negative integer."):
            _ = tool_call_llm(
                tool_nodes={mock_tool},
                name="Limited Tool Call Test Node",
                system_message=SystemMessage("system prompt"),
                llm=mock_llm(),
                max_tool_calls=neg_max_tool_calls,
            )
    else:
        class LimitedToolCallTestNode(ToolCallLLM):
            def __init__(self, user_input, llm=mock_llm()):
                super().__init__(user_input, llm, max_tool_calls=neg_max_tool_calls)
            @classmethod
            def tool_nodes(cls):
                return {mock_tool}
            @classmethod
            def name(cls):
                return "Limited Tool Call Test Node"
        mh = MessageHistory([SystemMessage("system prompt"), UserMessage("hello")])
        with pytest.raises(NodeInvocationError, match="max_tool_calls must be a non-negative integer."):
            await rt.call(LimitedToolCallTestNode, user_input=mh)