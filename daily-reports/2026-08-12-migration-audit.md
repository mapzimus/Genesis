# 2026-08-12 Post-Migration Cold-Resume Audit

A separate read-only task audited the v2.0.0 Claude-migration working tree (commit `01550aa`, mid-ceremony) using only repository files, per the protocol's cold-resume requirement.

Verdict: **FAIL** on the pre-publication state, with the blocking findings below. Findings marked *resolved by publication* are inherent to auditing mid-ceremony and clear when the publication action `act-migration-claude-003` completes; findings marked *fixed* were corrected before the branch was pushed.

| # | Finding | Disposition |
|---|---|---|
| A | `origin/main` still carries protocol v1.0.0 (Codex model, `.codex/config.toml`, live BRONTOSAURUS requirement); v2.0.0 existed only on the unpushed local branch | Resolved by publication and Max's merge; until the merge, `main` remains self-consistent v1.0.0 and the open draft pull request is the discoverable path to v2.0.0 |
| B | `STATE.json` and `READINESS.md` directed the agent to merge a pull request that did not exist and never named the migration branch | Fixed: both now name `claude/agent-cloud-environment-990zct` and the pending action `act-migration-claude-003` |
| C | Active run lock was committed with no protocol record naming it | Fixed: `decision-0003`, the approval, the action events, and `STATE.json.pending_external_actions` all name run `run-820453f7-0b19-43e4-a4d5-e990cd06a880`; the lock is released at ceremony end |
| D | Public `dashboard/public-summary.json` still reported protocol 1.0.0 | Resolved by publication: regenerated during the ceremony |
| E | `last_validated_at` and `last_snapshot` predated the migration; no 2026-08-12 artifact backed the readiness claims | Resolved by publication: ceremony-end validation and snapshot |
| F | `READINESS.md` checkboxes did not map 1:1 to `STATE.json.readiness` flags | Fixed: 13 boxes now name their flags in order |
| G | Frozen `high` effort declared everywhere but not machine-enforceable from the repository | Fixed: `TOOL_MANIFEST.md` now states the true enforcement boundary; effort verification added to the readiness dry-run evidence |
| H | Pre-v2 `approvals.csv` rows use the retired `codex_task` channel without annotation | Fixed: annotated in `TOOL_MANIFEST.md`; historical rows remain append-only |
| I | Validator did not guard `README.md`, `READINESS.md`, `MACHINE_READINESS.md` | Fixed: added to `required_paths` |

Consequence for readiness: `cold_resume_audit_passed` is set to `false`. The audit must be re-run from a fresh clone after the migration merges to `main`; the readiness gate blocks Day 1 until it passes. The 2026-08-08 v1.0.0 audit (PASS) remains valid for the superseded protocol.
