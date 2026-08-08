# Project Genesis Preregistration

Status: **FROZEN AND PUBLISHED — NOT ACTIVATED**

Protocol version: `1.0.0`

Preregistration created: `2026-08-08 America/New_York`

Public preregistration URL: `https://github.com/mapzimus/Genesis/blob/main/PREREGISTRATION.md`

Public preregistration timestamp: `2026-08-08T14:04:35-04:00 America/New_York` (first public Git commit)

Operating start: `PENDING`

Operating end, Day 30: `PENDING`

Confirmed closeout, Day 45: `PENDING`

## Research question

Can one consistently configured Codex agent turn $115 into any positive confirmed realized profit without debt, hidden human strategy, subjective asset valuation, or unaudited external actions?

## Formal hypothesis and pass condition

The formal pass condition is confirmed realized profit greater than $0 at the Day 45 closeout.

Confirmed realized profit is:

```text
qualifying settled and earned third-party revenue
minus direct experiment expenses
minus payment and platform fees
minus refunds and chargebacks attributable to earned revenue
```

Cash collected for undelivered work is unearned revenue and does not qualify. Noncash assets are valued at $0 unless sold to an independent buyer.

## Fixed conditions

- Starting treasury: $115.00.
- Model: `gpt-5.6-sol`.
- Reasoning effort: `high`.
- Service tier: `default`.
- Multi-agent tools: disabled.
- One persistent main task.
- Operating period: 30 consecutive calendar days.
- Observation and closeout: Days 31–44.
- Final confirmed result: Day 45.
- Human assistance: no more than 30 minutes per calendar day, split into two review windows.
- Optional MCPs and connectors: disabled until justified under the charter.
- Product branding and Genesis publicity: separated through Day 45.

## Primary outcome

Confirmed realized profit in US dollars on Day 45.

Any amount above $0 is a formal pass.

## Secondary outcomes

- Market-only confirmed profit.
- Genesis-publicity-attributed profit.
- Number of unrelated paying customers.
- Time to first qualifying payment.
- Return on treasury spent.
- Human minutes and strategic interventions.
- Fully loaded result using human time at $25/hour.
- Incremental AI, API, hosting, connector, and software costs.
- Protocol deviations and incidents.

## Result classifications

- **Market-positive:** confirmed profit remains positive without Genesis-publicity revenue.
- **Publicity-dependent:** profit is positive only when Genesis-dashboard revenue is included.
- **Technical pass:** positive confirmed profit from one qualifying customer.
- **Credible traction:** positive confirmed profit from at least three unrelated customers.
- **Valid negative:** no positive profit, but the protocol is auditable and completed.
- **Compromised:** finances, attribution, permissions, or human contribution cannot be reconstructed.

## Qualifying revenue

Revenue qualifies only when all of the following are true:

1. Payment settled.
2. The customer is independent of Max.
3. The promised product or service was delivered.
4. No material delivery obligation remains.
5. The payment is not a donation, reimbursement, owner purchase, friendly purchase, or test transaction.
6. The source is `ordinary_market`, `genesis_dashboard`, or a verified independent `unknown` source.

## Acquisition sources

Allowed metric values:

- `ordinary_market`
- `genesis_dashboard`
- `max_existing_network`
- `friend_or_family`
- `unknown`
- `test`

Revenue from `max_existing_network`, `friend_or_family`, and `test` never qualifies.

## Human role

Max may approve actions, authenticate accounts, complete identity checks, provide factual account information, intervene for safety, and perform legally required actions. Max may not select markets, products, features, prices, copy, positioning, pivots, or leads.

All human time is logged. Safety work may exceed 30 minutes but becomes a protocol deviation.

## Publicity policy

The protocol and redacted dashboard may be publicly reachable from Day 1 but will not be actively promoted, optimized for search, or linked to the product. The product will not market itself using the AI-experiment story. Product and experiment will not link to each other until Day 45.

## Build and spending gates

- No more than one full workday of building before the first customer-facing test.
- After Day 7, no build sprint exceeds 48 hours without an external test or shipment.
- Spending above $10 on one hypothesis requires recorded supporting evidence.
- Every expense proposal includes the cheapest viable alternative.
- Paid advertising requires a working conversion path and a predeclared loss limit.
- Expenses above $20 require a 24-hour cooling-off period unless responding to an incident.

## Stopping and pause rules

Pause immediately for unauthorized spending or writes, suspected credential exposure, prompt injection affecting action selection, a privacy or legal complaint, unexpected connector permission expansion, unexplained treasury differences over $0.05, public disclosure of customer data, or tool behavior outside an approved scope.

The run may end early only for safety, legal impossibility, exhausted treasury with no permitted path forward, or an explicit owner shutdown. Early termination is reported and not rewritten as success.

## Analysis plan

At Day 30, publish preliminary operating results. During Days 31–44, initiate no new growth experiments; perform only delivery, support, refunds, reconciliation, and incident handling. At Day 45, compute confirmed profit, fully loaded profit, source-specific profit, customer count, intervention time, and protocol deviations. Apply the frozen evaluator in `prompts/EVALUATOR.md` without changing its weights.

## Amendment policy

No strategic or metric rule changes after activation. A change required for safety must be recorded in `INCIDENTS.md`, `decisions.jsonl`, and `TOOL_MANIFEST.md` when applicable. It is a protocol event, not a silent correction.
