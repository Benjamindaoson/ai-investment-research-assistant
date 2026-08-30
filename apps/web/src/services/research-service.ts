export interface ResearchService {
  getToday(): Promise<unknown>;
  getResearchSetupOptions(): Promise<unknown>;
  proposeResearchPlan(input: unknown): Promise<unknown>;
  createResearchCase(input: unknown): Promise<unknown>;
}
