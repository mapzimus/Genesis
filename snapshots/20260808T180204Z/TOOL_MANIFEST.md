# Tool Manifest

Manifest version: `1.0.0`

Recorded: `2026-08-08 America/New_York`

## Fixed model parameters

| Parameter | Value |
|---|---|
| Model | `gpt-5.6-sol` |
| Reasoning effort | `high` |
| Service tier | `default` |
| Subagents | disabled |
| Sandbox | `workspace-write` |
| Approval policy | `on-request` |
| Shell network | disabled by default |
| Login shell | disabled |

## Day 0 permitted capabilities

- Project-local files and commands.
- Version control.
- Standard web search for research.
- Browser inspection and testing without unapproved external writes.

## Disabled optional MCPs

- `qgis`
- `node_repl`
- `firecrawl`

## Connector change record

No optional connector is currently authorized.

## Codex app automation

One paused same-task heartbeat (`genesis-operator-cycle`) is configured for the 9:00 AM operator and 6:00 PM close windows in America/New_York. It remains paused until both branches pass manual no-write dry runs and every other readiness gate is true. This is laboratory infrastructure, not an optional business connector.

Before enabling a connector, append a dated entry containing purpose, blocked capability, enabled tools, data scope, approval mode, cost, revocation test, prompt-injection test, and disabling condition.

## Connector policy

- Add connectors just in time.
- Use OAuth or environment-managed credentials.
- Never store credentials in this repository.
- Allowlist tools.
- Use `writes` approval mode or stricter.
- Block destructive and open-world tools unless explicitly approved.
- Verify revocation before production use.
- Disable the connector after its experiment ends.
