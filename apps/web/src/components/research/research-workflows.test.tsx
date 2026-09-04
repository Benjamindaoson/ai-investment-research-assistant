// @vitest-environment jsdom
import { QueryClient, QueryClientProvider } from "@tanstack/react-query";
import { cleanup, render, screen } from "@testing-library/react";
import userEvent from "@testing-library/user-event";
import { afterEach, beforeEach, describe, expect, it, vi } from "vitest";
import { NewResearchWorkspace } from "./new-research-workspace";
import { TodayWorklist } from "./today-worklist";
import { mockTodayData } from "@/lib/mock/fixtures/today";

const navigation = vi.hoisted(() => ({ push: vi.fn(), pathname: "/" }));
vi.mock("next/navigation", () => ({ useRouter: () => ({ push: navigation.push }), usePathname: () => navigation.pathname }));
afterEach(cleanup);

function renderWithQuery(node: React.ReactNode) {
  const client = new QueryClient({ defaultOptions: { queries: { retry: false }, mutations: { retry: false } } });
  return render(<QueryClientProvider client={client}>{node}</QueryClientProvider>);
}

describe("P0 research entry workflows", () => {
  beforeEach(() => navigation.push.mockReset());

  it("filters Today work and hands a question into Research Setup", async () => {
    const user = userEvent.setup();
    render(<TodayWorklist items={mockTodayData.items} fixtureNotice={mockTodayData.fixtureNotice} />);
    await user.click(screen.getByRole("tab", { name: /In research/ }));
    expect(screen.getAllByText("In research").length).toBeGreaterThan(0);
    expect(screen.queryByText("Needs review", { selector: "h2" })).toBeNull();
    await user.type(screen.getByLabelText("Ask a research question"), "Which agent infrastructure layers can become durable platforms?");
    await user.click(screen.getByRole("button", { name: /Set up research/ }));
    expect(navigation.push).toHaveBeenCalledWith(expect.stringContaining("/new-research?question="));
  });

  it("generates an editable plan and creates the mock Research Case", async () => {
    const user = userEvent.setup();
    renderWithQuery(<NewResearchWorkspace initialQuestion="Where will embodied intelligence create defensible value over three years?" />);
    await user.click(await screen.findByRole("button", { name: "Continue to research plan" }));
    expect(await screen.findByText("Structured research goal", { exact: false })).toBeTruthy();
    const firstQuestion = screen.getByLabelText("Market question 1");
    await user.clear(firstQuestion);
    await user.type(firstQuestion, "Estimate durable market value pools");
    await user.click(screen.getByRole("button", { name: "Start Research" }));
    expect(navigation.push).toHaveBeenCalledWith("/research/case-value-pools");
  });
});
