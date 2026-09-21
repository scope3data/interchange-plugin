"""Verify an Apostra account through the v3 MCP endpoint."""

import asyncio
import json
import os
from typing import Any, Protocol

import anyio

IO_TIMEOUT_SECONDS = 15

APOSTRA_MCP_URL = "https://api.interchange.io/mcp/v3"


class ToolClient(Protocol):
    async def call_tool(self, name: str, arguments: dict[str, Any]) -> Any: ...


async def verify_apostra_account(
    client: ToolClient, timeout: float = IO_TIMEOUT_SECONDS
) -> Any:
    """Make exactly one read-only call and fail closed on a tool error."""
    try:
        result = await asyncio.wait_for(client.call_tool("get_status", {}), timeout)
    except asyncio.TimeoutError as error:
        raise RuntimeError(
            "Apostra verification timed out. Check network access and retry."
        ) from error
    if result.isError or result.structuredContent is None:
        raise RuntimeError("Apostra account verification failed")
    return result.structuredContent


async def connect_and_verify(token: str, endpoint: str = APOSTRA_MCP_URL) -> Any:
    from mcp import ClientSession
    from mcp.client.streamable_http import streamablehttp_client

    headers = {"Authorization": f"Bearer {token}"}
    async with streamablehttp_client(endpoint, headers=headers) as streams:
        read_stream, write_stream, _ = streams
        async with ClientSession(read_stream, write_stream) as session:
            await session.initialize()
            return await verify_apostra_account(session)


async def run_verification(
    token: str, timeout: float = IO_TIMEOUT_SECONDS,
    endpoint: str = APOSTRA_MCP_URL
) -> Any:
    # Level cancellation reaches every SDK task and every teardown await.
    # asyncio.wait_for only cancels once, so SDK cleanup could outlive it.
    try:
        with anyio.fail_after(timeout):
            return await connect_and_verify(token, endpoint)
    except asyncio.TimeoutError as error:
        raise RuntimeError(
            "Apostra connection or verification timed out. "
            "Check network access and the MCP endpoint, then retry."
        ) from error


async def main() -> None:
    token = os.environ.get("APOSTRA_ACCESS_TOKEN")
    if not token:
        raise RuntimeError("Set APOSTRA_ACCESS_TOKEN before running")
    print(json.dumps(await run_verification(token), indent=2))


if __name__ == "__main__":
    asyncio.run(main())
