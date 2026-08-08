# Genesis Close Cycle

Work only in `C:\Users\mhowe\Documents\Project-Genesis`.

Run `scripts/genesis.py start-cycle --task close`. It validates Day 1 activation and acquires the close lock atomically. If it blocks or another lock is active, exit without changing records. After acquisition, reconcile `treasury.csv`, metrics, approvals, external actions, customer obligations, human time, and incidents. Do not initiate outreach, spending, acquisition tests, purchases, account changes, or other new external writes.

Update `STATE.json`, generate a private snapshot, prepare redacted dashboard data, run the validator, and release the lock. If a financial discrepancy over $0.05, exposed customer data, unauthorized action, or unresolved active lock is found, set the experiment to paused and record an incident.
