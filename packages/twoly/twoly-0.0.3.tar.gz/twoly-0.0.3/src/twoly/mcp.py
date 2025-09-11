from typing import Optional, TypedDict, List
import asyncio
import contextlib
from mcp import ClientSession, StdioServerParameters
from mcp.client.stdio import stdio_client
from langchain_mcp_adapters.tools import load_mcp_tools
from langchain_core.tools import BaseTool

class TwolyOptions(TypedDict, total=False):
    workspace: str
    nats_servers: str
    version: str

class TwolyMCP:
    def __init__(self, name: str, options: Optional[TwolyOptions] = None):
        self.name = name
        self.options = options
        _opts = options or {}
        nats_servers = _opts.get("nats_servers", "nats://localhost:4222")
        version = _opts.get("version", "latest")
        env = {
            "RUNTIME_NAME": name,
            "NATS_SERVERS": nats_servers,
        }
        if "workspace" in _opts:
            env["WORKSPACE_ID"] = _opts["workspace"]
        self.serverParams = StdioServerParameters(
            command="npx",
            args=["@2ly/runtime@" + version],
            env=env,
        )
        self._session: Optional[ClientSession] = None
        self._runner_task: Optional[asyncio.Task] = None
        self._started_future: Optional[asyncio.Future] = None
        self._stop_requested: bool = False
        self._runner_exception: Optional[BaseException] = None
        self._started = False
        self._startup_timeout_seconds = float(_opts.get("startup_timeout_seconds", 20.0))

    async def __aenter__(self) -> "TwolyMCP":
        await self.start()
        return self

    async def __aexit__(self, exc_type, exc, tb) -> None:
        await self.stop()

    def __del__(self) -> None:
        try:
            self._stop_requested = True
            if self._runner_task is not None:
                self._runner_task.cancel()
        except Exception:
            pass

    async def start(self) -> None:
        if self._started:
            return
        self._runner_exception = None
        self._started_future = asyncio.get_running_loop().create_future()
        self._stop_requested = False
        self._runner_task = asyncio.create_task(self._run_session())
        try:
            assert self._started_future is not None
            await asyncio.wait_for(self._started_future, timeout=self._startup_timeout_seconds)
        except asyncio.TimeoutError as error:
            self._stop_requested = True
            if self._runner_task is not None:
                self._runner_task.cancel()
                with contextlib.suppress(Exception, asyncio.CancelledError):
                    await self._runner_task
            self._runner_task = None
            self._started_future = None
            self._session = None
            self._started = False
            raise RuntimeError("MCP runtime startup timed out. Ensure runtime can start and dependencies are reachable.") from error
        if self._runner_exception is not None:
            await self.stop()
            raise RuntimeError("MCP runtime failed to start") from self._runner_exception
        self._started = True

    async def stop(self) -> None:
        if not self._started and self._runner_task is None:
            return
        try:
            self._stop_requested = True
            if self._runner_task is not None:
                try:
                    await asyncio.wait_for(self._runner_task, timeout=self._startup_timeout_seconds)
                except asyncio.TimeoutError:
                    self._runner_task.cancel()
                    with contextlib.suppress(Exception, asyncio.CancelledError):
                        await self._runner_task
                except asyncio.CancelledError:
                    pass
        finally:
            self._runner_task = None
            self._started_future = None
            self._session = None
            self._started = False

    async def _run_session(self) -> None:
        try:
            async with stdio_client(self.serverParams) as (read, write):
                async with ClientSession(read, write) as session:
                    self._session = session
                    await session.initialize()
                    if self._started_future is not None and not self._started_future.done():
                        self._started_future.set_result(None)
                    while not self._stop_requested:
                        await asyncio.sleep(0.01)
        except BaseException as error:
            self._runner_exception = error
            if self._started_future is not None and not self._started_future.done():
                self._started_future.set_result(None)
            raise
        finally:
            self._session = None

    async def get_langchain_tools(self) -> List[BaseTool]:
        await self.start()
        assert self._session is not None
        tools = await load_mcp_tools(self._session)
        return tools

    async def list_tools(self) -> List[BaseTool]:
        return await self.get_langchain_tools()

    async def tools(self) -> List[BaseTool]:
        return await self.get_langchain_tools()