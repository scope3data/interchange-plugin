# Connect, authenticate, and verify

Read the public [quickstart](https://docs.interchange.io/v3/quickstart) and
[MCP client setup](https://docs.interchange.io/v3/client-setup) for current
host-specific commands. Keep the public repository and protocol identifiers
spelled as published even when they retain `interchange` in their names.

## Interactive coding agent

1. Inspect existing plugins and remote MCP connections. Reuse an existing
   working V3 connection when it serves the intended account.
2. Set up a direct MCP connection using the host's supported remote streamable
   HTTP configuration: `https://api.interchange.io/mcp/v3`. If the skill was
   installed through `npx skills`, this connection is still a separate step.
   Skill dependencies describe the connection; do not assume the host
   automatically installed it.
3. Native `apostra-developer` plugin installation from the
   `scope3data/interchange-plugin` marketplace is pending mirror publication
   and fresh-install verification. Use direct MCP until both are complete;
   do not recommend installing the unpublished package.
4. Let the host perform OAuth discovery and credential storage. Do not ask
   the user to paste a token into chat or a repository file.
5. Call `get_status` first. Record the active account ID, account kind,
   readiness, and returned next actions without printing credential material.
6. Inspect `tools/list`. Use a returned account ID if an account switch is
   needed, then call `get_status` again. An account ID is not a seller ID.
7. Make one scoped read appropriate to the task. A buyer's seller discovery
   prototype can use `search` with `kind: "seller"`; a seller integration can
   start with its inventory sources. Use the current schema and retain the
   structured response. An empty result is a valid read, not sample data.

Do not modify billing, connections, campaigns, or account settings to make an
installation check pass. Explain a returned readiness blocker and proceed
only with the work the account can perform. If OAuth cannot complete in the
current host, give the exact connection action and finish locally testable work.

## Deployed application

Read [authentication](https://docs.interchange.io/v3/authentication) and its
[credential reference](https://docs.interchange.io/v2/authentication) before
selecting credentials. Choose supported user authorization or a documented
backend credential based on who the software represents. Store secrets in the
deployment's secret manager and expose only environment-variable names in
the project.

The interactive MCP OAuth token is bound to the exact MCP resource. Do not
copy it into a REST client or treat it as a deployable application credential.
Backend OAuth client credentials and an independently registered buyer agent
have different authority; consult the agent-management guide when independent
identity is required. Registration alone grants no advertiser access.

For a REST-only job, verify its credential with a documented read on the exact
account resource before any write. Do not force a second MCP integration into
an otherwise deterministic REST service only to run `get_status`.

## Retrieve facts as needed

With MCP available, find the relevant public documentation using
`search({ sources: ["docs"], query: "..." })`. Read the selected `document`
through that same tool before implementing its contract. Use returned citation
URLs in the handoff. Without MCP, use the public pages directly.

Do not invent a `/api/v3` equivalent of an MCP tool. Runtime schemas determine
which operations the active account can call; a documentation match, visible
tool, or successful login does not grant authority.
