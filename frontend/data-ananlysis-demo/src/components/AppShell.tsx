/**
 * AppShell - Professional Financial Analytics Layout
 *
 * Design: Clean, bright, information-dense like Bloomberg Terminal
 * but with modern UI. Reference: S&P Capital IQ, Reuters, Bloomberg
 */

import { Outlet, NavLink, useLocation, useParams } from "react-router-dom";
import { useQuery } from "@tanstack/react-query";
import { health } from "../api/client";

const NAV_ITEMS = [
  { path: "/today", label: "Home", icon: HomeIcon },
  { path: "/analyses", label: "Analyses", icon: AnalysesIcon },
  { path: "/data", label: "Data", icon: DataIcon },
  { path: "/semantics", label: "Semantics", icon: SemanticsIcon },
  { path: "/evaluation", label: "Evaluation", icon: EvaluationIcon },
  { path: "/settings", label: "Settings", icon: SettingsIcon },
];

export function AppShell() {
  const location = useLocation();
  const params = useParams();

  const { data: healthData } = useQuery({
    queryKey: ["health"],
    queryFn: health.check,
    refetchInterval: 30000,
  });

  const breadcrumbs = getBreadcrumbs(location.pathname, params);

  return (
    <div className="flex h-screen bg-[#F5F5F5]">
      {/* Left Navigation */}
      <nav className="w-[220px] bg-[#1A1A2E] text-white flex flex-col shrink-0">
        {/* Brand */}
        <div className="h-14 px-4 flex items-center border-b border-[#2D2D44]">
          <div className="w-8 h-8 bg-[#00D4AA] rounded flex items-center justify-center">
            <svg width="16" height="16" viewBox="0 0 16 16" fill="none">
              <path d="M4 8L7 11L12 5" stroke="#1A1A2E" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round"/>
            </svg>
          </div>
          <span className="ml-3 text-[14px] font-semibold">Enterprise Intel</span>
        </div>

        {/* Nav Items */}
        <div className="flex-1 py-2">
          {NAV_ITEMS.map(({ path, label, icon: Icon }) => (
            <NavLink
              key={path}
              to={path}
              className={({ isActive }) =>
                `flex items-center h-10 px-4 transition-colors ${
                  isActive
                    ? "bg-[#00D4AA]/20 text-[#00D4AA] border-r-2 border-[#00D4AA]"
                    : "text-[#9898B0] hover:bg-[#2D2D44] hover:text-white"
                }`
              }
            >
              <Icon className="w-4 h-4 mr-3" />
              <span className="text-[13px]">{label}</span>
            </NavLink>
          ))}
        </div>

        {/* Status */}
        <div className="p-4 border-t border-[#2D2D44]">
          <div className="flex items-center gap-2 text-[11px]">
            <span className={`w-2 h-2 rounded-full ${healthData?.data_available ? "bg-[#00D4AA]" : "bg-[#FFB800]" }`} />
            <span className="text-[#9898B0]">
              {healthData?.data_available ? "Data Ready" : "Data Pending"}
            </span>
          </div>
        </div>
      </nav>

      {/* Main Content */}
      <div className="flex-1 flex flex-col min-w-0 overflow-hidden">
        {/* Header */}
        <header className="h-14 bg-white border-b border-[#E5E7EB] flex items-center px-6 shrink-0">
          {/* Breadcrumbs */}
          <div className="flex items-center gap-2 text-[13px]">
            {breadcrumbs.map((crumb, i) => (
              <span key={crumb.path} className="flex items-center">
                {i > 0 && <span className="text-[#D1D5DB] mx-1">/</span>}
                <span className={i === breadcrumbs.length - 1 ? "text-[#1A1A2E] font-medium" : "text-[#6B7280]"}>
                  {crumb.label}
                </span>
              </span>
            ))}
          </div>

          <div className="flex-1" />

          {/* Right */}
          <div className="flex items-center gap-3">
            <span className={`px-2.5 py-1 text-[11px] font-medium rounded ${
              healthData?.data_available
                ? "bg-[#DCFCE7] text-[#16A34A]"
                : "bg-[#FEF3C7] text-[#D97706]"
            }`}>
              {healthData?.data_available ? "READY" : "PENDING"}
            </span>
          </div>
        </header>

        {/* Page Content */}
        <main className="flex-1 overflow-hidden bg-[#F5F5F5]">
          <Outlet />
        </main>
      </div>
    </div>
  );
}

function getBreadcrumbs(pathname: string, params: Record<string, string>) {
  const segments = pathname.split("/").filter(Boolean);
  const crumbs = [{ path: "/", label: "Home" }];
  let currentPath = "";

  const routeLabels: Record<string, string> = {
    today: "Home",
    analyses: "Analyses",
    "analysis/new": "New Analysis",
    data: "Data",
    semantics: "Semantics",
    evaluation: "Evaluation",
    settings: "Settings",
  };

  for (let i = 0; i < segments.length; i++) {
    currentPath += `/${segments[i]}`;
    const label = routeLabels[segments[i]] || (params.taskId && i === segments.length - 1 ? "Analysis" : segments[i]);
    crumbs.push({ path: currentPath, label });
  }
  return crumbs;
}

// Icons
function HomeIcon({ className }: { className?: string }) {
  return (
    <svg className={className} viewBox="0 0 20 20" fill="none" stroke="currentColor" strokeWidth="1.5">
      <path d="M3 10l7-7 7 7M17 10l-7 7 7-7" strokeLinecap="round" strokeLinejoin="round"/>
    </svg>
  );
}

function AnalysesIcon({ className }: { className?: string }) {
  return (
    <svg className={className} viewBox="0 0 20 20" fill="none" stroke="currentColor" strokeWidth="1.5">
      <rect x="3" y="3" width="14" height="14" rx="2"/>
      <path d="M6 12l3-4 3 4M10 8l4 4" strokeLinecap="round" strokeLinejoin="round"/>
    </svg>
  );
}

function DataIcon({ className }: { className?: string }) {
  return (
    <svg className={className} viewBox="0 0 20 20" fill="none" stroke="currentColor" strokeWidth="1.5">
      <ellipse cx="10" cy="6" rx="6" ry="2.5"/>
      <path d="M4 6v8c0 1.4 2.7 2.5 6 2.5s6-1.1 6-2.5V6M4 12c0 1.4 2.7 2.5 6 2.5s6-1.1 6-2.5" strokeLinecap="round"/>
    </svg>
  );
}

function SemanticsIcon({ className }: { className?: string }) {
  return (
    <svg className={className} viewBox="0 0 20 20" fill="none" stroke="currentColor" strokeWidth="1.5">
      <path d="M10 2L3 6v6l7 4 7-4V6l-7-4z"/>
      <path d="M10 10v4M7 8l7 4M13 8l-7 4"/>
    </svg>
  );
}

function EvaluationIcon({ className }: { className?: string }) {
  return (
    <svg className={className} viewBox="0 0 20 20" fill="none" stroke="currentColor" strokeWidth="1.5">
      <path d="M4 14l4-4 4 4 4-4M7 10l3-3 3 3" strokeLinecap="round" strokeLinejoin="round"/>
      <circle cx="10" cy="10" r="5"/>
    </svg>
  );
}

function SettingsIcon({ className }: { className?: string }) {
  return (
    <svg className={className} viewBox="0 0 20 20" fill="none" stroke="currentColor" strokeWidth="1.5">
      <circle cx="10" cy="10" r="2"/>
      <path d="M10 3v2M10 15v2M3 10h2M15 10h2M4.9 4.9l1.4 1.4M13.7 13.7l1.4 1.4M4.9 15.1l1.4-1.4M13.7 5.3l1.4-1.4" strokeLinecap="round"/>
    </svg>
  );
}
