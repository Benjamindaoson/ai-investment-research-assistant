import { mockTodayData } from "@/lib/mock/fixtures/today";
import { buildMockResearchPlan, mockResearchSetupOptions } from "@/lib/mock/fixtures/research-setup";
import { createResearchCaseInputSchema, researchSetupSchema } from "@/domain/research";
import { researchRunActionInputSchema, updatePlanInputSchema } from "@/domain/research";
import { mockResearchCaseWorkspace } from "@/lib/mock/fixtures/research-case";
import { mockEvidenceWorkspace } from "@/lib/mock/fixtures/evidence-workspace";
import { requestMoreResearchInputSchema, reviewClaimInputSchema, updateEvidenceStatusInputSchema } from "@/domain/research";
import type { ResearchService } from "./research-service";

export class MockResearchService implements ResearchService {
  private researchCase = structuredClone(mockResearchCaseWorkspace);
  private evidenceWorkspace = structuredClone(mockEvidenceWorkspace);
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
    createResearchCaseInputSchema.parse(input);
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
}
