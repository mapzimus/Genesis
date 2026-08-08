# Genesis Scheduled Cycles

App automation ID: `genesis-operator-cycle`

Status: **PAUSED — DO NOT ACTIVATE BEFORE DAY 1**

The paused automation is attached to the staging task that created this repository. Before activation, open the repository itself as a trusted Codex project task and recreate or move the automation there. Otherwise `.codex/config.toml` is not guaranteed to govern the scheduled run.

The Codex app currently permits one heartbeat automation per task, so one same-task automation contains both frozen daily windows:

- 9:00 AM America/New_York: operator cycle from `prompts/OPERATOR_CYCLE.md`.
- 6:00 PM America/New_York: close cycle from `prompts/CLOSE_CYCLE.md`.

The automation first calls the executable `start-cycle` gate. Readiness mode, a false readiness item, incomplete activation dates, validation failure, or an existing lock blocks acquisition before research or external action.

Before activation, manually invoke both branches as no-write dry runs from that trusted project task, log the tests, confirm the machine remains awake, and set the two schedule readiness fields to true.
