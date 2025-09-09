"""Comprehensive tool calling tests for llm-fiber."""

import asyncio
import json
from unittest.mock import MagicMock, patch

import pytest

from llm_fiber import (
    ChatMessage,
    Fiber,
    StreamEvent,
    StreamEventType,
    Usage,
)


class TestToolDefinition:
    """Test tool definition and validation."""

    def test_basic_tool_definition(self):
        """Test basic tool definition structure."""
        tool = {
            "type": "function",
            "function": {
                "name": "get_weather",
                "description": "Get current weather for a location",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "location": {
                            "type": "string",
                            "description": "The city and state, e.g. San Francisco, CA",
                        },
                        "unit": {
                            "type": "string",
                            "enum": ["celsius", "fahrenheit"],
                            "description": "Temperature unit",
                        },
                    },
                    "required": ["location"],
                },
            },
        }

        # Tool should have all required fields
        assert tool["type"] == "function"
        assert "name" in tool["function"]
        assert "description" in tool["function"]
        assert "parameters" in tool["function"]

    def test_complex_tool_definition(self):
        """Test complex tool with nested parameters."""
        tool = {
            "type": "function",
            "function": {
                "name": "search_database",
                "description": "Search database with complex filters",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "query": {"type": "string", "description": "Search query"},
                        "filters": {
                            "type": "object",
                            "properties": {
                                "date_range": {
                                    "type": "object",
                                    "properties": {
                                        "start": {"type": "string", "format": "date"},
                                        "end": {"type": "string", "format": "date"},
                                    },
                                },
                                "category": {"type": "array", "items": {"type": "string"}},
                            },
                        },
                        "limit": {"type": "integer", "minimum": 1, "maximum": 100},
                    },
                    "required": ["query"],
                },
            },
        }

        assert tool["function"]["name"] == "search_database"
        assert "filters" in tool["function"]["parameters"]["properties"]

    def test_tool_without_parameters(self):
        """Test tool definition without parameters."""
        tool = {
            "type": "function",
            "function": {
                "name": "get_random_fact",
                "description": "Get a random interesting fact",
                # No parameters
            },
        }

        assert "parameters" not in tool["function"]


class TestToolCallRequests:
    """Test tool call requests across providers."""

    @pytest.fixture
    def weather_tool(self):
        """Sample weather tool for testing."""
        return {
            "type": "function",
            "function": {
                "name": "get_weather",
                "description": "Get current weather",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "location": {"type": "string"},
                        "unit": {"type": "string", "enum": ["celsius", "fahrenheit"]},
                    },
                    "required": ["location"],
                },
            },
        }

    @pytest.fixture
    def calculation_tool(self):
        """Sample calculation tool for testing."""
        return {
            "type": "function",
            "function": {
                "name": "calculate",
                "description": "Perform mathematical calculation",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "expression": {"type": "string", "description": "Math expression"},
                        "precision": {"type": "integer", "minimum": 1, "maximum": 10},
                    },
                    "required": ["expression"],
                },
            },
        }

    @pytest.fixture
    def fiber_client(self):
        """Create Fiber client for testing."""
        return Fiber(
            default_model="gpt-4o", api_keys={"openai": "test-key"}, enable_observability=False
        )

    @pytest.mark.asyncio
    async def test_single_tool_call_request(self, fiber_client, weather_tool):
        """Test request with single tool."""
        mock_response = {
            "id": "chatcmpl-test",
            "choices": [
                {
                    "message": {
                        "role": "assistant",
                        "content": None,
                        "tool_calls": [
                            {
                                "id": "call_123",
                                "type": "function",
                                "function": {
                                    "name": "get_weather",
                                    "arguments": '{"location": "San Francisco", "unit": "celsius"}',
                                },
                            }
                        ],
                    },
                    "finish_reason": "tool_calls",
                }
            ],
            "usage": {"prompt_tokens": 50, "completion_tokens": 20, "total_tokens": 70},
        }

        with patch("httpx.AsyncClient.post") as mock_post:
            mock_post.return_value = MagicMock(status_code=200, json=lambda: mock_response)

            messages = [ChatMessage.user("What's the weather in San Francisco?")]
            result = await fiber_client.chat(messages, tools=[weather_tool])

            assert len(result.tool_calls) == 1
            tool_call = result.tool_calls[0]
            assert tool_call["function"]["name"] == "get_weather"
            assert "San Francisco" in tool_call["function"]["arguments"]

    @pytest.mark.asyncio
    async def test_multiple_tools_available(self, fiber_client, weather_tool, calculation_tool):
        """Test request with multiple tools available."""
        mock_response = {
            "id": "chatcmpl-test",
            "choices": [
                {
                    "message": {
                        "role": "assistant",
                        "content": "I'll calculate that for you.",
                        "tool_calls": [
                            {
                                "id": "call_456",
                                "type": "function",
                                "function": {
                                    "name": "calculate",
                                    "arguments": '{"expression": "2 + 2", "precision": 2}',
                                },
                            }
                        ],
                    },
                    "finish_reason": "tool_calls",
                }
            ],
            "usage": {"prompt_tokens": 60, "completion_tokens": 25, "total_tokens": 85},
        }

        with patch("httpx.AsyncClient.post") as mock_post:
            mock_post.return_value = MagicMock(status_code=200, json=lambda: mock_response)

            messages = [ChatMessage.user("What is 2 + 2?")]
            result = await fiber_client.chat(messages, tools=[weather_tool, calculation_tool])

            assert len(result.tool_calls) == 1
            assert result.tool_calls[0]["function"]["name"] == "calculate"
            assert result.text == "I'll calculate that for you."

    @pytest.mark.asyncio
    async def test_tool_choice_auto(self, fiber_client, weather_tool):
        """Test tool_choice='auto' behavior."""
        mock_response = {
            "choices": [
                {
                    "message": {"role": "assistant", "content": "The weather looks nice today!"},
                    "finish_reason": "stop",
                }
            ],
            "usage": {"prompt_tokens": 40, "completion_tokens": 10, "total_tokens": 50},
        }

        with patch("httpx.AsyncClient.post") as mock_post:
            mock_post.return_value = MagicMock(status_code=200, json=lambda: mock_response)

            messages = [ChatMessage.user("How are you today?")]
            result = await fiber_client.chat(messages, tools=[weather_tool], tool_choice="auto")

            # Should choose not to use tools for this query
            assert len(result.tool_calls) == 0
            assert "nice today" in result.text

    @pytest.mark.asyncio
    async def test_tool_choice_required(self, fiber_client, weather_tool):
        """Test tool_choice='required' behavior."""
        mock_response = {
            "choices": [
                {
                    "message": {
                        "role": "assistant",
                        "content": None,
                        "tool_calls": [
                            {
                                "id": "call_789",
                                "type": "function",
                                "function": {
                                    "name": "get_weather",
                                    "arguments": '{"location": "Unknown"}',
                                },
                            }
                        ],
                    },
                    "finish_reason": "tool_calls",
                }
            ],
            "usage": {"prompt_tokens": 45, "completion_tokens": 15, "total_tokens": 60},
        }

        with patch("httpx.AsyncClient.post") as mock_post:
            mock_post.return_value = MagicMock(status_code=200, json=lambda: mock_response)

            messages = [ChatMessage.user("Tell me a joke")]
            result = await fiber_client.chat(messages, tools=[weather_tool], tool_choice="required")

            # Should be forced to use a tool even for non-tool query
            assert len(result.tool_calls) == 1

    @pytest.mark.asyncio
    async def test_tool_choice_specific_function(
        self, fiber_client, weather_tool, calculation_tool
    ):
        """Test tool_choice with specific function."""
        mock_response = {
            "choices": [
                {
                    "message": {
                        "role": "assistant",
                        "content": None,
                        "tool_calls": [
                            {
                                "id": "call_specific",
                                "type": "function",
                                "function": {
                                    "name": "get_weather",
                                    "arguments": '{"location": "New York"}',
                                },
                            }
                        ],
                    },
                    "finish_reason": "tool_calls",
                }
            ],
            "usage": {"prompt_tokens": 55, "completion_tokens": 18, "total_tokens": 73},
        }

        with patch("httpx.AsyncClient.post") as mock_post:
            mock_post.return_value = MagicMock(status_code=200, json=lambda: mock_response)

            messages = [ChatMessage.user("What should I do today?")]
            result = await fiber_client.chat(
                messages,
                tools=[weather_tool, calculation_tool],
                tool_choice={"type": "function", "function": {"name": "get_weather"}},
            )

            # Should use the specified function
            assert len(result.tool_calls) == 1
            assert result.tool_calls[0]["function"]["name"] == "get_weather"


class TestToolCallResponses:
    """Test tool call response parsing and handling."""

    @pytest.fixture
    def fiber_client(self):
        """Create Fiber client for testing."""
        return Fiber(
            default_model="gpt-4o", api_keys={"openai": "test-key"}, enable_observability=False
        )

    @pytest.mark.asyncio
    async def test_multiple_tool_calls_in_response(self, fiber_client):
        """Test handling multiple tool calls in single response."""
        mock_response = {
            "choices": [
                {
                    "message": {
                        "role": "assistant",
                        "content": "I'll get the weather and calculate something for you.",
                        "tool_calls": [
                            {
                                "id": "call_1",
                                "type": "function",
                                "function": {
                                    "name": "get_weather",
                                    "arguments": '{"location": "Paris"}',
                                },
                            },
                            {
                                "id": "call_2",
                                "type": "function",
                                "function": {
                                    "name": "calculate",
                                    "arguments": '{"expression": "10 * 5"}',
                                },
                            },
                        ],
                    },
                    "finish_reason": "tool_calls",
                }
            ],
            "usage": {"prompt_tokens": 70, "completion_tokens": 40, "total_tokens": 110},
        }

        with patch("httpx.AsyncClient.post") as mock_post:
            mock_post.return_value = MagicMock(status_code=200, json=lambda: mock_response)

            messages = [ChatMessage.user("Get weather for Paris and calculate 10*5")]
            result = await fiber_client.chat(messages, tools=[])

            assert len(result.tool_calls) == 2
            assert result.tool_calls[0]["id"] == "call_1"
            assert result.tool_calls[1]["id"] == "call_2"
            assert "weather" in result.text.lower()
            assert "calculate" in result.text.lower()

    @pytest.mark.asyncio
    async def test_tool_call_with_complex_arguments(self, fiber_client):
        """Test tool call with complex nested arguments."""
        complex_args = {
            "query": "search term",
            "filters": {
                "date_range": {"start": "2024-01-01", "end": "2024-12-31"},
                "categories": ["tech", "science"],
                "metadata": {"priority": "high", "tags": ["urgent", "review"]},
            },
            "options": {"limit": 50, "sort": "relevance"},
        }

        mock_response = {
            "choices": [
                {
                    "message": {
                        "role": "assistant",
                        "content": None,
                        "tool_calls": [
                            {
                                "id": "call_complex",
                                "type": "function",
                                "function": {
                                    "name": "search_database",
                                    "arguments": json.dumps(complex_args),
                                },
                            }
                        ],
                    },
                    "finish_reason": "tool_calls",
                }
            ],
            "usage": {"prompt_tokens": 80, "completion_tokens": 50, "total_tokens": 130},
        }

        with patch("httpx.AsyncClient.post") as mock_post:
            mock_post.return_value = MagicMock(status_code=200, json=lambda: mock_response)

            messages = [ChatMessage.user("Search for complex data")]
            result = await fiber_client.chat(messages, tools=[])

            assert len(result.tool_calls) == 1
            parsed_args = json.loads(result.tool_calls[0]["function"]["arguments"])
            assert parsed_args["query"] == "search term"
            assert parsed_args["filters"]["categories"] == ["tech", "science"]

    @pytest.mark.asyncio
    async def test_malformed_tool_call_arguments(self, fiber_client):
        """Test handling of malformed tool call arguments."""
        mock_response = {
            "choices": [
                {
                    "message": {
                        "role": "assistant",
                        "content": "I'll try to call the function.",
                        "tool_calls": [
                            {
                                "id": "call_malformed",
                                "type": "function",
                                "function": {
                                    "name": "get_weather",
                                    # Malformed JSON
                                    "arguments": '{"location": "Boston", invalid_json}',
                                },
                            }
                        ],
                    },
                    "finish_reason": "tool_calls",
                }
            ],
            "usage": {"prompt_tokens": 30, "completion_tokens": 20, "total_tokens": 50},
        }

        with patch("httpx.AsyncClient.post") as mock_post:
            mock_post.return_value = MagicMock(status_code=200, json=lambda: mock_response)

            messages = [ChatMessage.user("Weather in Boston")]
            result = await fiber_client.chat(messages, tools=[])

            # Should still return the tool call even if arguments are malformed
            assert len(result.tool_calls) == 1
            assert result.tool_calls[0]["function"]["name"] == "get_weather"
            # The malformed arguments should be preserved as-is
            assert "invalid_json" in result.tool_calls[0]["function"]["arguments"]


class TestToolCallConversations:
    """Test complete tool call conversations."""

    @pytest.fixture
    def weather_tool(self):
        return {
            "type": "function",
            "function": {
                "name": "get_weather",
                "description": "Get weather information",
                "parameters": {
                    "type": "object",
                    "properties": {"location": {"type": "string"}},
                    "required": ["location"],
                },
            },
        }

    @pytest.fixture
    def fiber_client(self):
        return Fiber(
            default_model="gpt-4o", api_keys={"openai": "test-key"}, enable_observability=False
        )

    @pytest.mark.asyncio
    async def test_complete_tool_call_conversation(self, fiber_client, weather_tool):
        """Test complete conversation with tool call and response."""
        # First response: assistant makes tool call
        tool_call_response = {
            "choices": [
                {
                    "message": {
                        "role": "assistant",
                        "content": "I'll check the weather for you.",
                        "tool_calls": [
                            {
                                "id": "call_weather",
                                "type": "function",
                                "function": {
                                    "name": "get_weather",
                                    "arguments": '{"location": "Seattle"}',
                                },
                            }
                        ],
                    },
                    "finish_reason": "tool_calls",
                }
            ],
            "usage": {"prompt_tokens": 40, "completion_tokens": 25, "total_tokens": 65},
        }

        # Second response: assistant uses tool result
        final_response = {
            "choices": [
                {
                    "message": {
                        "role": "assistant",
                        "content": (
                            "Based on the weather data, it's currently 72°F and sunny in Seattle. "
                            "Perfect weather for outdoor activities!"
                        ),
                    },
                    "finish_reason": "stop",
                }
            ],
            "usage": {"prompt_tokens": 90, "completion_tokens": 35, "total_tokens": 125},
        }

        with patch("httpx.AsyncClient.post") as mock_post:
            # First call returns tool call
            mock_post.return_value = MagicMock(status_code=200, json=lambda: tool_call_response)

            messages = [ChatMessage.user("What's the weather in Seattle?")]
            result1 = await fiber_client.chat(messages, tools=[weather_tool])

            assert len(result1.tool_calls) == 1
            tool_call = result1.tool_calls[0]

            # Simulate tool execution
            tool_result = "Weather in Seattle: 72°F, sunny, light breeze"

            # Add tool call and result to conversation
            messages.append(
                ChatMessage.assistant(content=result1.text, tool_calls=result1.tool_calls)
            )
            messages.append(ChatMessage.tool(content=tool_result, tool_call_id=tool_call["id"]))

            # Second call with updated conversation
            mock_post.return_value = MagicMock(status_code=200, json=lambda: final_response)

            result2 = await fiber_client.chat(messages)

            assert len(result2.tool_calls) == 0
            assert "72°F" in result2.text
            assert "sunny" in result2.text

    @pytest.mark.asyncio
    async def test_tool_call_error_handling(self, fiber_client, weather_tool):
        """Test handling tool call errors in conversation."""
        # Assistant makes tool call
        tool_call_response = {
            "choices": [
                {
                    "message": {
                        "role": "assistant",
                        "content": None,
                        "tool_calls": [
                            {
                                "id": "call_weather",
                                "type": "function",
                                "function": {
                                    "name": "get_weather",
                                    "arguments": '{"location": "InvalidCity"}',
                                },
                            }
                        ],
                    },
                    "finish_reason": "tool_calls",
                }
            ],
            "usage": {"prompt_tokens": 40, "completion_tokens": 20, "total_tokens": 60},
        }

        # Assistant handles tool error
        error_response = {
            "choices": [
                {
                    "message": {
                        "role": "assistant",
                        "content": (
                            "I apologize, but I couldn't get weather information for that "
                            "location. "
                            "Could you please specify a valid city name?"
                        ),
                    },
                    "finish_reason": "stop",
                }
            ],
            "usage": {"prompt_tokens": 70, "completion_tokens": 30, "total_tokens": 100},
        }

        with patch("httpx.AsyncClient.post") as mock_post:
            # First call returns tool call
            mock_post.return_value = MagicMock(status_code=200, json=lambda: tool_call_response)

            messages = [ChatMessage.user("Weather in InvalidCity")]
            result1 = await fiber_client.chat(messages, tools=[weather_tool])

            # Simulate tool execution error
            tool_error = "Error: City 'InvalidCity' not found in weather database"

            # Add error to conversation
            messages.append(ChatMessage.assistant("", tool_calls=result1.tool_calls))
            messages.append(
                ChatMessage.tool(content=tool_error, tool_call_id=result1.tool_calls[0]["id"])
            )

            # Second call handles error
            mock_post.return_value = MagicMock(status_code=200, json=lambda: error_response)

            result2 = await fiber_client.chat(messages)

            assert "apologize" in result2.text.lower()
            assert "valid city" in result2.text.lower()


class TestStreamingToolCalls:
    """Test tool calls in streaming scenarios."""

    @pytest.fixture
    def fiber_client(self):
        return Fiber(
            default_model="gpt-4o", api_keys={"openai": "test-key"}, enable_observability=False
        )

    @pytest.mark.asyncio
    async def test_streaming_tool_call_events(self, fiber_client):
        """Test tool call events in streaming responses."""

        async def mock_stream():
            # Text chunks first
            yield StreamEvent.create_chunk("I'll help you with that calculation.")

            # Tool call event
            tool_call = {
                "id": "call_stream",
                "type": "function",
                "function": {"name": "calculate", "arguments": '{"expression": "15 * 23"}'},
            }
            yield StreamEvent.create_tool_call(tool_call)

            # Final usage
            yield StreamEvent.create_usage(Usage(prompt=35, completion=25, total=60))

        with patch.object(fiber_client, "chat_stream", return_value=mock_stream()):
            events = []
            async for event in fiber_client.chat_stream([ChatMessage.user("Calculate 15 * 23")]):
                events.append(event)

            assert len(events) == 3

            text_events = [e for e in events if e.type == StreamEventType.CHUNK]
            tool_events = [e for e in events if e.type == StreamEventType.TOOL_CALL]
            usage_events = [e for e in events if e.type == StreamEventType.USAGE]

            assert len(text_events) == 1
            assert len(tool_events) == 1
            assert len(usage_events) == 1

            assert tool_events[0].tool_call["function"]["name"] == "calculate"

    @pytest.mark.asyncio
    async def test_streaming_multiple_tool_calls(self, fiber_client):
        """Test multiple tool calls in streaming response."""

        async def mock_stream():
            yield StreamEvent.create_chunk("I'll need to call multiple functions.")

            # First tool call
            tool_call_1 = {
                "id": "call_1",
                "type": "function",
                "function": {"name": "get_weather", "arguments": '{"location": "NYC"}'},
            }
            yield StreamEvent.create_tool_call(tool_call_1)

            # Second tool call
            tool_call_2 = {
                "id": "call_2",
                "type": "function",
                "function": {"name": "calculate", "arguments": '{"expression": "2+2"}'},
            }
            yield StreamEvent.create_tool_call(tool_call_2)

            yield StreamEvent.create_usage(Usage(prompt=50, completion=30))

        with patch.object(fiber_client, "chat_stream", return_value=mock_stream()):
            events = []
            async for event in fiber_client.chat_stream([ChatMessage.user("Multi-tool request")]):
                events.append(event)

            tool_events = [e for e in events if e.type == StreamEventType.TOOL_CALL]
            assert len(tool_events) == 2
            assert tool_events[0].tool_call["id"] == "call_1"
            assert tool_events[1].tool_call["id"] == "call_2"

    @pytest.mark.asyncio
    async def test_streaming_tool_call_with_partial_arguments(self, fiber_client):
        """Test streaming tool call with arguments built incrementally."""

        async def mock_stream():
            # This simulates how some providers might stream tool call arguments
            yield StreamEvent.create_chunk("I'll search for that information.")

            # Tool call with partial arguments (some providers do this)
            tool_call = {
                "id": "call_partial",
                "type": "function",
                "function": {
                    "name": "search",
                    "arguments": '{"query": "machine learning", "limit":',  # Partial JSON
                },
            }
            yield StreamEvent.create_tool_call(tool_call)

            # Another chunk that might complete the arguments
            yield StreamEvent.create_chunk(" 10}")  # This might complete the JSON

            yield StreamEvent.create_usage(Usage(prompt=40, completion=20))

        with patch.object(fiber_client, "chat_stream", return_value=mock_stream()):
            events = []
            async for event in fiber_client.chat_stream([ChatMessage.user("Search ML info")]):
                events.append(event)

            tool_events = [e for e in events if e.type == StreamEventType.TOOL_CALL]
            assert len(tool_events) == 1
            # The partial arguments should be preserved
            assert "machine learning" in tool_events[0].tool_call["function"]["arguments"]

    class TestToolCallNormalization:
        """Test tool call normalization utilities."""

        def test_normalize_openai_tool_call(self):
            """Test normalizing OpenAI tool call format."""
            from llm_fiber.types import NormalizedToolCall, normalize_tool_call

            openai_tool = {
                "id": "call_123",
                "type": "function",
                "function": {
                    "name": "get_weather",
                    "arguments": '{"location": "San Francisco", "unit": "celsius"}',
                },
            }

            normalized = normalize_tool_call(openai_tool, "openai")

            assert isinstance(normalized, NormalizedToolCall)
            assert normalized.id == "call_123"
            assert normalized.name == "get_weather"
            assert normalized.arguments == {"location": "San Francisco", "unit": "celsius"}
            assert normalized.type == "function"

        def test_normalize_anthropic_tool_call(self):
            """Test normalizing Anthropic tool call format."""
            from llm_fiber.types import normalize_tool_call

            anthropic_tool = {
                "id": "toolu_123",
                "name": "calculate",
                "input": {"expression": "2 + 2"},
            }

            normalized = normalize_tool_call(anthropic_tool, "anthropic")

            assert normalized.id == "toolu_123"
            assert normalized.name == "calculate"
            assert normalized.arguments == {"expression": "2 + 2"}
            assert normalized.type == "function"

        def test_normalize_gemini_tool_call(self):
            """Test normalizing Gemini tool call format."""
            from llm_fiber.types import normalize_tool_call

            gemini_tool = {
                "functionCall": {
                    "name": "search_web",
                    "args": {"query": "machine learning", "max_results": 5},
                }
            }

            normalized = normalize_tool_call(gemini_tool, "gemini")

            assert normalized.name == "search_web"
            assert normalized.arguments == {"query": "machine learning", "max_results": 5}
            assert normalized.type == "function"
            assert normalized.id.startswith("call_")  # Generated ID

        def test_normalized_tool_call_conversions(self):
            """Test NormalizedToolCall format conversions."""
            from llm_fiber.types import NormalizedToolCall

            normalized = NormalizedToolCall(
                id="call_abc123",
                name="get_weather",
                arguments={"location": "NYC", "unit": "fahrenheit"},
            )

            # Test OpenAI format
            openai_format = normalized.to_openai_format()
            assert openai_format["id"] == "call_abc123"
            assert openai_format["type"] == "function"
            assert openai_format["function"]["name"] == "get_weather"
            assert '"location": "NYC"' in openai_format["function"]["arguments"]

            # Test Anthropic format
            anthropic_format = normalized.to_anthropic_format()
            assert anthropic_format["type"] == "tool_use"
            assert anthropic_format["id"] == "call_abc123"
            assert anthropic_format["name"] == "get_weather"
            assert anthropic_format["input"] == {"location": "NYC", "unit": "fahrenheit"}

            # Test Gemini format
            gemini_format = normalized.to_gemini_format()
            assert gemini_format["functionCall"]["name"] == "get_weather"
            assert gemini_format["functionCall"]["args"] == {
                "location": "NYC",
                "unit": "fahrenheit",
            }

        def test_validate_tool_call_format(self):
            """Test tool call format validation."""
            from llm_fiber.types import validate_tool_call_format

            # Valid OpenAI format
            valid_openai = {
                "id": "call_123",
                "type": "function",
                "function": {"name": "test", "arguments": "{}"},
            }
            assert validate_tool_call_format(valid_openai, "openai") is True

            # Invalid format - missing required fields
            invalid_openai = {"id": "call_123"}
            assert validate_tool_call_format(invalid_openai, "openai") is False

            # Valid Anthropic format
            valid_anthropic = {
                "id": "toolu_123",
                "name": "test",
                "input": {"param": "value"},
            }
            assert validate_tool_call_format(valid_anthropic, "anthropic") is True

        def test_create_tool_response_message(self):
            """Test creating tool response messages."""
            from llm_fiber.types import create_tool_response_message

            message = create_tool_response_message(
                tool_call_id="call_123", content="The weather is sunny", name="get_weather"
            )

            assert message.role == "tool"
            assert message.content == "The weather is sunny"
            assert message.tool_call_id == "call_123"
            assert message.name == "get_weather"

        def test_extract_tool_calls_from_stream_events(self):
            """Test extracting tool calls from stream events."""
            from llm_fiber.types import StreamEvent, extract_tool_calls_from_stream_events

            # Create mock stream events
            events = [
                StreamEvent.create_chunk("I'll help with that."),
                StreamEvent.create_tool_call(
                    {
                        "id": "call_1",
                        "type": "function",
                        "function": {"name": "calculate", "arguments": '{"expr": "2+2"}'},
                    }
                ),
                StreamEvent.create_tool_call(
                    {
                        "id": "call_2",
                        "type": "function",
                        "function": {"name": "search", "arguments": '{"query": "test"}'},
                    }
                ),
                StreamEvent.create_usage(Usage(prompt=25, completion=15)),
            ]

            tool_calls = extract_tool_calls_from_stream_events(events)

            assert len(tool_calls) == 2
            assert tool_calls[0].id == "call_1"
            assert tool_calls[0].name == "calculate"
            assert tool_calls[0].arguments == {"expr": "2+2"}
            assert tool_calls[1].id == "call_2"
            assert tool_calls[1].name == "search"
            assert tool_calls[1].arguments == {"query": "test"}

        def test_normalize_malformed_tool_call(self):
            """Test handling of malformed tool calls."""
            from llm_fiber import FiberValidationError
            from llm_fiber.types import normalize_tool_call

            # Missing required fields
            malformed_tool = {"id": "call_123"}

            with pytest.raises(FiberValidationError):
                normalize_tool_call(malformed_tool, "openai")

        def test_normalize_tool_call_with_invalid_json_arguments(self):
            """Test normalizing tool call with invalid JSON arguments."""
            from llm_fiber.types import normalize_tool_call

            openai_tool = {
                "id": "call_123",
                "type": "function",
                "function": {
                    "name": "get_weather",
                    "arguments": '{"location": "SF", invalid json',  # Invalid JSON
                },
            }

            normalized = normalize_tool_call(openai_tool, "openai")

            # Should handle invalid JSON gracefully
            assert normalized.id == "call_123"
            assert normalized.name == "get_weather"
            assert normalized.arguments == {}  # Fallback to empty dict


class TestProviderToolCallNormalization:
    """Test tool call normalization across providers."""

    def test_openai_tool_call_format(self):
        """Test OpenAI tool call format normalization."""
        openai_tool_call = {
            "id": "call_openai_123",
            "type": "function",
            "function": {
                "name": "get_weather",
                "arguments": '{"location": "Boston", "unit": "fahrenheit"}',
            },
        }

        # OpenAI format is the standard, should pass through unchanged
        assert openai_tool_call["id"] == "call_openai_123"
        assert openai_tool_call["type"] == "function"
        assert openai_tool_call["function"]["name"] == "get_weather"

    def test_anthropic_tool_call_format_normalization(self):
        """Test Anthropic tool call format normalization to OpenAI format."""
        # Anthropic might use different format internally
        anthropic_response = {
            "content": [
                {
                    "type": "tool_use",
                    "id": "toolu_123",
                    "name": "get_weather",
                    "input": {"location": "Boston", "unit": "fahrenheit"},
                }
            ]
        }

        # This would be normalized to OpenAI format by the provider adapter
        normalized = {
            "id": anthropic_response["content"][0]["id"],
            "type": "function",
            "function": {
                "name": anthropic_response["content"][0]["name"],
                "arguments": json.dumps(anthropic_response["content"][0]["input"]),
            },
        }

        assert normalized["id"] == "toolu_123"
        assert normalized["function"]["name"] == "get_weather"
        assert "Boston" in normalized["function"]["arguments"]

    def test_gemini_tool_call_format_normalization(self):
        """Test Gemini tool call format normalization to OpenAI format."""
        # Gemini might use different format
        gemini_response = {
            "candidates": [
                {
                    "content": {
                        "parts": [
                            {
                                "functionCall": {
                                    "name": "get_weather",
                                    "args": {"location": "Boston", "unit": "fahrenheit"},
                                }
                            }
                        ]
                    }
                }
            ]
        }

        # This would be normalized by the Gemini provider adapter
        function_call = gemini_response["candidates"][0]["content"]["parts"][0]["functionCall"]
        normalized = {
            "id": f"call_gemini_{hash(str(function_call))}",  # Generated ID
            "type": "function",
            "function": {
                "name": function_call["name"],
                "arguments": json.dumps(function_call["args"]),
            },
        }

        assert normalized["type"] == "function"
        assert normalized["function"]["name"] == "get_weather"
        assert "Boston" in normalized["function"]["arguments"]


class TestToolCallEdgeCases:
    """Test edge cases and error scenarios for tool calls."""

    @pytest.fixture
    def fiber_client(self):
        return Fiber(
            default_model="gpt-4o", api_keys={"openai": "test-key"}, enable_observability=False
        )

    @pytest.mark.asyncio
    async def test_empty_tool_calls_array(self, fiber_client):
        """Test response with empty tool_calls array."""
        mock_response = {
            "choices": [
                {
                    "message": {
                        "role": "assistant",
                        "content": "I can help without tools.",
                        "tool_calls": [],  # Empty array
                    },
                    "finish_reason": "stop",
                }
            ],
            "usage": {"prompt_tokens": 30, "completion_tokens": 10, "total_tokens": 40},
        }

        with patch("httpx.AsyncClient.post") as mock_post:
            mock_post.return_value = MagicMock(status_code=200, json=lambda: mock_response)

            messages = [ChatMessage.user("Just chat with me")]
            result = await fiber_client.chat(messages, tools=[])

            assert len(result.tool_calls) == 0
            assert result.text == "I can help without tools."

    @pytest.mark.asyncio
    async def test_missing_tool_calls_field(self, fiber_client):
        """Test response without tool_calls field at all."""
        mock_response = {
            "choices": [
                {
                    "message": {
                        "role": "assistant",
                        "content": "No tools needed for this response.",
                        # No tool_calls field
                    },
                    "finish_reason": "stop",
                }
            ],
            "usage": {"prompt_tokens": 25, "completion_tokens": 8, "total_tokens": 33},
        }

        with patch("httpx.AsyncClient.post") as mock_post:
            mock_post.return_value = MagicMock(status_code=200, json=lambda: mock_response)

            messages = [ChatMessage.user("Simple question")]
            result = await fiber_client.chat(messages)

            assert len(result.tool_calls) == 0
            assert result.text == "No tools needed for this response."

    @pytest.mark.asyncio
    async def test_tool_call_with_empty_arguments(self, fiber_client):
        """Test tool call with empty arguments string."""
        mock_response = {
            "choices": [
                {
                    "message": {
                        "role": "assistant",
                        "content": None,
                        "tool_calls": [
                            {
                                "id": "call_empty_args",
                                "type": "function",
                                "function": {
                                    "name": "get_random_fact",
                                    "arguments": "{}",  # Empty arguments
                                },
                            }
                        ],
                    },
                    "finish_reason": "tool_calls",
                }
            ],
            "usage": {"prompt_tokens": 20, "completion_tokens": 10, "total_tokens": 30},
        }

        with patch("httpx.AsyncClient.post") as mock_post:
            mock_post.return_value = MagicMock(status_code=200, json=lambda: mock_response)

            messages = [ChatMessage.user("Tell me a random fact")]
            result = await fiber_client.chat(messages, tools=[])

            assert len(result.tool_calls) == 1
            assert result.tool_calls[0]["function"]["arguments"] == "{}"

    @pytest.mark.asyncio
    async def test_tool_call_missing_required_fields(self, fiber_client):
        """Test tool call missing some required fields."""
        mock_response = {
            "choices": [
                {
                    "message": {
                        "role": "assistant",
                        "content": None,
                        "tool_calls": [
                            {
                                "id": "call_incomplete",
                                "type": "function",
                                "function": {
                                    "name": "incomplete_tool"
                                    # Missing arguments field
                                },
                            }
                        ],
                    },
                    "finish_reason": "tool_calls",
                }
            ],
            "usage": {"prompt_tokens": 25, "completion_tokens": 12, "total_tokens": 37},
        }

        with patch("httpx.AsyncClient.post") as mock_post:
            mock_post.return_value = MagicMock(status_code=200, json=lambda: mock_response)

            messages = [ChatMessage.user("Test incomplete tool")]
            result = await fiber_client.chat(messages, tools=[])

            assert len(result.tool_calls) == 1
            assert result.tool_calls[0]["function"]["name"] == "incomplete_tool"
            # Should handle missing arguments gracefully
            assert (
                "arguments" not in result.tool_calls[0]["function"]
                or result.tool_calls[0]["function"].get("arguments") is None
            )

    @pytest.mark.asyncio
    async def test_tool_call_with_null_values(self, fiber_client):
        """Test tool call with null values in fields."""
        mock_response = {
            "choices": [
                {
                    "message": {
                        "role": "assistant",
                        "content": None,
                        "tool_calls": [
                            {
                                "id": "call_null_values",
                                "type": "function",
                                "function": {
                                    "name": "test_function",
                                    "arguments": None,  # Null arguments
                                },
                            }
                        ],
                    },
                    "finish_reason": "tool_calls",
                }
            ],
            "usage": {"prompt_tokens": 30, "completion_tokens": 15, "total_tokens": 45},
        }

        with patch("httpx.AsyncClient.post") as mock_post:
            mock_post.return_value = MagicMock(status_code=200, json=lambda: mock_response)

            messages = [ChatMessage.user("Test null values")]
            result = await fiber_client.chat(messages, tools=[])

            assert len(result.tool_calls) == 1
            assert result.tool_calls[0]["function"]["name"] == "test_function"
            # Should handle null arguments
            assert result.tool_calls[0]["function"]["arguments"] is None

    @pytest.mark.asyncio
    async def test_extremely_large_tool_arguments(self, fiber_client):
        """Test tool call with very large arguments."""
        large_data = {"data": "x" * 10000}  # 10KB of data
        large_args = json.dumps(large_data)

        mock_response = {
            "choices": [
                {
                    "message": {
                        "role": "assistant",
                        "content": None,
                        "tool_calls": [
                            {
                                "id": "call_large",
                                "type": "function",
                                "function": {"name": "process_large_data", "arguments": large_args},
                            }
                        ],
                    },
                    "finish_reason": "tool_calls",
                }
            ],
            "usage": {"prompt_tokens": 100, "completion_tokens": 50, "total_tokens": 150},
        }

        with patch("httpx.AsyncClient.post") as mock_post:
            mock_post.return_value = MagicMock(status_code=200, json=lambda: mock_response)

            messages = [ChatMessage.user("Process large data")]
            result = await fiber_client.chat(messages, tools=[])

            assert len(result.tool_calls) == 1
            parsed_args = json.loads(result.tool_calls[0]["function"]["arguments"])
            assert len(parsed_args["data"]) == 10000

    @pytest.mark.asyncio
    async def test_unicode_in_tool_arguments(self, fiber_client):
        """Test tool call with unicode characters in arguments."""
        unicode_data = {
            "text": "Hello 世界! 🌍 Bonjour monde! Привет мир!",
            "emoji": "🚀🎉💡",
            "special_chars": "äöü ñ ç",
        }

        mock_response = {
            "choices": [
                {
                    "message": {
                        "role": "assistant",
                        "content": None,
                        "tool_calls": [
                            {
                                "id": "call_unicode",
                                "type": "function",
                                "function": {
                                    "name": "process_text",
                                    "arguments": json.dumps(unicode_data, ensure_ascii=False),
                                },
                            }
                        ],
                    },
                    "finish_reason": "tool_calls",
                }
            ],
            "usage": {"prompt_tokens": 40, "completion_tokens": 30, "total_tokens": 70},
        }

        with patch("httpx.AsyncClient.post") as mock_post:
            mock_post.return_value = MagicMock(status_code=200, json=lambda: mock_response)

            messages = [ChatMessage.user("Process unicode text")]
            result = await fiber_client.chat(messages, tools=[])

            assert len(result.tool_calls) == 1
            parsed_args = json.loads(result.tool_calls[0]["function"]["arguments"])
            assert "世界" in parsed_args["text"]
            assert "🚀" in parsed_args["emoji"]
            assert "ñ" in parsed_args["special_chars"]


class TestToolCallIntegration:
    """Integration tests for tool calls across the system."""

    @pytest.fixture
    def multi_provider_fiber(self):
        return Fiber(
            api_keys={
                "openai": "test-openai-key",
                "anthropic": "test-anthropic-key",
                "gemini": "test-gemini-key",
            },
            enable_observability=False,
        )

    @pytest.fixture
    def weather_tool(self):
        return {
            "type": "function",
            "function": {
                "name": "get_weather",
                "description": "Get weather information",
                "parameters": {
                    "type": "object",
                    "properties": {"location": {"type": "string"}},
                    "required": ["location"],
                },
            },
        }

    @pytest.mark.asyncio
    async def test_tool_calls_across_providers(self, multi_provider_fiber, weather_tool):
        """Test tool calls work consistently across providers."""
        test_cases = [
            ("gpt-4o", "openai"),
            ("claude-3-haiku-20240307", "anthropic"),
            ("gemini-1.5-flash", "gemini"),
        ]

        for model, provider in test_cases:
            if provider == "openai":
                mock_response = {
                    "choices": [
                        {
                            "message": {
                                "role": "assistant",
                                "content": f"Using {provider} to get weather",
                                "tool_calls": [
                                    {
                                        "id": f"call_{provider}",
                                        "type": "function",
                                        "function": {
                                            "name": "get_weather",
                                            "arguments": '{"location": "New York"}',
                                        },
                                    }
                                ],
                            },
                            "finish_reason": "tool_calls",
                        }
                    ],
                    "usage": {"prompt_tokens": 35, "completion_tokens": 20, "total_tokens": 55},
                }
            elif provider == "anthropic":
                mock_response = {
                    "content": [
                        {"type": "text", "text": f"Using {provider} to get weather"},
                        {
                            "type": "tool_use",
                            "id": f"call_{provider}",
                            "name": "get_weather",
                            "input": {"location": "New York"},
                        },
                    ],
                    "usage": {"input_tokens": 35, "output_tokens": 20},
                }
            else:  # gemini
                mock_response = {
                    "candidates": [
                        {
                            "content": {
                                "parts": [
                                    {"text": f"Using {provider} to get weather"},
                                    {
                                        "functionCall": {
                                            "name": "get_weather",
                                            "args": {"location": "New York"},
                                        }
                                    },
                                ]
                            }
                        }
                    ],
                    "usageMetadata": {
                        "promptTokenCount": 35,
                        "candidatesTokenCount": 20,
                        "totalTokenCount": 55,
                    },
                }

            with patch("httpx.AsyncClient.post") as mock_post:
                mock_post.return_value = MagicMock(status_code=200, json=lambda: mock_response)

                messages = [ChatMessage.user("Weather in NY")]
                result = await multi_provider_fiber.chat(
                    messages, model=model, tools=[weather_tool]
                )

                assert len(result.tool_calls) == 1
                assert result.tool_calls[0]["function"]["name"] == "get_weather"
                assert provider in result.text

    @pytest.mark.asyncio
    async def test_tool_calls_with_caching(self, multi_provider_fiber, weather_tool):
        """Test that tool calls work properly with caching enabled."""
        from llm_fiber.caching.memory import MemoryCacheAdapter

        cache = MemoryCacheAdapter(max_size=10)
        fiber_with_cache = Fiber(
            default_model="gpt-4o",
            api_keys={"openai": "test-key"},
            cache_adapter=cache,
            enable_observability=False,
        )

        mock_response = {
            "choices": [
                {
                    "message": {
                        "role": "assistant",
                        "content": "I'll get the weather for you.",
                        "tool_calls": [
                            {
                                "id": "call_cached",
                                "type": "function",
                                "function": {
                                    "name": "get_weather",
                                    "arguments": '{"location": "Boston"}',
                                },
                            }
                        ],
                    },
                    "finish_reason": "tool_calls",
                }
            ],
            "usage": {"prompt_tokens": 40, "completion_tokens": 25, "total_tokens": 65},
        }

        with patch("httpx.AsyncClient.post") as mock_post:
            mock_post.return_value = MagicMock(status_code=200, json=lambda: mock_response)

            messages = [ChatMessage.user("Weather in Boston")]

            # First call should hit the API
            result1 = await fiber_with_cache.chat(messages, tools=[weather_tool])
            assert len(result1.tool_calls) == 1
            assert mock_post.call_count == 1

            # Second identical call should hit cache
            result2 = await fiber_with_cache.chat(messages, tools=[weather_tool])
            assert len(result2.tool_calls) == 1
            assert result2.tool_calls[0]["id"] == result1.tool_calls[0]["id"]
            # Should still be 1 if cached
            assert mock_post.call_count == 1

    @pytest.mark.asyncio
    async def test_tool_calls_with_context_binding(self, multi_provider_fiber, weather_tool):
        """Test tool calls with bound context."""
        bound_fiber = multi_provider_fiber.bind(temperature=0.2, max_tokens=150)

        mock_response = {
            "choices": [
                {
                    "message": {
                        "role": "assistant",
                        "content": "Using bound context for weather request.",
                        "tool_calls": [
                            {
                                "id": "call_bound",
                                "type": "function",
                                "function": {
                                    "name": "get_weather",
                                    "arguments": '{"location": "Chicago"}',
                                },
                            }
                        ],
                    },
                    "finish_reason": "tool_calls",
                }
            ],
            "usage": {"prompt_tokens": 45, "completion_tokens": 28, "total_tokens": 73},
        }

        with patch("httpx.AsyncClient.post") as mock_post:
            mock_post.return_value = MagicMock(status_code=200, json=lambda: mock_response)

            messages = [ChatMessage.user("Chicago weather")]
            result = await bound_fiber.chat(messages, tools=[weather_tool])

            assert len(result.tool_calls) == 1
            assert "bound context" in result.text

    @pytest.mark.asyncio
    async def test_concurrent_tool_calls(self, multi_provider_fiber, weather_tool):
        """Test concurrent requests with tool calls."""
        mock_response = {
            "choices": [
                {
                    "message": {
                        "role": "assistant",
                        "content": "Getting weather information.",
                        "tool_calls": [
                            {
                                "id": "call_concurrent",
                                "type": "function",
                                "function": {
                                    "name": "get_weather",
                                    "arguments": '{"location": "Miami"}',
                                },
                            }
                        ],
                    },
                    "finish_reason": "tool_calls",
                }
            ],
            "usage": {"prompt_tokens": 35, "completion_tokens": 22, "total_tokens": 57},
        }

        with patch("httpx.AsyncClient.post") as mock_post:
            mock_post.return_value = MagicMock(status_code=200, json=lambda: mock_response)

            # Start multiple concurrent requests
            messages = [ChatMessage.user("Miami weather")]
            tasks = [
                asyncio.create_task(multi_provider_fiber.chat(messages, tools=[weather_tool]))
                for _ in range(3)
            ]

            results = await asyncio.gather(*tasks)

            # All should succeed with tool calls
            for result in results:
                assert len(result.tool_calls) == 1
                assert result.tool_calls[0]["function"]["name"] == "get_weather"
