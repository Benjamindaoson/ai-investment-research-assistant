// @vitest-environment jsdom
import { cleanup, render, screen } from "@testing-library/react";
import userEvent from "@testing-library/user-event";
import { afterEach, beforeEach, describe, expect, it, vi } from "vitest";
import { RuntimeIcReview } from "./runtime-ic-review";
import type { RuntimeRun } from "@/services/research-runtime-service";

const mockMutation = vi.hoisted(() => ({ mutate: vi.fn(), isPending: false, isError: false, isSuccess: false, error: null as Error | null }));
vi.mock("@/queries/use-runtime-run", () => ({ useCreateInvestmentCommitteeReviewMutation: () => mockMutation }));
afterEach(cleanup);
beforeEach(() => {
  mockMutation.mutate.mockReset();
  mockMutation.isPending = false;
  mockMutation.isError = false;
  mockMutation.isSuccess = false;
  mockMutation.error = null;
});

const run = {
  id: "run-1", case_id: "case-1", state: "COMPLETED", tasks: [],
  evidence: [{ id: "evidence-1", source_title: "Annual report", stance: "SUPPORTING", qualification: "QUALIFIED" }],
  claims: [], thesis: { id: "thesis-1", statement: "Thesis", bull: "Bull", base: "Base", bear: "Bear", claim_ids: [], review_status: "PENDING_REVIEW" },
  memo: null, financial_analysis: null, red_team_reviews: [], ic_reviews: [], decisions: [], tool_executions: [],
} as RuntimeRun;

describe("RuntimeIcReview", () => {
  it("shows missing role coverage and submits an evidence-linked panel view", async () => {
    const user = userEvent.setup();
    render(<RuntimeIcReview run={run} />);
    expect(screen.getByText("0/5 roles covered")).toBeTruthy();
    expect(screen.getByText("Bear case: not reviewed")).toBeTruthy();

    await user.type(screen.getByLabelText("Rationale"), "Financial evidence supports the thesis for now.");
    await user.selectOptions(screen.getByLabelText("Evidence", { exact: false }), "evidence-1");
    await user.click(screen.getByRole("button", { name: "Save IC review" }));

    expect(mockMutation.mutate).toHaveBeenCalledWith({
      role: "BULL", reviewer: "Investment committee reviewer", position: "MIXED", recommendation: "HOLD",
      rationale: "Financial evidence supports the thesis for now.", evidence_ids: ["evidence-1"],
    });
  });
});
