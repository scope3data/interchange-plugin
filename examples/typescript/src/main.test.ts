import assert from "node:assert/strict";
import { createServer } from "node:http";
import type { Socket } from "node:net";
import { setTimeout as delay } from "node:timers/promises";
import test from "node:test";

import {
  connectAndVerify,
  verifyApostraAccount,
  type ToolClient,
} from "./main.js";

test("verifies the account with one read-only call", async () => {
  const calls: string[] = [];
  const client: ToolClient = {
    async callTool(input) {
      calls.push(input.name);
      return {
        structuredContent: {
          activeAccount: { id: "buyer-123", kind: "buyer" },
        },
      };
    },
  };

  const status = await verifyApostraAccount(client);

  assert.deepEqual(calls, ["get_status"]);
  assert.deepEqual(status, {
    activeAccount: { id: "buyer-123", kind: "buyer" },
  });
});

test("fails closed when get_status does not return structured content", async () => {
  const client: ToolClient = {
    async callTool() {
      return { isError: true };
    },
  };

  await assert.rejects(
    verifyApostraAccount(client),
    /Apostra account verification failed/,
  );
});

test("cancels a stalled verification call", async () => {
  let signal: AbortSignal | undefined;
  const client: ToolClient = {
    callTool(_input, _schema, options) {
      signal = options?.signal;
      return new Promise(() => {});
    },
  };
  await assert.rejects(verifyApostraAccount(client, 20), /timed out.*retry/);
  assert.equal(signal?.aborted, true);
});

test("bounds a stalled HTTP connection", { timeout: 2000 }, async () => {
  const server = createServer(() => {});
  await new Promise<void>((resolve) => server.listen(0, "127.0.0.1", resolve));
  const address = server.address();
  assert.ok(address && typeof address !== "string");
  try {
    await assert.rejects(
      connectAndVerify(
        "local-test-token",
        50,
        `http://127.0.0.1:${address.port}/mcp`,
      ),
      /timed out.*retry/,
    );
  } finally {
    server.closeAllConnections();
    await new Promise<void>((resolve) => server.close(() => resolve()));
  }
});

for (const stallTool of [true, false]) {
  test(
    `closes all HTTP connections when ${stallTool ? "tools/call" : "DELETE teardown"} stalls`,
    { timeout: 3000 },
    async () => {
      const sockets = new Set<Socket>();
      const methods = new Set<string>();
      const server = createServer(async (request, response) => {
        methods.add(request.method ?? "");
        if (request.method === "GET") {
          response.writeHead(200, { "content-type": "text/event-stream" });
          response.write(": waiting\n\n");
          return;
        }
        if (request.method === "DELETE") return;
        let body = "";
        for await (const chunk of request) body += chunk;
        const message = JSON.parse(body);
        methods.add(message.method);
        if (message.method === "tools/call" && stallTool) return;
        if (message.id === undefined) {
          response.writeHead(202).end();
          return;
        }
        if (message.method === "initialize" && stallTool) await delay(120);
        response.writeHead(200, {
          "content-type": "application/json",
          "mcp-session-id": "local-session",
        });
        response.end(
          JSON.stringify({
            jsonrpc: "2.0",
            id: message.id,
            result:
              message.method === "initialize"
                ? {
                    protocolVersion: "2025-03-26",
                    capabilities: { tools: {} },
                    serverInfo: { name: "local", version: "1" },
                  }
                : {
                    content: [],
                    structuredContent: { activeAccount: { id: "local" } },
                  },
          }),
        );
      });
      server.on("connection", (socket) => {
        sockets.add(socket);
        socket.on("close", () => sockets.delete(socket));
      });
      await new Promise<void>((resolve) =>
        server.listen(0, "127.0.0.1", resolve),
      );
      const address = server.address();
      assert.ok(address && typeof address !== "string");
      const started = performance.now();
      try {
        await assert.rejects(
          connectAndVerify(
            "local-test-token",
            250,
            `http://127.0.0.1:${address.port}/mcp`,
          ),
          /timed out.*retry/,
        );
        assert.ok(
          performance.now() - started < 750,
          "public function exceeded its end-to-end bound",
        );
        assert.ok(methods.has("tools/call"));
        assert.ok(methods.has("GET"));
        if (!stallTool) assert.ok(methods.has("DELETE"));
        // Allow the server to observe remote socket closure, without closing it ourselves.
        for (let i = 0; i < 10; i++) await delay(5);
        assert.equal(
          sockets.size,
          0,
          "verification left network connections open",
        );
      } finally {
        for (const socket of sockets) socket.destroy();
        await new Promise<void>((resolve) => server.close(() => resolve()));
      }
    },
  );
}
