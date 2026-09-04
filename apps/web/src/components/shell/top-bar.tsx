"use client";

import { Bell, ChevronDown, CircleHelp, Menu, PanelRight, Search } from "lucide-react";
import { useUiStore } from "@/store/ui-store";

export function TopBar({ commandTriggerRef }: { commandTriggerRef: React.RefObject<HTMLButtonElement | null> }) {
  const openCommandPalette = useUiStore((state) => state.setCommandPaletteOpen);
  const openNavigation = useUiStore((state) => state.setNavigationDrawerOpen);
  const openContext = useUiStore((state) => state.setContextDrawerOpen);
  return (
    <header className="atlas-topbar">
      <button className="mobile-shell-action nav-drawer-trigger" type="button" aria-label="Open navigation" onClick={() => openNavigation(true)}><Menu size={19} /></button>
      <button ref={commandTriggerRef} className="search-control" type="button" aria-haspopup="dialog" onClick={() => openCommandPalette(true)}>
        <Search size={17} aria-hidden="true" /><span>Search companies, research, sources…</span><kbd>⌘ K</kbd>
      </button>
      <div className="top-actions">
        <button className="icon-action" type="button" aria-label="Help"><CircleHelp size={19} /></button>
        <button className="icon-action bell" type="button" aria-label="Notifications, 3 unread"><Bell size={19} /><i>3</i></button>
        <b className="user" aria-hidden="true">YZ</b>
        <span className="user-name">Yvonne Zhang<small>Research · AI &amp; Robotics</small></span>
        <ChevronDown size={14} aria-hidden="true" />
        <button className="mobile-shell-action context-drawer-trigger" type="button" aria-label="Open Today overview" onClick={() => openContext(true)}><PanelRight size={19} /></button>
      </div>
    </header>
  );
}
