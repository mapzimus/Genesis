# Readiness Evidence Record

Record only non-sensitive evidence. Do not include an email address, account number, payment token, credential, recovery code, legal identifier, or customer information in this public repository.

## Amended preregistration published

- Migration pull request merged to `main`: pull request #1, merge commit `387e0c5`, merged by the repository owner
- Amendment public timestamp recorded in `PREREGISTRATION.md`: `2026-08-12T18:28:54-04:00`
- Recorded at: `2026-08-12T18:50:00-04:00`

## Cloud session configuration

- Fresh-session `CLAUDE.md` auto-load verified: `PENDING`
- Fixed model parameters reported by the session: `PENDING`
- Session effort level confirmed `high`: `PENDING`
- Records push to `main` demonstrated from a cycle: `PENDING`
- Recorded at: `PENDING`

## Post-merge cold-resume re-audit

- Read-only audit re-run after the migration merged to `main`: `2026-08-12`, against commit `387e0c5`, by an ephemeral read-only subagent
- Verdict recorded in `daily-reports/`: PASS — `daily-reports/2026-08-12-postmerge-audit.md`

## Dedicated email

- Opaque account label: `PENDING`
- Authentication tested by Max: `PENDING`
- Recovery method held privately by Max: `PENDING`
- Recorded at: `PENDING`

## Payment readiness

- Provider: `PENDING`
- Legally usable account confirmed by Max: `PENDING`
- Payment collection capability verified: `PENDING`
- Refund and payout controls verified: `PENDING`
- Credentials and financial identifiers kept outside repository: `PENDING`
- Recorded at: `PENDING`

## Treasury separation

- Opaque envelope/account label: `PENDING`
- Opening amount: `$115.00`
- No debt or credit facility attached: `PENDING`
- Confirmed by Max at: `PENDING`

## Routines

- `genesis-operator-cycle` Routine ID: `trig_01VqPMDoHhkXgokqw8mLspdb`, cron `0 13 * * *` UTC (9:00 AM America/New_York)
- `genesis-close-cycle` Routine ID: `trig_01BPPQKGmnTp7myYnicRDVap`, cron `0 22 * * *` UTC (6:00 PM America/New_York)
- Environment: `env_01FpWyRFDFdtNACAXGkYHnjz`; each firing creates a fresh session
- Completion notifications (push and email) configured: yes, on both
- Current state: **disabled**. Both were created enabled by the API and disabled immediately in the same run, per `CLOUD_ENVIRONMENT.md`. Enabling is gated on both dry runs and the rest of the checklist.
- Recorded at: `2026-08-13T12:59:00-04:00`

### Closed gap — connector access in fired sessions

Neither Routine stores MCP connectors, so a fired session starts without GitHub issue tools. Confirmed by the 2026-08-13 dry runs: each Routine's stored `allowed_tools` list contains no `mcp__github__*` entries, so a fired session could not have read an `approval-request` issue, transcribed a decision, posted a `daily-report`, or opened an `incident`.

- Resolution: on 2026-08-14 Max chose to drop the dependency instead of satisfying it. Communication moved to the git-only channel — `OWNER_INBOX.md` plus committed `daily-reports/` — under `apr-comms-008`. A scheduled cycle now reaches Max with git alone, and the connector is no longer needed by any part of the protocol.
- Status: `RESOLVED BY DESIGN` — to be confirmed live by the repeated dry runs, which must show a fired session reading `OWNER_INBOX.md` and running `scripts/genesis.py inbox` successfully.

## Operator dry run

- Session ID: `cse_01FSHBBcRHXm4cSB9NgEkohz` (Routine `trig_01VqPMDoHhkXgokqw8mLspdb`)
- Timestamp: `2026-08-13T17:03:22Z`, reached idle at `17:05:26Z`
- Readiness branch correctly blocked market research: yes — no research, outreach, spending, or external action resulted
- Lock acquisition/overlap/release behavior: correct — the director's lock `run-cd06ee35` remained active and owned throughout; the fired session never acquired, stole, or released it, because `start_cycle` evaluates the readiness gate before `acquire_lock`
- Repository changes: none — `main` stayed at `8b8e61a` under continuous watch for 152 s, no new branches, director working tree untouched
- Result: **not accepted.** Safe behavior, but the session ran on `claude-sonnet-5` and without GitHub issue tools. See `daily-reports/2026-08-13-dry-runs.md`. Must be repeated after the Routines are corrected.

## Close dry run

- Session ID: `cse_013D2hLVpBGNUaERhkcRXCwx` (Routine `trig_01BPPQKGmnTp7myYnicRDVap`)
- Timestamp: `2026-08-13T17:06:37Z`, reached idle at `17:10:36Z`
- No outreach or spending initiated: confirmed — none
- Reconciliation/dashboard/snapshot behavior: not exercised, because the readiness gate correctly blocked the cycle before reconciliation; this must be re-verified after activation prerequisites are met
- Repository changes: none — `main` stayed at `8b8e61a` under continuous watch for 175 s and on re-check, no new branches, director working tree untouched
- Result: **not accepted.** Same two configuration defects as the operator run. Must be repeated after the Routines are corrected.

### Closed gap — wrong model in fired sessions

Both fired sessions served `claude-sonnet-5`, not the preregistered `claude-fable-5`. The Routine's session configuration overrides the repository's `.claude/settings.json`, so scheduled cycles would have breached the fixed-model condition in `PREREGISTRATION.md`.

- Resolution: Max chose to have the director set the model directly. Both Routines were updated on 2026-08-13 under `apr-model-007` / `act-model-007`; each now reports `model: claude-fable-5` in its session configuration, with cron, prompt, notifications, environment, and disabled state unchanged.
- Status: `RESOLVED IN CONFIGURATION` — still to be confirmed live by the repeated dry runs.
