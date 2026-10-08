// @vitest-environment jsdom
import { cleanup, render, screen } from "@testing-library/react";
import { afterEach, describe, expect, it } from "vitest";
import { RuntimeEventTrace } from "./runtime-event-trace";

afterEach(cleanup);

const event = { seq: 2, run_id: "run-1", event_type: "TASK_COMPLETED", payload: { task_id: "market", evidence_count: 2 }, occurred_at: "2026-09-14T00:00:00.000Z" };

describe("RuntimeEventTrace", () => {
  it("renders the populated audit trace with structured payload", () => {
    render(<RuntimeEventTrace events={[event]} isPending={false} error={null} />);
    expect(screen.getByRole("heading", { name: "Run events" })).toBeTruthy();
    expect(screen.getByText("TASK_COMPLETED")).toBeTruthy();
    expect(screen.getByText(/\"task_id\": \"market\"/)).toBeTruthy();
  });

  it("keeps loading, empty, and error states explicit", () => {
    const { rerender } = render(<RuntimeEventTrace events={undefined} isPending={true} error={null} />);
    expect(screen.getByText("Loading durable event history…")).toBeTruthy();
    rerender(<RuntimeEventTrace events={[]} isPending={false} error={null} />);
    expect(screen.getByText("No durable events have been recorded for this run.")).toBeTruthy();
    rerender(<RuntimeEventTrace events={undefined} isPending={false} error={new Error("runtime unavailable")} />);
    expect(screen.getByRole("alert").textContent).toContain("runtime unavailable");
  });
});
