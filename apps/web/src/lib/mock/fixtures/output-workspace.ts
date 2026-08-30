import type { OutputWorkspace } from "@/domain/research";

export const mockOutputWorkspace: OutputWorkspace = {
  fixtureNotice: "Mock research data — for product demonstration only",
  reviewQueue: [
    { id: "review-claim-data", kind: "claim", title: "Robot data is a binding constraint", detail: "Strong supporting evidence exists, but synthetic-data counter-evidence needs analyst judgment.", status: "pending", priority: "high", evidenceIds: ["ev-pi-data", "ev-synthetic"] },
    { id: "review-finding-infra", kind: "finding", title: "Data infrastructure is an important value pool", detail: "Review whether financing and hiring signals justify the current High confidence label.", status: "pending", priority: "high", evidenceIds: ["ev-hiring", "ev-funding"] },
    { id: "review-conflict-synthetic", kind: "conflict", title: "Real-world versus synthetic data dependence", detail: "Sources conflict on how quickly synthetic data reduces real-world collection requirements.", status: "pending", priority: "medium", evidenceIds: ["ev-synthetic", "ev-paper-transfer"] },
    { id: "review-thesis-platform", kind: "thesis", title: "Infrastructure captures more value than whole robots", detail: "Challenge the vertical-integration assumption before approving the current thesis.", status: "changes-requested", priority: "high", evidenceIds: ["ev-vertical"] },
    { id: "review-brief-v3", kind: "brief", title: "Living Brief V3", detail: "Final analyst approval is required before this version becomes current.", status: "pending", priority: "medium", evidenceIds: [] },
  ],
  reviewAudit: [{ id: "audit-1", targetId: "review-thesis-platform", action: "changes-requested", note: "Add explicit vertical-integration counter-case.", actor: "Demo Analyst", occurredAt: "2026-08-30T10:30:00.000Z" }],
  brief: {
    id: "brief-value-pools", title: "Embodied Intelligence Value Pools — Living Brief", status: "in-review", updatedAt: "2026-08-30T10:25:00.000Z",
    sections: [
      { key: "executive-summary", title: "Executive Summary", content: "Robot data, model tooling, and deployment infrastructure appear positioned to capture meaningful value, but vertical integration and slow commercial adoption remain material counter-cases." },
      { key: "current-thesis", title: "Current Thesis", content: "Over the next three years, the most defensible value may accrue to data, model, and developer infrastructure rather than undifferentiated whole-robot manufacturing." },
      { key: "key-findings", title: "Key Findings", content: "Data quality remains a scaling constraint. Simulation complements real-world collection. Deployment reliability is a larger commercial bottleneck than demo capability." },
      { key: "industry-landscape", title: "Industry Landscape", content: "The stack spans robot OEMs, actuators, sensors, data collection, simulation, foundation models, training infrastructure, and deployment platforms." },
      { key: "competitive-landscape", title: "Competitive Landscape", content: "Tesla and integrated OEMs internalize more of the stack; Figure and 1X combine model and hardware; independent model and tooling companies compete for platform leverage." },
      { key: "technology-landscape", title: "Technology Landscape", content: "VLA models, world models, fleet learning, simulation, and data engines are converging, while robust cross-task generalization remains unproven." },
      { key: "evidence", title: "Evidence", content: "Hiring, technical releases, and financing support growing investment in robot-data and deployment infrastructure." },
      { key: "counter-evidence", title: "Counter Evidence", content: "Synthetic data efficiency and vertically integrated OEM stacks could reduce the addressable market for independent infrastructure." },
      { key: "risks", title: "Risks", content: "Technology reliability, commercialization timing, manufacturing economics, and platform absorption are the primary risks." },
      { key: "catalysts", title: "Catalysts", content: "Scaled paid deployments, new generalization benchmarks, major procurement orders, and infrastructure financing could update the thesis." },
      { key: "open-questions", title: "Open Questions", content: "Will pilots convert to repeat orders? How quickly can synthetic data close transfer gaps? Which stack layers remain independently purchasable?" },
      { key: "analyst-notes", title: "Analyst Notes", content: "Maintain a challenged stance until commercial repeatability and third-party willingness to pay become clearer." },
    ],
  },
  versions: [
    { id: "v3", label: "V3 — Aug 30", createdAt: "2026-08-30T10:25:00.000Z", summary: "Counter-evidence increased and the thesis narrowed from all infrastructure to data and deployment tooling.", changes: [{ kind: "thesis", label: "Thesis narrowed", before: "Infrastructure broadly captures excess value.", after: "Data and deployment tooling may capture defensible value." }, { kind: "evidence-added", label: "Synthetic-data paper added", before: "Not covered", after: "4 counter-evidence passages linked" }, { kind: "risk", label: "Vertical integration elevated", before: "Medium", after: "High" }] },
    { id: "v2", label: "V2 — Aug 20", createdAt: "2026-08-20T14:00:00.000Z", summary: "Commercial timing weakened while data-infrastructure evidence strengthened.", changes: [{ kind: "confidence", label: "Commercial confidence", before: "High", after: "Medium" }, { kind: "evidence-added", label: "Hiring evidence", before: "3 sources", after: "7 sources" }] },
    { id: "v1", label: "V1 — Aug 12", createdAt: "2026-08-12T14:00:00.000Z", summary: "Initial evidence-backed research baseline.", changes: [] },
  ],
  library: [
    { id: "lib-paper-vla", title: "Scaling synthetic-to-real transfer", kind: "paper", industry: "Embodied Intelligence", sourceType: "Paper", tags: ["VLA", "synthetic data"], date: "2026-05-20", status: "verified" },
    { id: "lib-figure-update", title: "Figure platform technical update", kind: "company-document", company: "Figure", industry: "Humanoid Robotics", sourceType: "Official", tags: ["Figure", "Helix"], date: "2026-08-18", status: "verified" },
    { id: "lib-evidence-data", title: "Robot data bottleneck evidence set", kind: "evidence", industry: "Robot Data", sourceType: "Evidence", tags: ["data", "counter-evidence"], date: "2026-08-30", status: "needs-review" },
    { id: "lib-report-market", title: "Embodied intelligence value-chain report", kind: "report", industry: "Embodied Intelligence", sourceType: "Industry Report", tags: ["value chain", "market"], date: "2026-08-01", status: "saved" },
    { id: "lib-upload-notes", title: "Analyst interview notes.pdf", kind: "uploaded-file", company: "Figure", industry: "Humanoid Robotics", sourceType: "User Upload", tags: ["interview", "commercialization"], date: "2026-08-27", status: "needs-review" },
    { id: "lib-source-hiring", title: "Manufacturing and deployment hiring page", kind: "saved-source", company: "Figure", industry: "Humanoid Robotics", sourceType: "Hiring", tags: ["talent", "manufacturing"], date: "2026-08-29", status: "saved" },
  ],
};
