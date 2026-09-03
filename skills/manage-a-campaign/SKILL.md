---
name: manage-a-campaign
description: Review and manage an existing Interchange buyer campaign. Use when a user asks about campaign status, delivery, spend, pacing, an existing campaign's creatives, blockers, launch, pause, archive, budget or flight changes, troubleshooting, or what needs attention.
---

# Manage a Campaign

Ground every recommendation and change in the current campaign, delivery, and creative records from the attached Interchange V3 buyer server.

## Workflow

1. Call `get_status` and confirm the active buyer account.
2. Use `search` to find the intended campaign and `get` with `include: ["mediaBuys", "creatives"]` to read its current revision, phase, flight, budget, media buys, creatives, and blockers. Ask the user to choose if more than one campaign matches.
3. For delivery questions, call `get_delivery` with `report: "campaign_delivery"`, the narrowest useful campaign or media-buy filters, and an explicit inclusive UTC `range` no longer than 90 days. Choose only needed metrics and dimensions. Follow pagination with the unchanged query and returned cursor.
4. Report delivery evidence with its denomination, freshness, finality, missing values, and truncation. Distinguish observed facts from recommendations; do not turn missing measurement into zero performance.
5. Inspect related creatives or creative collections with `search` and `get` when readiness or delivery indicates a creative issue. Do not claim approval, attachment, or provider propagation unless returned evidence proves it.
   - `save_creative` manages only creative-manifest metadata: name, message, and format kind. If the request means uploading or attaching a file, URL, or external asset, stop and explain that the current V3 tool cannot perform it.
6. Explain what needs attention and propose the smallest supported change. Before any write, show the exact target, current revision, requested fields, expected effect, and material risk.
7. After confirmation:
   - Use `save_campaign` for supported campaign changes with the current `expectedRevision` and a stable idempotency key. Reuse that key only when retrying the exact same intent.
   - To launch, first call `save_campaign` with `desiredPhase: "active"` and without `confirmLaunch`. Show the returned preview, obtain confirmation, then call it again with `confirmLaunch: true`, the preview's revision as `expectedRevision`, and the required idempotency key.
   - Use `save_creative` or `save_creative_collection` for confirmed creative changes with exact IDs.
   - Treat campaign or creative archival and financial changes as destructive; require explicit confirmation immediately before the call.
8. Read the updated campaign and relevant delivery evidence again. Report the observed result, warnings, partial writes, downstream errors, and unresolved actions.

## Safety rules

- Never invent IDs, revisions, metrics, statuses, prices, or causal explanations.
- Do not silently retry a non-idempotent mutation. Re-read state before deciding whether a retry is safe.
- Never broaden a requested budget, flight, seller, creative, or campaign change.
- Do not claim success from prose alone; require a successful tool result and verify the resulting state.
- If the requested operation is unavailable in the current tool catalog, state the boundary and offer the nearest supported read or next action.
- Campaign cancellation and unarchiving are not supported by the current V3 tool. Do not imply that pause, archive, and cancellation are interchangeable.

If the user needs buyer-account prerequisites, hand off to the account-readiness skill. If the user needs a new draft campaign, proposal round, or first media-buy staging, hand off to the campaign-setup skill.
