import { z } from "zod";

export const researchStatusSchema = z.enum([
  "needs-review",
  "in-research",
  "awaiting-review",
  "completed",
  "cancelled",
  "failed",
]);
export type ResearchStatus = z.infer<typeof researchStatusSchema>;

export const prioritySchema = z.enum(["low", "medium", "high"]);
export type Priority = z.infer<typeof prioritySchema>;

export const sourceSchema = z.object({
  id: z.string(),
  title: z.string(),
  publisher: z.string(),
  url: z.string().url(),
  publishedAt: z.string().datetime(),
  retrievedAt: z.string().datetime().optional(),
  author: z.string().optional(),
  kind: z.enum(["official", "filing", "paper", "patent", "github", "hiring", "interview", "news", "industry-report", "user-upload", "dataset", "website"]),
  originalDocument: z.string().optional(),
});
export type Source = z.infer<typeof sourceSchema>;

export const evidenceSchema = z.object({
  id: z.string(),
  sourceId: z.string(),
  excerpt: z.string(),
  citation: z.string(),
  stance: z.enum(["supporting", "counter", "neutral"]),
  verificationStatus: z.enum(["unverified", "verified", "partially-supported", "conflicting", "needs-review", "rejected"]),
});
export type Evidence = z.infer<typeof evidenceSchema>;

export const claimSchema = z.object({
  id: z.string(),
  statement: z.string(),
  evidenceIds: z.array(z.string()),
  confidence: z.number().min(0).max(1),
  status: z.enum(["draft", "supported", "challenged", "rejected"]),
});
export type Claim = z.infer<typeof claimSchema>;

export const thesisSchema = z.object({
  id: z.string(),
  title: z.string(),
  summary: z.string(),
  claimIds: z.array(z.string()),
  status: z.enum(["draft", "active", "under-review", "superseded"]),
  updatedAt: z.string().datetime(),
});
export type Thesis = z.infer<typeof thesisSchema>;

export const companySchema = z.object({
  id: z.string(),
  name: z.string(),
  ticker: z.string(),
  sector: z.string(),
  description: z.string().optional(),
});
export type Company = z.infer<typeof companySchema>;

export const researchCaseSchema = z.object({
  id: z.string(),
  companyId: z.string(),
  title: z.string(),
  question: z.string(),
  status: researchStatusSchema,
  priority: prioritySchema,
  openQuestion: z.string(),
  completedWork: z.string(),
  updatedAt: z.string().datetime(),
});
export type ResearchCase = z.infer<typeof researchCaseSchema>;

export const researchRunSchema = z.object({
  id: z.string(),
  researchCaseId: z.string(),
  status: z.enum(["queued", "running", "awaiting-review", "completed", "cancelled", "failed"]),
  stage: z.enum(["planning", "searching", "reading", "extracting", "analyzing", "counter-evidence", "human-review", "completed"]),
  startedAt: z.string().datetime().optional(),
  completedAt: z.string().datetime().optional(),
});
export type ResearchRun = z.infer<typeof researchRunSchema>;

export const activitySchema = z.object({
  id: z.string(),
  researchCaseId: z.string().optional(),
  kind: z.enum(["created", "started", "source-added", "evidence-extracted", "review-requested", "completed"]),
  summary: z.string(),
  occurredAt: z.string().datetime(),
});
export type Activity = z.infer<typeof activitySchema>;

export const todayResearchItemSchema = researchCaseSchema.extend({ company: companySchema });
export type TodayResearchItem = z.infer<typeof todayResearchItemSchema>;

export const todayOverviewSchema = z.object({
  updatedAtLabel: z.string(),
  stats: z.array(z.object({ label: z.string(), value: z.number(), kind: z.enum(["research", "progress", "review", "completed"]) })),
  coverage: z.array(z.object({ label: z.string(), value: z.number().min(0).max(100) })),
  triggers: z.array(z.object({ label: z.string(), value: z.number().min(0).max(100) })),
});
export type TodayOverview = z.infer<typeof todayOverviewSchema>;

export const todayDataSchema = z.object({
  fixtureNotice: z.literal("Mock research data — for product demonstration only"),
  items: z.array(todayResearchItemSchema),
  overview: todayOverviewSchema,
});
export type TodayData = z.infer<typeof todayDataSchema>;

export const researchScopeSchema = z.enum(["quick", "deep"]);
export type ResearchScope = z.infer<typeof researchScopeSchema>;

export const researchTargetKindSchema = z.enum(["company", "technology", "industry"]);
export const researchTargetSchema = z.object({
  id: z.string(),
  label: z.string(),
  kind: researchTargetKindSchema,
});
export type ResearchTarget = z.infer<typeof researchTargetSchema>;

export const researchSourceTypeSchema = z.enum([
  "official",
  "research-papers",
  "news",
  "github",
  "patents",
  "hiring",
  "uploaded-documents",
]);
export type ResearchSourceType = z.infer<typeof researchSourceTypeSchema>;

export const researchSetupSchema = z.object({
  question: z.string().trim().min(12, "Use at least 12 characters so the research goal is specific."),
  scope: researchScopeSchema,
  targetIds: z.array(z.string()).min(1, "Select at least one company, technology, or industry."),
  timeRange: z.enum(["12-months", "3-years", "custom"]),
  customTimeRange: z.string().optional(),
  sourceTypes: z.array(researchSourceTypeSchema).min(1, "Select at least one source type."),
  attachmentNames: z.array(z.string()),
}).superRefine((value, context) => {
  if (value.timeRange === "custom" && !value.customTimeRange?.trim()) {
    context.addIssue({ code: "custom", path: ["customTimeRange"], message: "Describe the custom time range." });
  }
});
export type ResearchSetup = z.infer<typeof researchSetupSchema>;

export const planTaskStatusSchema = z.enum(["completed", "running", "pending", "needs-review"]);
export const planTaskSchema = z.object({
  id: z.string(),
  question: z.string().min(3),
  priority: z.number().int().min(1),
  status: planTaskStatusSchema,
});
export type PlanTask = z.infer<typeof planTaskSchema>;

export const researchPlanSectionSchema = z.object({
  id: z.string(),
  title: z.enum(["Market", "Technology", "Competition", "Value Chain", "Risk"]),
  tasks: z.array(planTaskSchema).min(1),
});
export type ResearchPlanSection = z.infer<typeof researchPlanSectionSchema>;

export const researchPlanSchema = z.object({
  goal: z.string(),
  sections: z.array(researchPlanSectionSchema).min(1),
});
export type ResearchPlan = z.infer<typeof researchPlanSchema>;

export const researchSetupOptionsSchema = z.object({
  fixtureNotice: z.literal("Mock research data — for product demonstration only"),
  targets: z.array(researchTargetSchema),
  recommendedSourceTypes: z.array(researchSourceTypeSchema),
});
export type ResearchSetupOptions = z.infer<typeof researchSetupOptionsSchema>;

export const createResearchCaseInputSchema = z.object({
  setup: researchSetupSchema,
  plan: researchPlanSchema,
});
export type CreateResearchCaseInput = z.infer<typeof createResearchCaseInputSchema>;

export const createResearchCaseResultSchema = z.object({ caseId: z.string(), runId: z.string() });
export type CreateResearchCaseResult = z.infer<typeof createResearchCaseResultSchema>;

export const findingConfidenceSchema = z.enum(["high", "medium", "low", "needs-review"]);
export const researchFindingSchema = z.object({
  id: z.string(),
  title: z.string(),
  summary: z.string(),
  confidence: findingConfidenceSchema,
  supportingSignals: z.array(z.string()),
  supportingEvidenceCount: z.number().int().nonnegative(),
  counterEvidenceCount: z.number().int().nonnegative(),
  revealedAtStage: researchRunSchema.shape.stage,
});
export type ResearchFinding = z.infer<typeof researchFindingSchema>;

export const researchTimelineEventSchema = z.object({
  id: z.string(),
  stage: researchRunSchema.shape.stage,
  label: z.string(),
  detail: z.string(),
});
export type ResearchTimelineEvent = z.infer<typeof researchTimelineEventSchema>;

export const researchCaseWorkspaceSchema = z.object({
  fixtureNotice: z.literal("Mock research data — for product demonstration only"),
  case: researchCaseSchema,
  researchGoal: z.string(),
  scope: researchScopeSchema,
  evidenceCoverage: z.number().min(0).max(100),
  plan: researchPlanSchema,
  run: researchRunSchema,
  timeline: z.array(researchTimelineEventSchema),
  findings: z.array(researchFindingSchema),
});
export type ResearchCaseWorkspace = z.infer<typeof researchCaseWorkspaceSchema>;

export const updatePlanInputSchema = z.object({ caseId: z.string(), plan: researchPlanSchema });
export type UpdatePlanInput = z.infer<typeof updatePlanInputSchema>;

export const researchRunActionSchema = z.enum(["start", "cancel", "restart", "complete"]);
export type ResearchRunAction = z.infer<typeof researchRunActionSchema>;
export const researchRunActionInputSchema = z.object({ caseId: z.string(), action: researchRunActionSchema });
export type ResearchRunActionInput = z.infer<typeof researchRunActionInputSchema>;

export const evidenceWorkspaceSchema = z.object({
  fixtureNotice: z.literal("Mock research data — for product demonstration only"),
  caseId: z.string(),
  claims: z.array(claimSchema),
  evidence: z.array(evidenceSchema),
  sources: z.array(sourceSchema),
  reviewLog: z.array(z.object({
    id: z.string(),
    action: z.enum(["claim-approved", "claim-rejected", "evidence-status-changed", "more-research-requested"]),
    targetId: z.string(),
    summary: z.string(),
    actor: z.string(),
    occurredAt: z.string().datetime(),
  })),
});
export type EvidenceWorkspace = z.infer<typeof evidenceWorkspaceSchema>;

export const updateEvidenceStatusInputSchema = z.object({ caseId: z.string(), evidenceId: z.string(), status: evidenceSchema.shape.verificationStatus });
export type UpdateEvidenceStatusInput = z.infer<typeof updateEvidenceStatusInputSchema>;
export const reviewClaimInputSchema = z.object({ caseId: z.string(), claimId: z.string(), decision: z.enum(["approve", "reject"]) });
export type ReviewClaimInput = z.infer<typeof reviewClaimInputSchema>;
export const requestMoreResearchInputSchema = z.object({ caseId: z.string(), claimId: z.string(), question: z.string().min(5) });
export type RequestMoreResearchInput = z.infer<typeof requestMoreResearchInputSchema>;

export const companyResearchSectionSchema = z.object({
  id: z.string(),
  title: z.enum(["Technology", "Commercialization", "Competition", "Talent Signals", "Funding / Financial", "Risks"]),
  summary: z.string(),
  signals: z.array(z.string()),
  evidenceCount: z.number().int().nonnegative(),
});
export type CompanyResearchSection = z.infer<typeof companyResearchSectionSchema>;

export const structuredThesisSchema = z.object({
  id: z.string(),
  statement: z.string().min(10),
  status: z.enum(["draft", "active", "challenged", "approved"]),
  assumptions: z.array(z.object({ id: z.string(), statement: z.string(), status: z.enum(["supported", "uncertain", "challenged"]) })),
  supportingEvidenceIds: z.array(z.string()),
  counterEvidenceIds: z.array(z.string()),
  disconfirmingConditions: z.array(z.object({ id: z.string(), statement: z.string(), triggered: z.boolean() })),
  updatedAt: z.string().datetime(),
});
export type StructuredThesis = z.infer<typeof structuredThesisSchema>;

export const decisionItemSchema = z.object({
  id: z.string(),
  kind: z.enum(["risk", "catalyst", "monitor"]),
  category: z.string(),
  title: z.string().min(3),
  detail: z.string().min(3),
  status: z.enum(["active", "watching", "triggered", "resolved"]),
  importance: z.enum(["high", "medium", "low"]),
  evidenceIds: z.array(z.string()),
});
export type DecisionItem = z.infer<typeof decisionItemSchema>;

export const decisionWorkspaceSchema = z.object({
  fixtureNotice: z.literal("Mock research data — for product demonstration only"),
  company: companySchema,
  currentThesis: structuredThesisSchema,
  whatChanged: z.array(z.object({ id: z.string(), date: z.string(), kind: z.enum(["partnership", "product", "hiring", "technology", "funding"]), summary: z.string(), materiality: z.enum(["high", "medium", "low"]) })),
  companySections: z.array(companyResearchSectionSchema),
  evidenceCoverage: z.array(z.object({ label: z.string(), value: z.number().min(0).max(100) })),
  decisionItems: z.array(decisionItemSchema),
});
export type DecisionWorkspace = z.infer<typeof decisionWorkspaceSchema>;

export const updateThesisInputSchema = z.object({ companyId: z.string(), thesis: structuredThesisSchema });
export type UpdateThesisInput = z.infer<typeof updateThesisInputSchema>;
export const upsertDecisionItemInputSchema = z.object({ companyId: z.string(), item: decisionItemSchema });
export type UpsertDecisionItemInput = z.infer<typeof upsertDecisionItemInputSchema>;

export const reviewQueueItemSchema = z.object({
  id: z.string(),
  kind: z.enum(["claim", "finding", "evidence", "thesis", "conflict", "brief"]),
  title: z.string(),
  detail: z.string(),
  status: z.enum(["pending", "approved", "rejected", "changes-requested"]),
  priority: prioritySchema,
  evidenceIds: z.array(z.string()),
});
export type ReviewQueueItem = z.infer<typeof reviewQueueItemSchema>;
export const reviewAuditSchema = z.object({ id: z.string(), targetId: z.string(), action: z.enum(["approved", "rejected", "changes-requested", "note-added", "brief-approved"]), note: z.string().optional(), actor: z.string(), occurredAt: z.string().datetime() });
export type ReviewAudit = z.infer<typeof reviewAuditSchema>;

export const briefSectionKeySchema = z.enum(["executive-summary", "current-thesis", "key-findings", "industry-landscape", "competitive-landscape", "technology-landscape", "evidence", "counter-evidence", "risks", "catalysts", "open-questions", "analyst-notes"]);
export const livingBriefSchema = z.object({ id: z.string(), title: z.string(), status: z.enum(["draft", "in-review", "approved"]), updatedAt: z.string().datetime(), sections: z.array(z.object({ key: briefSectionKeySchema, title: z.string(), content: z.string() })) });
export type LivingBrief = z.infer<typeof livingBriefSchema>;
export const briefVersionSchema = z.object({ id: z.string(), label: z.string(), createdAt: z.string().datetime(), summary: z.string(), changes: z.array(z.object({ kind: z.enum(["thesis", "evidence-added", "evidence-removed", "risk", "confidence"]), label: z.string(), before: z.string(), after: z.string() })) });
export type BriefVersion = z.infer<typeof briefVersionSchema>;

export const libraryItemSchema = z.object({ id: z.string(), title: z.string(), kind: z.enum(["uploaded-file", "report", "paper", "company-document", "evidence", "saved-source"]), company: z.string().optional(), industry: z.string(), sourceType: z.string(), tags: z.array(z.string()), date: z.string(), status: z.enum(["verified", "needs-review", "saved"]) });
export type LibraryItem = z.infer<typeof libraryItemSchema>;

export const outputWorkspaceSchema = z.object({ fixtureNotice: z.literal("Mock research data — for product demonstration only"), reviewQueue: z.array(reviewQueueItemSchema), reviewAudit: z.array(reviewAuditSchema), brief: livingBriefSchema, versions: z.array(briefVersionSchema), library: z.array(libraryItemSchema) });
export type OutputWorkspace = z.infer<typeof outputWorkspaceSchema>;
export const performReviewInputSchema = z.object({ targetId: z.string(), action: z.enum(["approved", "rejected", "changes-requested", "note-added", "brief-approved"]), note: z.string().optional() });
export type PerformReviewInput = z.infer<typeof performReviewInputSchema>;
export const updateBriefInputSchema = z.object({ brief: livingBriefSchema });
export type UpdateBriefInput = z.infer<typeof updateBriefInputSchema>;
