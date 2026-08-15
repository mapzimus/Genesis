# 2026-08-15 Scheduled Cycle Dry Runs — Repeat

Both Routines were fired once each, sequentially, as no-write dry runs under approval `apr-dryruns-009` (`decision-0009`, `act-dryruns-009`), against `main` at `10395c2` — the first state carrying both corrections. The director held run lock `run-9459d338-798a-4b52-82cf-1244f388cd95` throughout.

## What happened

| | Operator | Close |
|---|---|---|
| Routine | `trig_01VqPMDoHhkXgokqw8mLspdb` | `trig_01BPPQKGmnTp7myYnicRDVap` |
| Session | `cse_017CjVnpN9RpXg4ZRABBojsL` | `cse_01UPKPH3zB6P8CHNUGEJUtu4` |
| Fired at | 2026-08-15T01:24:21Z | 2026-08-15T01:28:09Z |
| Reached idle | 01:26:58Z | 01:30:33Z |
| Output tokens | 8,307 | 7,393 |
| **Model served** | **`claude-fable-5`** | **`claude-fable-5`** |

## Result: both accepted

- **Model corrected at runtime.** Both sessions report `claude-fable-5` in `session_context.model` and `last_served_model`. The 2026-08-13 defect, where fired sessions were served `claude-sonnet-5` in breach of the preregistered fixed condition, does not reproduce.
- **No repository change.** `main` stayed at `10395c2`, watched continuously for 193 s and 257 s and re-checked afterward. No commits, no new branches, director working tree clean.
- **Lock untouched.** Still `active` and owned by `run-9459d338` after both runs. Neither session acquired, stole, nor released it, as expected from `start_cycle` evaluating the readiness gate before `acquire_lock`.
- **No outreach, spending, purchase, account change, or market research.**
- **Connector dependency gone.** The blocking gap of 2026-08-13 cannot recur: `OWNER_INBOX.md` is an ordinary file in the session's clone, so reaching Max needs only git, which every firing already demonstrates by cloning.

## Recorded limitation

A readiness-blocked cycle produces no artifact, and the director cannot read another session's transcript, so each session's own report of running `scripts/genesis.py inbox` was not directly observed. Acceptance rests on the directly verified evidence above plus the structural point that the inbox is a tracked file in the clone rather than a networked resource. This is stated rather than glossed over; the first live cycle after activation will exercise the inbox path with an artifact to inspect.

## Readiness consequence

`operator_schedule_tested` and `close_schedule_tested` are set **true**. Readiness advances to 8 of 13.

Both Routines remain **disabled**. Per `AUTOMATIONS.md`, enabling additionally requires every other readiness item true and Day 1 selected.

Five items remain false:

- `dedicated_email_ready`, `payment_method_ready`, `treasury_separated` — owner-side.
- `cloud_session_config_verified` — these runs confirm a fresh session runs on `claude-fable-5`, but the Routine prompt *instructs* reading `CLAUDE.md` rather than proving it auto-loads, and the `high` effort setting is not observable in session metadata. Not claimed as satisfied.
- `records_push_verified` — not exercised, because both cycles correctly blocked at the readiness gate before reaching any push. It can only be demonstrated by a cycle that passes the gate.
