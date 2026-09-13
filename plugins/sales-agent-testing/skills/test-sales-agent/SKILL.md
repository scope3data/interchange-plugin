---
name: test-sales-agent
description: Test an AdCP Sales Agent or Interchange Storefront through ordinary V3 buyer tools. Use when a seller asks to test its own supply, replay a brief, verify Product discovery, stage a no-spend sandbox media buy, exercise a creative handoff, or collect an evidence-oriented validation report without legacy test wrappers.
---

# Test a Sales Agent

Exercise the Agent through the same `/mcp/v3` tools an ordinary buyer uses. Treat sandbox as a safety property of the Advertiser and its resources, not as a separate test API.

Read [references/scenarios.json](references/scenarios.json) before selecting a scenario. Read [references/fixtures.json](references/fixtures.json) only when the user has not supplied a brief or creative.

## Guardrails

- Use only named tools from `https://api.interchange.io/mcp/v3`. Never call `api_call`, `run_buyer_infra_test_campaign`, `plan_inventory_source_test_campaign`, or `execute_inventory_source_test_campaign`.
- Keep mutations inside an Advertiser returned with `sandbox: true`. Retain that structured creation result through staging and launch; sandbox is immutable, and the integrated V3 write path re-proves the Campaign's own-supply scope server-side. Stop if the run loses that evidence or changes Advertiser or Campaign identity.
- Target only the authenticated Media Company's own Seller. Copy Seller, Product, Proposal, query, and revision identifiers, plus Source and Sales Agent identifiers when returned, exactly from structured tool responses.
- When the user names an Agent or Source, use only Products attributed to that exact returned identifier. Report `not_attributable` if the response cannot prove the target.
- Never infer a pass from prose. Retain structured results and server-returned request, trace, activity, execution, and correlation identifiers.
- Ask for explicit confirmation before `save_media_buy` and before `save_campaign` activates a Campaign. State that the action is sandbox/no-spend.
- Never call a run certified. Report observed, failed, and unexercised assertions plus cleanup status. Interchange independently decides certification from trusted evidence.
- Use fictional synthetic fixtures only. Never persist customer creatives or confidential briefs as fixtures.
- Give each run fresh `scope3/run-id` and `scope3/workflow-id` values. Attach them to every request with `scope3/skill-id: test-sales-agent@1.5.1`, the exact `scope3/scenario-id`, and current `scope3/step-id` in `_meta`. On `search` or `get` calls for `seller` or `connection`, also attach `scope3/sellers-activation-state-version: 2`; it negotiates the truthful activation-state response shape and grants no authority. Keep run and workflow values through cleanup. They are correlation hints, not authority or evidence by themselves.
- Apply each step's timeout, attempt ceiling, dependency, evidence allowlist, and cleanup declaration from the structured scenario. Always run cleanup in reverse mutation order, even after failure or cancellation.
- In `brief-discovery`, use `save_connection` only to set `advertiserActivation` for the exact resolved Seller and run-owned sandbox Advertiser. Require its Seller control-plane readback to confirm that exact Advertiser, decision, and effective state; request intent alone is not evidence. Never change account selection. Restoring and rereading `DEFAULT` is mandatory cleanup.

## Select a scenario

1. Call `get_status` and resolve any returned account action.
2. Resolve the organization's own Seller with `search({kind: "seller"})` and retain the exact returned Seller `id`.
3. Choose the least-mutating applicable scenario:
   - `brief-discovery` observes Products for one brief without staging a MediaBuy.
   - `own-supply-transaction` stages and activates a sandbox purchase after confirmation.
   - Treat creative handoff as unavailable while every matching fixture has `executable: false`.
4. State the selected scenario, mutations, evidence boundary, and cleanup before execution.

## Enforce terminal Product provenance

A Product seen before discovery completes is provisional and cannot authorize a buy.

1. Read the Seller Product catalog and retain its `productQueryId`, catalog revision and completeness marker, Products, and returned provenance fields.
2. Follow continuation metadata within the scenario bounds. Accept a catalog for selection only when `catalog.ext.interchange.results_complete` is `true`.
3. Select a Product from that terminal response. Retain one indivisible tuple: Product ID, Seller ID, Product query ID, Product query revision, and Source ID, Sales Agent ID, and pricing option ID when present.
4. Immediately before `save_media_buy`, prove the selected Product still exists in the terminal catalog with the exact same tuple. Never merge a stale Product ID with another Product's Seller, Source, Sales Agent, query, revision, or price.
5. If the Product disappears, any tuple field changes, discovery expires, or completeness is not proven, stop before mutation and report `product_disappeared` with the safe catalog diagnostics. Re-run discovery only as a new selection; never replay the stale ID.

## Run brief discovery

1. Create a fresh run-owned sandbox Advertiser with `save_advertiser`.
2. Call `save_connection` for the exact resolved Seller with `advertiserActivation: { advertiserId, decision: "ENABLED" }`. This temporary advertiser preference does not change account selection.
3. Create a draft Campaign with `save_campaign` using the supplied or synthetic brief, small budget, bounded dates, and a unique idempotency key.
4. Read the own Seller with `get({kind: "seller", id, advertiserId, include: ["products"]})` using the exact Seller and sandbox Advertiser IDs.
5. Enforce terminal Product provenance. Present exact Products, prices, canonical formats, returned ownership, partial failures, and completion state.
6. Do not call `save_media_buy`. Archive the created Campaign, call `save_connection` for the same Seller and Advertiser with decision `"DEFAULT"`, then archive the Advertiser. Reverse cleanup is mandatory after success, failure, or cancellation.

This scenario proves only discovery for the exact brief and observed implementation.

## Run an own-supply transaction

Follow the versioned `own-supply-transaction` discovery steps, then:

1. Present the terminal Product tuple and request confirmation.
2. Call `save_media_buy` with that exact tuple. Use the terminal `productQueryId` as the idempotency key. Refuse stale or reconstructed provenance.
3. Create only a metadata Creative with `save_creative` while no approved executable asset exists. Do not claim sync or launch readiness from record creation.
4. Read the Campaign with `get`, including MediaBuys and Creatives. Verify the staged objects belong to the sandbox Campaign.
5. Preview activation with `save_campaign`. Require `action: "pending_confirmation"`, show `launch`, request confirmation, then activate using `confirmLaunch: true`, the returned `campaign.revision`, and a fresh idempotency key.
6. Read the Seller timeline with `get({kind: "media_buy", id, buyerCustomerId})`, using the staged MediaBuy ID and the current `get_status` account ID to disambiguate the own-supply buyer. Require the returned `mediaBuyId`, `stages`, and `legs`. Call `get_delivery` only with `report: "campaign_delivery"`, a bounded date range, and the exact MediaBuy filter.
7. Archive the Creative, then the containing Campaign, then the Advertiser through ordinary V3 lifecycle fields. V3 does not expose independent MediaBuy cancellation; the Campaign owns its cleanup, so report the exact MediaBuy ID and this limitation rather than inventing a cancellation call.

`pending_creatives` is not creative-handoff success. Creative propagation requires an approved executable fixture and seller-side readback of the exact Creative identity; version 1.5.1 deliberately provides no such asset.

## Return evidence

Return a compact report containing the target Seller and observed Agent/Source; scenario and skill version; fixture IDs; ordered V3 calls and outcomes; exact terminal Product tuple; returned server correlation IDs; affected Campaign, MediaBuy, and Creative IDs; assertions passed, failed, and unexercised; bounded seller-side status or delivery; and reverse-order cleanup results, including advertiser activation restoration.

Never include credentials, signed URLs, confidential brief content, raw customer creative payloads, or another tenant's identity.
