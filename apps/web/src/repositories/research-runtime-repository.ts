import type { FinancialAnalysisResult, FinancialSnapshotInput, InvestmentMemory, ResearchRuntimeService, RuntimeMemo, RuntimeTrace } from "@/services/research-runtime-service";

export class ResearchRuntimeRepository {
  constructor(private readonly service: ResearchRuntimeService) {}

  getTrace(runId: string): Promise<RuntimeTrace> {
    return this.service.getTrace(runId);
  }

  getMemo(runId: string): Promise<RuntimeMemo> { return this.service.getMemo(runId); }
  getMemory(target: string): Promise<InvestmentMemory> { return this.service.getMemory(target); }
  analyzeFinancials(snapshot: FinancialSnapshotInput): Promise<FinancialAnalysisResult> { return this.service.analyzeFinancials(snapshot); }
}
