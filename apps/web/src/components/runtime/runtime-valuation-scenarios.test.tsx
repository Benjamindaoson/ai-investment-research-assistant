// @vitest-environment jsdom
import { cleanup, render, screen } from "@testing-library/react";
import { afterEach, describe, expect, it } from "vitest";
import { RuntimeValuationScenarios } from "./runtime-valuation-scenarios";
import type { ValuationScenarios } from "@/services/research-runtime-service";

afterEach(cleanup);

describe("RuntimeValuationScenarios", () => {
  it("renders all scenarios as an illustrative read-only artifact", () => {
    render(<RuntimeValuationScenarios artifact={{
      id: "valuation-1", run_id: "run-1", case_id: "case-1", input_hash: "a".repeat(64), base_revenue: "100", base_revenue_evidence_ids: ["evidence-1"], provenance: { illustrative: true },
      scenarios: ["BULL", "BASE", "BEAR"].map((scenario) => ({
        scenario: scenario as "BULL" | "BASE" | "BEAR",
        assumptions: {} as ValuationScenarios["scenarios"][number]["assumptions"],
        projected_revenue: "110", projected_operating_income: "22", free_cash_flow: "16.5", terminal_value: "206.25", equity_value: "216.25", value_per_share: "21.625",
      })),
    }} />);

    expect(screen.getByRole("heading", { name: "Explicit Bull / Base / Bear bridge" })).toBeTruthy();
    expect(screen.getAllByText("110")).toHaveLength(3);
    expect(screen.getByText("Illustrative terminal-value bridge only; assumptions are explicit and evidence-linked. This is not a price target or investment advice.")).toBeTruthy();
  });
});
