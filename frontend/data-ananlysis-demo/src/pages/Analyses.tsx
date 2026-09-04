/**
 * Analyses Page - List of all analyses
 */

import { useState } from "react";
import { useNavigate } from "react-router-dom";
import { useQuery } from "@tanstack/react-query";
import { analysisApi } from "../api/client";

export function AnalysesPage() {
  const navigate = useNavigate();
  const [search, setSearch] = useState("");

  const { data, isLoading } = useQuery({
    queryKey: ["analyses"],
    queryFn: analysisApi.list,
    refetchInterval: 10000,
  });

  const analyses = data?.items || [];
  const filtered = analyses.filter((a) =>
    !search || a.question.toLowerCase().includes(search.toLowerCase())
  );

  return (
    <div className="h-full flex flex-col">
      {/* Header */}
      <div className="px-6 py-4 bg-white border-b border-[#E5E7EB] shrink-0">
        <div className="flex items-center justify-between mb-4">
          <h1 className="text-[20px] font-semibold text-[#1A1A2E]">Analyses</h1>
          <button
            onClick={() => navigate("/today")}
            className="px-4 py-2 bg-[#00D4AA] text-white text-[14px] font-medium rounded-lg hover:bg-[#00B894]"
          >
            New Analysis
          </button>
        </div>

        {/* Search */}
        <div className="relative max-w-md">
          <svg className="absolute left-3 top-1/2 -translate-y-1/2 w-4 h-4 text-[#9CA3AF]" viewBox="0 0 20 20" fill="none" stroke="currentColor" strokeWidth="1.5">
            <circle cx="9" cy="9" r="6"/>
            <path d="M13 13l4 4" strokeLinecap="round"/>
          </svg>
          <input
            type="text"
            value={search}
            onChange={(e) => setSearch(e.target.value)}
            placeholder="Search analyses..."
            className="w-full pl-10 pr-4 py-2 text-[14px] border border-[#E5E7EB] rounded-lg outline-none focus:border-[#00D4AA]"
          />
        </div>
      </div>

      {/* Table */}
      <div className="flex-1 overflow-y-auto">
        {isLoading ? (
          <div className="p-6">
            {[1, 2, 3].map((i) => (
              <div key={i} className="h-14 bg-white border-b border-[#E5E7EB] animate-pulse mb-2 rounded" />
            ))}
          </div>
        ) : filtered.length === 0 ? (
          <div className="p-12 text-center">
            <p className="text-[14px] text-[#9CA3AF] mb-4">
              {search ? `No analyses matching "${search}"` : "No analyses yet"}
            </p>
            <button
              onClick={() => navigate("/today")}
              className="text-[14px] text-[#00D4AA] hover:underline"
            >
              Create your first analysis
            </button>
          </div>
        ) : (
          <table className="w-full">
            <thead className="bg-white sticky top-0">
              <tr className="text-left text-[11px] text-[#6B7280] uppercase border-b border-[#E5E7EB]">
                <th className="px-6 py-3 font-semibold">Question</th>
                <th className="px-4 py-3 font-semibold w-28">Status</th>
                <th className="px-4 py-3 font-semibold w-40">Created</th>
                <th className="px-4 py-3 font-semibold w-40">Updated</th>
              </tr>
            </thead>
            <tbody>
              {filtered.map((analysis) => (
                <tr
                  key={analysis.id}
                  onClick={() => navigate(`/analyses/${analysis.id}`)}
                  className="bg-white border-b border-[#F3F4F6] hover:bg-[#F9FAFB] cursor-pointer transition-colors"
                >
                  <td className="px-6 py-4">
                    <span className="text-[14px] text-[#1A1A2E]">{analysis.question}</span>
                  </td>
                  <td className="px-4 py-4">
                    <StatusBadge state={analysis.state || analysis.status} />
                  </td>
                  <td className="px-4 py-4 text-[13px] text-[#6B7280]">
                    {new Date(analysis.createdAt).toLocaleDateString()}
                  </td>
                  <td className="px-4 py-4 text-[13px] text-[#6B7280]">
                    {new Date(analysis.updatedAt).toLocaleDateString()}
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        )}
      </div>
    </div>
  );
}

function StatusBadge({ state }: { state?: string }) {
  const config: Record<string, { label: string; bg: string; text: string }> = {
    COMPLETED: { label: "Done", bg: "bg-[#DCFCE7]", text: "text-[#16A34A]" },
    RUNNING: { label: "Running", bg: "bg-[#DBEAFE]", text: "text-[#2563EB]" },
    PARTIAL: { label: "Partial", bg: "bg-[#FEF3C7]", text: "text-[#D97706]" },
    FAILED: { label: "Failed", bg: "bg-[#FEE2E2]", text: "text-[#DC2626]" },
  };

  const { label, bg, text } = config[state?.toUpperCase() || ""] || {
    label: "Unknown",
    bg: "bg-[#F3F4F6]",
    text: "text-[#6B7280]",
  };

  return (
    <span className={`px-2 py-0.5 text-[11px] font-medium rounded ${bg} ${text}`}>
      {label}
    </span>
  );
}
