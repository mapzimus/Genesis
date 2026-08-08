const money = new Intl.NumberFormat("en-US", { style: "currency", currency: "USD" });

const text = (id, value) => {
  document.getElementById(id).textContent = value;
};

fetch("public-summary.json", { cache: "no-store" })
  .then((response) => {
    if (!response.ok) throw new Error(`Dashboard data returned ${response.status}`);
    return response.json();
  })
  .then((data) => {
    text("status", data.status);
    text("day", data.day);
    text("phase", data.phase.replaceAll("_", " "));
    text("updated", new Date(data.generated_at).toLocaleString());
    text("starting-cash", money.format(data.starting_cash));
    text("current-cash", money.format(data.current_cash));
    text("earned-revenue", money.format(data.confirmed_earned_revenue));
    text("unearned-revenue", money.format(data.unearned_revenue_liability));
    text("costs", money.format(data.direct_expenses + data.fees + data.refunds_chargebacks));
    text("profit", money.format(data.confirmed_realized_profit));
    text("fully-loaded", money.format(data.fully_loaded_result));
    text("customers", data.qualifying_customers);
    text("market-profit", money.format(data.market_only_profit_conservative));
    text("publicity-revenue", money.format(data.publicity_earned_revenue));
    text("approvals", data.pending_approval_count);
    text("incidents", data.unresolved_incident_count);
    text("human-minutes", `${data.human_minutes} minutes`);
    text("notice", data.notice);
    text("protocol", data.protocol_version);
  })
  .catch((error) => {
    text("status", "Data unavailable");
    text("notice", error.message);
  });
