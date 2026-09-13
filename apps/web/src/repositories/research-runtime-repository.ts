import type { FinancialAnalysisResult, FinancialSnapshotInput, InvestmentMemory, ResearchRuntimeService, RuntimeMemo, RuntimeRunControl, RuntimeTrace } from "@/services/research-runtime-service";

export class ResearchRuntimeRepository {
  constructor(private readonly service: ResearchRuntimeService) {}

  getTrace(runId: string): Promise<RuntimeTrace> {
    return this.service.getTrace(runId);
  }

  cancelRun(runId: string, reason: string): Promise<RuntimeRunControl> { return this.service.cancelRun(runId, reason); }
  getMemo(runId: string): Promise<RuntimeMemo> { return this.service.getMemo(runId); }
  getMemory(target: string): Promise<InvestmentMemory> { return this.service.getMemory(target); }
  analyzeFinancials(snapshot: FinancialSnapshotInput): Promise<FinancialAnalysisResult> { return this.service.analyzeFinancials(snapshot); }
}
