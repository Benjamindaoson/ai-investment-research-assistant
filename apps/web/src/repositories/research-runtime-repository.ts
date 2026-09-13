import type { FinancialAnalysisResult, FinancialSnapshotInput, InvestmentMemory, ResearchRuntimeService, RuntimeCaseInput, RuntimeCaseResult, RuntimeMemo, RuntimeRun, RuntimeRunControl, RuntimeTrace } from "@/services/research-runtime-service";

export class ResearchRuntimeRepository {
  constructor(private readonly service: ResearchRuntimeService) {}

  createCase(input: RuntimeCaseInput): Promise<RuntimeCaseResult> { return this.service.createCase(input); }
  getRun(runId: string): Promise<RuntimeRun> { return this.service.getRun(runId); }
  executeRun(runId: string): Promise<RuntimeRun> { return this.service.executeRun(runId); }
  getTrace(runId: string): Promise<RuntimeTrace> {
    return this.service.getTrace(runId);
  }

  cancelRun(runId: string, reason: string): Promise<RuntimeRunControl> { return this.service.cancelRun(runId, reason); }
  getMemo(runId: string): Promise<RuntimeMemo> { return this.service.getMemo(runId); }
  getMemory(target: string): Promise<InvestmentMemory> { return this.service.getMemory(target); }
  getMemoryForRun(runId: string): Promise<InvestmentMemory> { return this.service.getMemoryForRun(runId); }
  analyzeFinancials(snapshot: FinancialSnapshotInput): Promise<FinancialAnalysisResult> { return this.service.analyzeFinancials(snapshot); }
}
