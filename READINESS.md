# Day 1 Readiness Gate

Day 1 is blocked until every box below is complete. Completing the workspace and tests does not start the experiment.

Each box maps to the identically ordered flag in `STATE.json.readiness`; the checklist and the flags must always agree.

- [x] `amended_preregistration_published` — Max merged migration pull request #1 to `main` at `2026-08-12T18:28:54-04:00` (commit `387e0c5`); the timestamp is recorded in `PREREGISTRATION.md`. The v1.0.0 preregistration and frozen evaluator were published and timestamped 2026-08-08.
- [ ] `cloud_session_config_verified` — A fresh Claude Code cloud session created from this repository loads `CLAUDE.md` automatically and reports the fixed parameters, including `high` effort (replaces the v1 trusted-Codex-task item).
- [ ] `records_push_verified` — A cloud session demonstrates the push discipline: a records commit lands on `main` from inside a cycle (replaces the v1 keep-awake item).
- [ ] `dedicated_email_ready` — Dedicated Genesis email exists and authentication works.
- [ ] `payment_method_ready` — A legally usable payment method is verified and can be revoked or disabled.
- [x] `preview_hosting_ready` — Free preview/static hosting works through GitHub Pages.
- [ ] `treasury_separated` — Exactly $115 is separated in the accounting envelope.
- [x] `dashboard_publish_path_ready` — A safe public path exists at `https://mapzimus.github.io/Genesis/`.
- [x] `acceptance_tests_passed` — The automated acceptance suite passes (17/17 on 2026-08-12).
- [x] `cold_resume_audit_passed` — A separate read-only task reconstructs the experiment state from repository files only. PASS on 2026-08-08 (v1.0.0). The 2026-08-12 pre-publication re-audit returned FAIL (`daily-reports/2026-08-12-migration-audit.md`); after the merge, the re-audit of `main` at `387e0c5` returned PASS (`daily-reports/2026-08-12-postmerge-audit.md`).
- [x] `routines_created` — Both Routines are created per `AUTOMATIONS.md`, disabled, with their IDs recorded in `READINESS_EVIDENCE.md`. An unresolved connector gap affecting the issue channels is recorded there and must be closed before enabling.
- [x] `operator_schedule_tested` — Operator cycle completed an **accepted** no-write manual dry run on 2026-08-15 against `main` at `10395c2`: served `claude-fable-5`, blocked at the readiness gate, changed nothing, left the lock intact (`daily-reports/2026-08-15-dry-runs-repeat.md`). The 2026-08-13 attempt was not accepted; both of its causes are now closed.
- [x] `close_schedule_tested` — Close cycle completed an **accepted** no-write manual dry run on 2026-08-15 under the same conditions and with the same result.

When all boxes are complete, record the evidence without credentials, calculate the three dates from the selected Day 1, update `STATE.json`, and only then activate the frozen goal and the Routines.

Never add a product idea, market recommendation, customer list, product name, domain, marketing copy, or strategic hint during readiness.
