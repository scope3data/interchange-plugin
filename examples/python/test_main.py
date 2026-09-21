import asyncio
import importlib
import json
import time
import unittest
from types import SimpleNamespace
from unittest.mock import patch

from main import run_verification, verify_apostra_account


class FakeClient:
    def __init__(self, result):
        self.result = result
        self.calls = []

    async def call_tool(self, name, arguments):
        self.calls.append((name, arguments))
        return self.result


class VerifyAccountTest(unittest.IsolatedAsyncioTestCase):
    async def test_verifies_with_one_read_only_call(self):
        expected = {"activeAccount": {"id": "buyer-123", "kind": "buyer"}}
        client = FakeClient(
            SimpleNamespace(isError=False, structuredContent=expected)
        )

        status = await verify_apostra_account(client)

        self.assertEqual(status, expected)
        self.assertEqual(client.calls, [("get_status", {})])

    async def test_fails_closed_on_tool_error(self):
        client = FakeClient(SimpleNamespace(isError=True, structuredContent=None))
        with self.assertRaisesRegex(RuntimeError, "verification failed"):
            await verify_apostra_account(client)

    async def test_cancels_stalled_tool_call(self):
        cancelled = asyncio.Event()

        class StalledClient:
            async def call_tool(self, name, arguments):
                try:
                    await asyncio.Event().wait()
                finally:
                    cancelled.set()

        with self.assertRaisesRegex(RuntimeError, "verification timed out.*retry"):
            await verify_apostra_account(StalledClient(), timeout=0.01)
        self.assertTrue(cancelled.is_set())

    async def test_cancels_stalled_connection(self):
        cancelled = asyncio.Event()

        async def stalled_connect(*args):
            try:
                await asyncio.Event().wait()
            finally:
                cancelled.set()

        with (
            patch("main.connect_and_verify", stalled_connect),
            self.assertRaisesRegex(RuntimeError, "connection or verification timed out.*retry"),
        ):
            await run_verification("local-test-token", timeout=0.01)
        self.assertTrue(cancelled.is_set())

    async def test_bounds_stalled_http_connection(self):
        # Keep module import time outside the short network deadline.
        importlib.import_module("mcp.client.streamable_http")
        closed = asyncio.Event()

        async def stalled_server(reader, writer):
            try:
                await reader.read()
            finally:
                writer.close()
                await writer.wait_closed()
                closed.set()

        server = await asyncio.start_server(stalled_server, "127.0.0.1", 0)
        port = server.sockets[0].getsockname()[1]
        try:
            with self.assertRaisesRegex(RuntimeError, "connection or verification timed out.*retry"):
                await asyncio.wait_for(
                    run_verification("local-test-token", timeout=0.5,
                                     endpoint=f"http://127.0.0.1:{port}/mcp"),
                    timeout=2,
                )
            await asyncio.wait_for(closed.wait(), timeout=2)
        finally:
            server.close()
            await server.wait_closed()

    async def assert_bounded_session(self, stall_tool):
        importlib.import_module("mcp.client.streamable_http")
        writers = set()
        handlers = set()
        methods = set()
        baseline = asyncio.all_tasks()

        async def server_handler(reader, writer):
            writers.add(writer)
            handlers.add(asyncio.current_task())
            try:
                while True:
                    header = await reader.readuntil(b"\r\n\r\n")
                    lines = header.decode().split("\r\n")
                    method = lines[0].split()[0]
                    methods.add(method)
                    headers = dict(line.lower().split(": ", 1) for line in lines[1:] if ": " in line)
                    body = await reader.readexactly(int(headers.get("content-length", 0)))
                    if method == "GET":
                        writer.write(b"HTTP/1.1 200 OK\r\nContent-Type: text/event-stream\r\n\r\n: waiting\n\n")
                        await writer.drain()
                        await reader.read()
                        return
                    if method == "DELETE":
                        await reader.read()
                        return
                    message = json.loads(body)
                    methods.add(message["method"])
                    if message["method"] == "tools/call" and stall_tool:
                        await reader.read()
                        return
                    if "id" not in message:
                        writer.write(b"HTTP/1.1 202 Accepted\r\nContent-Length: 0\r\n\r\n")
                    else:
                        if message["method"] == "initialize":
                            result = {
                                "protocolVersion": "2025-03-26",
                                "capabilities": {"tools": {}},
                                "serverInfo": {"name": "local", "version": "1"},
                            }
                        elif message["method"] == "tools/list":
                            result = {"tools": [{
                                "name": "get_status",
                                "inputSchema": {"type": "object"},
                            }]}
                        else:
                            result = {"content": [], "structuredContent": {"activeAccount": {"id": "local"}}}
                        payload = json.dumps({"jsonrpc": "2.0", "id": message["id"], "result": result}).encode()
                        writer.write(b"HTTP/1.1 200 OK\r\nContent-Type: application/json\r\nMcp-Session-Id: local-session\r\n"
                                     + f"Content-Length: {len(payload)}\r\n\r\n".encode() + payload)
                    await writer.drain()
            except (asyncio.IncompleteReadError, ConnectionError):
                pass
            finally:
                writer.close()
                await writer.wait_closed()
                writers.discard(writer)
                handlers.discard(asyncio.current_task())

        server = await asyncio.start_server(server_handler, "127.0.0.1", 0)
        port = server.sockets[0].getsockname()[1]
        operation = asyncio.create_task(run_verification(
            "local-test-token", timeout=0.25, endpoint=f"http://127.0.0.1:{port}/mcp"))
        started = time.monotonic()
        try:
            # asyncio.wait observes the bound without trying to cancel a stuck cleanup.
            done, _ = await asyncio.wait({operation}, timeout=0.75)
            self.assertIn(operation, done, "public function exceeded its end-to-end bound")
            with self.assertRaisesRegex(RuntimeError, "timed out.*retry"):
                operation.result()
            self.assertLess(time.monotonic() - started, 0.75)
            self.assertIn("tools/call", methods)
            self.assertIn("GET", methods)
            if not stall_tool:
                self.assertIn("DELETE", methods)
            for _ in range(20):
                await asyncio.sleep(0.01)
            self.assertFalse(writers, "verification left network connections open")
            self.assertFalse(asyncio.all_tasks() - baseline - handlers,
                             "verification left SDK tasks running")
        finally:
            for writer in list(writers):
                writer.close()
            if not operation.done():
                operation.cancel()
            await asyncio.gather(operation, return_exceptions=True)
            await asyncio.gather(*handlers, return_exceptions=True)
            server.close()
            await server.wait_closed()

    async def test_closes_stalled_tool_and_get_stream(self):
        await self.assert_bounded_session(stall_tool=True)

    async def test_closes_stalled_delete_and_get_stream(self):
        await self.assert_bounded_session(stall_tool=False)


if __name__ == "__main__":
    unittest.main()
