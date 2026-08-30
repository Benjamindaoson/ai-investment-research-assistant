import { todayDataSchema, type TodayData } from "@/domain/research";
import type { ResearchService } from "@/services/research-service";

export interface ResearchRepository {
  getToday(): Promise<TodayData>;
}

export class DefaultResearchRepository implements ResearchRepository {
  constructor(private readonly service: ResearchService) {}
  async getToday() { return todayDataSchema.parse(await this.service.getToday()); }
}
