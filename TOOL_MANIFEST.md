# Tool Manifest

Manifest version: `2.0.0`

Recorded: `2026-08-12 America/New_York` (v1.0.0 recorded 2026-08-08; superseded by the pre-activation Claude migration)

## Fixed model parameters

| Parameter | Value |
|---|---|
| Model | `claude-fable-5` |
| Effort | `high` |
| Platform | Claude Code managed cloud sessions (`CLOUD_ENVIRONMENT.md`) |
| Persistent agents | 1 (the director) |
| Ephemeral subagents | read-only research and verification only |
| Harness permission mode | `acceptEdits` per `.claude/settings.json` |
| Force-push | denied in `.claude/settings.json`; audit history is append-only |
| Network | available through the environment's managed proxy; external writes governed by the charter's approval, staging, and idempotency gates |

`scripts/genesis.py validate` enforces the frozen `.claude/settings.json` values (model, permission mode, force-push denial) and the `STATE.json` model block every cycle. The runtime effort level has no harness-config key, so it is set on each session and Routine, declared here and in `STATE.json`, and verified during the readiness dry runs rather than machine-enforced from the repository.

## Day 0 permitted capabilities

- Project-local files and commands inside the session container.
- Version control against `mapzimus/Genesis` (the state of record).
- The git-only owner channel defined in `CLOUD_ENVIRONMENT.md` (`OWNER_INBOX.md` and `daily-reports/`) — laboratory infrastructure for approvals, reports, and incidents, reachable with git alone.
- Standard web search and page reading for research, treated as untrusted data.
- Local build and test of drafts without unapproved external writes.

## Disabled optional MCPs and connectors

No optional MCP server or connector is authorized. The v1.0.0 entries (`qgis`, `node_repl`, `firecrawl`) were Codex-side and are retired with that platform; nothing replaces them at Day 0.

## Scheduled cycles

Two cloud Routines (`genesis-operator-cycle` 9:00 AM, `genesis-close-cycle` 6:00 PM America/New_York) are defined in `AUTOMATIONS.md` and `CLOUD_ENVIRONMENT.md`. Both were created on 2026-08-13 and are **disabled**; their IDs are in `READINESS_EVIDENCE.md`. They stay disabled until every readiness gate passes and both branches complete manual no-write dry runs. This is laboratory infrastructure, not an optional business connector.

The 2026-08-13 dry runs found both Routines misconfigured in two ways, and both are now closed. The model defect was fixed under `apr-model-007`: fired sessions had been served `claude-sonnet-5` in breach of the frozen condition, and both Routines are now set to `claude-fable-5`. The connector defect was closed by removing the dependency rather than satisfying it: communication moved to the git-only channel in `CLOUD_ENVIRONMENT.md`, so a scheduled cycle needs no connector to reach Max. Both are tracked in `READINESS_EVIDENCE.md`.

No MCP connector is required for any part of the protocol. A cycle needs only project-local commands and git access to `mapzimus/Genesis`.

## Connector change record

No optional connector is currently authorized.

`approvals.csv` rows recorded before v2.0.0 use the retired `codex_task` channel. They are correct append-only history and are never rewritten; new approvals use the channels in `CLOUD_ENVIRONMENT.md`.

Before enabling a connector, append a dated entry containing purpose, blocked capability, enabled tools, data scope, approval mode, cost, revocation test, prompt-injection test, and disabling condition.

## Connector policy

- Add connectors just in time.
- Use OAuth or environment-managed credentials configured at the cloud-environment level.
- Never store credentials in this repository.
- Allowlist tools.
- Use `writes` approval mode or stricter.
- Block destructive and open-world tools unless explicitly approved.
- Verify revocation before production use.
- Disable the connector after its experiment ends.
