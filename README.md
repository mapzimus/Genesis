# Project Genesis

Project Genesis is a controlled, live entrepreneurship experiment operated by Max Howe and directed by one consistently configured Codex agent.

Public protocol: https://github.com/mapzimus/Genesis/blob/main/PREREGISTRATION.md

Passive dashboard: https://mapzimus.github.io/Genesis/

The workspace is in **readiness mode**. Day 1 has not started. Do not begin opportunity research until every readiness item in `STATE.json` is true, the acceptance suite passes, and the preregistration is published and timestamped.

## Fixed design

- Operating period: 30 consecutive calendar days in America/New_York.
- Financial closeout: 14 additional days.
- Starting treasury: $115.00.
- Formal pass: confirmed realized profit greater than $0 on Day 45.
- Model: `gpt-5.6-sol` with `high` reasoning.
- One main agent; no subagents.
- Human assistance: two 15-minute windows per day.
- Product and transparency reporting remain separate through Day 45.

## Before activating Day 1

1. Create the dedicated Genesis email address.
2. Verify a legally usable payment method.
3. Verify access to free preview/static hosting.
4. Separate the $115 accounting envelope.
5. Configure the computer to remain awake for scheduled local runs.
6. Run `python scripts/genesis.py validate`.
7. Run `python -m unittest discover -s tests -v`.
8. Fill in the experiment dates in `PREREGISTRATION.md` and `STATE.json`.
9. Publish a redacted copy of `PREREGISTRATION.md` and record its URL and timestamp.
10. Create and manually test the two scheduled prompts in `prompts/`.
11. Set `status` to `active` only after all readiness items are true.

On BRONTOSAURUS, use:

```powershell
& 'C:\Users\mhowe\AppData\Local\Python\bin\python.exe' scripts\genesis.py validate
& 'C:\Users\mhowe\AppData\Local\Python\bin\python.exe' -m unittest discover -s tests -v
```

## Normal operation

- `AGENTS.md` is the operating instruction set.
- `PREREGISTRATION.md` and `GENESIS_CHARTER.md` are frozen governance records.
- `STATE.json` is the cold-resume summary.
- CSV and JSONL files are the authoritative audit trail.
- `RUN_LOCK.json` prevents overlapping runs.
- `scripts/genesis.py` validates records, manages the run lock, checks action idempotency, produces snapshots, and prepares public dashboard data.
- `dashboard/` contains only redacted public information.

## Common commands

```powershell
python scripts/genesis.py validate
python scripts/genesis.py acquire-lock --task operator
python scripts/genesis.py release-lock --run-id <run-id>
python scripts/genesis.py check-action --action-id <action-id>
python scripts/genesis.py begin-action --action-id <action-id> --run-id <run-id>
python scripts/genesis.py snapshot
python scripts/genesis.py dashboard
```

External-action commands also require the current `run_id` and a pre-existing sanitized decision record. This makes the separation between research and execution machine-checkable.

Follow `OPERATIONS.md` for the planned → executing → completed sequence. An executing action blocks automatic retries after a crash.

Record secondary, non-treasury costs in `economic-costs.csv`. Human time comes from `interventions.csv`; the public summary computes the fully loaded result without double-counting costs already in `treasury.csv`.

Never put credentials, raw customer correspondence, payment details, or personal information in this repository.
