import { describe, expect, it } from "vitest";
import { DefaultResearchRepository } from "./research-repository";
import { MockResearchService } from "@/services/mock-research-service";
import type { ResearchService } from "@/services/research-service";
import type { ResearchSetup } from "@/domain/research";

describe("DefaultResearchRepository", () => {
  it("validates and returns clearly labelled mock Today data", async () => {
    const repository = new DefaultResearchRepository(new MockResearchService());
    const data = await repository.getToday();
    expect(data.fixtureNotice).toContain("Mock research data");
    expect(data.items).toHaveLength(12);
    expect(data.items[0].company.name).toBe("NVIDIA");
  });

  it("rejects an invalid service contract response", async () => {
    const service = { getToday: async () => ({ items: "invalid" }) } as unknown as ResearchService;
    const repository = new DefaultResearchRepository(service);
    await expect(repository.getToday()).rejects.toThrow();
  });

  it("creates an editable P0 plan through the typed mock boundary", async () => {
    const repository = new DefaultResearchRepository(new MockResearchService());
    const options = await repository.getResearchSetupOptions();
    const setup: ResearchSetup = {
      question: "Where will embodied intelligence create durable value over three years?",
      scope: "deep" as const,
      targetIds: [options.targets[0].id],
      timeRange: "3-years" as const,
      customTimeRange: "",
      sourceTypes: ["official", "research-papers"],
      attachmentNames: [],
    };
    const plan = await repository.proposeResearchPlan(setup);
    expect(plan.sections.map((section) => section.title)).toEqual(["Market", "Technology", "Competition", "Value Chain", "Risk"]);
    expect(plan.goal).toContain("disconfirming evidence");
    await expect(repository.createResearchCase({ setup, plan })).resolves.toEqual({ caseId: "case-value-pools", runId: "run-value-pools-01" });
  });

  it("persists plan changes and explicit run controls through the mock service", async () => {
    const repository = new DefaultResearchRepository(new MockResearchService());
    const workspace = await repository.getResearchCase("case-value-pools");
    const changedPlan = { ...workspace.plan, goal: "Updated analyst-controlled research goal" };
    await expect(repository.updateResearchPlan({ caseId: workspace.case.id, plan: changedPlan })).resolves.toMatchObject({ plan: { goal: changedPlan.goal } });
    await expect(repository.controlResearchRun({ caseId: workspace.case.id, action: "start" })).resolves.toMatchObject({ run: { status: "running", stage: "planning" } });
    await expect(repository.controlResearchRun({ caseId: workspace.case.id, action: "cancel" })).resolves.toMatchObject({ run: { status: "cancelled" } });
    await expect(repository.controlResearchRun({ caseId: workspace.case.id, action: "restart" })).resolves.toMatchObject({ run: { status: "running" } });
    await expect(repository.controlResearchRun({ caseId: workspace.case.id, action: "complete" })).resolves.toMatchObject({ run: { status: "completed" }, evidenceCoverage: 78 });
  });
});
