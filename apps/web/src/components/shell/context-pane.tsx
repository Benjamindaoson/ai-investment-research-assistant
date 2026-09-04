import type { ReactNode } from "react";

export function ContextPane({ children }: { children: ReactNode }) {
  return <aside className="atlas-context" aria-label="Page context">{children}</aside>;
}
