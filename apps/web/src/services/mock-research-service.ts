import { mockTodayData } from "@/lib/mock/fixtures/today";
import { buildMockResearchPlan, mockResearchSetupOptions } from "@/lib/mock/fixtures/research-setup";
import { createResearchCaseInputSchema, researchSetupSchema } from "@/domain/research";
import { researchRunActionInputSchema, updatePlanInputSchema } from "@/domain/research";
import { mockResearchCaseWorkspace } from "@/lib/mock/fixtures/research-case";
import { mockEvidenceWorkspace } from "@/lib/mock/fixtures/evidence-workspace";
import { requestMoreResearchInputSchema, reviewClaimInputSchema, updateEvidenceStatusInputSchema } from "@/domain/research";
import type { ResearchService } from "./research-service";
import { mockDecisionWorkspace } from "@/lib/mock/fixtures/decision-workspace";
import { updateThesisInputSchema, upsertDecisionItemInputSchema } from "@/domain/research";
import { mockOutputWorkspace } from "@/lib/mock/fixtures/output-workspace";
import { performReviewInputSchema, updateBriefInputSchema } from "@/domain/research";
import { updateFindingInputSchema } from "@/domain/research";

export class MockResearchService implements ResearchService {
  private researchCase = structuredClone(mockResearchCaseWorkspace);
  private evidenceWorkspace = structuredClone(mockEvidenceWorkspace);
  private decisionWorkspace = structuredClone(mockDecisionWorkspace);
  private outputWorkspace = structuredClone(mockOutputWorkspace);
  async getToday() {
    await Promise.resolve();
    return structuredClone(mockTodayData);
  }
  async getResearchSetupOptions() {
    await Promise.resolve();
    return structuredClone(mockResearchSetupOptions);
  }
  async proposeResearchPlan(input: unknown) {
    await Promise.resolve();
    return buildMockResearchPlan(researchSetupSchema.parse(input));
  }
  async createResearchCase(input: unknown) {
    await Promise.resolve();
    const parsed = createResearchCaseInputSchema.parse(input);
    this.researchCase.case.question = parsed.setup.question;
    this.researchCase.case.title = parsed.setup.question;
    this.researchCase.researchGoal = parsed.plan.goal;
    this.researchCase.plan = structuredClone(parsed.plan);
    this.researchCase.scope = parsed.setup.scope;
    this.researchCase.run.status = "queued";
    this.researchCase.run.stage = "planning";
    this.researchCase.evidenceCoverage = 0;
    return { caseId: "case-value-pools", runId: "run-value-pools-01" };
  }
  async getResearchCase(caseId: string) {
    await Promise.resolve();
    if (caseId !== this.researchCase.case.id) throw new Error(`Mock research case ${caseId} was not found.`);
    return structuredClone(this.researchCase);
  }
  async updateResearchPlan(input: unknown) {
    await Promise.resolve();
    const parsed = updatePlanInputSchema.parse(input);
    if (parsed.caseId !== this.researchCase.case.id) throw new Error(`Mock research case ${parsed.caseId} was not found.`);
    this.researchCase.plan = structuredClone(parsed.plan);
    return structuredClone(this.researchCase);
  }
  async controlResearchRun(input: unknown) {
    await Promise.resolve();
    const parsed = researchRunActionInputSchema.parse(input);
    if (parsed.caseId !== this.researchCase.case.id) throw new Error(`Mock research case ${parsed.caseId} was not found.`);
    if (parsed.action === "cancel") {
      this.researchCase.run.status = "cancelled";
      this.researchCase.case.status = "cancelled";
    } else if (parsed.action === "complete") {
      this.researchCase.run.status = "completed";
      this.researchCase.run.stage = "completed";
      this.researchCase.run.completedAt = "2026-08-30T09:40:00.000Z";
      this.researchCase.case.status = "awaiting-review";
      this.researchCase.evidenceCoverage = 78;
    } else {
      this.researchCase.run.status = "running";
      this.researchCase.run.stage = "planning";
      this.researchCase.run.startedAt = "2026-08-30T09:32:00.000Z";
      this.researchCase.run.completedAt = undefined;
      this.researchCase.case.status = "in-research";
    }
    return structuredClone(this.researchCase);
  }
  async updateFinding(input: unknown) {
    await Promise.resolve();
    const parsed = updateFindingInputSchema.parse(input);
    if (parsed.caseId !== this.researchCase.case.id) throw new Error("Mock research case was not found.");
    const index = this.researchCase.findings.findIndex((finding) => finding.id === parsed.finding.id);
    if (index < 0) throw new Error("Mock finding was not found.");
    this.researchCase.findings[index] = structuredClone(parsed.finding);
    return structuredClone(this.researchCase);
  }
  async getEvidenceWorkspace(caseId: string) {
    await Promise.resolve();
    if (caseId !== this.evidenceWorkspace.caseId) throw new Error(`Mock evidence workspace ${caseId} was not found.`);
    return structuredClone(this.evidenceWorkspace);
  }
  async updateEvidenceStatus(input: unknown) {
    await Promise.resolve();
    const parsed = updateEvidenceStatusInputSchema.parse(input);
    const evidence = this.evidenceWorkspace.evidence.find((item) => item.id === parsed.evidenceId);
    if (!evidence || parsed.caseId !== this.evidenceWorkspace.caseId) throw new Error("Mock evidence was not found.");
    evidence.verificationStatus = parsed.status;
    this.evidenceWorkspace.reviewLog.unshift({ id: `review-${this.evidenceWorkspace.reviewLog.length + 1}`, action: "evidence-status-changed", targetId: evidence.id, summary: `Evidence status changed to ${parsed.status}.`, actor: "Demo Analyst", occurredAt: "2026-08-30T10:00:00.000Z" });
    return structuredClone(this.evidenceWorkspace);
  }
  async reviewClaim(input: unknown) {
    await Promise.resolve();
    const parsed = reviewClaimInputSchema.parse(input);
    const claim = this.evidenceWorkspace.claims.find((item) => item.id === parsed.claimId);
    if (!claim || parsed.caseId !== this.evidenceWorkspace.caseId) throw new Error("Mock claim was not found.");
    claim.status = parsed.decision === "approve" ? "supported" : "rejected";
    this.evidenceWorkspace.reviewLog.unshift({ id: `review-${this.evidenceWorkspace.reviewLog.length + 1}`, action: parsed.decision === "approve" ? "claim-approved" : "claim-rejected", targetId: claim.id, summary: `Claim ${parsed.decision === "approve" ? "approved" : "rejected"} by analyst.`, actor: "Demo Analyst", occurredAt: "2026-08-30T10:01:00.000Z" });
    return structuredClone(this.evidenceWorkspace);
  }
  async requestMoreResearch(input: unknown) {
    await Promise.resolve();
    const parsed = requestMoreResearchInputSchema.parse(input);
    this.evidenceWorkspace.reviewLog.unshift({ id: `review-${this.evidenceWorkspace.reviewLog.length + 1}`, action: "more-research-requested", targetId: parsed.claimId, summary: parsed.question, actor: "Demo Analyst", occurredAt: "2026-08-30T10:02:00.000Z" });
    return structuredClone(this.evidenceWorkspace);
  }
  async getDecisionWorkspace(companyId: string) {
    await Promise.resolve();
    if (companyId !== this.decisionWorkspace.company.id) throw new Error(`Mock company workspace ${companyId} was not found.`);
    return structuredClone(this.decisionWorkspace);
  }
  async updateThesis(input: unknown) {
    await Promise.resolve();
    const parsed = updateThesisInputSchema.parse(input);
    if (parsed.companyId !== this.decisionWorkspace.company.id) throw new Error("Mock company was not found.");
    this.decisionWorkspace.currentThesis = structuredClone(parsed.thesis);
    return structuredClone(this.decisionWorkspace);
  }
  async upsertDecisionItem(input: unknown) {
    await Promise.resolve();
    const parsed = upsertDecisionItemInputSchema.parse(input);
    if (parsed.companyId !== this.decisionWorkspace.company.id) throw new Error("Mock company was not found.");
    const index = this.decisionWorkspace.decisionItems.findIndex((item) => item.id === parsed.item.id);
    if (index >= 0) this.decisionWorkspace.decisionItems[index] = structuredClone(parsed.item);
    else this.decisionWorkspace.decisionItems.unshift(structuredClone(parsed.item));
    return structuredClone(this.decisionWorkspace);
  }
  async getOutputWorkspace() { await Promise.resolve(); return structuredClone(this.outputWorkspace); }
  async performReview(input: unknown) {
    await Promise.resolve();
    const parsed = performReviewInputSchema.parse(input);
    const item = this.outputWorkspace.reviewQueue.find((entry) => entry.id === parsed.targetId);
    if (item && parsed.action !== "note-added") item.status = parsed.action === "brief-approved" ? "approved" : parsed.action;
    if (parsed.action === "brief-approved") this.outputWorkspace.brief.status = "approved";
    this.outputWorkspace.reviewAudit.unshift({ id: `audit-${this.outputWorkspace.reviewAudit.length + 1}`, targetId: parsed.targetId, action: parsed.action, note: parsed.note, actor: "Demo Analyst", occurredAt: "2026-08-30T10:40:00.000Z" });
    return structuredClone(this.outputWorkspace);
  }
  async updateBrief(input: unknown) {
    await Promise.resolve();
    const parsed = updateBriefInputSchema.parse(input);
    this.outputWorkspace.brief = structuredClone(parsed.brief);
    return structuredClone(this.outputWorkspace);
  }
}
