import type { Metadata } from "next";
import type { ReactNode } from "react";
import { AppProviders } from "@/providers/app-providers";
import "./globals.css";

export const metadata: Metadata = {
  title: "Atlas Research",
  description: "Evidence-first AI research workspace prototype",
};

export default function RootLayout({ children }: Readonly<{ children: ReactNode }>) {
  return (
    <html lang="en" className="h-full antialiased">
      <body><AppProviders>{children}</AppProviders></body>
    </html>
  );
}
