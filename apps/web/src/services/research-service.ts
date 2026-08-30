export interface ResearchService {
  getToday(): Promise<unknown>;
  getResearchSetupOptions(): Promise<unknown>;
  proposeResearchPlan(input: unknown): Promise<unknown>;
  createResearchCase(input: unknown): Promise<unknown>;
  getResearchCase(caseId: string): Promise<unknown>;
  updateResearchPlan(input: unknown): Promise<unknown>;
  controlResearchRun(input: unknown): Promise<unknown>;
}
