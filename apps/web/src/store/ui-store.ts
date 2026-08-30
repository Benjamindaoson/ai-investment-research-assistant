import { create } from "zustand";

type UiState = {
  commandPaletteOpen: boolean;
  navigationDrawerOpen: boolean;
  contextDrawerOpen: boolean;
  setCommandPaletteOpen: (open: boolean) => void;
  setNavigationDrawerOpen: (open: boolean) => void;
  setContextDrawerOpen: (open: boolean) => void;
};

export const useUiStore = create<UiState>((set) => ({
  commandPaletteOpen: false,
  navigationDrawerOpen: false,
  contextDrawerOpen: false,
  setCommandPaletteOpen: (commandPaletteOpen) => set({ commandPaletteOpen }),
  setNavigationDrawerOpen: (navigationDrawerOpen) => set({ navigationDrawerOpen }),
  setContextDrawerOpen: (contextDrawerOpen) => set({ contextDrawerOpen }),
}));
