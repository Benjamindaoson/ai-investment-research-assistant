// @vitest-environment jsdom
import { cleanup, render, screen } from "@testing-library/react";
import { afterEach, describe, expect, it } from "vitest";
import { RuntimeClaimTrace } from "./runtime-claim-trace";

afterEach(cleanup);

describe("RuntimeClaimTrace", () => {
  it("renders claim details and identifies evidence missing from the run", () => {
    render(<RuntimeClaimTrace claims={[{
      id: "claim-1", task_id: "fundamentals", statement: "Revenue evidence qualifies.", status: "QUALIFIED",
      confidence: 0.75, evidence_ids: ["evidence-1", "evidence-missing"],
    }]} evidence={[{ id: "evidence-1", stance: "SUPPORTING", qualification: "QUALIFIED" }]} />);

    expect(screen.getByText("Revenue evidence qualifies.")).toBeTruthy();
    expect(screen.getByText("QUALIFIED")).toBeTruthy();
    expect(screen.getByText("Claim confidence: 75.0% · not investment advice.")).toBeTruthy();
    expect(screen.getByText("Unresolved evidence: evidence-missing")).toBeTruthy();
  });

  it("keeps historical minimal claims renderable without inventing details", () => {
    render(<RuntimeClaimTrace claims={[{ id: "claim-old", status: "NEEDS_REVIEW", evidence_ids: [] }]} evidence={[]} />);
    expect(screen.getByText("Claim statement unavailable from this response.")).toBeTruthy();
    expect(screen.getByText("Task unavailable · claim-old")).toBeTruthy();
    expect(screen.getByText("Claim confidence unavailable.")).toBeTruthy();
  });

  it("renders an explicit empty state", () => {
    render(<RuntimeClaimTrace claims={[]} evidence={[]} />);
    expect(screen.getByText("No claims returned for this run.")).toBeTruthy();
  });
});
