"use client";

import * as Dialog from "@radix-ui/react-dialog";
import { Command, Plus, Search } from "lucide-react";
import { useRouter } from "next/navigation";
import { useEffect, useMemo, useState } from "react";
import { useUiStore } from "@/store/ui-store";

const commands = [
  { label: "Start new research", href: "/new-research", create: true }, { label: "Go to Today", href: "/" },
  { label: "Go to Companies", href: "/companies" }, { label: "Go to Industries", href: "/industries" }, { label: "Open library", href: "/library" },
];

export function CommandPalette({ triggerRef }: { triggerRef: React.RefObject<HTMLButtonElement | null> }) {
  const router = useRouter();
  const open = useUiStore((state) => state.commandPaletteOpen);
  const setOpen = useUiStore((state) => state.setCommandPaletteOpen);
  const [query, setQuery] = useState("");
  const [activeIndex, setActiveIndex] = useState(0);
  const filtered = useMemo(() => commands.filter((command) => command.label.toLowerCase().includes(query.toLowerCase())), [query]);

  useEffect(() => {
    const onKeyDown = (event: KeyboardEvent) => {
      if ((event.metaKey || event.ctrlKey) && event.key.toLowerCase() === "k") { event.preventDefault(); setOpen(!open); }
    };
    window.addEventListener("keydown", onKeyDown);
    return () => window.removeEventListener("keydown", onKeyDown);
  }, [open, setOpen]);

  const select = (href: string) => { setOpen(false); router.push(href); };
  return (
    <Dialog.Root open={open} onOpenChange={(next) => { setOpen(next); if (!next) setQuery(""); }}>
      <Dialog.Portal>
        <Dialog.Overlay className="palette-backdrop" />
        <Dialog.Content className="palette" aria-describedby={undefined} onCloseAutoFocus={(event) => { event.preventDefault(); triggerRef.current?.focus(); }}>
          <Dialog.Title className="sr-only">Command palette</Dialog.Title>
          <div><Search size={18} aria-hidden="true" /><input value={query} onChange={(event) => { setQuery(event.target.value); setActiveIndex(0); }} onKeyDown={(event) => {
            if (event.key === "ArrowDown") { event.preventDefault(); setActiveIndex((index) => Math.min(index + 1, filtered.length - 1)); }
            if (event.key === "ArrowUp") { event.preventDefault(); setActiveIndex((index) => Math.max(index - 1, 0)); }
            if (event.key === "Enter" && filtered[activeIndex]) select(filtered[activeIndex].href);
          }} placeholder="Search commands, companies, or sources…" aria-label="Search commands" autoFocus /><kbd>Esc</kbd></div>
          <p>NAVIGATE</p>
          <div role="listbox" aria-label="Commands">
            {filtered.map((item, index) => <button key={item.label} type="button" role="option" aria-selected={index === activeIndex} className={index === activeIndex ? "command-active" : ""} onMouseMove={() => setActiveIndex(index)} onClick={() => select(item.href)}>{item.create ? <Plus size={17} /> : <Command size={17} />}{item.label}<Command size={14} /></button>)}
            {filtered.length === 0 && <span className="command-empty">No matching commands</span>}
          </div>
        </Dialog.Content>
      </Dialog.Portal>
    </Dialog.Root>
  );
}
