// @vitest-environment jsdom
import { cleanup, fireEvent, render, screen } from "@testing-library/react";
import { afterEach, describe, expect, it, vi } from "vitest";
import { RuntimeMemoExport } from "./runtime-memo-export";
import type { RuntimeMemo } from "@/services/research-runtime-service";

afterEach(cleanup);

const memo: RuntimeMemo = {
  id: "memo-1", run_id: "run-1", case_id: "case-1", title: "ACME memo", status: "DRAFT", executive_summary: "Observed.", thesis_id: "thesis-1", claim_ids: [], evidence_ids: ["evidence-1"], counter_evidence_ids: [], unresolved_requirement_ids: [], sections: [], provenance: {}, generated_at: "2026-09-14T00:00:00.000Z",
};

describe("RuntimeMemoExport", () => {
  it("offers no export when there is no memo and downloads when one exists", () => {
    const createObjectURL = vi.fn(() => "blob:test");
    const revokeObjectURL = vi.fn();
    Object.defineProperty(URL, "createObjectURL", { configurable: true, value: createObjectURL });
    Object.defineProperty(URL, "revokeObjectURL", { configurable: true, value: revokeObjectURL });
    const click = vi.spyOn(HTMLAnchorElement.prototype, "click").mockImplementation(() => undefined);
    const { rerender } = render(<RuntimeMemoExport run={{ id: "run-1", state: "COMPLETED", memo: null }} />);
    expect(screen.queryByRole("button")).toBeNull();
    rerender(<RuntimeMemoExport run={{ id: "run/1", state: "COMPLETED", memo }} />);
    fireEvent.click(screen.getByRole("button", { name: "Download Markdown memo" }));
    expect(createObjectURL).toHaveBeenCalledOnce();
    expect(revokeObjectURL).toHaveBeenCalledWith("blob:test");
    expect(click).toHaveBeenCalledOnce();
    click.mockRestore();
  });
});
