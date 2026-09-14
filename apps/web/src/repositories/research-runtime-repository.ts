import type { DecisionRecordInput, EvidenceLinkedFinancialAnalysisInput, FinancialAnalysisResult, FinancialSnapshotInput, InvestmentMemory, RedTeamReview, RedTeamReviewInput, ResearchRuntimeService, RuntimeCaseInput, RuntimeCaseResult, RuntimeMemo, RuntimeRun, RuntimeRunControl, RuntimeTrace, ValuationScenarios } from "@/services/research-runtime-service";

export class ResearchRuntimeRepository {
  constructor(private readonly service: ResearchRuntimeService) {}

  createCase(input: RuntimeCaseInput): Promise<RuntimeCaseResult> { return this.service.createCase(input); }
  getRun(runId: string): Promise<RuntimeRun> { return this.service.getRun(runId); }
  executeRun(runId: string): Promise<RuntimeRun> { return this.service.executeRun(runId); }
  replanRun(runId: string): Promise<RuntimeRun> { return this.service.replanRun(runId); }
  getTrace(runId: string): Promise<RuntimeTrace> {
    return this.service.getTrace(runId);
  }

  cancelRun(runId: string, reason: string): Promise<RuntimeRunControl> { return this.service.cancelRun(runId, reason); }
  getMemo(runId: string): Promise<RuntimeMemo> { return this.service.getMemo(runId); }
  getMemory(target: string): Promise<InvestmentMemory> { return this.service.getMemory(target); }
  getMemoryForRun(runId: string): Promise<InvestmentMemory> { return this.service.getMemoryForRun(runId); }
  analyzeFinancials(snapshot: FinancialSnapshotInput): Promise<FinancialAnalysisResult> { return this.service.analyzeFinancials(snapshot); }
  analyzeFinancialsForRun(runId: string, input: EvidenceLinkedFinancialAnalysisInput): Promise<FinancialAnalysisResult> {
    return this.service.analyzeFinancialsForRun(runId, input);
  }
  getFinancialAnalysisForRun(runId: string): Promise<FinancialAnalysisResult> { return this.service.getFinancialAnalysisForRun(runId); }
  getValuationScenarios(runId: string): Promise<ValuationScenarios> { return this.service.getValuationScenarios(runId); }
  createRedTeamReview(runId: string, input: RedTeamReviewInput): Promise<RuntimeRun> { return this.service.createRedTeamReview(runId, input); }
  getRedTeamReviews(runId: string): Promise<RedTeamReview[]> { return this.service.getRedTeamReviews(runId); }
  recordDecision(runId: string, input: DecisionRecordInput): Promise<RuntimeRun> { return this.service.recordDecision(runId, input); }
}
