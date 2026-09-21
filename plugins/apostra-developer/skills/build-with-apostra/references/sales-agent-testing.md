# Test a sales agent

Use the [seller workflow](https://docs.interchange.io/v2/setup/v3/seller-workflows#test-your-own-supply)
and [sandbox guide](https://docs.interchange.io/v2/features/sandbox) to establish
the current account's testing path. Retrieve
`get({ kind: "skill", id: "test-sales-agent" })` before a remote test. Follow
that returned version's declared scenarios, fixtures, bounds, and cleanup;
do not copy a scenario from an older installed package.

## Select the evidence to collect

- A local protocol or mapping test uses synthetic fixtures and proves only
  the application's behavior.
- Brief discovery exercises the authenticated company's own supply and
  observes products without staging a buy. It still creates temporary sandbox
  resources; it is not the read-only installation check.
- An own-supply transaction stages and activates a sandbox buy after the
  scenario's explicit confirmations. Sandbox status must come from the
  returned advertiser, not its name or a test-mode string.

Keep the exact seller, advertiser, campaign, source or agent target, product
query, revision, and offer provenance returned by the tools. A provisional
product page does not authorize staging. Follow the scenario's continuation
steps to a terminal catalog and stop if the selected offer disappears or its
provenance cannot be established.

When the account cannot retrieve the skill or expose the required tools,
report the missing access or capability and finish any local fixture tests.
Do not route around that boundary with legacy test wrappers or a live buyer
advertiser.

## Finish with evidence and cleanup

Run the scenario's declared cleanup in reverse mutation order after success,
failure, or cancellation. Preserve enough IDs to retry cleanup, and report any
resources that remain. Restoring a temporary advertiser activation preference
is part of cleanup when the scenario changes it.

Report assertions observed, failed, and unexercised; exact server result
references; and cleanup status. A staged record is not delivery, a metadata
creative is not an executed creative handoff, and an observed test is not
independent certification. Never claim a local starter passed without running
its deterministic test command.
