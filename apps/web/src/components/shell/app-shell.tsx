"use client";

import { useRef, type ReactNode } from "react";
import { CommandPalette } from "./command-palette";
import { ContextPane } from "./context-pane";
import { NavigationRail } from "./navigation-rail";
import { ShellDrawers } from "./shell-drawers";
import { TopBar } from "./top-bar";

export function AppShell({ children, context }: { children: ReactNode; context: ReactNode }) {
  const commandTriggerRef = useRef<HTMLButtonElement>(null);
  return (
    <div className="atlas-shell">
      <aside className="atlas-sidebar" aria-label="Workspace navigation"><NavigationRail /></aside>
      <div className="atlas-app"><TopBar commandTriggerRef={commandTriggerRef} /><main className="atlas-main" id="main-content">{children}</main></div>
      <ContextPane>{context}</ContextPane>
      <ShellDrawers context={context} />
      <CommandPalette triggerRef={commandTriggerRef} />
    </div>
  );
}
