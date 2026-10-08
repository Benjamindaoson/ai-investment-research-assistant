// @vitest-environment jsdom
import { cleanup, render, screen } from "@testing-library/react";
import { afterEach, describe, expect, it } from "vitest";
import { RuntimeCaseInbox } from "./runtime-case-inbox";
import type { RuntimeResearchCase } from "@/services/research-runtime-service";

afterEach(cleanup);

const researchCase: RuntimeResearchCase & { latest_run_id: string | null } = { id: "case-1", target: "ACME", question: "Assess ACME margin durability.", mandate: { decision_type: "INVESTMENT_COMMITTEE", time_horizon: "12 months", materiality: "MEDIUM", required_outputs: ["investment memo"], constraints: [] }, created_at: "2026-09-14T00:00:00.000Z", latest_run_id: "run-1" };

describe("RuntimeCaseInbox", () => {
  it("renders case metadata and the latest run link", () => {
    render(<RuntimeCaseInbox cases={[researchCase]} isPending={false} error={null} />);
    expect(screen.getByText("ACME")).toBeTruthy();
    expect(screen.getByText("Assess ACME margin durability.")).toBeTruthy();
    expect(screen.getByRole("link", { name: "Open latest run" }).getAttribute("href")).toBe("/runtime/run-1");
  });

  it("shows explicit loading, empty, error, and no-run states", () => {
    const { rerender } = render(<RuntimeCaseInbox cases={undefined} isPending error={null} />);
    expect(screen.getByText("Loading research cases…")).toBeTruthy();
    rerender(<RuntimeCaseInbox cases={[]} isPending={false} error={null} />);
    expect(screen.getByText("No durable ResearchCases yet. Create the first one below.")).toBeTruthy();
    rerender(<RuntimeCaseInbox cases={[{ ...researchCase, latest_run_id: null }]} isPending={false} error={null} />);
    expect(screen.getByText("No run yet")).toBeTruthy();
    rerender(<RuntimeCaseInbox cases={undefined} isPending={false} error={new Error("runtime unavailable")} />);
    expect(screen.getByRole("alert").textContent).toContain("runtime unavailable");
  });
});
