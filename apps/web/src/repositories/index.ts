import { DefaultResearchRepository } from "./research-repository";
import { MockResearchService } from "@/services/mock-research-service";
import { createActorAwareRuntimeFetch } from "@/services/runtime-actor-fetch";
import { createResearchRuntimeService } from "@/services/research-runtime-service";
import { ResearchRuntimeRepository } from "./research-runtime-repository";

export const researchRepository = new DefaultResearchRepository(new MockResearchService());
export const researchRuntimeRepository = new ResearchRuntimeRepository(
  createResearchRuntimeService(
    process.env.NEXT_PUBLIC_RESEARCH_RUNTIME_URL,
    createActorAwareRuntimeFetch(fetch.bind(globalThis)),
  ),
);
