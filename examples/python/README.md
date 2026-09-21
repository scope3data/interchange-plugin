# Apostra Python starter

This Python 3.11+ starter connects to Apostra's v3 MCP endpoint with a scoped
access token and makes one read-only `get_status` call. Connection,
verification, and session teardown share a 15-second deadline. The starter
cancels SDK tasks and closes HTTP connections before returning. On timeout,
check network access and the MCP endpoint, then retry. For browser OAuth, use the
[direct MCP quickstart](https://docs.interchange.io/v3/quickstart).

```sh
python -m venv .venv
. .venv/bin/activate
pip install -r requirements.txt
APOSTRA_ACCESS_TOKEN='your-scoped-token' python main.py
python -m unittest test_main.py
```

Keep the token in an environment variable or secret manager. Do not commit it.
After verification works, follow the
[build-an-agent guide](https://docs.interchange.io/v3/build-an-agent) to add
tool discovery, durable checkpoints, confirmation gates, and retries.
