---
name: set-up-an-event-source
description: Set up or reuse advertiser conversion tracking when a buyer needs a social-platform source, website or app events, a server feed, CRM data, or a measurement partner.
---

# Set Up an Event Source

Use this workflow when a buyer wants to measure a conversion, attach conversion tracking to a campaign, or connect event data from a social platform or measurement partner.

## Establish the measurement job

1. Identify the advertiser and the conversion outcome the buyer wants to observe. Do not create a source until the advertiser is explicit.
2. Call `search` with `kind: "measurement_source"` and `filter.advertiserId`. Use the buyer's provider or outcome words as `query` when useful.
3. Reuse a source only when its name, `eventSourceId`, event types, and integration platform match the buyer's intent. Health is evidence, not an eligibility gate: a new source can be used while `not_seen`, but say that no event has arrived yet.

## Choose the source path

### Native social-platform source

Use an ID returned by the connected platform, product, or account flow. Never invent a pixel, form, channel, profile, or dataset ID. If no authorized native source is returned, stop and ask the buyer to connect or select the provider account that owns it.

Do not register a native platform source as if Interchange hosted it. Some products expose a built-in event-source sentinel in their execution template; copy that exact value only when the product declares it.

### Buyer or measurement-partner feed

Use `save_measurement_source` with `sourceType: "event"`, a stable buyer-assigned `eventSourceId`, a clear name, and the exact supported event types. Set `integrationPlatform` to the system that will send the events, such as the buyer's server, CRM, or measurement partner.

- For browser-originated data, list only the domains authorized to send it.
- For a server-to-server or partner feed, `allowedDomains: []` is valid.
- Add `mapping` when the source's fields differ from the accepted event shape. Define a stable event ID and deduplication rule before sending production data.
- Use `testEventCode` only when the sender can preserve it on test events.

The returned `setup` object is the installation handoff. Registration saves configuration; it does not install a tag, authorize a provider account, send historical data, or prove that events are flowing.

Billy Grace and other measurement partners follow this server-feed path unless connection discovery explicitly returns a native connector and its authorized source IDs. Do not claim a native connector from the provider name alone.

## Verify before claiming success

1. Read the exact source with `get`, passing the returned measurement-source `id` and `advertiserId`.
2. Report the health state plainly:
   - `not_seen`: configured, but no accepted event yet.
   - `receiving`: at least one event has been accepted.
   - `needs_attention`: the latest ingestion evidence is an error.
3. Do not convert `not_seen` into a failure or wait to create the campaign. Give the buyer the setup instructions and a concrete verification step.

## Attach it to a campaign

When the buyer wants conversion optimization, read the current campaign first. Then call `save_campaign` with the exact `eventSourceId` from the measurement source inside the intended event optimization goal. The measurement-source `id` begins with `event:` and addresses the V3 noun; campaign goals use the separate raw `eventSourceId` field.

Never attach a dangling or guessed ID. If the buyer chooses to proceed without conversion tracking, omit the conversion goal and state that the campaign will not optimize against that outcome.

## Safe updates and removal

Use the returned measurement-source `id` for changes. Send only changed fields. Archive only after confirming the buyer no longer needs the source; archiving makes existing campaign references stop resolving. Do not use archive as a way to rotate credentials or repair a mapping.

## Completion report

State which advertiser owns the source, whether it was reused or created, its raw campaign `eventSourceId`, current health, required setup action, and whether it was attached to a campaign. Keep native provider authorization, source registration, first-event receipt, and campaign attachment as separate facts.
