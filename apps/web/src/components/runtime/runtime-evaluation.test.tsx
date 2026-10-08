// @vitest-environment jsdom
import { cleanup, render, screen } from "@testing-library/react";
import { afterEach, describe, expect, it } from "vitest";
import { RuntimeEvaluation } from "./runtime-evaluation";

afterEach(cleanup);

describe("RuntimeEvaluation", () => {
  it("renders overall and per-check results without recomputing them", () => {
    render(<RuntimeEvaluation evaluation={{ id: "evaluation-1", case_id: "case-1", run_id: "run-1", evaluator: "scorer-v1", case_hash: "a".repeat(64), passed: false, checks: [{ name: "memo", status: "FAIL", detail: "Memo is incomplete." }, { name: "coverage", status: "N/A", detail: "Not observed." }], evaluated_at: "2026-09-14T00:00:00.000Z" }} isPending={false} error={null} />);
    expect(screen.getAllByText("FAIL")).toHaveLength(2);
    expect(screen.getByText("memo")).toBeTruthy();
    expect(screen.getByText("Memo is incomplete.")).toBeTruthy();
    expect(screen.getByText("N/A")).toBeTruthy();
  });

  it("distinguishes not evaluated and retrieval error states", () => {
    const { rerender } = render(<RuntimeEvaluation evaluation={null} isPending={false} error={null} />);
    expect(screen.getByText("No evaluation artifact has been recorded for this run.")).toBeTruthy();
    rerender(<RuntimeEvaluation evaluation={undefined} isPending={false} error={new Error("runtime unavailable")} />);
    expect(screen.getByRole("alert").textContent).toContain("runtime unavailable");
  });
});
