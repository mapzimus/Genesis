# 2026-08-12 Post-Merge Cold-Resume Audit

Max merged pull request #1 at `2026-08-12T18:28:54-04:00` (commit `387e0c5`), publishing protocol v2.0.0 to `main`. A separate read-only task then re-ran the cold-resume audit required by `READINESS.md`, using only the repository files at that commit.

Verdict: **PASS.**

- Validator green with zero errors; treasury recomputation matches `STATE.json` to the cent.
- All three external actions (`act-readiness-github-publish-001`, `act-readiness-github-sync-002`, `act-migration-claude-003`) are terminally complete with matching approvals, sanitized decisions, and byte-identical scope hashes; no orphaned executing action; run lock idle and its run named in the records, closing finding C of the pre-publication audit.
- The readiness checklist maps 1:1, in order, to the `STATE.json.readiness` flags.
- Scheduling and communication are defined once (`CLOUD_ENVIRONMENT.md`) and restated consistently; every Codex/BRONTOSAURUS reference outside historical records is a marked v1→v2 comparison.
- The one stale item — `next_permitted_action` still awaiting the pull request #1 merge — was judged trivially recoverable because the merged files are self-evidencing and the same sentence carries the post-merge instruction; it is corrected by this record set.

Non-blocking findings and dispositions:

1. **Owner time was unlogged.** `interventions.csv` was header-only despite readiness-period owner activity, while the protocol requires logging all human time. Disposition: two retroactive entries added for 2026-08-12 (migration directive; pull-request review and merge) with durations recorded as estimates pending Max's confirmation in a review window. Owner activity on 2026-08-08 (the two v1.0.0 approvals) predates this correction and remains unlogged; Max may supply an estimate to complete the record, or it stands as a noted v1-period gap.
2. **`daily-reports/` naming.** Readiness-period audits use descriptive suffixes rather than the `day-NN` operating-day pattern; the README pattern applies to operating days, so no change.
3. **`daily-report` issue label** does not exist yet; create it when the first close-cycle report posts.
