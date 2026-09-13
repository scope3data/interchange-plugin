---
name: inspect-tag-sheet
description: Inspect CSV, XLS, or XLSX advertising tag sheets locally with Interchange's versioned parser profile. Use when a buyer wants to preview how many creative rows the parser finds, diagnose an unrecognized sheet, or report a privacy-safe parser receipt without uploading creative tags.
---

# Inspect a tag sheet

Run the immutable offline inspector before uploading a tag sheet. It reads the workbook on the user's machine and prints only a sanitized parse receipt. It never executes formulas, tags, scripts, or network requests, and it never prints filenames, worksheet names, headers, placement names, tag markup, URLs, or cell values.

Read [references/parser-profile.json](references/parser-profile.json) to explain the versioned mappings. Read [references/scenarios.json](references/scenarios.json) before choosing a workflow.

## Guardrails

- Never paste, attach, or transmit the workbook to Interchange merely to inspect it.
- Download the inspector only from the immutable versioned URL below. If the host cannot execute a local command, give the user the command to run; do not claim that inspection occurred.
- Treat exit code `0` as “parsed,” not “correct.” Compare `rowCount`, `mode`, roles, and rule IDs with what the user expected.
- Treat exit code `2`, `mode: empty`, a row-count mismatch, or unexpected rule selection as a diagnosis to review. Do not expose workbook content while explaining it.
- Treat exit code `66` as a local file-access problem. Ask the user to verify the path and permissions; do not create or submit a parser report because no workbook was parsed.
- A receipt is deliberately content-free. It is useful for clustering and reproduction routing, but it is not proof that a particular tag or URL is correct.
- Do not call `save_ask` without explicit confirmation. When confirmed, send only the receipt, the skill version, and a short user-approved statement of expected versus observed behavior. Never send the workbook, raw headers, tags, URLs, filenames, or cell values.
- Give each run `scope3/skill-id: inspect-tag-sheet@1.0.0` and the selected scenario ID when the host supports request metadata.

## Run locally

Download and run the self-contained Node.js inspector:

```bash
inspector_dir="$(mktemp -d "${TMPDIR:-/tmp}/inspect-tag-sheet.XXXXXX")" &&
inspector_tmp="$inspector_dir/inspect-tag-sheet.mjs" &&
trap 'rm -rf "$inspector_dir"' EXIT &&
curl -fsSLo "$inspector_tmp" https://api.interchange.io/skills/inspect-tag-sheet/1.0.0/scripts/inspect-tag-sheet.mjs &&
node "$inspector_tmp" /path/to/tag-sheet.xlsx
```

The inspector needs Node.js 20 or newer and makes no network calls. Keep the `.mjs` suffix if adapting the command so Node loads the inspector as an ES module. The output follows [references/receipt.schema.json](references/receipt.schema.json).

## Interpret the receipt

- `mode: container` means rows contain creative markup and can create one creative per row.
- `mode: sidecar` means rows describe sibling uploaded files.
- `mode: source` means the sheet contains destination-sensitive representations such as VAST or Internal Redirect; a compatible destination must be chosen before trafficking.
- `mode: empty` means the workbook was readable but the current profile found no usable rows. This is the strongest mapping-library improvement signal.
- `appliedRuleIds` names the finite parser rules used. `recognizedRoles` names semantic fields, never the source headers.
- `diagnosticCodes` is a closed taxonomy. It contains no parser exception text.

Compare the receipt with the user's expectation. Report the parser and profile versions, parsed mode, row count, roles, rules, and diagnostics. Do not infer or reconstruct workbook content.

## Report a mapping issue

Interchange automatically records content-free evidence when its production upload parser rejects a workbook or returns no usable rows. When the same readable-empty shape recurs across customers, Interchange sends one deduplicated, content-free signal for team review, so the client does not need to file the first report.

If local inspection finds a different problem—such as a plausible but wrong row count—show the sanitized receipt and ask whether the user wants to report it. After confirmation, use `save_ask` with `type: "support"` and include only:

- `inspect-tag-sheet@1.0.0`;
- the complete sanitized receipt;
- the user-approved expected row count or mode; and
- the observed row count or mode.

The team reproduces the shape with synthetic or explicitly approved sanitized data, adds a regression fixture, updates the versioned mapping profile, and publishes a new immutable skill/profile version. Customer workbooks never become corpus fixtures by default.
