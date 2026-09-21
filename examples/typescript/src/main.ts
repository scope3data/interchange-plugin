import { Client } from "@modelcontextprotocol/sdk/client/index.js";
import { StreamableHTTPClientTransport } from "@modelcontextprotocol/sdk/client/streamableHttp.js";
import { Agent } from "undici";

export const IO_TIMEOUT_MS = 15_000;

export const APOSTRA_MCP_URL = "https://api.interchange.io/mcp/v3";

export interface ToolClient {
  callTool(
    input: { name: string; arguments: Record<string, unknown> },
    schema?: undefined,
    options?: { signal: AbortSignal; timeout: number },
  ): Promise<Record<string, unknown>>;
}

export async function verifyApostraAccount(
  client: ToolClient,
  timeoutMs = IO_TIMEOUT_MS,
): Promise<unknown> {
  const result = await withDeadline(
    (signal) =>
      client.callTool({ name: "get_status", arguments: {} }, undefined, {
        signal,
        timeout: timeoutMs,
      }),
    timeoutMs,
  );
  if (result.isError || result.structuredContent === undefined) {
    throw new Error("Apostra account verification failed");
  }
  return result.structuredContent;
}

async function withDeadline<T>(
  operation: (signal: AbortSignal) => Promise<T>,
  timeoutMs: number,
): Promise<T> {
  const controller = new AbortController();
  let timer: ReturnType<typeof setTimeout> | undefined;
  const deadline = new Promise<never>((_, reject) => {
    timer = setTimeout(() => {
      const error = new Error(
        "Apostra connection or verification timed out. Check network access and the MCP endpoint, then retry.",
      );
      controller.abort(error);
      reject(error);
    }, timeoutMs);
  });
  try {
    return await Promise.race([operation(controller.signal), deadline]);
  } finally {
    clearTimeout(timer);
  }
}

export async function connectAndVerify(
  token: string,
  timeoutMs = IO_TIMEOUT_MS,
  endpoint = APOSTRA_MCP_URL,
): Promise<unknown> {
  const url = new URL(endpoint);
  const lifetime = new AbortController();
  const timeoutError = new Error(
    "Apostra connection or verification timed out. Check network access and the MCP endpoint, then retry.",
  );
  const timer = setTimeout(() => lifetime.abort(timeoutError), timeoutMs);
  const pending = new Set<Promise<Response>>();
  const dispatcher = new Agent();
  const client = new Client({
    name: "apostra-typescript-starter",
    version: "1.0.0",
  });
  const transport = new StreamableHTTPClientTransport(url, {
    requestInit: { headers: { Authorization: `Bearer ${token}` } },
    // The SDK replaces requestInit.signal. Bind the lifetime at the actual
    // fetch boundary so POST, GET, DELETE and cancellation notices all stop.
    fetch: (url, init) => {
      const options: RequestInit & { dispatcher: Agent } = {
        ...init,
        dispatcher,
        signal: AbortSignal.any([
          lifetime.signal,
          ...(init?.signal ? [init.signal] : []),
        ]),
      };
      const request = fetch(url, options);
      pending.add(request);
      void request.then(
        () => pending.delete(request),
        () => pending.delete(request),
      );
      return request;
    },
  });
  try {
    await client.connect(transport, {
      signal: lifetime.signal,
      timeout: timeoutMs,
    });
    const status = await verifyApostraAccount(client, timeoutMs);
    await transport.terminateSession();
    return status;
  } catch (error) {
    if (lifetime.signal.aborted) throw timeoutError;
    throw error;
  } finally {
    lifetime.abort();
    clearTimeout(timer);
    try {
      await client.close();
    } finally {
      // Own the pool: aborting fetch alone can leave replacement/idle sockets.
      // destroy() closes them locally, without waiting for the remote peer.
      await dispatcher.destroy();
      await Promise.allSettled(pending);
    }
  }
}

async function main(): Promise<void> {
  const token = process.env.APOSTRA_ACCESS_TOKEN;
  if (!token) throw new Error("Set APOSTRA_ACCESS_TOKEN before running");
  console.log(JSON.stringify(await connectAndVerify(token), null, 2));
}

if (import.meta.url === `file://${process.argv[1]}`) {
  await main();
}
