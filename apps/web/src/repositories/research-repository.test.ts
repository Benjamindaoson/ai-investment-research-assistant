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

  it("preserves evidence semantics, provenance, and analyst review mutations", async () => {
    const repository = new DefaultResearchRepository(new MockResearchService());
    const workspace = await repository.getEvidenceWorkspace("case-value-pools");
    expect(new Set(workspace.evidence.map((item) => item.stance))).toEqual(new Set(["supporting", "counter"]));
    expect(workspace.sources.every((source) => source.url && source.publishedAt)).toBe(true);
    const conflicting = workspace.evidence.find((item) => item.verificationStatus === "conflicting");
    expect(conflicting).toBeDefined();
    const changed = await repository.updateEvidenceStatus({ caseId: workspace.caseId, evidenceId: conflicting!.id, status: "verified" });
    expect(changed.evidence.find((item) => item.id === conflicting!.id)?.verificationStatus).toBe("verified");
    expect(changed.reviewLog[0].action).toBe("evidence-status-changed");
    const reviewed = await repository.reviewClaim({ caseId: workspace.caseId, claimId: workspace.claims[0].id, decision: "reject" });
    expect(reviewed.claims[0].status).toBe("rejected");
    const requested = await repository.requestMoreResearch({ caseId: workspace.caseId, claimId: workspace.claims[0].id, question: "Test whether synthetic data changes this conclusion." });
    expect(requested.reviewLog[0]).toMatchObject({ action: "more-research-requested", targetId: workspace.claims[0].id });
  });

  it("persists structured thesis and decision-workspace controls", async () => {
    const repository = new DefaultResearchRepository(new MockResearchService());
    const workspace = await repository.getDecisionWorkspace("figure");
    expect(workspace.companySections.map((section) => section.title)).toEqual(["Technology", "Commercialization", "Competition", "Talent Signals", "Funding / Financial", "Risks"]);
    expect(workspace.currentThesis.disconfirmingConditions.length).toBeGreaterThan(0);
    expect(workspace.decisionItems.some((item) => item.kind === "risk")).toBe(true);
    expect(workspace.decisionItems.some((item) => item.kind === "catalyst")).toBe(true);
    expect(workspace.decisionItems.some((item) => item.kind === "monitor")).toBe(true);
    const thesis = { ...workspace.currentThesis, status: "approved" as const, statement: `${workspace.currentThesis.statement} Analyst reviewed.` };
    await expect(repository.updateThesis({ companyId: "figure", thesis })).resolves.toMatchObject({ currentThesis: { status: "approved", statement: thesis.statement } });
    const risk = workspace.decisionItems.find((item) => item.kind === "risk")!;
    await expect(repository.upsertDecisionItem({ companyId: "figure", item: { ...risk, status: "triggered" } })).resolves.toMatchObject({ decisionItems: expect.arrayContaining([expect.objectContaining({ id: risk.id, status: "triggered" })]) });
  });

  it("supports human review, complete living briefs, versions, and library assets", async () => {
    const repository = new DefaultResearchRepository(new MockResearchService());
    const output = await repository.getOutputWorkspace();
    expect(output.brief.sections.map((section) => section.key)).toEqual(["executive-summary", "current-thesis", "key-findings", "industry-landscape", "competitive-landscape", "technology-landscape", "evidence", "counter-evidence", "risks", "catalysts", "open-questions", "analyst-notes"]);
    expect(output.versions[0].changes.some((change) => change.kind === "thesis")).toBe(true);
    expect(new Set(output.library.map((item) => item.kind))).toEqual(new Set(["uploaded-file", "report", "paper", "company-document", "evidence", "saved-source"]));
    const target = output.reviewQueue[0];
    const reviewed = await repository.performReview({ targetId: target.id, action: "approved", note: "Evidence checked." });
    expect(reviewed.reviewQueue.find((item) => item.id === target.id)?.status).toBe("approved");
    expect(reviewed.reviewAudit[0]).toMatchObject({ targetId: target.id, action: "approved", note: "Evidence checked." });
    const approved = await repository.performReview({ targetId: "review-brief-v3", action: "brief-approved" });
    expect(approved.brief.status).toBe("approved");
    const brief = { ...approved.brief, sections: approved.brief.sections.map((section) => section.key === "analyst-notes" ? { ...section, content: "Updated analyst judgment." } : section) };
    await expect(repository.updateBrief({ brief })).resolves.toMatchObject({ brief: { sections: expect.arrayContaining([expect.objectContaining({ key: "analyst-notes", content: "Updated analyst judgment." })]) } });
  });
});
