"use client";

import * as Dialog from "@radix-ui/react-dialog";
import { X } from "lucide-react";
import type { ReactNode } from "react";
import { NavigationRail } from "./navigation-rail";
import { useUiStore } from "@/store/ui-store";

function Drawer({ open, onOpenChange, side, title, children }: { open: boolean; onOpenChange: (open: boolean) => void; side: "left" | "right"; title: string; children: ReactNode }) {
  return (
    <Dialog.Root open={open} onOpenChange={onOpenChange}>
      <Dialog.Portal>
        <Dialog.Overlay className="drawer-overlay" />
        <Dialog.Content className={`drawer-content drawer-${side}`} aria-describedby={undefined}>
          <Dialog.Title className="sr-only">{title}</Dialog.Title>
          <Dialog.Close className="drawer-close" aria-label={`Close ${title}`}><X size={18} /></Dialog.Close>
          {children}
        </Dialog.Content>
      </Dialog.Portal>
    </Dialog.Root>
  );
}

export function ShellDrawers({ context }: { context: ReactNode }) {
  const navigationOpen = useUiStore((state) => state.navigationDrawerOpen);
  const contextOpen = useUiStore((state) => state.contextDrawerOpen);
  const setNavigationOpen = useUiStore((state) => state.setNavigationDrawerOpen);
  const setContextOpen = useUiStore((state) => state.setContextDrawerOpen);
  return (
    <>
      <Drawer open={navigationOpen} onOpenChange={setNavigationOpen} side="left" title="Navigation">
        <div className="drawer-navigation"><NavigationRail onNavigate={() => setNavigationOpen(false)} /></div>
      </Drawer>
      <Drawer open={contextOpen} onOpenChange={setContextOpen} side="right" title="Today overview">
        <div className="drawer-context">{context}</div>
      </Drawer>
    </>
  );
}
