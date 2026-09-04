import { DefaultResearchRepository } from "./research-repository";
import { MockResearchService } from "@/services/mock-research-service";

export const researchRepository = new DefaultResearchRepository(new MockResearchService());
