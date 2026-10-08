// @vitest-environment jsdom
import { cleanup, render, screen } from "@testing-library/react";
import { afterEach, describe, expect, it } from "vitest";
import { RuntimeCalculationLedger } from "./runtime-calculation-ledger";

afterEach(cleanup);

describe("RuntimeCalculationLedger", () => {
  it("renders formula, inputs, output, and evidence read-only", () => {
    render(<RuntimeCalculationLedger entries={[{
      metric: "revenue_growth_pct",
      formula: "(revenue / prior_revenue - 1) × 100",
      inputs: { revenue: "120", prior_revenue: "100" },
      value: "20",
      unit: "%",
      status: "AVAILABLE",
      reason: null,
      evidence_ids: ["evidence-1"],
    }]} />);

    expect(screen.getByText("revenue growth pct")).toBeTruthy();
    expect(screen.getByText("(revenue / prior_revenue - 1) × 100")).toBeTruthy();
    expect(screen.getByText(/revenue=120 · prior_revenue=100/)).toBeTruthy();
    expect(screen.getByRole("listitem").textContent).toContain("Output: 20 %");
    expect(screen.getByText("Evidence: evidence-1")).toBeTruthy();
  });

  it("does not fabricate a ledger for historical results", () => {
    render(<RuntimeCalculationLedger entries={[]} />);

    expect(screen.getByText(/unavailable for this historical artifact/)).toBeTruthy();
    expect(screen.queryByText("(revenue / prior_revenue - 1) × 100")).toBeNull();
  });
});
