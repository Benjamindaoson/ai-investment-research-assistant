// @vitest-environment jsdom
import { cleanup, render, screen } from "@testing-library/react";
import userEvent from "@testing-library/user-event";
import { afterEach, beforeEach, describe, expect, it, vi } from "vitest";
import { FinancialAnalysisForm } from "./financial-analysis-form";
import type { RuntimeRun } from "@/services/research-runtime-service";

const mockMutation = vi.hoisted(() => ({
  mutate: vi.fn(),
  isPending: false,
  isError: false,
  isSuccess: false,
  error: null as Error | null,
}));

vi.mock("@/queries/use-runtime-run", () => ({ useAnalyzeRuntimeFinancialsMutation: () => mockMutation }));
afterEach(cleanup);
beforeEach(() => {
  mockMutation.mutate.mockReset();
  mockMutation.isPending = false;
  mockMutation.isError = false;
  mockMutation.isSuccess = false;
  mockMutation.error = null;
});

const run = {
  id: "run-1",
  case_id: "case-1",
  state: "COMPLETED",
  tasks: [],
  evidence: [
    { id: "evidence-qualified", source_title: "FY2025 filing", stance: "SUPPORTING", qualification: "QUALIFIED" },
    { id: "evidence-review", source_title: "Unverified note", stance: "SUPPORTING", qualification: "NEEDS_REVIEW" },
  ],
  claims: [],
  thesis: null,
  memo: null,
  financial_analysis: null,
  red_team_reviews: [], decisions: [],
} as RuntimeRun;

describe("FinancialAnalysisForm", () => {
  it("does not enable submission until required inputs and evidence are selected", async () => {
    const user = userEvent.setup();
    render(<FinancialAnalysisForm run={run} />);
    const submit = screen.getByRole("button", { name: "Save analysis" });
    expect(submit).toHaveProperty("disabled", true);
    expect(screen.getByRole("option", { name: /FY2025 filing/ })).toBeTruthy();
    expect(screen.queryByRole("option", { name: /Unverified note/ })).toBeNull();

    await user.type(screen.getByLabelText("Revenue"), "120.00");
    await user.selectOptions(screen.getByLabelText("Revenue evidence"), "evidence-qualified");
    expect(submit).toHaveProperty("disabled", false);
  });

  it("pairs prior revenue with separate qualified evidence and submits strings", async () => {
    const user = userEvent.setup();
    render(<FinancialAnalysisForm run={run} />);
    await user.type(screen.getByLabelText("Revenue"), "120.00");
    await user.selectOptions(screen.getByLabelText("Revenue evidence"), "evidence-qualified");
    await user.type(screen.getByLabelText(/Prior revenue/), "100.00");
    expect(screen.getByRole("button", { name: "Save analysis" })).toHaveProperty("disabled", true);
    await user.selectOptions(screen.getByLabelText("Prior revenue evidence"), "evidence-qualified");
    await user.click(screen.getByRole("button", { name: "Save analysis" }));

    expect(mockMutation.mutate).toHaveBeenCalledWith({
      snapshot: { period: "FY2025", revenue: "120.00", prior_revenue: "100.00" },
      evidence_ids: { revenue: ["evidence-qualified"], prior_revenue: ["evidence-qualified"] },
    });
  });

  it("shows backend errors and does not fabricate a result", () => {
    mockMutation.isError = true;
    mockMutation.error = new Error("Evidence mapping rejected");
    render(<FinancialAnalysisForm run={run} />);
    expect(screen.getByRole("alert").textContent).toContain("Evidence mapping rejected");
    expect(screen.queryByRole("status")).toBeNull();
  });
});
