# Apostra developer marketplace

Connect a coding agent to Apostra, verify the account, and build an advertising
workflow. Start with `apostra-developer`; install the narrower operating
packages only when you need them. Packages do not grant account permissions.
Apostra OAuth and server-side entitlements remain authoritative.

## Install in Codex

```sh
codex plugin marketplace add scope3data/interchange-plugin
codex plugin add apostra-developer@interchange-plugin
```

The native plugin installs both the `build-with-apostra` skill and the Apostra
MCP connection. Complete OAuth when prompted, then ask Codex: "Verify my
Apostra account and help me build a seller discovery prototype."

## Install in Claude Code

```
/plugin marketplace add scope3data/interchange-plugin
/plugin install apostra-developer@interchange-plugin
```

Complete OAuth when prompted. Never paste API keys or provider credentials
into a prompt.

## Install the skill in another compatible agent

```sh
npx skills add scope3data/interchange-plugin \
  --skill build-with-apostra \
  --yes
```

This route installs the instructions only. Connect the agent's MCP client to
`https://api.interchange.io/mcp/v3`, complete OAuth, and run the read-only
`get_status` check before building.

## Packages

| Package | Purpose | Current canonical skills |
|---|---|---|
| `apostra-developer` | Plan, run, automate, and report on advertising across sellers, or build those jobs into an application. | `build-with-apostra@1.0.0` |
| `amc-listing` | Build and maintain an Agentic Media Company listing in Interchange. | MCP access; workflow skill forthcoming |
| `amc-merchandising` | Merchandise an Agentic Media Company's inventory and products in Interchange. | MCP access; workflow skill forthcoming |
| `amc-distribution` | Prepare and distribute an Agentic Media Company through supported agent channels. | `publish-an-openai-app@1.0.0` |
| `amc-campaign-management` | Operate seller-side campaigns and delivery in Interchange. | MCP access; workflow skill forthcoming |
| `buyer-account-setup` | Prepare an Interchange buyer account for campaign execution. | `get-account-ready-to-buy@1.0.0` |
| `buyer-campaign-management` | Discover sellers, create campaigns, request proposals, and manage delivery. | `buy-from-seller@1.3.0`, `set-up-a-campaign@1.3.0`, `set-up-an-event-source@1.0.0`, `manage-a-campaign@1.1.0` |
| `buyer-creative-management` | Prepare and inspect buyer creative inputs for campaign execution. | `inspect-tag-sheet@1.0.0`, `generate-campaign-creatives@1.0.0` |
| `buyer-reporting` | Inspect buyer campaign delivery and reporting in Interchange. | `set-up-an-event-source@1.0.0` |
| `sales-agent-testing` | Test a first-party or third-party AdCP sales agent with governed buyer workflows. | `test-sales-agent@1.5.1` |
| `amc-self-serve-buyer` | Bundle buyer workflows for an Agentic Media Company's own self-serve plugin. | `get-account-ready-to-buy@1.0.0`, `buy-from-seller@1.3.0`, `set-up-a-campaign@1.3.0`, `set-up-an-event-source@1.0.0`, `manage-a-campaign@1.1.0`, `inspect-tag-sheet@1.0.0`, `generate-campaign-creatives@1.0.0` |

`amc-self-serve-buyer` is the aggregate buyer package an Agentic Media
Company can bundle into its own self-serve plugin. `sales-agent-testing`
is the package for first-party or third-party agent validation.

Skill files are composed from the canonical, versioned Interchange skill
registry. When a registry current-version pointer or referenced asset changes,
the source workflow opens a reviewed sync PR for this repository.

Every durable change remains confirmation-gated by the underlying Apostra
tool contract. Build guides live at https://docs.interchange.io/v3/overview.

## License

Licensed under the [Apache License, Version 2.0](LICENSE). Copyright 2026 Scope3 PBC.

## About this repository

This is a generated public mirror. Do not hand-edit it: the next reviewed sync
will overwrite local changes. `SOURCE_DIGEST` records the composed content
checkpoint.
