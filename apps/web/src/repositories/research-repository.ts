import {
  createResearchCaseInputSchema,
  createResearchCaseResultSchema,
  researchPlanSchema,
  researchSetupOptionsSchema,
  researchSetupSchema,
  todayDataSchema,
  type CreateResearchCaseInput,
  type CreateResearchCaseResult,
  type ResearchPlan,
  type ResearchSetup,
  type ResearchSetupOptions,
  type TodayData,
  researchCaseWorkspaceSchema,
  researchRunActionInputSchema,
  updatePlanInputSchema,
  type ResearchCaseWorkspace,
  type ResearchRunActionInput,
  type UpdatePlanInput,
} from "@/domain/research";
import type { ResearchService } from "@/services/research-service";

export interface ResearchRepository {
  getToday(): Promise<TodayData>;
  getResearchSetupOptions(): Promise<ResearchSetupOptions>;
  proposeResearchPlan(input: ResearchSetup): Promise<ResearchPlan>;
  createResearchCase(input: CreateResearchCaseInput): Promise<CreateResearchCaseResult>;
  getResearchCase(caseId: string): Promise<ResearchCaseWorkspace>;
  updateResearchPlan(input: UpdatePlanInput): Promise<ResearchCaseWorkspace>;
  controlResearchRun(input: ResearchRunActionInput): Promise<ResearchCaseWorkspace>;
}

export class DefaultResearchRepository implements ResearchRepository {
  constructor(private readonly service: ResearchService) {}
  async getToday() { return todayDataSchema.parse(await this.service.getToday()); }
  async getResearchSetupOptions() { return researchSetupOptionsSchema.parse(await this.service.getResearchSetupOptions()); }
  async proposeResearchPlan(input: ResearchSetup) {
    return researchPlanSchema.parse(await this.service.proposeResearchPlan(researchSetupSchema.parse(input)));
  }
  async createResearchCase(input: CreateResearchCaseInput) {
    return createResearchCaseResultSchema.parse(await this.service.createResearchCase(createResearchCaseInputSchema.parse(input)));
  }
  async getResearchCase(caseId: string) { return researchCaseWorkspaceSchema.parse(await this.service.getResearchCase(caseId)); }
  async updateResearchPlan(input: UpdatePlanInput) {
    return researchCaseWorkspaceSchema.parse(await this.service.updateResearchPlan(updatePlanInputSchema.parse(input)));
  }
  async controlResearchRun(input: ResearchRunActionInput) {
    return researchCaseWorkspaceSchema.parse(await this.service.controlResearchRun(researchRunActionInputSchema.parse(input)));
  }
}
