// @vitest-environment jsdom
import { cleanup, fireEvent, render, screen } from "@testing-library/react";
import { afterEach, beforeEach, describe, expect, it, vi } from "vitest";
import { ValuationScenarioForm } from "./valuation-scenario-form";
import type { RuntimeRun } from "@/services/research-runtime-service";

const mockMutation = vi.hoisted(() => ({ mutate: vi.fn(), isPending: false, isError: false, isSuccess: false, error: null as Error | null }));
vi.mock("@/queries/use-runtime-run", () => ({ useAnalyzeRuntimeValuationMutation: () => mockMutation }));
afterEach(cleanup);
beforeEach(() => { mockMutation.mutate.mockReset(); mockMutation.isPending = false; mockMutation.isError = false; mockMutation.isSuccess = false; mockMutation.error = null; });

const run = {
  id: "run-1", case_id: "case-1", state: "COMPLETED", tasks: [],
  evidence: [{ id: "evidence-1", source_title: "FY2025 filing", stance: "SUPPORTING", qualification: "QUALIFIED" }],
  claims: [], thesis: null, memo: null, financial_analysis: null, valuation_scenarios: null,
  red_team_reviews: [], decisions: [], tool_executions: [],
} as RuntimeRun;

describe("ValuationScenarioForm", () => {
  it("keeps submission disabled until every assumption and evidence source is present", async () => {
    render(<ValuationScenarioForm run={run} />);
    const submit = screen.getByRole("button", { name: "Save valuation scenarios" });
    expect(submit).toHaveProperty("disabled", true);

    for (const input of screen.getAllByRole("spinbutton")) fireEvent.change(input, { target: { value: "10" } });
    for (const select of screen.getAllByRole("combobox")) fireEvent.change(select, { target: { value: "evidence-1" } });
    expect(submit).toHaveProperty("disabled", false);
    fireEvent.click(submit);

    expect(mockMutation.mutate).toHaveBeenCalledWith(expect.objectContaining({
      base_revenue: "10",
      base_revenue_evidence_ids: ["evidence-1"],
      scenarios: expect.arrayContaining([expect.objectContaining({ name: "BULL", evidence_ids: expect.objectContaining({ revenue_growth_pct: ["evidence-1"] }) })]),
    }));
  });

  it("does not render new valuation work for a blocked run", () => {
    render(<ValuationScenarioForm run={{ ...run, state: "BLOCKED" }} />);
    expect(screen.queryByText("Build Bull / Base / Bear scenarios")).toBeNull();
  });

  it("shows the saved state and backend error without inventing an artifact", () => {
    mockMutation.isSuccess = true;
    const { rerender } = render(<ValuationScenarioForm run={run} />);
    expect(screen.getByRole("status").textContent).toContain("durable");
    mockMutation.isSuccess = false;
    mockMutation.isError = true;
    mockMutation.error = new Error("Evidence mapping rejected");
    rerender(<ValuationScenarioForm run={run} />);
    expect(screen.getByRole("alert").textContent).toContain("Evidence mapping rejected");
    expect(screen.queryByText("Valuation scenarios saved as a durable, evidence-linked artifact.")).toBeNull();
  });
});
