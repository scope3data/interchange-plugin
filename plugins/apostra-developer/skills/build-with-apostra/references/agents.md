# Build an application or agent

Read [build an agent](https://docs.interchange.io/v3/build-an-agent)
and the [buyer workflow](https://docs.interchange.io/v2/setup/v3/buyer-workflows)
for the requested part of the loop. Apostra keeps the canonical campaign,
transaction, and delivery state. The application may keep IDs, approvals,
checkpoints, and its own data without rebuilding seller-specific adapters.

## Seller discovery prototype

Build a read-only slice first:

1. Complete connection verification and retain the account kind.
2. Inspect the current `search` schema and search `kind: "seller"` with the
   developer's query. Preserve each returned seller ID and name.
3. Follow the returned pagination contract within an explicit result/page
   bound. Distinguish no matches, partial results, account denial, and a tool
   error. Never turn an MCP `isError` result into a successful empty list.
4. Present the returned records in the project's existing CLI or UI. Keep the
   MCP transport behind a small interface so fixture tests need no account.
5. Run a deterministic test covering successful discovery and a meaningful
   failure or continuation case. Then run the read-only live example when
   credentials are available and report its result separately.

Discovery does not require creating an advertiser, campaign, seller connection,
or media buy. Requesting live proposals is a later workflow that requires its
own campaign context; do not smuggle it into this prototype.

The public TypeScript and Python starters are pending mirror publication and
fresh-install verification. Build the read-only example using the
[direct MCP connection](connection.md) and current runtime schema.
Adapt the example to the repository's package manager and test runner. Do not
overwrite existing files to reproduce a blank-repository example.

## Connect a seller

First establish whether the developer means connecting a buyer to an existing
seller or publishing their own inventory. Read the applicable
[buyer workflow](https://docs.interchange.io/v2/setup/v3/buyer-workflows) or
[seller workflow](https://docs.interchange.io/v2/setup/v3/seller-workflows).

Resolve an existing seller through the authenticated catalog and inspect the
returned connection/readiness state. Follow the specific supported connection
action and human authorization handoff. A website URL or guessed ID is not a
seller identity, provider grant, or execution-ready connection. For owned
inventory, follow the seller's source, product, and publication workflow rather
than creating a buyer connection as a substitute.

## Durable buyer-agent loop

Choose the hybrid model when an agent makes decisions but the application
must resume after a process restart:

1. Keep the advertiser, draft campaign, discovery execution, product query,
   selected offers, creative versions, media buys, and returned revisions in a
   durable store. Store approval records alongside the exact object revision.
2. Drive the workflow from fresh reads. Use the current catalog and buyer
   guide for typed saves and `request_proposals`; preserve returned qualified
   identifiers without reconstructing them.
3. Persist an asynchronous request's returned handle before scheduling a
   continuation. Poll that execution and follow result cursors within bounded
   retries. A restart resumes the saved operation; it does not create another
   proposal round with a fresh key.
4. Make the application enforce the confirmation boundary. Preview campaign
   launch with `save_campaign`, present the returned launch plan, and obtain
   the authorized user's decision before the separate confirmation call. Use
   the returned revision and each call's documented idempotency semantics.
5. On a conflict, timeout, or partial-write response, re-read persisted state
   before deciding whether to retry. Do not infer launch from staging or from
   a transport-level success.
6. Query delivery for an explicit scope and window. Keep Apostra report and
   object references in the orchestrator; build a separate warehouse only
   when the developer's data requirements call for one.

Test a restart between scheduling and completion, duplicate delivery of a
workflow event, and a changed revision between preview and confirmation.
Tests must prove the application does not duplicate the operation or launch
an unapproved revision. Default tests use fixtures and never buy media.

## Give independent software an identity

An interactive coding agent using a user's connection is not automatically an
installed buyer agent. Register only when the software needs its own identity,
credentials, advertiser grants, and lifecycle.

Read [manage buyer agents](https://docs.interchange.io/v2/setup/buyer-agent-credentials)
before implementing registration or access. Where advertised by the current
catalog, `save_buyer_agent` supports external-agent management under its
direct-administrator boundary. Use the documented console or REST path for
controls absent from V3. Keep identity creation, credential provisioning,
advertiser grants, and machine-notification setup as separate outcomes.
Never put one-time credential secrets in chat, generated source, or test
fixtures. Do not promise a hosted runtime merely because registration exists.
