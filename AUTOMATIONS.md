# Genesis Scheduled Cycles

Status: **CREATED AND DISABLED — DO NOT ENABLE BEFORE THE DRY RUNS PASS**

The v1.0.0 Codex desktop-app automation (`genesis-operator-cycle`, paused) is retired with that platform. Scheduling now uses two cloud Routines that each create a fresh Claude Code session in this repository's environment, per `CLOUD_ENVIRONMENT.md`.

## Routine definitions

| Name | Cron (UTC, while EDT) | Local window | Prompt |
|---|---|---|---|
| `genesis-operator-cycle` | `0 13 * * *` | 9:00 AM America/New_York | Read `CLAUDE.md`, then follow `prompts/OPERATOR_CYCLE.md` exactly. |
| `genesis-close-cycle` | `0 22 * * *` | 6:00 PM America/New_York | Read `CLAUDE.md`, then follow `prompts/CLOSE_CYCLE.md` exactly. |

- Each firing creates a fresh session (cold resume from `main`); no session state carries between firings.
- Completion notifications: push and email to Max on every firing.
- The Routine prompt is a bootstrap pointer only; the governing instructions are the version-controlled files in `prompts/`, so cycle behavior changes are auditable commits.
- If Day 1 falls after 2026-09-17, apply the DST shift documented in `CLOUD_ENVIRONMENT.md` on 2026-11-01 and record it in `decisions.jsonl`.

## Activation gate

The Routines were created during readiness, from a session Max directed, and were disabled immediately. A disabled Routine never fires, so creation is safe at any point; **enabling** is what the dry runs gate. Firing is additionally safe by construction — the executable `start-cycle` gate blocks on readiness mode, false readiness items, incomplete activation dates, validation failure, or an existing lock before any research or external action — but that backstop is not a substitute for the dry runs.

Before enabling either Routine:

1. Manually invoke the operator branch in a fresh cloud session; confirm it blocks in readiness mode without research, external action, or record damage, and that a records push to `main` lands.
2. Manually invoke the close branch the same way; confirm reconciliation, snapshot, and dashboard behavior with no outreach or spending.
3. Log both tests in `READINESS_EVIDENCE.md` and set the two schedule readiness fields true.
4. Enable both Routines only after every other readiness item is true and Day 1 is selected, then record the enable in `decisions.jsonl`.

Recorded Routine IDs are in `READINESS_EVIDENCE.md`.
