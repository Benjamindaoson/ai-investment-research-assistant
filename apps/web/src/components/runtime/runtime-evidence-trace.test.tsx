// @vitest-environment jsdom
import { cleanup, render, screen } from "@testing-library/react";
import { afterEach, describe, expect, it } from "vitest";
import { RuntimeEvidenceTrace } from "./runtime-evidence-trace";

afterEach(cleanup);

describe("RuntimeEvidenceTrace", () => {
  it("renders full provenance and keeps counter stance visible", () => {
    render(<RuntimeEvidenceTrace evidence={[
      {
        id: "evidence-1", task_id: "fundamentals", requirement_id: "revenue", stance: "SUPPORTING",
        qualification: "QUALIFIED", source_id: "filing-1", source_title: "FY2025 filing", excerpt: "Revenue increased.",
        provider: "finevidence", source_url: "https://example.test/filing", locator: "page:12", content_hash: "a".repeat(64),
      },
      {
        id: "evidence-2", stance: "COUNTER", qualification: "NEEDS_REVIEW", source_title: "Risk disclosure", excerpt: "Demand may soften.",
      },
    ]} />);

    expect(screen.getByText("FY2025 filing")).toBeTruthy();
    expect(screen.getByText("Revenue increased.")).toBeTruthy();
    expect(screen.getByText("SUPPORTING")).toBeTruthy();
    expect(screen.getByText("COUNTER")).toBeTruthy();
    expect(screen.getByText("Provenance complete")).toBeTruthy();
    expect(screen.getByText("Provenance incomplete")).toBeTruthy();
    expect(screen.getByRole("link", { name: "Open source" }).getAttribute("href")).toBe("https://example.test/filing");
    expect(screen.getByText(`Hash: ${"a".repeat(64)}`)).toBeTruthy();
  });

  it("does not fabricate detail for an empty evidence response", () => {
    render(<RuntimeEvidenceTrace evidence={[]} />);
    expect(screen.getByText("No evidence records returned for this run.")).toBeTruthy();
    expect(screen.queryByRole("link", { name: "Open source" })).toBeNull();
  });
});
