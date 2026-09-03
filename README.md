# Interchange

Plan, buy, and manage advertising through the Interchange V3 MCP server.

## Install

```
/plugin marketplace add scope3data/interchange-plugin
/plugin install interchange
```

Complete OAuth when prompted. Never paste API keys or provider credentials
into a prompt — provider authorization uses the browser URLs Interchange
returns.

## What's included

- `.claude-plugin/plugin.json` — the Claude Code / Cowork plugin manifest.
- `.claude-plugin/marketplace.json` — lets this repo be added directly as a
  marketplace (`/plugin marketplace add`, above).
- `.mcp.json` — the remote Interchange V3 MCP connection (OAuth, no keys).
- `skills/` — three canonical buyer skills: get an account ready to buy,
  set up a campaign, and manage a live campaign.
- `assets/` — the directory and composer icons.
- `LICENSE` — Apache License, Version 2.0 (see License, below).

Every durable change made through these skills remains confirmation-gated
by the underlying Interchange tool contract.

## Documentation

Full product documentation lives at https://docs.interchange.io.

## License

Licensed under the [Apache License, Version 2.0](LICENSE). Copyright 2026 Scope3 PBC.

## About this repository

This repository is a generated mirror. Its content is composed and synced
from Scope3's internal monorepo by an automated workflow, and every sync is
reviewed by a human before it reaches `main` — do not hand-edit files here,
they will be overwritten by the next sync. `SOURCE_DIGEST` at the repo
root records the content checkpoint of the last sync.
