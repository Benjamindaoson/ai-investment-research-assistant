// @vitest-environment jsdom
import { cleanup, render, screen } from "@testing-library/react";
import { afterEach, describe, expect, it } from "vitest";
import { RuntimeProviderReadiness } from "./runtime-provider-readiness";

afterEach(cleanup);

const health = { status: "ok" as const, service: "runtime", evidence_mode: "LIVE_EXTERNAL" as const, evidence_provider: "finevidence-http", planner: "planner · v1", synthesizer: "synthesizer · v1", tools: ["external-evidence"] };

describe("RuntimeProviderReadiness", () => {
  it("distinguishes live provider readiness from quality", () => {
    render(<RuntimeProviderReadiness health={health} isPending={false} error={null} />);
    expect(screen.getByText("Live external evidence")).toBeTruthy();
    expect(screen.getByText("finevidence-http")).toBeTruthy();
    expect(screen.getByText(/not evidence quality/)).toBeTruthy();
  });

  it("renders loading and failure states", () => {
    const { rerender } = render(<RuntimeProviderReadiness health={undefined} isPending={true} error={null} />);
    expect(screen.getByText("Checking configured runtime providers…")).toBeTruthy();
    rerender(<RuntimeProviderReadiness health={undefined} isPending={false} error={new Error("runtime unavailable")} />);
    expect(screen.getByRole("alert").textContent).toContain("runtime unavailable");
  });
});
