import type { ResearchCaseWorkspace } from "@/domain/research";
import { buildMockResearchPlan } from "./research-setup";

const question = "未来三年 AI 基础设施公司的利润池是否具备持久性？";
const setup = {
  question,
  scope: "deep" as const,
  targetIds: ["industry-infrastructure", "technology-ai-infra"],
  timeRange: "3-years" as const,
  customTimeRange: "",
  sourceTypes: ["official", "research-papers", "news", "filings", "transcripts"] as const,
  attachmentNames: [],
};

export const mockResearchCaseWorkspace: ResearchCaseWorkspace = {
  fixtureNotice: "Synthetic research data — product demonstration only; not investment advice",
  case: {
    id: "case-margin-durability",
    companyId: "industry-infrastructure",
    title: question,
    question,
    status: "in-research",
    priority: "high",
    openQuestion: "Will capital intensity and cloud pricing compress the apparent margin pool?",
    completedWork: "Research framing and plan review",
    updatedAt: "2026-08-30T09:30:00.000Z",
  },
  researchGoal: "Assess whether AI infrastructure and enterprise software can compound revenue and free cash flow without structurally worsening capital intensity or competitive pressure.",
  scope: "deep",
  evidenceCoverage: 18,
  plan: buildMockResearchPlan({ ...setup, sourceTypes: [...setup.sourceTypes] }),
  run: {
    id: "run-margin-durability-01",
    researchCaseId: "case-margin-durability",
    status: "queued",
    stage: "planning",
  },
  timeline: [
    { id: "event-planning", stage: "planning", label: "Planning research", detail: "Decomposing five research lenses and prioritizing counter-evidence." },
    { id: "event-searching", stage: "searching", label: "Searching primary sources", detail: "Scanning filings, earnings releases, transcripts, and market disclosures." },
    { id: "event-reading", stage: "reading", label: "Reading selected documents", detail: "Found 14 relevant documents and 3 financial disclosures for closer review." },
    { id: "event-extracting", stage: "extracting", label: "Extracting evidence", detail: "Linking source passages to claims with citation locations and reporting periods." },
    { id: "event-analyzing", stage: "analyzing", label: "Updating findings", detail: "Comparing growth, margin, reinvestment, and competitive value pools." },
    { id: "event-counter", stage: "counter-evidence", label: "Searching counter-evidence", detail: "Testing pricing pressure, customer concentration, and capex-return scenarios." },
    { id: "event-review", stage: "human-review", label: "Preparing analyst review", detail: "Flagging conflicts and conclusions that require human judgment." },
    { id: "event-complete", stage: "completed", label: "Research pass completed", detail: "Findings, evidence, and counter-evidence are ready for review." },
  ],
  findings: [
    {
      id: "finding-margin-pool",
      title: "AI infrastructure can support a durable margin pool, but only with operating leverage",
      summary: "Demand and pricing evidence support strong growth, while capital intensity and customer concentration constrain how much revenue converts to durable free cash flow.",
      confidence: "high",
      supportingSignals: ["Usage growth remains visible in customer disclosures", "Gross margin expands with workload scale", "Mission-critical workloads raise switching costs"],
      supportingEvidenceCount: 12,
      counterEvidenceCount: 3,
      revealedAtStage: "extracting",
    },
    {
      id: "finding-capex",
      title: "Capacity investment is productive only if utilization catches up",
      summary: "Accelerated infrastructure spending can extend the growth runway, but return evidence is uneven and depends on deployment timing.",
      confidence: "medium",
      supportingSignals: ["Backlog supports near-term demand", "New capacity is tied to contracted workloads"],
      supportingEvidenceCount: 8,
      counterEvidenceCount: 4,
      revealedAtStage: "analyzing",
    },
    {
      id: "finding-pricing",
      title: "Platform competition could compress independent software pricing",
      summary: "Large cloud and software vendors can bundle adjacent capabilities, weakening standalone pricing power even when product usage expands.",
      confidence: "needs-review",
      supportingSignals: ["Bundling is increasing across adjacent platforms", "Procurement behavior remains poorly disclosed"],
      supportingEvidenceCount: 5,
      counterEvidenceCount: 6,
      revealedAtStage: "counter-evidence",
    },
  ],
};
