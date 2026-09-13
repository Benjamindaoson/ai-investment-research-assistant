// @vitest-environment jsdom
import { cleanup, render, screen } from "@testing-library/react";
import userEvent from "@testing-library/user-event";
import { afterEach, beforeEach, describe, expect, it, vi } from "vitest";
import { RuntimeDecisionForm } from "./runtime-decision-form";
import type { RuntimeRun } from "@/services/research-runtime-service";

const mockMutation = vi.hoisted(() => ({
  mutate: vi.fn(),
  isPending: false,
  isError: false,
  isSuccess: false,
  error: null as Error | null,
}));

vi.mock("@/queries/use-runtime-run", () => ({ useRecordRuntimeDecisionMutation: () => mockMutation }));
afterEach(cleanup);
beforeEach(() => {
  mockMutation.mutate.mockReset();
  mockMutation.isPending = false;
  mockMutation.isError = false;
  mockMutation.isSuccess = false;
  mockMutation.error = null;
});

const run = {
  id: "run-1", case_id: "case-1", state: "COMPLETED", tasks: [], evidence: [], claims: [],
  thesis: { id: "thesis-1", statement: "Thesis", bull: "Bull", base: "Base", bear: "Bear", claim_ids: [], review_status: "PENDING_REVIEW" },
  memo: null, financial_analysis: null, red_team_reviews: [], decisions: [], tool_executions: [],
} as RuntimeRun;

describe("RuntimeDecisionForm", () => {
  it("submits the selected action against the current thesis", async () => {
    const user = userEvent.setup();
    render(<RuntimeDecisionForm run={run} />);

    await user.selectOptions(screen.getByLabelText("Action"), "REQUEST_RESEARCH");
    await user.type(screen.getByLabelText("Rationale"), "Validate churn assumptions before approval.");
    await user.click(screen.getByRole("button", { name: "Record decision" }));

    expect(mockMutation.mutate).toHaveBeenCalledWith({
      actor: "Analyst",
      action: "REQUEST_RESEARCH",
      target_id: "thesis-1",
      rationale: "Validate churn assumptions before approval.",
    });
  });

  it("does not allow an empty rationale", () => {
    render(<RuntimeDecisionForm run={run} />);
    expect(screen.getByRole("button", { name: "Record decision" })).toHaveProperty("disabled", true);
  });

  it("surfaces backend rejection without a success state", () => {
    mockMutation.isError = true;
    mockMutation.error = new Error("only a completed run can approve a thesis");
    render(<RuntimeDecisionForm run={run} />);
    expect(screen.getByRole("alert").textContent).toContain("only a completed run");
    expect(screen.queryByRole("status")).toBeNull();
  });
});
