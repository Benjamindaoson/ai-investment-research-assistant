import { beforeEach, describe, expect, it } from "vitest";
import { useUiStore } from "./ui-store";

describe("UI store", () => {
  beforeEach(() => useUiStore.setState({ commandPaletteOpen: false, navigationDrawerOpen: false, contextDrawerOpen: false }));
  it("owns command palette and responsive drawer state", () => {
    useUiStore.getState().setCommandPaletteOpen(true);
    useUiStore.getState().setNavigationDrawerOpen(true);
    expect(useUiStore.getState()).toMatchObject({ commandPaletteOpen: true, navigationDrawerOpen: true, contextDrawerOpen: false });
  });
});
