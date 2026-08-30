"use client";

import Link from "next/link";
import { usePathname } from "next/navigation";
import { BookOpen, ChevronDown, Clock3, FileText, Grid2X2, Home, Library, Menu, Plus, Target } from "lucide-react";

const primaryItems = [
  { label: "Today", href: "/", icon: Home },
  { label: "Research", href: "/research", icon: FileText },
  { label: "Companies", href: "/companies", icon: BookOpen },
  { label: "Industries", href: "/industries", icon: Grid2X2 },
  { label: "Watchlist", href: "/watchlist", icon: Target },
  { label: "Library", href: "/library", icon: Library },
] as const;

export function NavigationRail({ onNavigate }: { onNavigate?: () => void }) {
  const pathname = usePathname();
  return (
    <div className="navigation-rail-inner">
      <div className="atlas-brand">◇ Atlas Research</div>
      <Link className="atlas-new" href="/new-research" onClick={onNavigate}>
        <Plus size={17} />New research<ChevronDown size={15} aria-hidden="true" />
      </Link>
      <nav aria-label="Primary navigation">
        {primaryItems.map(({ label, href, icon: Icon }) => {
          const active = href === "/" ? pathname === "/" : pathname.startsWith(href);
          return (
          <Link className={`atlas-nav ${active ? "active" : ""}`} href={href} aria-current={active ? "page" : undefined} key={label} onClick={onNavigate}>
            <Icon size={18} aria-hidden="true" />{label}
          </Link>
        );})}
      </nav>
      <div className="atlas-rule" />
      <small>WORKSPACE</small>
      <Link className="atlas-nav" href="/activity" onClick={onNavigate}><Clock3 size={18} aria-hidden="true" />Research activity</Link>
      <button className="atlas-nav rail-collapse" type="button"><Menu size={18} aria-hidden="true" />Collapse sidebar</button>
    </div>
  );
}
