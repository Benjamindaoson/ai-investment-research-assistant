import { describe, expect, it } from "vitest";
import { DefaultResearchRepository } from "./research-repository";
import { MockResearchService } from "@/services/mock-research-service";

describe("DefaultResearchRepository", () => {
  it("validates and returns clearly labelled mock Today data", async () => {
    const repository = new DefaultResearchRepository(new MockResearchService());
    const data = await repository.getToday();
    expect(data.fixtureNotice).toContain("Mock research data");
    expect(data.items).toHaveLength(12);
    expect(data.items[0].company.name).toBe("NVIDIA");
  });

  it("rejects an invalid service contract response", async () => {
    const repository = new DefaultResearchRepository({ getToday: async () => ({ items: "invalid" }) });
    await expect(repository.getToday()).rejects.toThrow();
  });
});
