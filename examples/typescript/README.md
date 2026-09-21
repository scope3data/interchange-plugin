# Apostra TypeScript starter

This Node.js 20.18.1+ starter connects to Apostra's v3 MCP endpoint with a scoped
access token and makes one read-only `get_status` call. The 15-second deadline
covers connection, verification, and session teardown. The starter closes its
HTTP connections before returning. On timeout, check network access and the MCP
endpoint, then retry. For browser OAuth, use the
[direct MCP quickstart](https://docs.interchange.io/v3/quickstart).

```sh
npm install
APOSTRA_ACCESS_TOKEN='your-scoped-token' npm start
npm test
```

Keep the token in an environment variable or secret manager. Do not commit it.
After verification works, follow the
[build-an-agent guide](https://docs.interchange.io/v3/build-an-agent) to add
tool discovery, durable checkpoints, confirmation gates, and retries.
