import type { DecisionWorkspace } from "@/domain/research";

export const mockDecisionWorkspace: DecisionWorkspace = {
  fixtureNotice: "Mock research data — for product demonstration only",
  company: { id: "figure", name: "Figure", ticker: "PRIVATE", sector: "Humanoid robotics", description: "Mock company workspace for general-purpose humanoid robotics research." },
  currentThesis: {
    id: "thesis-figure-platform",
    statement: "Figure is attempting to build a general-purpose robotics platform through foundation-model capability paired with commercial deployment, but manufacturing scale and task reliability remain decisive constraints.",
    status: "challenged",
    assumptions: [
      { id: "assumption-generalization", statement: "Helix-style models continue improving cross-task generalization.", status: "uncertain" },
      { id: "assumption-demand", statement: "Enterprise customers convert pilots into repeat deployments.", status: "challenged" },
      { id: "assumption-scale", statement: "Manufacturing can scale without degrading unit economics or reliability.", status: "uncertain" },
      { id: "assumption-stack", statement: "A vertically integrated model-plus-hardware stack creates durable differentiation.", status: "supported" },
    ],
    supportingEvidenceIds: ["ev-pi-data", "ev-hiring", "ev-funding"],
    counterEvidenceIds: ["ev-synthetic", "ev-vertical"],
    disconfirmingConditions: [
      { id: "condition-reliability", statement: "Task reliability fails to improve across real customer environments for two release cycles.", triggered: false },
      { id: "condition-pilots", statement: "Reported enterprise pilots do not convert into repeat paid deployments.", triggered: false },
      { id: "condition-cost", statement: "Unit economics remain structurally above addressable labor cost after scaled production.", triggered: false },
    ],
    updatedAt: "2026-08-30T10:10:00.000Z",
  },
  whatChanged: [
    { id: "change-partner", date: "2026-08-26", kind: "partnership", summary: "Mock enterprise deployment partnership expanded to a second workflow.", materiality: "high" },
    { id: "change-helix", date: "2026-08-18", kind: "technology", summary: "New manipulation demonstration increased task breadth but omitted reliability metrics.", materiality: "medium" },
    { id: "change-hiring", date: "2026-08-11", kind: "hiring", summary: "Manufacturing and field-operations hiring increased across two locations.", materiality: "medium" },
  ],
  companySections: [
    { id: "company-technology", title: "Technology", summary: "Foundation-model control, manipulation, data collection, and integrated hardware are the central technical bets.", signals: ["Helix / VLA roadmap", "Cross-task manipulation", "Fleet data engine"], evidenceCount: 14 },
    { id: "company-commercial", title: "Commercialization", summary: "Evidence supports active enterprise pilots, while paid deployment scale and renewal behavior remain unclear.", signals: ["Customer pilots", "Deployment reliability", "Manufacturing ramp"], evidenceCount: 9 },
    { id: "company-competition", title: "Competition", summary: "Tesla, 1X, Physical Intelligence, and Chinese OEMs pressure different layers of the integrated strategy.", signals: ["Tesla Optimus", "1X", "Physical Intelligence", "Chinese humanoid OEMs"], evidenceCount: 11 },
    { id: "company-talent", title: "Talent Signals", summary: "Hiring growth is concentrated in data operations, manufacturing, safety, and deployment engineering.", signals: ["Field operations", "Data curation", "Manufacturing engineering"], evidenceCount: 7 },
    { id: "company-funding", title: "Funding / Financial", summary: "Private funding supports a capital-intensive roadmap; disclosed unit economics remain limited.", signals: ["Private financing", "Capex intensity", "Undisclosed unit economics"], evidenceCount: 5 },
    { id: "company-risks", title: "Risks", summary: "Reliability, manufacturing yield, customer concentration, and vertically integrated competition dominate the risk map.", signals: ["Task reliability", "Yield and cost", "Pilot conversion"], evidenceCount: 10 },
  ],
  evidenceCoverage: [{ label: "Technology", value: 86 }, { label: "Commercialization", value: 61 }, { label: "Competition", value: 74 }, { label: "Talent", value: 68 }, { label: "Financial", value: 42 }],
  decisionItems: [
    { id: "risk-technology", kind: "risk", category: "Technology Risk", title: "VLA scaling may not translate into field reliability", detail: "Benchmark and demo progress may fail under long-tail customer conditions.", status: "active", importance: "high", evidenceIds: ["ev-paper-transfer"] },
    { id: "risk-commercial", kind: "risk", category: "Commercial Risk", title: "Commercialization may take longer than market expectations", detail: "Pilots can remain bespoke and services-heavy without repeatable economics.", status: "watching", importance: "high", evidenceIds: ["ev-vertical"] },
    { id: "risk-competitive", kind: "risk", category: "Competitive Risk", title: "Platform value may be absorbed by larger integrated players", detail: "OEMs and compute platforms can internalize data and development infrastructure.", status: "active", importance: "medium", evidenceIds: ["ev-vertical"] },
    { id: "catalyst-deployment", kind: "catalyst", category: "Commercial", title: "Scaled paid deployment disclosed", detail: "A material multi-site deployment with repeat orders would strengthen the thesis.", status: "watching", importance: "high", evidenceIds: [] },
    { id: "catalyst-model", kind: "catalyst", category: "Technology", title: "New foundation model release", detail: "Cross-task reliability and generalization metrics would test platform differentiation.", status: "watching", importance: "medium", evidenceIds: [] },
    { id: "monitor-volume", kind: "monitor", category: "Deployment", title: "Robot deployment volume", detail: "Track paid units, repeat orders, and active customer sites.", status: "watching", importance: "high", evidenceIds: [] },
    { id: "monitor-cost", kind: "monitor", category: "Economics", title: "Unit and inference cost", detail: "Track manufacturing cost-down and per-task inference expense.", status: "watching", importance: "high", evidenceIds: [] },
    { id: "monitor-data", kind: "monitor", category: "Data", title: "Training data scale", detail: "Track real-world hours, task diversity, and synthetic-to-real mix.", status: "watching", importance: "medium", evidenceIds: [] },
    { id: "monitor-hiring", kind: "monitor", category: "Talent", title: "Deployment and manufacturing hiring", detail: "Track role openings and geographic expansion as operating signals.", status: "watching", importance: "medium", evidenceIds: [] },
  ],
};
