import { mockTodayData } from "@/lib/mock/fixtures/today";
import type { ResearchService } from "./research-service";

export class MockResearchService implements ResearchService {
  async getToday() {
    await Promise.resolve();
    return structuredClone(mockTodayData);
  }
}
