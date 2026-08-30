import { mockTodayData } from "@/lib/mock/fixtures/today";
import { buildMockResearchPlan, mockResearchSetupOptions } from "@/lib/mock/fixtures/research-setup";
import { createResearchCaseInputSchema, researchSetupSchema } from "@/domain/research";
import { researchRunActionInputSchema, updatePlanInputSchema } from "@/domain/research";
import { mockResearchCaseWorkspace } from "@/lib/mock/fixtures/research-case";
import type { ResearchService } from "./research-service";

export class MockResearchService implements ResearchService {
  private researchCase = structuredClone(mockResearchCaseWorkspace);
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
}
