from __future__ import annotations

import csv
import importlib.util
import json
import shutil
import sys
import tempfile
import unittest
from datetime import datetime, timedelta, timezone
from pathlib import Path


SOURCE_ROOT = Path(__file__).resolve().parents[1]
SPEC = importlib.util.spec_from_file_location("genesis", SOURCE_ROOT / "scripts" / "genesis.py")
genesis = importlib.util.module_from_spec(SPEC)
assert SPEC and SPEC.loader
sys.modules[SPEC.name] = genesis
SPEC.loader.exec_module(genesis)


class GenesisAcceptanceTests(unittest.TestCase):
    def setUp(self) -> None:
        self.temp = tempfile.TemporaryDirectory()
        self.root = Path(self.temp.name) / "Project-Genesis"
        shutil.copytree(
            SOURCE_ROOT,
            self.root,
            ignore=shutil.ignore_patterns(".git", "__pycache__", "*.pyc", "RUN_LOCK.guard"),
        )
        self.original_root = genesis.ROOT
        genesis.ROOT = self.root
        genesis.save_json(
            self.root / "RUN_LOCK.json",
            {
                "status": "idle",
                "run_id": None,
                "task_type": None,
                "started_at": None,
                "expected_max_minutes": None,
                "last_heartbeat": None,
                "released_at": None,
                "release_reason": None,
            },
        )

    def tearDown(self) -> None:
        genesis.ROOT = self.original_root
        self.temp.cleanup()

    def append_treasury(self, **updates: str) -> None:
        path = self.root / "treasury.csv"
        with path.open("r", encoding="utf-8", newline="") as handle:
            reader = csv.DictReader(handle)
            fields = list(reader.fieldnames or [])
        row = {field: "" for field in fields}
        row.update(
            {
                "entry_id": "tx-test",
                "timestamp_et": "2026-08-09T09:00:00-04:00",
                "event_type": "customer_payment",
                "description": "Acceptance fixture",
                "counterparty_class": "customer",
                "acquisition_source": "ordinary_market",
                "cash_change": "20.00",
                "earned_revenue_change": "0.00",
                "unearned_revenue_change": "20.00",
                "expense_amount": "0.00",
                "fee_amount": "0.00",
                "profit_refund_amount": "0.00",
                "balance": "135.00",
                "qualifying_revenue": "false",
                "payment_settled": "true",
                "fees_known": "true",
                "delivered": "false",
                "material_obligation_remaining": "true",
                "transaction_valid": "true",
                "independent_customer": "true",
            }
        )
        row.update(updates)
        with path.open("a", encoding="utf-8", newline="") as handle:
            csv.DictWriter(handle, fieldnames=fields).writerow(row)
        state = genesis.load_json(self.root / "STATE.json")
        state["treasury"]["current_cash"] = float(row["balance"])
        genesis.save_json(self.root / "STATE.json", state)

    def add_approval_and_decision(self, permitted: bool = True) -> None:
        approvals = self.root / "approvals.csv"
        with approvals.open("r", encoding="utf-8", newline="") as handle:
            fields = list(csv.DictReader(handle).fieldnames or [])
        row = {field: "" for field in fields}
        row.update(
            {
                "approval_id": "apr-1",
                "requested_at_et": "2026-08-08T09:00:00-04:00",
                "decided_at_et": "2026-08-08T09:01:00-04:00",
                "expires_at_et": "2099-01-01T00:00:00-05:00",
                "action_type": "publish",
                "description": "Publish fixture",
                "scope_hash": "a" * 64,
                "decision": "approved",
                "decided_by": "Max Howe",
            }
        )
        with approvals.open("a", encoding="utf-8", newline="") as handle:
            csv.DictWriter(handle, fieldnames=fields).writerow(row)
        decision = {
            "decision_id": "dec-1",
            "timestamp_et": "2026-08-08T08:00:00-04:00",
            "record_type": "sanitized_decision",
            "external_execution_permitted": permitted,
            "untrusted_instructions_detected": False,
            "evidence": {
                "observed_facts": [],
                "third_party_claims": [],
                "inferences": [],
                "unknowns": [],
                "contrary": [],
            },
        }
        (self.root / "decisions.jsonl").write_text(json.dumps(decision) + "\n", encoding="utf-8")

    def test_blank_workspace_reconciles_to_cent(self) -> None:
        result = genesis.validate_workspace()
        self.assertTrue(result.ok, result.errors)
        self.assertEqual(result.summary["ledger"]["cash"], 115.0)
        self.assertEqual(result.summary["ledger"]["confirmed_realized_profit"], 0.0)

    def test_unearned_cash_is_excluded_from_profit(self) -> None:
        self.append_treasury()
        result = genesis.validate_workspace()
        self.assertTrue(result.ok, result.errors)
        self.assertEqual(result.summary["ledger"]["unearned_revenue"], 20.0)
        self.assertEqual(result.summary["ledger"]["confirmed_realized_profit"], 0.0)

    def test_earned_revenue_requires_every_confirmation_gate(self) -> None:
        self.append_treasury(
            earned_revenue_change="20.00",
            unearned_revenue_change="0.00",
            qualifying_revenue="true",
            delivered="false",
        )
        result = genesis.validate_workspace()
        self.assertFalse(result.ok)
        self.assertTrue(any("recognizes earned revenue" in error for error in result.errors))

    def test_friend_or_test_revenue_cannot_qualify(self) -> None:
        self.append_treasury(
            earned_revenue_change="20.00",
            unearned_revenue_change="0.00",
            qualifying_revenue="true",
            delivered="true",
            material_obligation_remaining="false",
            acquisition_source="friend_or_family",
            counterparty_class="friend",
        )
        result = genesis.validate_workspace()
        self.assertFalse(result.ok)
        self.assertTrue(any("improperly qualifies" in error for error in result.errors))

    def test_wrong_running_balance_is_rejected(self) -> None:
        self.append_treasury(balance="134.99")
        result = genesis.validate_workspace()
        self.assertFalse(result.ok)
        self.assertTrue(any("expected 135.00" in error for error in result.errors))

    def test_overlapping_runs_are_blocked(self) -> None:
        run_id = genesis.acquire_lock("operator", 120, False)
        with self.assertRaises(genesis.GenesisError):
            genesis.acquire_lock("close", 120, False)
        genesis.release_lock(run_id, "acceptance test")

    def test_stale_lock_requires_incident_marker_and_explicit_recovery(self) -> None:
        old_id = "run-stale-fixture"
        stale = (datetime.now(timezone.utc) - timedelta(hours=3)).isoformat()
        genesis.save_json(
            self.root / "RUN_LOCK.json",
            {
                "status": "active",
                "run_id": old_id,
                "task_type": "operator",
                "started_at": stale,
                "expected_max_minutes": 120,
                "last_heartbeat": stale,
                "released_at": None,
                "release_reason": None,
            },
        )
        with self.assertRaises(genesis.GenesisError):
            genesis.acquire_lock("manual", 120, True)
        with (self.root / "INCIDENTS.md").open("a", encoding="utf-8") as handle:
            handle.write(f"\nSTALE_LOCK_RECOVERY: {old_id}\n")
        recovered = genesis.acquire_lock("manual", 120, True)
        genesis.release_lock(recovered, "acceptance test")

    def test_external_action_requires_active_lock_approval_and_sanitized_decision(self) -> None:
        self.add_approval_and_decision(permitted=False)
        run_id = genesis.acquire_lock("manual", 120, False)
        with self.assertRaises(genesis.GenesisError):
            genesis.plan_action("act-1", "publish", "apr-1", "dec-1", run_id, "fixture", "a" * 64)
        genesis.release_lock(run_id, "acceptance test")

    def test_duplicate_external_action_completion_is_blocked(self) -> None:
        self.add_approval_and_decision(permitted=True)
        run_id = genesis.acquire_lock("manual", 120, False)
        genesis.plan_action("act-1", "publish", "apr-1", "dec-1", run_id, "fixture", "a" * 64)
        genesis.begin_action("act-1", run_id)
        genesis.complete_action("act-1", run_id, "published")
        with self.assertRaises(genesis.GenesisError):
            genesis.complete_action("act-1", run_id, "published twice")
        genesis.release_lock(run_id, "acceptance test")

    def test_executing_action_blocks_automatic_retry_after_crash(self) -> None:
        self.add_approval_and_decision(permitted=True)
        run_id = genesis.acquire_lock("manual", 120, False)
        genesis.plan_action("act-1", "publish", "apr-1", "dec-1", run_id, "fixture", "a" * 64)
        genesis.begin_action("act-1", run_id)
        self.assertEqual(genesis.action_status("act-1"), "executing")
        with self.assertRaises(genesis.GenesisError):
            genesis.begin_action("act-1", run_id)
        genesis.release_lock(run_id, "acceptance test")

    def test_unapproved_expense_is_blocked(self) -> None:
        self.append_treasury(
            event_type="expense",
            cash_change="-5.00",
            unearned_revenue_change="0.00",
            expense_amount="5.00",
            balance="110.00",
        )
        result = genesis.validate_workspace()
        self.assertFalse(result.ok)
        self.assertTrue(any("expense lacks a matching approved" in error for error in result.errors))

    def test_public_dashboard_rejects_customer_email_or_secret(self) -> None:
        path = self.root / "dashboard" / "leak.txt"
        path.write_text("customer@example.com", encoding="utf-8")
        result = genesis.validate_workspace()
        self.assertFalse(result.ok)
        self.assertTrue(any("Public dashboard contains possible" in error for error in result.errors))

    def test_frozen_evaluator_has_all_weights(self) -> None:
        evaluator = (self.root / "prompts" / "EVALUATOR.md").read_text(encoding="utf-8")
        for weight in ["35 points", "20 points", "15 points", "10 points", "5 points"]:
            self.assertIn(weight, evaluator)
        self.assertIn("fully loaded sensitivity", evaluator)

    def test_frozen_model_config_is_enforced(self) -> None:
        settings_path = self.root / ".claude" / "settings.json"
        settings = genesis.load_json(settings_path)
        settings["model"] = "claude-haiku-4-5"
        settings["permissions"]["deny"] = []
        genesis.save_json(settings_path, settings)
        result = genesis.validate_workspace()
        self.assertFalse(result.ok)
        self.assertTrue(any('model = "claude-fable-5"' in error for error in result.errors))
        self.assertTrue(any("deny force pushes" in error for error in result.errors))

    def test_state_cannot_activate_with_incomplete_readiness(self) -> None:
        state = genesis.load_json(self.root / "STATE.json")
        state["status"] = "active"
        genesis.save_json(self.root / "STATE.json", state)
        result = genesis.validate_workspace()
        self.assertFalse(result.ok)
        self.assertTrue(any("readiness items remain false" in error for error in result.errors))

    def test_start_cycle_is_blocked_in_readiness_before_lock_acquisition(self) -> None:
        with self.assertRaises(genesis.GenesisError):
            genesis.start_cycle("operator", 120)
        lock = genesis.load_json(self.root / "RUN_LOCK.json")
        self.assertEqual(lock["status"], "idle")

    def test_start_cycle_acquires_lock_only_after_full_activation(self) -> None:
        state = genesis.load_json(self.root / "STATE.json")
        state["status"] = "active"
        state["current_day"] = 1
        state["experiment_start"] = "2026-08-09T00:00:00-04:00"
        state["readiness"] = {key: True for key in state["readiness"]}
        genesis.save_json(self.root / "STATE.json", state)
        run_id = genesis.start_cycle("operator", 120)
        lock = genesis.load_json(self.root / "RUN_LOCK.json")
        self.assertEqual(lock["status"], "active")
        self.assertEqual(lock["run_id"], run_id)
        genesis.release_lock(run_id, "acceptance test")


if __name__ == "__main__":
    unittest.main()
