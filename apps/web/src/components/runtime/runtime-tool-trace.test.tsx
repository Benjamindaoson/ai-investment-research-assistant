// @vitest-environment jsdom
import { cleanup, render, screen } from "@testing-library/react";
import { afterEach, describe, expect, it } from "vitest";
import { RuntimeToolTrace } from "./runtime-tool-trace";

afterEach(cleanup);

describe("RuntimeToolTrace", () => {
  it("renders successful and failed execution receipts without changing status", () => {
    render(<RuntimeToolTrace executions={[
      { id: "tool-1", task_id: "market", tool_name: "research", status: "SUCCEEDED", result_hash: "a".repeat(16), started_at: "2026-09-14T00:00:00.000Z", completed_at: "2026-09-14T00:00:01.000Z" },
      { id: "tool-2", task_id: "risk", tool_name: "research", status: "FAILED", result_hash: "b".repeat(16), started_at: "2026-09-14T00:00:02.000Z", completed_at: "2026-09-14T00:00:03.000Z", error_type: "TimeoutError", error_message: "provider timed out", error_hash: "c".repeat(64) },
    ]} />);

    expect(screen.getAllByText("research")).toHaveLength(2);
    expect(screen.getByText("SUCCEEDED")).toBeTruthy();
    expect(screen.getByText("FAILED")).toBeTruthy();
    expect(screen.getByText(`Result hash: ${"a".repeat(16)}`)).toBeTruthy();
    expect(screen.getByText("Failure: TimeoutError: provider timed out")).toBeTruthy();
    expect(screen.getByText(`Diagnostic hash: ${"c".repeat(64)}`)).toBeTruthy();
    expect(screen.getByText("Started: 2026-09-14T00:00:02.000Z")).toBeTruthy();
  });

  it("renders an explicit empty state for historical runs", () => {
    render(<RuntimeToolTrace executions={[]} />);
    expect(screen.getByText("No tool execution receipts returned for this run.")).toBeTruthy();
  });

  it("renders unresolved attempts as requiring explicit resolution", () => {
    render(<RuntimeToolTrace executions={[{
      id: "tool-unknown",
      task_id: "market",
      tool_name: "research",
      status: "UNKNOWN_EFFECT",
      attempt_key: "run-1:market:attempt-1",
      result_hash: "d".repeat(64),
      started_at: "2026-09-14T00:00:04.000Z",
      completed_at: null,
      error_type: "InFlight",
      error_message: "Provider result has not been acknowledged.",
      error_hash: "d".repeat(64),
    }]} />);

    expect(screen.getByText("UNKNOWN_EFFECT")).toBeTruthy();
    expect(screen.getByText("Attempt: run-1:market:attempt-1")).toBeTruthy();
    expect(screen.getByText("Outcome unknown: explicit operator resolution is required before retry.")).toBeTruthy();
    expect(screen.getByText("Completed: not recorded")).toBeTruthy();
  });
});
