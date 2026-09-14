import type { DecisionRecordInput, EvaluationResult, EvidenceLinkedFinancialAnalysisInput, FinancialAnalysisResult, FinancialSnapshotInput, InvestmentCommitteeReview, InvestmentCommitteeReviewInput, InvestmentMemory, RedTeamReview, RedTeamReviewInput, ResearchRuntimeService, RuntimeCaseInput, RuntimeCaseResult, RuntimeEvent, RuntimeMemo, RuntimeResearchCase, RuntimeRun, RuntimeRunControl, RuntimeTrace, ValuationScenarioInput, ValuationScenarios } from "@/services/research-runtime-service";

export class ResearchRuntimeRepository {
  constructor(private readonly service: ResearchRuntimeService) {}

  createCase(input: RuntimeCaseInput): Promise<RuntimeCaseResult> { return this.service.createCase(input); }
  getCases(): Promise<RuntimeResearchCase[]> { return this.service.getCases(); }
  createCaseRun(caseId: string): Promise<RuntimeCaseResult> { return this.service.createCaseRun(caseId); }
  getRun(runId: string): Promise<RuntimeRun> { return this.service.getRun(runId); }
  getCaseRuns(caseId: string): Promise<RuntimeRun[]> { return this.service.getCaseRuns(caseId); }
  getEvaluation(runId: string): Promise<EvaluationResult | null> { return this.service.getEvaluation(runId); }
  getEvents(runId: string): Promise<RuntimeEvent[]> { return this.service.getEvents(runId); }
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
  analyzeValuationScenarios(runId: string, input: ValuationScenarioInput): Promise<ValuationScenarios> { return this.service.analyzeValuationScenarios(runId, input); }
  createRedTeamReview(runId: string, input: RedTeamReviewInput): Promise<RuntimeRun> { return this.service.createRedTeamReview(runId, input); }
  getRedTeamReviews(runId: string): Promise<RedTeamReview[]> { return this.service.getRedTeamReviews(runId); }
  createInvestmentCommitteeReview(runId: string, input: InvestmentCommitteeReviewInput): Promise<RuntimeRun> { return this.service.createInvestmentCommitteeReview(runId, input); }
  getInvestmentCommitteeReviews(runId: string): Promise<InvestmentCommitteeReview[]> { return this.service.getInvestmentCommitteeReviews(runId); }
  recordDecision(runId: string, input: DecisionRecordInput): Promise<RuntimeRun> { return this.service.recordDecision(runId, input); }
}
