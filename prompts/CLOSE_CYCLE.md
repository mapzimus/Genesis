# Genesis Close Cycle

Work only in this session's clone of `mapzimus/Genesis`. Confirm you are on `main` and pull the latest state first; the remote repository is the source of truth.

Run `scripts/genesis.py start-cycle --task close`. It validates Day 1 activation and acquires the close lock atomically. If it blocks or another lock is active, exit without changing records. After acquisition, immediately commit `RUN_LOCK.json` and push to `main`; if the push is rejected, release the lock and exit without retrying (push-to-claim, per `CLOUD_ENVIRONMENT.md`).

Reconcile `treasury.csv`, metrics, approvals, external actions, customer obligations, human time, and incidents. Do not initiate outreach, spending, acquisition tests, purchases, account changes, or other new external writes.

Update `STATE.json`, generate a private snapshot, prepare redacted dashboard data, run the validator, release the lock, and commit and push to `main`. Write the day's summary to `daily-reports/` per `CLOUD_ENVIRONMENT.md`. If a financial discrepancy over $0.05, exposed customer data, unauthorized action, or unresolved active lock is found, set the experiment to paused, record an incident in `INCIDENTS.md`, and announce it under Requests in `OWNER_INBOX.md`.
