---
name: publish-an-openai-app
description: Prepare and guide publication of an Interchange-powered app in OpenAI. Use when a seller administrator asks what is ready, needs help configuring the app's CNAME or OpenAI challenge, wants a submission checklist or package, or needs guidance for portal fields, reviewer access, screenshots, locales, release notes, scans, and the review video.
---

# Publish an OpenAI App

Guide a seller administrator from Interchange Distribution readiness through the manual OpenAI submission. Use only the existing Distribution surfaces for state: `get` reads it, and `save_seller` changes its OpenAI challenge token. Never invent a provider-specific tool or claim that Interchange tested or submitted an OpenAI draft.

Canonical customer documentation: <https://docs.interchange.io/v2/reference/white-label-chatgpt-app>

## Workflow

1. Confirm that the active account is the Seller Account the user intends to publish and that the user is an administrator. If either is false, stop and explain which account or administrator is required.
2. Call `get({ kind: "distribution" })`. Treat the returned Distribution object as the authority on the public hostname, CNAME target, ownership record, hostname status, MCP URL, and OpenAI challenge status.
3. Work through hostname readiness:
   - Give the user the exact CNAME and ownership records returned by Distribution. Do not guess DNS values.
   - Ask the user to make the DNS changes with their DNS provider, then call `get({ kind: "distribution" })` again.
   - Treat `hostname.status: "active"` as Interchange's server-verified CNAME/ownership result. A pending or failed state is not ready; report the returned next action.
   - Do not describe this as testing OpenAI publication. Interchange can verify its hostname and challenge endpoint, not the state of an OpenAI portal draft.
4. When OpenAI gives the user a challenge token, ask them to confirm the exact value and call `save_seller({ distribution: { openaiChallengeToken: "<exact token>" } })` as a separate write. Replacing or removing a token requires the matching `confirmReplace` or `confirmRemove` field and immediate confirmation. Re-read Distribution afterward and report its observed challenge status.
5. Direct the administrator to download a fresh OpenAI submission package from Distribution settings. Do not claim the MCP tool downloaded it. Use its `README.md` and `readiness-report.json` as the snapshot-specific authority for imported JSON, included assets, missing items, manual portal fields, approved prompts, test cases, and the video shot list.
6. Before portal submission, walk through every manual group:
   - publisher identity, monitored contact, app identity, descriptions, category, website, support, privacy, and Terms URLs;
   - directory and composer logos, screenshots, starter prompts, supported locales, and country availability;
   - production MCP URL, OAuth redirect allowlist, reviewer account, fresh tool and skill scan, tool annotations, justifications, tests, confirmations, and UI CSP/origins;
   - policy and data attestations, release version, release notes, and the final review video.
7. Treat reviewer credentials and portal-only evidence as manual and sensitive. Never request, store, repeat, or place credentials, OAuth tokens, challenge tokens, or private customer data in a generated file or ordinary chat response. The publisher enters reviewer credentials only in OpenAI's protected portal.
8. Keep completion evidence honest:
   - `READY_FOR_PORTAL` means Interchange found no package-level blocker; `MANUAL_STEPS_REMAIN` still requires owner and reviewer work.
   - Never infer that a locale, country, policy answer, screenshot, scan, reviewer account, or video is complete. Ask the owner to verify it in the portal.
   - Never claim an uploaded OpenAI draft updates automatically. Regenerate and re-import after listing, branding, hostname, legal URL, account role, tool surface, test case, canonical skill, locale, or Discovery publication changes.
9. Finish with a compact checklist grouped as: ready in Distribution, missing in Interchange, manual in OpenAI, and stale since the last package. Name the next owner action and stop at any unresolved blocker.

## Stop conditions

- Do not publish, submit, or approve an OpenAI app on the user's behalf.
- Do not invent DNS records, portal values, reviewer evidence, supported locales, or completion state.
- Do not use unrelated seller writes to work around missing Distribution state.
- If `get({ kind: "distribution" })` or the nested `save_seller` Distribution input is unavailable, report that the current account, role, or V3 surface cannot perform this workflow and point to the canonical documentation.
