import type { ResearchRuntimeService, RuntimeTrace } from "@/services/research-runtime-service";

export class ResearchRuntimeRepository {
  constructor(private readonly service: ResearchRuntimeService) {}

  getTrace(runId: string): Promise<RuntimeTrace> {
    return this.service.getTrace(runId);
  }
}
