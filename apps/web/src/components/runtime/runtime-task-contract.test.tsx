// @vitest-environment jsdom
import { cleanup, render, screen } from "@testing-library/react";
import { afterEach, describe, expect, it } from "vitest";
import { RuntimeTaskContract } from "./runtime-task-contract";

afterEach(cleanup);

describe("RuntimeTaskContract", () => {
  it("renders purpose, dependencies, evidence gates, and missing requirements", () => {
    render(<RuntimeTaskContract tasks={[{
      id: "fundamentals", title: "Financial fundamentals", state: "COMPLETED", purpose: "Assess operating durability.",
      depends_on: ["market"], tool_name: "financial-data", evidence_requirements: [{ id: "revenue", description: "Revenue trend", minimum_records: 2, required_stances: ["SUPPORTING"], fact_type: "RETRIEVED_FACT", role: "value", criticality: "CRITICAL", evidence_role: "VALUE_SUPPORT", metric: "revenue", period: "FY2025" }],
    }]} traceTasks={[{ id: "fundamentals", state: "COMPLETED", depends_on: ["market"], missing_requirement_ids: ["revenue"] }]} />);

    expect(screen.getByText("Assess operating durability.")).toBeTruthy();
    expect(screen.getByText("Tool: financial-data")).toBeTruthy();
    expect(screen.getByText("Depends on: market")).toBeTruthy();
    expect(screen.getByText("Revenue trend · minimum 2 · SUPPORTING")).toBeTruthy();
    expect(screen.getByText("RETRIEVED_FACT · value · CRITICAL · VALUE_SUPPORT · revenue / FY2025")).toBeTruthy();
    expect(screen.getByText("Missing requirements: revenue")).toBeTruthy();
  });

  it("keeps historical minimal tasks explicit", () => {
    render(<RuntimeTaskContract tasks={[{ id: "market", title: "Market", state: "PENDING" }]} />);
    expect(screen.getByText("Task purpose unavailable from this response.")).toBeTruthy();
    expect(screen.getByText("Evidence requirements unavailable from this response.")).toBeTruthy();
    expect(screen.getByText("Requirement status unavailable from trace.")).toBeTruthy();
  });
});
