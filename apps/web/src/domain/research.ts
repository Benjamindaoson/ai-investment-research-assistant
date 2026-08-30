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
  kind: z.enum(["filing", "paper", "news", "interview", "dataset", "website"]),
});
export type Source = z.infer<typeof sourceSchema>;

export const evidenceSchema = z.object({
  id: z.string(),
  sourceId: z.string(),
  excerpt: z.string(),
  citation: z.string(),
  stance: z.enum(["supporting", "counter", "neutral"]),
  verificationStatus: z.enum(["unverified", "verified", "disputed"]),
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
