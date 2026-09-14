// @vitest-environment jsdom
import { cleanup, render, screen } from "@testing-library/react";
import { afterEach, describe, expect, it } from "vitest";
import { RuntimeCaseHistory } from "./runtime-case-history";
import type { RuntimeRun } from "@/services/research-runtime-service";

afterEach(cleanup);

const run = { id: "run-1", case_id: "case-1", state: "COMPLETED", tasks: [], tool_executions: [], evidence: [], claims: [], thesis: null, memo: null, financial_analysis: null, red_team_reviews: [], decisions: [], created_at: "2026-09-14T00:00:00.000Z" } as RuntimeRun;

describe("RuntimeCaseHistory", () => {
  it("marks the active run and links historical runs", () => {
    render(<RuntimeCaseHistory runs={[run, { ...run, id: "run-2", state: "PARTIAL" }]} activeRunId="run-1" isPending={false} error={null} />);
    expect(screen.getByText(/Active run/)).toBeTruthy();
    expect(screen.getByText(/Historical run/)).toBeTruthy();
    expect(screen.getByRole("link", { name: "Open run" }).getAttribute("href")).toBe("/runtime/run-2");
  });

  it("preserves explicit loading, empty, and error states", () => {
    const { rerender } = render(<RuntimeCaseHistory runs={undefined} activeRunId="run-1" isPending error={null} />);
    expect(screen.getByText("Loading case history…")).toBeTruthy();
    rerender(<RuntimeCaseHistory runs={[]} activeRunId="run-1" isPending={false} error={null} />);
    expect(screen.getByText("No durable runs are recorded for this ResearchCase.")).toBeTruthy();
    rerender(<RuntimeCaseHistory runs={undefined} activeRunId="run-1" isPending={false} error={new Error("runtime unavailable")} />);
    expect(screen.getByRole("alert").textContent).toContain("runtime unavailable");
  });
});
