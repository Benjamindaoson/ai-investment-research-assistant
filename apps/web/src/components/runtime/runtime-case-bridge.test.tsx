// @vitest-environment jsdom

import { render, screen } from "@testing-library/react";
import { beforeEach, describe, expect, it, vi } from "vitest";
import { RuntimeCaseBridge } from "./runtime-case-bridge";

const mock = vi.hoisted(() => ({
  query: { data: undefined as Array<{ id: string }> | undefined, isPending: true, isError: false, error: null as Error | null, refetch: vi.fn() },
  replace: vi.fn(),
}));

vi.mock("next/navigation", () => ({ useRouter: () => ({ replace: mock.replace, push: vi.fn() }), usePathname: () => "/research/case-1" }));
vi.mock("@/queries/use-runtime-run", () => ({ useRuntimeCaseRunsQuery: () => mock.query }));

describe("RuntimeCaseBridge", () => {
  beforeEach(() => {
    mock.replace.mockReset();
    mock.query = { data: undefined, isPending: true, isError: false, error: null, refetch: vi.fn() };
  });

  it("navigates an existing case to its latest durable run", () => {
    mock.query = { data: [{ id: "run-1" }, { id: "run-2" }], isPending: false, isError: false, error: null, refetch: vi.fn() };
    render(<RuntimeCaseBridge caseId="case-1" />);
    expect(mock.replace).toHaveBeenCalledWith("/runtime/run-2");
  });

  it("reports a missing durable run instead of rendering fixture data", () => {
    mock.query = { data: [], isPending: false, isError: false, error: null, refetch: vi.fn() };
    render(<RuntimeCaseBridge caseId="case-1" />);
    expect(screen.getByText("No durable run exists for this case")).toBeTruthy();
  });
});
