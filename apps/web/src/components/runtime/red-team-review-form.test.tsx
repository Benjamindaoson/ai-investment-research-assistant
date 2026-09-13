// @vitest-environment jsdom
import { cleanup, render, screen } from "@testing-library/react";
import userEvent from "@testing-library/user-event";
import { afterEach, beforeEach, describe, expect, it, vi } from "vitest";
import { RedTeamReviewForm } from "./red-team-review-form";
import type { RuntimeRun } from "@/services/research-runtime-service";

const mockMutation = vi.hoisted(() => ({
  mutate: vi.fn(),
  isPending: false,
  isError: false,
  isSuccess: false,
  error: null as Error | null,
}));

vi.mock("@/queries/use-runtime-run", () => ({ useCreateRedTeamReviewMutation: () => mockMutation }));
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
  evidence: [
    { id: "supporting", source_title: "Filing", stance: "SUPPORTING", qualification: "QUALIFIED" },
    { id: "counter", source_title: "Risk disclosure", stance: "COUNTER", qualification: "QUALIFIED" },
    { id: "conflicting", source_title: "Conflicting note", stance: "CONFLICTING", qualification: "NEEDS_REVIEW" },
  ],
  claims: [], thesis: { id: "thesis-1", statement: "Thesis", bull: "Bull", base: "Base", bear: "Bear", claim_ids: [], review_status: "PENDING_REVIEW" },
  memo: null, financial_analysis: null, red_team_reviews: [],
} as RuntimeRun;

describe("RedTeamReviewForm", () => {
  it("offers only disconfirming evidence and submits an explicit review", async () => {
    const user = userEvent.setup();
    render(<RedTeamReviewForm run={run} />);
    expect(screen.getByRole("option", { name: /Risk disclosure/ })).toBeTruthy();
    expect(screen.getByRole("option", { name: /Conflicting note/ })).toBeTruthy();
    expect(screen.queryByRole("option", { name: /Filing/ })).toBeNull();
    expect(screen.getByRole("button", { name: "Save red-team review" })).toHaveProperty("disabled", true);

    await user.type(screen.getByLabelText("Challenge"), "Demand may soften.");
    await user.type(screen.getByLabelText("Rationale"), "The counter signal is material.");
    await user.selectOptions(screen.getByRole("listbox", { name: /Disconfirming evidence/ }), "counter");
    await user.click(screen.getByRole("button", { name: "Save red-team review" }));

    expect(mockMutation.mutate).toHaveBeenCalledWith({
      reviewer: "Investment analyst",
      challenge: "Demand may soften.",
      rationale: "The counter signal is material.",
      outcome: "REQUIRES_RESEARCH",
      evidence_ids: ["counter"],
    });
  });

  it("shows backend errors without a success state", () => {
    mockMutation.isError = true;
    mockMutation.error = new Error("Review rejected");
    render(<RedTeamReviewForm run={run} />);
    expect(screen.getByRole("alert").textContent).toContain("Review rejected");
    expect(screen.queryByRole("status")).toBeNull();
  });
});
