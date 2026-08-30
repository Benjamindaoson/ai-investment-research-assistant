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
  evidenceWorkspaceSchema,
  requestMoreResearchInputSchema,
  reviewClaimInputSchema,
  updateEvidenceStatusInputSchema,
  type EvidenceWorkspace,
  type RequestMoreResearchInput,
  type ReviewClaimInput,
  type UpdateEvidenceStatusInput,
  decisionWorkspaceSchema,
  updateThesisInputSchema,
  upsertDecisionItemInputSchema,
  type DecisionWorkspace,
  type UpdateThesisInput,
  type UpsertDecisionItemInput,
  outputWorkspaceSchema,
  performReviewInputSchema,
  updateBriefInputSchema,
  type OutputWorkspace,
  type PerformReviewInput,
  type UpdateBriefInput,
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
  getEvidenceWorkspace(caseId: string): Promise<EvidenceWorkspace>;
  updateEvidenceStatus(input: UpdateEvidenceStatusInput): Promise<EvidenceWorkspace>;
  reviewClaim(input: ReviewClaimInput): Promise<EvidenceWorkspace>;
  requestMoreResearch(input: RequestMoreResearchInput): Promise<EvidenceWorkspace>;
  getDecisionWorkspace(companyId: string): Promise<DecisionWorkspace>;
  updateThesis(input: UpdateThesisInput): Promise<DecisionWorkspace>;
  upsertDecisionItem(input: UpsertDecisionItemInput): Promise<DecisionWorkspace>;
  getOutputWorkspace(): Promise<OutputWorkspace>;
  performReview(input: PerformReviewInput): Promise<OutputWorkspace>;
  updateBrief(input: UpdateBriefInput): Promise<OutputWorkspace>;
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
  async getEvidenceWorkspace(caseId: string) { return evidenceWorkspaceSchema.parse(await this.service.getEvidenceWorkspace(caseId)); }
  async updateEvidenceStatus(input: UpdateEvidenceStatusInput) { return evidenceWorkspaceSchema.parse(await this.service.updateEvidenceStatus(updateEvidenceStatusInputSchema.parse(input))); }
  async reviewClaim(input: ReviewClaimInput) { return evidenceWorkspaceSchema.parse(await this.service.reviewClaim(reviewClaimInputSchema.parse(input))); }
  async requestMoreResearch(input: RequestMoreResearchInput) { return evidenceWorkspaceSchema.parse(await this.service.requestMoreResearch(requestMoreResearchInputSchema.parse(input))); }
  async getDecisionWorkspace(companyId: string) { return decisionWorkspaceSchema.parse(await this.service.getDecisionWorkspace(companyId)); }
  async updateThesis(input: UpdateThesisInput) { return decisionWorkspaceSchema.parse(await this.service.updateThesis(updateThesisInputSchema.parse(input))); }
  async upsertDecisionItem(input: UpsertDecisionItemInput) { return decisionWorkspaceSchema.parse(await this.service.upsertDecisionItem(upsertDecisionItemInputSchema.parse(input))); }
  async getOutputWorkspace() { return outputWorkspaceSchema.parse(await this.service.getOutputWorkspace()); }
  async performReview(input: PerformReviewInput) { return outputWorkspaceSchema.parse(await this.service.performReview(performReviewInputSchema.parse(input))); }
  async updateBrief(input: UpdateBriefInput) { return outputWorkspaceSchema.parse(await this.service.updateBrief(updateBriefInputSchema.parse(input))); }
}
