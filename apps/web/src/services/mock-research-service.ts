import { mockTodayData } from "@/lib/mock/fixtures/today";
import { buildMockResearchPlan, mockResearchSetupOptions } from "@/lib/mock/fixtures/research-setup";
import { createResearchCaseInputSchema, researchSetupSchema } from "@/domain/research";
import type { ResearchService } from "./research-service";

export class MockResearchService implements ResearchService {
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
}
