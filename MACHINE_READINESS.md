# Machine Readiness — SUPERSEDED

Superseded: `2026-08-12` by the v2.0.0 Claude migration. The runtime moved from the local machine BRONTOSAURUS to Claude Code managed cloud sessions; see `CLOUD_ENVIRONMENT.md`. No local machine must stay awake, and no Genesis-specific power setting remains in force. The original v1.0.0 record is preserved below for the audit trail.

---

## BRONTOSAURUS Machine Readiness (v1.0.0, historical)

Verified: `2026-08-08 America/New_York`

- Active power plan: Lenovo Legion Performance Mode.
- AC sleep timeout: never.
- AC hibernate timeout: never.
- Battery sleep timeout: 10 minutes; intentionally unchanged for battery safety.
- Battery hibernate timeout: 10 minutes; intentionally unchanged for battery safety.
- Verification state: connected to AC power with 98% charge.
- Windows timezone: Eastern Time (US & Canada), matching the protocol.
- Clock cross-check: local UTC time was 1.47 seconds ahead of GitHub's HTTP date on 2026-08-08, which is adequate for the daily schedule.
- Windows Time service reported temporarily unsynchronized; an immediate resync required administrator elevation. This is not currently a timing blocker, but recheck it during the schedule dry runs.

No power-setting change was required. After the migration, there is no setting to restore because these were the pre-existing AC settings.
