import type { OutputWorkspace } from "@/domain/research";

export const mockOutputWorkspace: OutputWorkspace = {
  fixtureNotice: "Synthetic research data — product demonstration only; not investment advice",
  reviewQueue: [
    { id: "review-claim-margin", kind: "claim", title: "AI infrastructure demand can support durable margins", detail: "Supporting evidence exists, but capacity-return counter-evidence needs analyst judgment.", status: "pending", priority: "high", evidenceIds: ["ev-demand", "ev-capex"] },
    { id: "review-finding-utilization", kind: "finding", title: "Utilization is the key return variable", detail: "Review whether backlog and capacity evidence justify the current High confidence label.", status: "pending", priority: "high", evidenceIds: ["ev-margin", "ev-capex"] },
    { id: "review-conflict-pricing", kind: "conflict", title: "Workflow lock-in versus bundled pricing", detail: "Sources conflict on whether integration depth protects standalone pricing power.", status: "pending", priority: "medium", evidenceIds: ["ev-retention", "ev-pricing"] },
    { id: "review-thesis-margin", kind: "thesis", title: "Northstar can compound, but capital intensity is decisive", detail: "Challenge the operating-leverage assumption before approving the current thesis.", status: "changes-requested", priority: "high", evidenceIds: ["ev-capex"] },
    { id: "review-brief-v3", kind: "brief", title: "Living Brief V3", detail: "Final analyst approval is required before this version becomes current.", status: "pending", priority: "medium", evidenceIds: [] },
  ],
  reviewAudit: [{ id: "audit-1", targetId: "review-thesis-margin", action: "changes-requested", note: "Add explicit pricing-pressure and utilization counter-cases.", actor: "Demo Analyst", occurredAt: "2026-08-30T10:30:00.000Z" }],
  brief: {
    id: "brief-margin-durability", title: "AI Infrastructure Margin Durability — Living Brief", status: "in-review", updatedAt: "2026-08-30T10:25:00.000Z",
    sections: [
      { key: "executive-summary", title: "Executive Summary", content: "AI infrastructure demand supports a credible growth and gross-margin opportunity, but utilization, pricing pressure, and capital intensity remain material counter-cases." },
      { key: "current-thesis", title: "Current Thesis", content: "Over the next three years, durable value may accrue to mission-critical infrastructure and workflow integration, provided incremental capacity earns an acceptable return." },
      { key: "key-findings", title: "Key Findings", content: "Demand is visible, utilization determines returns, and bundled alternatives are the most important competitive challenge." },
      { key: "industry-landscape", title: "Industry Landscape", content: "The stack spans semiconductors, data centers, cloud platforms, observability, security, and application software." },
      { key: "competitive-landscape", title: "Competitive Landscape", content: "Large cloud vendors bundle adjacent capabilities while specialist platforms compete through workflow depth, reliability, and customer integration." },
      { key: "technology-landscape", title: "Technology Landscape", content: "AI workloads are increasing infrastructure demand, while measurable reliability and unit-cost improvements remain uneven." },
      { key: "evidence", title: "Evidence", content: "Filings, transcripts, and industry disclosures support demand and integration signals; return evidence is more incomplete." },
      { key: "counter-evidence", title: "Counter Evidence", content: "Capacity built ahead of utilization and bundled pricing could reduce the addressable margin pool for independent platforms." },
      { key: "risks", title: "Risks", content: "Utilization, pricing, customer concentration, capital intensity, and competitive bundling are the primary risks." },
      { key: "catalysts", title: "Catalysts", content: "Higher renewal, scaled production workloads, improving cash conversion, and stable pricing would update the thesis." },
      { key: "open-questions", title: "Open Questions", content: "Will backlog convert into repeat workloads? Can utilization catch up with capacity? Which capabilities remain independently purchasable?" },
      { key: "analyst-notes", title: "Analyst Notes", content: "Maintain a challenged stance until cash conversion and third-party willingness to pay become clearer." },
    ],
  },
  versions: [
    { id: "v3", label: "V3 — Aug 30", createdAt: "2026-08-30T10:25:00.000Z", summary: "Counter-evidence increased and the thesis narrowed from broad AI growth to utilization and workflow economics.", changes: [{ kind: "thesis", label: "Thesis narrowed", before: "AI growth broadly captures excess value.", after: "Mission-critical infrastructure may capture defensible value with operating leverage." }, { kind: "evidence-added", label: "Capacity-return evidence added", before: "Not covered", after: "4 counter-evidence passages linked" }, { kind: "risk", label: "Pricing pressure elevated", before: "Medium", after: "High" }] },
    { id: "v2", label: "V2 — Aug 20", createdAt: "2026-08-20T14:00:00.000Z", summary: "Commercial timing weakened while retention and infrastructure evidence strengthened.", changes: [{ kind: "confidence", label: "Commercial confidence", before: "High", after: "Medium" }, { kind: "evidence-added", label: "Retention evidence", before: "3 sources", after: "7 sources" }] },
    { id: "v1", label: "V1 — Aug 12", createdAt: "2026-08-12T14:00:00.000Z", summary: "Initial evidence-backed research baseline.", changes: [] },
  ],
  library: [
    { id: "lib-paper-returns", title: "Measuring infrastructure utilization and returns", kind: "paper", industry: "AI Infrastructure", sourceType: "Paper", tags: ["returns", "utilization"], date: "2026-05-20", status: "verified" },
    { id: "lib-northstar-update", title: "Northstar Analytics operating update", kind: "company-document", company: "Northstar Analytics", industry: "AI Infrastructure", sourceType: "Official", tags: ["Northstar", "margins"], date: "2026-08-18", status: "verified" },
    { id: "lib-evidence-margin", title: "AI infrastructure margin evidence set", kind: "evidence", industry: "AI Infrastructure", sourceType: "Evidence", tags: ["margin", "counter-evidence"], date: "2026-08-30", status: "needs-review" },
    { id: "lib-report-market", title: "Enterprise infrastructure value-chain report", kind: "report", industry: "Enterprise Software", sourceType: "Industry Report", tags: ["value chain", "market"], date: "2026-08-01", status: "saved" },
    { id: "lib-upload-notes", title: "Analyst interview notes.pdf", kind: "uploaded-file", company: "Northstar Analytics", industry: "AI Infrastructure", sourceType: "User Upload", tags: ["interview", "commercialization"], date: "2026-08-27", status: "needs-review" },
    { id: "lib-source-earnings", title: "Earnings call transcript", kind: "saved-source", company: "Northstar Analytics", industry: "AI Infrastructure", sourceType: "Transcript", tags: ["retention", "capex"], date: "2026-08-29", status: "saved" },
  ],
};
