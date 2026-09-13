import type { DecisionWorkspace } from "@/domain/research";

export const mockDecisionWorkspace: DecisionWorkspace = {
  fixtureNotice: "Synthetic research data — product demonstration only; not investment advice",
  company: { id: "northstar", name: "Northstar Analytics", ticker: "NSTAR", sector: "AI infrastructure software", description: "Synthetic public-company workspace for testing evidence-first financial analysis." },
  currentThesis: {
    id: "thesis-northstar-margin",
    statement: "Northstar can compound recurring revenue and gross profit through mission-critical AI infrastructure, but durable free cash flow depends on utilization catching up with capacity investment and pricing remaining rational.",
    status: "challenged",
    assumptions: [
      { id: "assumption-retention", statement: "Embedded customer workflows sustain net retention above the cost of new capacity.", status: "uncertain" },
      { id: "assumption-demand", statement: "Enterprise demand converts from pilots into repeat production workloads.", status: "challenged" },
      { id: "assumption-scale", statement: "Capacity can scale without structurally diluting free-cash-flow margins.", status: "uncertain" },
      { id: "assumption-platform", statement: "Workflow integration creates durable differentiation against bundled alternatives.", status: "supported" },
    ],
    supportingEvidenceIds: ["ev-demand", "ev-margin", "ev-retention"],
    counterEvidenceIds: ["ev-capex", "ev-pricing"],
    disconfirmingConditions: [
      { id: "condition-retention", statement: "Net retention falls below the cost of incremental infrastructure for two reporting periods.", triggered: false },
      { id: "condition-demand", statement: "Reported backlog does not convert into repeat paid production workloads.", triggered: false },
      { id: "condition-cost", statement: "Unit economics remain structurally below the hurdle rate after scaled deployment.", triggered: false },
    ],
    updatedAt: "2026-08-30T10:10:00.000Z",
  },
  whatChanged: [
    { id: "change-contracts", date: "2026-08-26", kind: "partnership", summary: "Synthetic enterprise contract pipeline expanded, but conversion evidence remains incomplete.", materiality: "high" },
    { id: "change-utilization", date: "2026-08-18", kind: "technology", summary: "New capacity came online before full utilization, increasing the return sensitivity of the thesis.", materiality: "medium" },
    { id: "change-hiring", date: "2026-08-11", kind: "hiring", summary: "Infrastructure and field-operations hiring increased across two locations.", materiality: "medium" },
  ],
  companySections: [
    { id: "company-technology", title: "Technology", summary: "AI infrastructure, workload reliability, and integration depth are the central technical bets.", signals: ["Workload reliability", "Integration depth", "Utilization curve"], evidenceCount: 14 },
    { id: "company-commercial", title: "Commercialization", summary: "Evidence supports active enterprise demand, while paid production scale and renewal behavior remain unclear.", signals: ["Customer pipeline", "Production conversion", "Renewal behavior"], evidenceCount: 9 },
    { id: "company-competition", title: "Competition", summary: "Cloud platforms and bundled software vendors pressure different layers of the standalone strategy.", signals: ["Bundled alternatives", "Switching costs", "Procurement concentration"], evidenceCount: 11 },
    { id: "company-talent", title: "Talent Signals", summary: "Hiring growth is concentrated in infrastructure, sales engineering, and reliability operations.", signals: ["Platform engineering", "Sales engineering", "Reliability"], evidenceCount: 7 },
    { id: "company-funding", title: "Funding / Financial", summary: "The roadmap is capital intensive; disclosed incremental returns remain limited.", signals: ["Capex intensity", "Cash conversion", "Funding access"], evidenceCount: 5 },
    { id: "company-risks", title: "Risks", summary: "Utilization, pricing, customer concentration, and bundled competition dominate the risk map.", signals: ["Utilization", "Pricing", "Customer concentration"], evidenceCount: 10 },
  ],
  evidenceCoverage: [{ label: "Technology", value: 86 }, { label: "Commercialization", value: 61 }, { label: "Competition", value: 74 }, { label: "Talent", value: 68 }, { label: "Financial", value: 42 }],
  decisionItems: [
    { id: "risk-technology", kind: "risk", category: "Technology Risk", title: "Infrastructure scale may not translate into durable utilization", detail: "Capacity and benchmark progress may fail to become repeat production workloads.", status: "active", importance: "high", evidenceIds: ["ev-capex"] },
    { id: "risk-commercial", kind: "risk", category: "Commercial Risk", title: "Conversion may take longer than market expectations", detail: "Pilots can remain bespoke and services-heavy without repeatable economics.", status: "watching", importance: "high", evidenceIds: ["ev-retention"] },
    { id: "risk-competitive", kind: "risk", category: "Competitive Risk", title: "Platform value may be absorbed by bundled alternatives", detail: "Large vendors can internalize adjacent capabilities and compress standalone pricing.", status: "active", importance: "medium", evidenceIds: ["ev-pricing"] },
    { id: "catalyst-deployment", kind: "catalyst", category: "Commercial", title: "Scaled production workload disclosed", detail: "A material multi-site deployment with repeat orders would strengthen the thesis.", status: "watching", importance: "high", evidenceIds: [] },
    { id: "catalyst-product", kind: "catalyst", category: "Technology", title: "Operating leverage demonstrated", detail: "Stable reliability at lower incremental cost would test platform differentiation.", status: "watching", importance: "medium", evidenceIds: [] },
    { id: "monitor-volume", kind: "monitor", category: "Demand", title: "Production workload volume", detail: "Track paid workloads, repeat orders, and active enterprise accounts.", status: "watching", importance: "high", evidenceIds: [] },
    { id: "monitor-cost", kind: "monitor", category: "Economics", title: "Unit and infrastructure cost", detail: "Track capacity utilization, depreciation, and per-workload cost.", status: "watching", importance: "high", evidenceIds: [] },
    { id: "monitor-retention", kind: "monitor", category: "Retention", title: "Net retention and expansion", detail: "Track renewal, expansion, and customer concentration signals.", status: "watching", importance: "medium", evidenceIds: [] },
    { id: "monitor-hiring", kind: "monitor", category: "Talent", title: "Platform and reliability hiring", detail: "Track operating investment and geographic expansion as business signals.", status: "watching", importance: "medium", evidenceIds: [] },
  ],
};
