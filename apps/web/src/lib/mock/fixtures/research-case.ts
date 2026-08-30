import type { ResearchCaseWorkspace } from "@/domain/research";
import { buildMockResearchPlan } from "./research-setup";

const question = "未来三年具身智能产业最大的价值池在哪里？";
const setup = {
  question,
  scope: "deep" as const,
  targetIds: ["industry-embodied", "technology-robot-data"],
  timeRange: "3-years" as const,
  customTimeRange: "",
  sourceTypes: ["official", "research-papers", "news", "patents", "hiring"] as const,
  attachmentNames: [],
};

export const mockResearchCaseWorkspace: ResearchCaseWorkspace = {
  fixtureNotice: "Mock research data — for product demonstration only",
  case: {
    id: "case-value-pools",
    companyId: "industry-embodied",
    title: question,
    question,
    status: "in-research",
    priority: "high",
    openQuestion: "Can synthetic data materially weaken the real-world data bottleneck?",
    completedWork: "Research framing and plan review",
    updatedAt: "2026-08-30T09:30:00.000Z",
  },
  researchGoal: "Identify large, defensible, commercially viable value pools in embodied intelligence where competition is not yet structurally fixed.",
  scope: "deep",
  evidenceCoverage: 18,
  plan: buildMockResearchPlan({ ...setup, sourceTypes: [...setup.sourceTypes] }),
  run: {
    id: "run-value-pools-01",
    researchCaseId: "case-value-pools",
    status: "queued",
    stage: "planning",
  },
  timeline: [
    { id: "event-planning", stage: "planning", label: "Planning research", detail: "Decomposing five research lenses and prioritizing counter-evidence." },
    { id: "event-searching", stage: "searching", label: "Searching official sources", detail: "Scanning company releases, patents, hiring pages, and industry disclosures." },
    { id: "event-reading", stage: "reading", label: "Reading selected documents", detail: "Found 14 relevant documents and 3 VLA papers for closer review." },
    { id: "event-extracting", stage: "extracting", label: "Extracting evidence", detail: "Linking source passages to claims with citation locations." },
    { id: "event-analyzing", stage: "analyzing", label: "Updating findings", detail: "Comparing data, model, simulation, hardware, and deployment value pools." },
    { id: "event-counter", stage: "counter-evidence", label: "Searching counter-evidence", detail: "Testing synthetic data, vertical integration, and weak generalization scenarios." },
    { id: "event-review", stage: "human-review", label: "Preparing analyst review", detail: "Flagging conflicts and conclusions that require human judgment." },
    { id: "event-complete", stage: "completed", label: "Research pass completed", detail: "Findings, evidence, and counter-evidence are ready for review." },
  ],
  findings: [
    {
      id: "finding-data-infra",
      title: "Robot data infrastructure is emerging as a critical value pool",
      summary: "Model developers and robot companies are expanding collection, curation, and evaluation infrastructure faster than broadly deployable robot volumes.",
      confidence: "high",
      supportingSignals: ["Multiple developers expanded data collection operations", "Foundation-model roadmaps cite data quality as a scaling constraint", "New financing targets robot-data infrastructure"],
      supportingEvidenceCount: 12,
      counterEvidenceCount: 3,
      revealedAtStage: "extracting",
    },
    {
      id: "finding-simulation",
      title: "Simulation is valuable, but unlikely to remove real-world data demand",
      summary: "Synthetic data expands edge-case coverage while transfer gaps preserve demand for real-world demonstrations and evaluation.",
      confidence: "medium",
      supportingSignals: ["Sim-to-real remains task dependent", "Hybrid datasets appear across recent technical releases"],
      supportingEvidenceCount: 8,
      counterEvidenceCount: 4,
      revealedAtStage: "analyzing",
    },
    {
      id: "finding-integration",
      title: "Vertical integration could compress independent infrastructure margins",
      summary: "Leading robot manufacturers may internalize training stacks, weakening third-party model and data suppliers.",
      confidence: "needs-review",
      supportingSignals: ["Several leaders are building proprietary collection systems", "Commercial procurement behavior remains poorly disclosed"],
      supportingEvidenceCount: 5,
      counterEvidenceCount: 6,
      revealedAtStage: "counter-evidence",
    },
  ],
};
