import type { ValuationScenarios } from "@/services/research-runtime-service";

export function RuntimeValuationScenarios({ artifact }: { artifact: ValuationScenarios }) {
  return <section className="decision-panel runtime-valuation-panel">
    <header><div><small>VALUATION SCENARIOS · ILLUSTRATIVE</small><h2>Explicit Bull / Base / Bear bridge</h2></div><span>v1 · Decimal</span></header>
    <div className="runtime-valuation-grid">
      <div className="runtime-valuation-header"><span>Scenario</span><span>Revenue</span><span>Operating income</span><span>FCF</span><span>Terminal value</span><span>Equity value</span><span>Value / share</span></div>
      {artifact.scenarios.map((scenario) => <div className="runtime-valuation-row" key={scenario.scenario}><b>{scenario.scenario}</b><span>{scenario.projected_revenue}</span><span>{scenario.projected_operating_income}</span><span>{scenario.free_cash_flow}</span><span>{scenario.terminal_value}</span><span>{scenario.equity_value}</span><strong>{scenario.value_per_share}</strong></div>)}
    </div>
    <p className="form-note">Illustrative terminal-value bridge only; assumptions are explicit and evidence-linked. This is not a price target or investment advice.</p>
  </section>;
}
