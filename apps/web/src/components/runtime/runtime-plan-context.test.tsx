// @vitest-environment jsdom
import { cleanup, render, screen } from "@testing-library/react";
import { afterEach, describe, expect, it } from "vitest";
import { RuntimePlanContext } from "./runtime-plan-context";
import type { RuntimePlan } from "@/services/research-runtime-service";

afterEach(cleanup);

const plan = {
  id: "plan-1", case_id: "case-1", question: "Assess ACME", planner_name: "deterministic-financial-planner",
  planner_version: "v1", input_hash: "a".repeat(64), status: "VALIDATED",
  mandate: {
    decision_type: "DUE_DILIGENCE", time_horizon: "36 months", materiality: "HIGH",
    required_outputs: ["investment memo", "valuation sensitivity"], constraints: ["No management projections"],
  },
} as RuntimePlan;

describe("RuntimePlanContext", () => {
  it("renders planner identity and mandate without editing controls", () => {
    render(<RuntimePlanContext plan={plan} />);
    expect(screen.getByText("deterministic-financial-planner · v1")).toBeTruthy();
    expect(screen.getByText("DUE_DILIGENCE")).toBeTruthy();
    expect(screen.getByText("36 months")).toBeTruthy();
    expect(screen.getByText("investment memo · valuation sensitivity")).toBeTruthy();
    expect(screen.getByText("No management projections")).toBeTruthy();
    expect(screen.queryByRole("textbox")).toBeNull();
  });

  it("labels historical runs with no plan context", () => {
    render(<RuntimePlanContext />);
    expect(screen.getByText("Plan context is unavailable in this historical run response.")).toBeTruthy();
  });
});
