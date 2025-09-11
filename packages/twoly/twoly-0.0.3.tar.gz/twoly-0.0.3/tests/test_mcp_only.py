import asyncio
from types import SimpleNamespace
import pytest
from unittest.mock import AsyncMock, patch

from twoly.mcp_only import TwolyMCPWithoutAdapter, TwolyOptions


class _ToolObj(SimpleNamespace):
    pass


class _ToolsResult(SimpleNamespace):
    pass


class TestTwolyMCPWithoutAdapterInit:
    def test_init_defaults(self):
        instance = TwolyMCPWithoutAdapter("rt")
        assert instance.name == "rt"
        assert instance.serverParams.command == "npx"
        assert instance.serverParams.args == ["@2ly/runtime@latest"]
        assert instance.serverParams.env["RUNTIME_NAME"] == "rt"
        assert instance.serverParams.env["NATS_SERVERS"] == "nats://localhost:4222"

    def test_init_with_options(self):
        options: TwolyOptions = {
            "workspace": "ws",
            "nats_servers": "nats://custom:4222",
            "version": "1.2.3",
        }
        instance = TwolyMCPWithoutAdapter("rt2", options)
        assert instance.serverParams.args == ["@2ly/runtime@1.2.3"]
        assert instance.serverParams.env["WORKSPACE_ID"] == "ws"
        assert instance.serverParams.env["NATS_SERVERS"] == "nats://custom:4222"


@pytest.mark.asyncio
async def test_get_langchain_tools_and_tools_dict():
    mock_read = AsyncMock()
    mock_write = AsyncMock()
    mock_session = AsyncMock()
    tool_a = _ToolObj(name="tA", description="A", inputSchema={"type": "object", "properties": {}})
    tool_b = _ToolObj(name="tB", description="B", inputSchema=None)
    mock_session.list_tools = AsyncMock(return_value=_ToolsResult(tools=[tool_a, tool_b]))
    mock_session.initialize = AsyncMock()

    stdio_ctx = AsyncMock()
    stdio_ctx.__aenter__.return_value = (mock_read, mock_write)
    stdio_ctx.__aexit__.return_value = None

    client_ctx = AsyncMock()
    client_ctx.__aenter__.return_value = mock_session
    client_ctx.__aexit__.return_value = None

    with patch("twoly.mcp_only.stdio_client", return_value=stdio_ctx) as _stdio, \
         patch("twoly.mcp_only.ClientSession", return_value=client_ctx) as _client:
        instance = TwolyMCPWithoutAdapter("rt")
        lc_tools = await instance.get_langchain_tools()
        assert [t.name for t in lc_tools] == ["tA", "tB"]
        tools_dict = await instance.tools()
        assert isinstance(tools_dict, list)
        assert {d["name"] for d in tools_dict} == {"tA", "tB"}
        await instance.stop()


@pytest.mark.asyncio
async def test_call_tool_uses_same_session_and_returns_content():
    mock_read = AsyncMock()
    mock_write = AsyncMock()
    mock_session = AsyncMock()
    mock_session.initialize = AsyncMock()
    mock_session.list_tools = AsyncMock(return_value=_ToolsResult(tools=[]))
    mock_session.call_tool = AsyncMock(return_value=SimpleNamespace(content=[{"type": "text", "text": "ok"}], isError=False))

    stdio_ctx = AsyncMock()
    stdio_ctx.__aenter__.return_value = (mock_read, mock_write)
    stdio_ctx.__aexit__.return_value = None

    client_ctx = AsyncMock()
    client_ctx.__aenter__.return_value = mock_session
    client_ctx.__aexit__.return_value = None

    with patch("twoly.mcp_only.stdio_client", return_value=stdio_ctx), \
         patch("twoly.mcp_only.ClientSession", return_value=client_ctx):
        instance = TwolyMCPWithoutAdapter("rt")
        await instance.get_langchain_tools()
        result = await instance.call_tool("x", {"a": 1})
        assert result == {"content": [{"type": "text", "text": "ok"}], "isError": False}
        mock_session.call_tool.assert_awaited_once_with("x", {"a": 1})
        await instance.stop()


@pytest.mark.asyncio
async def test_start_timeout_raises_runtime_error_and_cleans_up():
    with patch("twoly.mcp_only.asyncio.wait_for", side_effect=asyncio.TimeoutError), \
         patch("twoly.mcp_only.stdio_client") as stdio_mock:
        stdio_mock.return_value.__aenter__.return_value = (AsyncMock(), AsyncMock())
        instance = TwolyMCPWithoutAdapter("rt", {"startup_timeout_seconds": 0.01})
        with pytest.raises(RuntimeError, match="startup timed out"):
            await instance.start()
        await instance.stop()


# New test to ensure the session is initialized lazily on first use
@pytest.mark.asyncio
async def test_lazy_initialization_only_on_first_use():
    with patch("twoly.mcp_only.stdio_client") as stdio_mock, \
         patch("twoly.mcp_only.ClientSession") as client_mock:
        instance = TwolyMCPWithoutAdapter("rt")
        assert stdio_mock.called is False

        mock_read = AsyncMock()
        mock_write = AsyncMock()
        stdio_ctx = AsyncMock()
        stdio_ctx.__aenter__.return_value = (mock_read, mock_write)
        stdio_ctx.__aexit__.return_value = None
        stdio_mock.return_value = stdio_ctx

        mock_session = AsyncMock()
        mock_session.initialize = AsyncMock()
        mock_session.list_tools = AsyncMock(return_value=_ToolsResult(tools=[]))
        client_ctx = AsyncMock()
        client_ctx.__aenter__.return_value = mock_session
        client_ctx.__aexit__.return_value = None
        client_mock.return_value = client_ctx

        await instance.get_langchain_tools()
        assert stdio_mock.called is True
        await instance.stop()


@pytest.mark.asyncio
async def test_stop_closes_session_and_clears_state():
    mock_read = AsyncMock()
    mock_write = AsyncMock()

    stdio_ctx = AsyncMock()
    stdio_ctx.__aenter__.return_value = (mock_read, mock_write)
    stdio_ctx.__aexit__.return_value = None

    mock_session = AsyncMock()
    mock_session.initialize = AsyncMock()
    mock_session.list_tools = AsyncMock(return_value=_ToolsResult(tools=[]))

    client_ctx = AsyncMock()
    client_ctx.__aenter__.return_value = mock_session
    client_ctx.__aexit__.return_value = None

    with patch("twoly.mcp_only.stdio_client", return_value=stdio_ctx), \
         patch("twoly.mcp_only.ClientSession", return_value=client_ctx):
        instance = TwolyMCPWithoutAdapter("rt")
        await instance.get_langchain_tools()
        assert instance._session is not None
        await instance.stop()
        assert client_ctx.__aexit__.await_count == 1
        assert instance._session is None
        assert instance._runner_task is None
        assert instance._started is False
        # Optional: new internals
        assert getattr(instance, "_started_future", None) is None
