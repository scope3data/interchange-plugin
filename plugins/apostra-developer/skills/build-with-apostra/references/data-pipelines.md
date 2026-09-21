# Bring data in and get data out

Identify the source system, destination, advertiser, data shape, and expected
freshness before choosing an API. Reuse an existing scheduler, warehouse, or
secret manager. The integration's local tests should validate mapping and
retry behavior without sending customer data.

## Event ingestion handoff

Read [bring data in](https://docs.interchange.io/v3/bring-data-in) and retrieve
the applicable `set-up-an-event-source` skill through the active account's
`get` tool before source mutations.

1. Read the advertiser's measurement sources and reuse a matching source
   when appropriate. Native provider source IDs must come from that provider's
   authorized connection; a partner name alone does not establish a connector.
2. Use the supported source-configuration workflow. Treat its returned
   `setup` object as an installation handoff, not proof of a running sender.
3. Build the sender against the documented ingestion contract. Per-event
   records and pre-aggregated measurement outcomes have different endpoints;
   select by data shape, not by which example is shortest. Use V2 REST for
   runtime event ingestion where the V3 catalog has no equivalent.
4. Define stable event IDs, time-zone handling, field mapping, bounded
   retries, and deduplication. Test the mapping with synthetic events and
   verify partial failures are surfaced rather than counted as accepted.
5. When a live test is authorized, use the documented test-event mechanism,
   inspect its receipt, and read the source health. Preserve the difference
   between configuration saved, test accepted, and production events flowing.
6. Attach conversion tracking to a campaign only when requested. Use the
   source's raw `eventSourceId` for the campaign goal; the `event:`-prefixed
   measurement-source noun ID addresses a different object.

Do not send production events to prove installation or claim that `not_seen`
means a source is unusable. Return the sender's next command and the exact
observable receipt or health state still needed.

## Reporting pipeline

Read [build a reporting pipeline](https://docs.interchange.io/v3/reporting-pipeline)
and its linked contract guides. Choose the
output the developer actually needs:

| Need | Integration to build |
| --- | --- |
| An agent answers a campaign-performance question | V3 `get_delivery` with explicit metrics, dimensions, window, and scope |
| A backend pulls aggregate metrics on a schedule | The documented V2 reporting REST contract and the application's scheduler |
| A one-off aggregate file | The documented CSV export; fetch its signed URL through the consuming backend |
| Recurring log-level data in owned cloud storage | Data Delivery credential and Output configuration with an observed destination probe |

For agent reports, read the current `get_delivery` schema and
[delivery workflow](https://docs.interchange.io/v2/setup/v3/buyer-workflows#7-query-campaign-delivery).
Follow pagination and preserve unavailable metrics, currency, and period
information. Do not reinterpret missing data as zero or sum incompatible
currencies. Seller-reported delivery and independently measured events answer
different questions; name the source in the result.

For a scheduled aggregate pull, implement this small pipeline:

1. Resolve and read the exact authorized advertiser or campaign.
2. Choose explicit UTC date windows and a repeatable output key that includes
   scope, date, dimensions, and currency as appropriate for the returned shape.
3. Validate each response and upsert the same window on retry. Delivery can
   arrive or be corrected later, so choose and document a bounded lookback
   instead of permanently closing yesterday after its first read.
4. Advance the checkpoint only after the destination write succeeds. Test a
   repeated window and a destination failure to prove recovery does not lose
   or double-count rows.
5. Record last successful fetch, source period, and destination write time.
   An empty response alone does not prove the source is current.

For recurring Data Delivery, use the documented cloud-access handoff, read
current configuration, preserve unrelated entries in full-replacement arrays,
register the destination, observe its validation status, and configure the
requested Outputs. The cloud owner grants IAM access. A validated probe proves
destination access; report the pipeline as delivering only after the intended
output is observed. Do not invent an empty file when no source data exists.

Keep signed export URLs and cloud credentials out of logs, chat, fixtures, and
screenshots. A reporting export is sensitive data even after it is downloaded.
Machine notifications can wake an application where supported; they do not
replace the reporting records. Retrieve the relevant notification guide before
implementing a callback rather than inventing a generic V3 webhook tool.
