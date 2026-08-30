// @vitest-environment jsdom
import { QueryClient, QueryClientProvider } from "@tanstack/react-query";
import { cleanup, render, screen, within } from "@testing-library/react";
import userEvent from "@testing-library/user-event";
import { afterEach, describe, expect, it, vi } from "vitest";
import { EvidenceWorkspace } from "@/components/evidence/evidence-workspace";
import { HumanReviewWorkspace, LibraryWorkspace } from "@/components/outputs/output-workspaces";

vi.mock("next/navigation", () => ({ useRouter: () => ({ push: vi.fn() }), usePathname: () => "/evidence" }));
afterEach(cleanup);

function renderWorkspace(node: React.ReactNode) {
  const client = new QueryClient({ defaultOptions: { queries: { retry: false }, mutations: { retry: false } } });
  return render(<QueryClientProvider client={client}>{node}</QueryClientProvider>);
}

describe("P0 evidence, review, and library interactions", () => {
  it("keeps supporting and counter evidence separate and records a status change", async () => {
    const user = userEvent.setup();
    renderWorkspace(<EvidenceWorkspace caseId="case-value-pools" />);
    expect(await screen.findByText("Supporting Evidence")).toBeTruthy();
    expect(screen.getByText("Counter Evidence")).toBeTruthy();
    const status = await screen.findByLabelText("Verification status for ev-pi-data");
    await user.selectOptions(status, "needs-review");
    expect(await screen.findByText("Evidence status changed to needs-review.")).toBeTruthy();
  });

  it("approves a queued human-review item and exposes the audit action", async () => {
    const user = userEvent.setup();
    renderWorkspace(<HumanReviewWorkspace />);
    const detail = await screen.findAllByText("Robot data is a binding constraint");
    expect(detail.length).toBeGreaterThan(1);
    await user.type(screen.getByLabelText("Analyst note"), "Checked support and counter-evidence.");
    await user.click(screen.getByRole("button", { name: "Approve" }));
    const history = await screen.findAllByText("Checked support and counter-evidence.");
    expect(history.length).toBeGreaterThan(1);
  });

  it("filters the research library by asset type", async () => {
    const user = userEvent.setup();
    renderWorkspace(<LibraryWorkspace />);
    const table = await screen.findByText("Scaling synthetic-to-real transfer");
    expect(table).toBeTruthy();
    await user.selectOptions(screen.getByLabelText("Type"), "paper");
    expect(screen.getByText("Scaling synthetic-to-real transfer")).toBeTruthy();
    expect(within(screen.getByRole("main")).queryByText("Figure platform technical update")).toBeNull();
  });
});
