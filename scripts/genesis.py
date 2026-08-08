#!/usr/bin/env python3
"""Project Genesis protocol validator and operating utilities.

This module uses only the Python standard library so it can run before the
experiment selects a technology stack.
"""

from __future__ import annotations

import argparse
import csv
import hashlib
import json
import os
import re
import shutil
import sys
import uuid
from dataclasses import dataclass
from datetime import datetime, timedelta, timezone
from decimal import Decimal, InvalidOperation, ROUND_HALF_UP
from pathlib import Path
from typing import Any, Iterable


ROOT = Path(__file__).resolve().parents[1]
CENT = Decimal("0.01")
ALLOWED_SOURCES = {
    "ordinary_market",
    "genesis_dashboard",
    "max_existing_network",
    "friend_or_family",
    "unknown",
    "test",
}
NONQUALIFYING_SOURCES = {"max_existing_network", "friend_or_family", "test"}
NONQUALIFYING_COUNTERPARTIES = {"owner", "friend", "family", "test", "donor"}
TRUE_VALUES = {"true", "1", "yes"}
SECRET_PATTERNS = {
    "OpenAI-style key": re.compile(r"\bsk-[A-Za-z0-9_-]{16,}\b"),
    "AWS access key": re.compile(r"\bAKIA[0-9A-Z]{16}\b"),
    "private key": re.compile(r"-----BEGIN (?:RSA |EC |OPENSSH )?PRIVATE KEY-----"),
    "bearer token": re.compile(r"\bBearer\s+[A-Za-z0-9._~+/=-]{20,}", re.I),
    "email address": re.compile(r"\b[A-Z0-9._%+-]+@[A-Z0-9.-]+\.[A-Z]{2,}\b", re.I),
}


class GenesisError(RuntimeError):
    """A protocol or data error."""


@dataclass
class ValidationResult:
    errors: list[str]
    warnings: list[str]
    summary: dict[str, Any]

    @property
    def ok(self) -> bool:
        return not self.errors


def now_utc() -> datetime:
    return datetime.now(timezone.utc)


def iso_now() -> str:
    return now_utc().isoformat(timespec="seconds")


def parse_datetime(value: str | None, *, field: str) -> datetime:
    if not value:
        raise GenesisError(f"{field} is missing")
    try:
        parsed = datetime.fromisoformat(value.replace("Z", "+00:00"))
    except ValueError as exc:
        raise GenesisError(f"{field} is not valid ISO-8601: {value}") from exc
    if parsed.tzinfo is None:
        raise GenesisError(f"{field} must include a UTC offset: {value}")
    return parsed


def money(value: str | int | float | Decimal | None, *, field: str) -> Decimal:
    try:
        return Decimal(str(value or "0")).quantize(CENT, rounding=ROUND_HALF_UP)
    except (InvalidOperation, ValueError) as exc:
        raise GenesisError(f"{field} is not a valid monetary amount: {value}") from exc


def load_json(path: Path) -> Any:
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except FileNotFoundError as exc:
        raise GenesisError(f"Missing required file: {path}") from exc
    except json.JSONDecodeError as exc:
        raise GenesisError(f"Invalid JSON in {path}: {exc}") from exc


def save_json(path: Path, data: Any) -> None:
    temp = path.with_suffix(path.suffix + ".tmp")
    temp.write_text(json.dumps(data, indent=2) + "\n", encoding="utf-8")
    os.replace(temp, path)


def read_jsonl(path: Path) -> list[dict[str, Any]]:
    rows: list[dict[str, Any]] = []
    if not path.exists():
        raise GenesisError(f"Missing required file: {path}")
    for number, raw in enumerate(path.read_text(encoding="utf-8").splitlines(), start=1):
        if not raw.strip():
            continue
        try:
            item = json.loads(raw)
        except json.JSONDecodeError as exc:
            raise GenesisError(f"Invalid JSONL at {path}:{number}: {exc}") from exc
        if not isinstance(item, dict):
            raise GenesisError(f"JSONL item at {path}:{number} must be an object")
        rows.append(item)
    return rows


def append_jsonl(path: Path, item: dict[str, Any]) -> None:
    with path.open("a", encoding="utf-8", newline="\n") as handle:
        handle.write(json.dumps(item, separators=(",", ":")) + "\n")


def read_csv(path: Path) -> list[dict[str, str]]:
    try:
        with path.open("r", encoding="utf-8-sig", newline="") as handle:
            return list(csv.DictReader(handle))
    except FileNotFoundError as exc:
        raise GenesisError(f"Missing required file: {path}") from exc


def sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(65536), b""):
            digest.update(chunk)
    return digest.hexdigest()


def validate_config(errors: list[str]) -> None:
    path = ROOT / ".codex" / "config.toml"
    try:
        text = path.read_text(encoding="utf-8")
    except FileNotFoundError:
        errors.append("Missing .codex/config.toml")
        return
    required_fragments = [
        'model = "gpt-5.6-sol"',
        'model_reasoning_effort = "high"',
        'service_tier = "default"',
        'approval_policy = "on-request"',
        'sandbox_mode = "workspace-write"',
        "allow_login_shell = false",
        "[agents]\nenabled = false",
        "[sandbox_workspace_write]\nnetwork_access = false",
        "[mcp_servers.qgis]\nenabled = false",
        "[mcp_servers.node_repl]\nenabled = false",
        "[mcp_servers.firecrawl]\nenabled = false",
        '[apps._default]\ndefault_tools_approval_mode = "writes"',
        "destructive_enabled = false",
        "open_world_enabled = false",
    ]
    for fragment in required_fragments:
        if fragment not in text:
            errors.append(f"Codex config is missing fixed setting: {fragment!r}")


def validate_ledger(errors: list[str]) -> dict[str, Any]:
    rows = read_csv(ROOT / "treasury.csv")
    approvals = {row.get("approval_id", ""): row for row in read_csv(ROOT / "approvals.csv")}
    required = {
        "entry_id",
        "timestamp_et",
        "event_type",
        "counterparty_class",
        "acquisition_source",
        "cash_change",
        "earned_revenue_change",
        "unearned_revenue_change",
        "expense_amount",
        "fee_amount",
        "profit_refund_amount",
        "balance",
        "qualifying_revenue",
        "payment_settled",
        "fees_known",
        "delivered",
        "material_obligation_remaining",
        "transaction_valid",
        "independent_customer",
    }
    if not rows:
        errors.append("Treasury ledger has no starting entry")
        return {}
    missing = required - set(rows[0])
    if missing:
        errors.append(f"Treasury ledger is missing columns: {sorted(missing)}")
        return {}

    ids: set[str] = set()
    running_cash = Decimal("0.00")
    earned = Decimal("0.00")
    unearned = Decimal("0.00")
    expenses = Decimal("0.00")
    fees = Decimal("0.00")
    refunds = Decimal("0.00")
    market_earned = Decimal("0.00")
    publicity_earned = Decimal("0.00")

    for index, row in enumerate(rows, start=2):
        entry_id = row.get("entry_id", "").strip()
        if not entry_id:
            errors.append(f"treasury.csv:{index} has no entry_id")
        elif entry_id in ids:
            errors.append(f"treasury.csv:{index} duplicates entry_id {entry_id}")
        ids.add(entry_id)
        try:
            parse_datetime(row.get("timestamp_et"), field=f"treasury.csv:{index} timestamp_et")
            cash_change = money(row.get("cash_change"), field=f"treasury.csv:{index} cash_change")
            earned_change = money(
                row.get("earned_revenue_change"),
                field=f"treasury.csv:{index} earned_revenue_change",
            )
            unearned_change = money(
                row.get("unearned_revenue_change"),
                field=f"treasury.csv:{index} unearned_revenue_change",
            )
            expense = money(row.get("expense_amount"), field=f"treasury.csv:{index} expense_amount")
            fee = money(row.get("fee_amount"), field=f"treasury.csv:{index} fee_amount")
            refund = money(
                row.get("profit_refund_amount"),
                field=f"treasury.csv:{index} profit_refund_amount",
            )
            stated_balance = money(row.get("balance"), field=f"treasury.csv:{index} balance")
        except GenesisError as exc:
            errors.append(str(exc))
            continue

        source = row.get("acquisition_source", "").strip()
        if source not in ALLOWED_SOURCES:
            errors.append(f"treasury.csv:{index} has invalid acquisition_source {source!r}")

        running_cash = (running_cash + cash_change).quantize(CENT)
        if stated_balance != running_cash:
            errors.append(
                f"treasury.csv:{index} balance is {stated_balance}, expected {running_cash}"
            )
        if running_cash < 0:
            errors.append(f"treasury.csv:{index} produces negative treasury {running_cash}")

        earned += earned_change
        unearned += unearned_change
        expenses += expense
        fees += fee
        refunds += refund
        if unearned < 0:
            errors.append(f"treasury.csv:{index} produces negative unearned-revenue liability")
        if min(expense, fee, refund) < 0:
            errors.append(f"treasury.csv:{index} expense, fee, and refund amounts must be nonnegative")

        qualifying = row.get("qualifying_revenue", "").strip().lower() == "true"
        counterparty = row.get("counterparty_class", "").strip().lower()
        settled = row.get("payment_settled", "").strip().lower() in TRUE_VALUES
        fees_known = row.get("fees_known", "").strip().lower() in TRUE_VALUES
        delivered = row.get("delivered", "").strip().lower() in TRUE_VALUES
        obligation_remaining = (
            row.get("material_obligation_remaining", "").strip().lower() in TRUE_VALUES
        )
        transaction_valid = row.get("transaction_valid", "").strip().lower() in TRUE_VALUES
        independent = row.get("independent_customer", "").strip().lower() in TRUE_VALUES
        approval_id = row.get("approval_id", "").strip()

        if expense > 0:
            approval = approvals.get(approval_id)
            if not approval or approval.get("decision", "").strip().lower() != "approved":
                errors.append(f"treasury.csv:{index} expense lacks a matching approved approval_id")
        if earned_change > 0 and not all(
            [settled, fees_known, delivered, transaction_valid, independent]
        ):
            errors.append(
                f"treasury.csv:{index} recognizes earned revenue without settled payment, "
                "known fees, delivery, validity, and customer independence"
            )
        if earned_change > 0 and obligation_remaining:
            errors.append(f"treasury.csv:{index} recognizes earned revenue with work still owed")
        if qualifying and not all(
            [settled, fees_known, delivered, transaction_valid, independent]
        ):
            errors.append(f"treasury.csv:{index} qualifies revenue before every confirmation gate")
        if qualifying and obligation_remaining:
            errors.append(f"treasury.csv:{index} qualifies revenue with a material obligation")
        if qualifying and source in NONQUALIFYING_SOURCES:
            errors.append(f"treasury.csv:{index} improperly qualifies source {source}")
        if qualifying and counterparty in NONQUALIFYING_COUNTERPARTIES:
            errors.append(f"treasury.csv:{index} improperly qualifies counterparty {counterparty}")
        if qualifying and earned_change <= 0:
            errors.append(f"treasury.csv:{index} qualifies revenue without a positive earned change")
        if qualifying and source == "ordinary_market":
            market_earned += earned_change
        if qualifying and source == "genesis_dashboard":
            publicity_earned += earned_change

    profit = (earned - expenses - fees - refunds).quantize(CENT)
    market_profit = (market_earned - expenses - fees - refunds).quantize(CENT)
    return {
        "cash": float(running_cash),
        "earned_revenue": float(earned),
        "unearned_revenue": float(unearned),
        "expenses": float(expenses),
        "fees": float(fees),
        "refunds_chargebacks": float(refunds),
        "confirmed_realized_profit": float(profit),
        "market_only_profit_conservative": float(market_profit),
        "publicity_earned_revenue": float(publicity_earned),
        "entry_count": len(rows),
    }


def validate_secondary_costs(errors: list[str]) -> dict[str, Any]:
    intervention_rows = read_csv(ROOT / "interventions.csv")
    cost_rows = read_csv(ROOT / "economic-costs.csv")
    total_minutes = Decimal("0")
    minutes_by_day: dict[str, Decimal] = {}
    for index, row in enumerate(intervention_rows, start=2):
        try:
            timestamp = parse_datetime(
                row.get("timestamp_et"), field=f"interventions.csv:{index} timestamp_et"
            )
            minutes = Decimal(row.get("duration_minutes") or "0")
        except (GenesisError, InvalidOperation) as exc:
            errors.append(str(exc))
            continue
        if minutes < 0:
            errors.append(f"interventions.csv:{index} has negative duration")
            continue
        total_minutes += minutes
        day = timestamp.astimezone().date().isoformat()
        minutes_by_day[day] = minutes_by_day.get(day, Decimal("0")) + minutes
    for day, minutes in minutes_by_day.items():
        if minutes > 30:
            matching = [
                row
                for row in intervention_rows
                if row.get("timestamp_et", "").startswith(day)
            ]
            if not all(row.get("protocol_deviation", "").lower() in TRUE_VALUES for row in matching):
                errors.append(f"Human time exceeds 30 minutes on {day} without deviation records")

    incremental_unbooked = Decimal("0.00")
    imputed_free = Decimal("0.00")
    for index, row in enumerate(cost_rows, start=2):
        try:
            amount = money(row.get("amount_usd"), field=f"economic-costs.csv:{index} amount_usd")
        except GenesisError as exc:
            errors.append(str(exc))
            continue
        if amount < 0:
            errors.append(f"economic-costs.csv:{index} amount must be nonnegative")
            continue
        kind = row.get("cost_type", "").strip()
        already_booked = row.get("already_in_treasury", "").strip().lower() in TRUE_VALUES
        if kind not in {"ai_api_connector", "free_service_market_equivalent"}:
            errors.append(f"economic-costs.csv:{index} has unsupported cost_type {kind!r}")
        elif not already_booked and kind == "ai_api_connector":
            incremental_unbooked += amount
        elif not already_booked and kind == "free_service_market_equivalent":
            imputed_free += amount

    human_cost = (total_minutes / Decimal("60") * Decimal("25")).quantize(CENT)
    return {
        "human_minutes": float(total_minutes),
        "human_cost_at_25_per_hour": float(human_cost),
        "incremental_ai_connector_cost_not_in_treasury": float(incremental_unbooked),
        "imputed_free_service_cost": float(imputed_free),
    }


def validate_decisions(errors: list[str]) -> dict[str, Any]:
    rows = read_jsonl(ROOT / "decisions.jsonl")
    ids: set[str] = set()
    for index, row in enumerate(rows, start=1):
        decision_id = str(row.get("decision_id", "")).strip()
        if not decision_id:
            errors.append(f"decisions.jsonl:{index} has no decision_id")
        elif decision_id in ids:
            errors.append(f"decisions.jsonl:{index} duplicates decision_id {decision_id}")
        ids.add(decision_id)
        try:
            parse_datetime(row.get("timestamp_et"), field=f"decisions.jsonl:{index} timestamp_et")
        except GenesisError as exc:
            errors.append(str(exc))
        evidence = row.get("evidence", {})
        if not isinstance(evidence, dict):
            errors.append(f"decisions.jsonl:{index} evidence must be an object")
        elif not all(
            key in evidence
            for key in ["observed_facts", "third_party_claims", "inferences", "unknowns", "contrary"]
        ):
            errors.append(f"decisions.jsonl:{index} omits a required evidence category")
    return {"decision_count": len(rows)}


def validate_actions(errors: list[str]) -> dict[str, Any]:
    approvals = {row.get("approval_id", ""): row for row in read_csv(ROOT / "approvals.csv")}
    events = read_jsonl(ROOT / "external-actions.jsonl")
    completed: set[str] = set()
    planned: set[str] = set()
    for index, event in enumerate(events, start=1):
        action_id = str(event.get("action_id", "")).strip()
        status = str(event.get("status", "")).strip()
        if not action_id:
            errors.append(f"external-actions.jsonl:{index} has no action_id")
            continue
        if status == "planned":
            planned.add(action_id)
            approval_id = str(event.get("approval_id", "")).strip()
            approval = approvals.get(approval_id)
            if not approval:
                errors.append(f"Action {action_id} references missing approval {approval_id!r}")
            elif approval.get("decision", "").strip().lower() != "approved":
                errors.append(f"Action {action_id} references an approval that is not approved")
            decision_id = str(event.get("decision_id", "")).strip()
            decisions = {row.get("decision_id"): row for row in read_jsonl(ROOT / "decisions.jsonl")}
            decision = decisions.get(decision_id)
            if not decision or decision.get("record_type") != "sanitized_decision":
                errors.append(f"Action {action_id} lacks a sanitized decision record")
            elif decision.get("external_execution_permitted") is not True:
                errors.append(f"Action {action_id} decision does not permit external execution")
        elif status == "completed":
            if action_id in completed:
                errors.append(f"Action {action_id} has more than one completed event")
            if action_id not in planned:
                errors.append(f"Action {action_id} completed without an earlier planned event")
            completed.add(action_id)
        elif status not in {"failed", "cancelled"}:
            errors.append(f"Action {action_id} has unsupported status {status!r}")
    return {"planned_actions": len(planned), "completed_actions": len(completed)}


def scan_dashboard(errors: list[str]) -> None:
    dashboard = ROOT / "dashboard"
    for path in dashboard.rglob("*"):
        if not path.is_file() or path.suffix.lower() not in {".html", ".css", ".js", ".json", ".txt"}:
            continue
        text = path.read_text(encoding="utf-8", errors="replace")
        for label, pattern in SECRET_PATTERNS.items():
            if pattern.search(text):
                errors.append(f"Public dashboard contains possible {label}: {path.name}")


def validate_workspace() -> ValidationResult:
    errors: list[str] = []
    warnings: list[str] = []
    required_paths = [
        "PREREGISTRATION.md",
        "GENESIS_CHARTER.md",
        "AGENTS.md",
        ".codex/config.toml",
        "TOOL_MANIFEST.md",
        "STATE.json",
        "RUN_LOCK.json",
        "treasury.csv",
        "decisions.jsonl",
        "approvals.csv",
        "external-actions.jsonl",
        "interventions.csv",
        "metrics.csv",
        "economic-costs.csv",
        "INCIDENTS.md",
        "prompts/EVALUATOR.md",
    ]
    for relative in required_paths:
        if not (ROOT / relative).exists():
            errors.append(f"Missing required path: {relative}")

    validate_config(errors)
    try:
        ledger = validate_ledger(errors)
    except GenesisError as exc:
        errors.append(str(exc))
        ledger = {}
    try:
        secondary = validate_secondary_costs(errors)
    except GenesisError as exc:
        errors.append(str(exc))
        secondary = {}
    try:
        decisions = validate_decisions(errors)
    except GenesisError as exc:
        errors.append(str(exc))
        decisions = {}
    try:
        actions = validate_actions(errors)
    except GenesisError as exc:
        errors.append(str(exc))
        actions = {}
    try:
        state = load_json(ROOT / "STATE.json")
        if state.get("model") != {
            "name": "gpt-5.6-sol",
            "reasoning_effort": "high",
            "service_tier": "default",
            "subagents_enabled": False,
        }:
            errors.append("STATE.json model parameters do not match the frozen protocol")
        if ledger and money(state["treasury"]["current_cash"], field="state current_cash") != money(
            ledger["cash"], field="ledger cash"
        ):
            errors.append("STATE.json current_cash does not match treasury.csv")
        if state.get("status") == "active" and not all(state.get("readiness", {}).values()):
            errors.append("Experiment is active while readiness items remain false")
        required_state_keys = {
            "status", "phase", "current_day", "treasury", "active_initiatives",
            "pending_approvals", "pending_external_actions", "customer_obligations",
            "unresolved_incidents", "next_permitted_action", "readiness",
        }
        missing_state = required_state_keys - set(state)
        if missing_state:
            errors.append(f"STATE.json is not cold-resumable; missing {sorted(missing_state)}")
        if state.get("status") == "readiness":
            warnings.append("Experiment remains in readiness mode; Day 1 has not started")
    except (GenesisError, KeyError, TypeError) as exc:
        errors.append(f"STATE.json validation failed: {exc}")
        state = {}

    try:
        lock = load_json(ROOT / "RUN_LOCK.json")
        if lock.get("status") not in {"idle", "active"}:
            errors.append("RUN_LOCK.json status must be idle or active")
        if lock.get("status") == "active":
            heartbeat = parse_datetime(lock.get("last_heartbeat"), field="RUN_LOCK last_heartbeat")
            if now_utc() - heartbeat > timedelta(hours=2):
                warnings.append("RUN_LOCK.json contains a stale active lock requiring explicit recovery")
    except GenesisError as exc:
        errors.append(str(exc))

    try:
        read_jsonl(ROOT / "decisions.jsonl")
    except GenesisError as exc:
        errors.append(str(exc))
    scan_dashboard(errors)

    return ValidationResult(
        errors=errors,
        warnings=warnings,
        summary={
            "ledger": ledger,
            "secondary_costs": secondary,
            "decisions": decisions,
            "actions": actions,
            "status": state.get("status"),
        },
    )


def guard_path() -> Path:
    return ROOT / "RUN_LOCK.guard"


def acquire_guard() -> int:
    try:
        return os.open(guard_path(), os.O_CREAT | os.O_EXCL | os.O_WRONLY)
    except FileExistsError as exc:
        raise GenesisError("Another process is updating the run lock") from exc


def release_guard(fd: int) -> None:
    os.close(fd)
    guard_path().unlink(missing_ok=True)


def acquire_lock(task_type: str, expected_max_minutes: int, recover_stale: bool) -> str:
    fd = acquire_guard()
    try:
        path = ROOT / "RUN_LOCK.json"
        lock = load_json(path)
        if lock.get("status") == "active":
            heartbeat = parse_datetime(lock.get("last_heartbeat"), field="RUN_LOCK last_heartbeat")
            stale = now_utc() - heartbeat > timedelta(hours=2)
            if not stale:
                raise GenesisError(f"Run lock is active for run {lock.get('run_id')}")
            if not recover_stale:
                raise GenesisError("Run lock is stale; use --recover-stale after recording an incident")
            incident_text = (ROOT / "INCIDENTS.md").read_text(encoding="utf-8")
            recovery_marker = f"STALE_LOCK_RECOVERY: {lock.get('run_id')}"
            if recovery_marker not in incident_text:
                raise GenesisError(
                    f"Stale-lock recovery requires an INCIDENTS.md entry containing {recovery_marker!r}"
                )
        run_id = f"run-{uuid.uuid4()}"
        timestamp = iso_now()
        save_json(
            path,
            {
                "status": "active",
                "run_id": run_id,
                "task_type": task_type,
                "started_at": timestamp,
                "expected_max_minutes": expected_max_minutes,
                "last_heartbeat": timestamp,
                "released_at": None,
                "release_reason": None,
            },
        )
        return run_id
    finally:
        release_guard(fd)


def heartbeat(run_id: str) -> None:
    fd = acquire_guard()
    try:
        path = ROOT / "RUN_LOCK.json"
        lock = load_json(path)
        if lock.get("status") != "active" or lock.get("run_id") != run_id:
            raise GenesisError("Cannot heartbeat: run ID does not own the active lock")
        lock["last_heartbeat"] = iso_now()
        save_json(path, lock)
    finally:
        release_guard(fd)


def release_lock(run_id: str, reason: str) -> None:
    fd = acquire_guard()
    try:
        path = ROOT / "RUN_LOCK.json"
        lock = load_json(path)
        if lock.get("status") != "active" or lock.get("run_id") != run_id:
            raise GenesisError("Cannot release: run ID does not own the active lock")
        lock.update(
            {
                "status": "idle",
                "last_heartbeat": iso_now(),
                "released_at": iso_now(),
                "release_reason": reason,
            }
        )
        save_json(path, lock)
    finally:
        release_guard(fd)


def action_events(action_id: str) -> list[dict[str, Any]]:
    return [
        item
        for item in read_jsonl(ROOT / "external-actions.jsonl")
        if item.get("action_id") == action_id
    ]


def check_action(action_id: str) -> bool:
    return any(event.get("status") == "completed" for event in action_events(action_id))


def require_active_lock(run_id: str) -> None:
    lock = load_json(ROOT / "RUN_LOCK.json")
    if lock.get("status") != "active" or lock.get("run_id") != run_id:
        raise GenesisError("External action blocked: run ID does not own the active lock")


def sanitized_decision(decision_id: str) -> dict[str, Any]:
    records = [
        row for row in read_jsonl(ROOT / "decisions.jsonl") if row.get("decision_id") == decision_id
    ]
    if len(records) != 1:
        raise GenesisError(f"Sanitized decision {decision_id!r} was not found exactly once")
    record = records[0]
    if record.get("record_type") != "sanitized_decision":
        raise GenesisError("External action requires record_type=sanitized_decision")
    if record.get("external_execution_permitted") is not True:
        raise GenesisError("Sanitized decision does not permit external execution")
    return record


def approved_record(approval_id: str) -> dict[str, str]:
    records = [row for row in read_csv(ROOT / "approvals.csv") if row.get("approval_id") == approval_id]
    if len(records) != 1:
        raise GenesisError(f"Approval {approval_id!r} was not found exactly once")
    record = records[0]
    if record.get("decision", "").strip().lower() != "approved":
        raise GenesisError(f"Approval {approval_id!r} is not approved")
    expires = parse_datetime(record.get("expires_at_et"), field=f"approval {approval_id} expires_at_et")
    if expires < now_utc():
        raise GenesisError(f"Approval {approval_id!r} has expired")
    return record


def plan_action(
    action_id: str,
    action_type: str,
    approval_id: str,
    decision_id: str,
    run_id: str,
    description: str,
    scope_hash: str,
) -> None:
    require_active_lock(run_id)
    if action_events(action_id):
        raise GenesisError(f"Action {action_id!r} already exists")
    approval = approved_record(approval_id)
    sanitized_decision(decision_id)
    if approval.get("scope_hash") and approval.get("scope_hash") != scope_hash:
        raise GenesisError("Action scope hash does not match the approval")
    append_jsonl(
        ROOT / "external-actions.jsonl",
        {
            "event_id": f"evt-{uuid.uuid4()}",
            "action_id": action_id,
            "timestamp_et": iso_now(),
            "action_type": action_type,
            "status": "planned",
            "approval_id": approval_id,
            "decision_id": decision_id,
            "run_id": run_id,
            "scope_hash": scope_hash,
            "description": description,
        },
    )


def complete_action(action_id: str, run_id: str, result: str) -> None:
    require_active_lock(run_id)
    events = action_events(action_id)
    if not any(event.get("status") == "planned" for event in events):
        raise GenesisError("Action has no planned event")
    if any(event.get("status") == "completed" for event in events):
        raise GenesisError("Action is already completed; duplicate execution blocked")
    planned = next(event for event in events if event.get("status") == "planned")
    approved_record(str(planned.get("approval_id")))
    append_jsonl(
        ROOT / "external-actions.jsonl",
        {
            "event_id": f"evt-{uuid.uuid4()}",
            "action_id": action_id,
            "timestamp_et": iso_now(),
            "action_type": planned.get("action_type"),
            "status": "completed",
            "approval_id": planned.get("approval_id"),
            "decision_id": planned.get("decision_id"),
            "run_id": run_id,
            "scope_hash": planned.get("scope_hash"),
            "result": result,
        },
    )


def generate_dashboard(result: ValidationResult | None = None) -> Path:
    result = result or validate_workspace()
    if not result.ok:
        raise GenesisError("Cannot generate dashboard while validation errors exist")
    state = load_json(ROOT / "STATE.json")
    ledger = result.summary["ledger"]
    secondary = result.summary["secondary_costs"]
    metrics = read_csv(ROOT / "metrics.csv")
    paying_subjects = {
        row.get("anonymous_subject_id")
        for row in metrics
        if row.get("event_type") == "payment_confirmed"
        and row.get("qualifying", "").lower() == "true"
        and row.get("anonymous_subject_id")
    }
    payload = {
        "generated_at": iso_now(),
        "protocol_version": state["protocol_version"],
        "status": state["status"],
        "day": state["current_day"],
        "phase": state["phase"],
        "starting_cash": state["treasury"]["starting_cash"],
        "current_cash": ledger["cash"],
        "confirmed_earned_revenue": ledger["earned_revenue"],
        "unearned_revenue_liability": ledger["unearned_revenue"],
        "direct_expenses": ledger["expenses"],
        "fees": ledger["fees"],
        "refunds_chargebacks": ledger["refunds_chargebacks"],
        "confirmed_realized_profit": ledger["confirmed_realized_profit"],
        "market_only_profit_conservative": ledger["market_only_profit_conservative"],
        "publicity_earned_revenue": ledger["publicity_earned_revenue"],
        "qualifying_customers": len(paying_subjects),
        "active_hypothesis": state.get("active_hypothesis"),
        "pending_approval_count": len(state.get("pending_approvals", [])),
        "unresolved_incident_count": len(state.get("unresolved_incidents", [])),
        "human_minutes": secondary["human_minutes"],
        "human_cost_at_25_per_hour": secondary["human_cost_at_25_per_hour"],
        "incremental_ai_connector_cost_not_in_treasury": secondary[
            "incremental_ai_connector_cost_not_in_treasury"
        ],
        "imputed_free_service_cost": secondary["imputed_free_service_cost"],
        "fully_loaded_result": round(
            ledger["confirmed_realized_profit"]
            - secondary["human_cost_at_25_per_hour"]
            - secondary["incremental_ai_connector_cost_not_in_treasury"]
            - secondary["imputed_free_service_cost"],
            2,
        ),
        "notice": "AI-directed experiment operated by Max Howe. Customer data is excluded.",
    }
    destination = ROOT / "dashboard" / "public-summary.json"
    save_json(destination, payload)
    return destination


def create_snapshot(result: ValidationResult | None = None) -> Path:
    result = result or validate_workspace()
    if not result.ok:
        raise GenesisError("Cannot snapshot while validation errors exist")
    stamp = now_utc().strftime("%Y%m%dT%H%M%SZ")
    destination = ROOT / "snapshots" / stamp
    destination.mkdir(parents=False, exist_ok=False)
    for relative in [
        "STATE.json",
        "RUN_LOCK.json",
        "TOOL_MANIFEST.md",
        "treasury.csv",
        "approvals.csv",
        "external-actions.jsonl",
        "interventions.csv",
        "metrics.csv",
        "economic-costs.csv",
        "INCIDENTS.md",
        "decisions.jsonl",
        "PREREGISTRATION.md",
        "GENESIS_CHARTER.md",
    ]:
        shutil.copy2(ROOT / relative, destination / Path(relative).name)
    save_json(
        destination / "validation.json",
        {
            "validated_at": iso_now(),
            "errors": result.errors,
            "warnings": result.warnings,
            "summary": result.summary,
            "hashes": {
                path.name: sha256_file(path)
                for path in destination.iterdir()
                if path.is_file() and path.name != "validation.json"
            },
        },
    )
    return destination


def print_validation(result: ValidationResult) -> None:
    print("Project Genesis validation")
    print(f"Status: {'PASS' if result.ok else 'FAIL'}")
    for warning in result.warnings:
        print(f"WARNING: {warning}")
    for error in result.errors:
        print(f"ERROR: {error}")
    print(json.dumps(result.summary, indent=2))


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description=__doc__)
    commands = parser.add_subparsers(dest="command", required=True)
    commands.add_parser("validate", help="Validate the workspace without modifying it")

    acquire = commands.add_parser("acquire-lock", help="Acquire the atomic run lock")
    acquire.add_argument("--task", required=True, choices=["operator", "close", "audit", "manual"])
    acquire.add_argument("--expected-max-minutes", type=int, default=120)
    acquire.add_argument("--recover-stale", action="store_true")

    pulse = commands.add_parser("heartbeat", help="Refresh an owned run lock")
    pulse.add_argument("--run-id", required=True)

    release = commands.add_parser("release-lock", help="Release an owned run lock")
    release.add_argument("--run-id", required=True)
    release.add_argument("--reason", default="completed")

    check = commands.add_parser("check-action", help="Check whether an action already completed")
    check.add_argument("--action-id", required=True)

    plan = commands.add_parser("plan-action", help="Record an approved external action before execution")
    plan.add_argument("--action-id", required=True)
    plan.add_argument("--action-type", required=True)
    plan.add_argument("--approval-id", required=True)
    plan.add_argument("--decision-id", required=True)
    plan.add_argument("--run-id", required=True)
    plan.add_argument("--description", required=True)
    plan.add_argument("--scope-hash", required=True)

    complete = commands.add_parser("complete-action", help="Mark one planned external action completed")
    complete.add_argument("--action-id", required=True)
    complete.add_argument("--run-id", required=True)
    complete.add_argument("--result", required=True)

    commands.add_parser("dashboard", help="Generate redacted public dashboard data")
    commands.add_parser("snapshot", help="Create an auditable private snapshot")
    return parser


def main(argv: list[str] | None = None) -> int:
    args = build_parser().parse_args(argv)
    try:
        if args.command == "validate":
            result = validate_workspace()
            print_validation(result)
            return 0 if result.ok else 1
        if args.command == "acquire-lock":
            print(acquire_lock(args.task, args.expected_max_minutes, args.recover_stale))
            return 0
        if args.command == "heartbeat":
            heartbeat(args.run_id)
            print("heartbeat recorded")
            return 0
        if args.command == "release-lock":
            release_lock(args.run_id, args.reason)
            print("lock released")
            return 0
        if args.command == "check-action":
            completed = check_action(args.action_id)
            print("completed" if completed else "not completed")
            return 3 if completed else 0
        if args.command == "plan-action":
            plan_action(
                args.action_id,
                args.action_type,
                args.approval_id,
                args.decision_id,
                args.run_id,
                args.description,
                args.scope_hash,
            )
            print("action planned")
            return 0
        if args.command == "complete-action":
            complete_action(args.action_id, args.run_id, args.result)
            print("action completed")
            return 0
        if args.command == "dashboard":
            print(generate_dashboard())
            return 0
        if args.command == "snapshot":
            print(create_snapshot())
            return 0
    except GenesisError as exc:
        print(f"ERROR: {exc}", file=sys.stderr)
        return 2
    return 2


if __name__ == "__main__":
    raise SystemExit(main())
