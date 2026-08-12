# Project Genesis

Project Genesis is a controlled, live entrepreneurship experiment operated by Max Howe and directed by one consistently configured Claude agent.

Public protocol: https://github.com/mapzimus/Genesis/blob/main/PREREGISTRATION.md

Passive dashboard: https://mapzimus.github.io/Genesis/

The workspace is in **readiness mode**. Day 1 has not started. Do not begin opportunity research until every readiness item in `STATE.json` is true, the acceptance suite passes, and the amended preregistration is published and timestamped.

## Fixed design

- Operating period: 30 consecutive calendar days in America/New_York.
- Financial closeout: 14 additional days.
- Starting treasury: $115.00.
- Formal pass: confirmed realized profit greater than $0 on Day 45.
- Model: `claude-fable-5` with `high` effort.
- One director per cycle; ephemeral subagents for read-only research only.
- Runtime: Claude Code managed cloud sessions per `CLOUD_ENVIRONMENT.md`.
- Human assistance: two 15-minute windows per day.
- Product and transparency reporting remain separate through Day 45.

## Before activating Day 1

Work through `READINESS.md`. In outline:

1. Merge the v2.0.0 migration to `main` and record the amendment timestamp.
2. Verify a fresh cloud session loads `CLAUDE.md` and can push records to `main`.
3. Create the dedicated Genesis email address.
4. Verify a legally usable payment method.
5. Separate the $115 accounting envelope.
6. Run `python3 scripts/genesis.py validate` and `python3 -m unittest discover -s tests -v`.
7. Create the two Routines per `AUTOMATIONS.md` and dry-run both cycles.
8. Fill in the experiment dates in `PREREGISTRATION.md` and `STATE.json`.
9. Set `status` to `active` only after all readiness items are true.

## Normal operation

- `CLAUDE.md` is the operating instruction set, loaded automatically in every session (`AGENTS.md` points to it).
- `PREREGISTRATION.md` and `GENESIS_CHARTER.md` are frozen governance records.
- `CLOUD_ENVIRONMENT.md` defines the runtime, scheduling, state discipline, and how Genesis and Max communicate.
- `STATE.json` is the cold-resume summary.
- CSV and JSONL files are the authoritative audit trail.
- `RUN_LOCK.json` prevents overlapping runs; the push-to-claim rule in `CLOUD_ENVIRONMENT.md` makes it effective across ephemeral containers.
- `scripts/genesis.py` validates records, manages the run lock, checks action idempotency, produces snapshots, and prepares public dashboard data.
- `dashboard/` contains only redacted public information.

## Common commands

```bash
python3 scripts/genesis.py validate
python3 scripts/genesis.py acquire-lock --task operator
python3 scripts/genesis.py start-cycle --task operator
python3 scripts/genesis.py release-lock --run-id <run-id>
python3 scripts/genesis.py check-action --action-id <action-id>
python3 scripts/genesis.py begin-action --action-id <action-id> --run-id <run-id>
python3 scripts/genesis.py snapshot
python3 scripts/genesis.py dashboard
```

External-action commands also require the current `run_id` and a pre-existing sanitized decision record. This makes the separation between research and execution machine-checkable.

Follow `OPERATIONS.md` for the planned → executing → completed sequence. An executing action blocks automatic retries after a crash.

Record secondary, non-treasury costs in `economic-costs.csv`. Human time comes from `interventions.csv`; the public summary computes the fully loaded result without double-counting costs already in `treasury.csv`.

Never put credentials, raw customer correspondence, payment details, or personal information in this repository.
