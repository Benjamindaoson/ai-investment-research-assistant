/**
 * Dashboard Page - Analytics view
 */

import { useParams } from "react-router-dom";
import { useQuery } from "@tanstack/react-query";
import { analysisApi } from "../api/client";

export function DashboardPage() {
  const { taskId } = useParams<{ taskId: string }>();

  const { data: task, isLoading } = useQuery({
    queryKey: ["task", taskId],
    queryFn: () => analysisApi.get(taskId!),
    enabled: !!taskId,
  });

  if (isLoading) {
    return <LoadingSpinner />;
  }

  const claims = task?.claims || [];

  return (
    <div className="h-full overflow-y-auto p-6">
      <div className="max-w-6xl mx-auto">
        <h2 className="text-[18px] font-semibold text-[#1A1A2E] mb-6">Dashboard</h2>

        {/* KPI Cards */}
        <div className="grid grid-cols-2 lg:grid-cols-4 gap-4 mb-6">
          {claims.slice(0, 4).map((claim, i) => (
            <div key={claim.id} className="bg-white rounded-xl border border-[#E5E7EB] p-5">
              <p className="text-[11px] text-[#9CA3AF] uppercase mb-2">Finding {i + 1}</p>
              <p className="text-[14px] text-[#1A1A2E] line-clamp-2">{claim.text}</p>
            </div>
          ))}
          {claims.length < 4 && Array.from({ length: 4 - claims.length }).map((_, i) => (
            <div key={`empty-${i}`} className="bg-[#F9FAFB] rounded-xl border border-[#E5E7EB] p-5 opacity-50">
              <p className="text-[11px] text-[#9CA3AF] uppercase mb-2">—</p>
              <p className="text-[14px] text-[#9CA3AF]">No data</p>
            </div>
          ))}
        </div>

        {/* Findings Table */}
        <div className="bg-white rounded-xl border border-[#E5E7EB] overflow-hidden">
          <div className="px-5 py-4 border-b border-[#E5E7EB]">
            <h3 className="text-[14px] font-semibold text-[#1A1A2E]">Key Findings</h3>
          </div>
          {claims.length === 0 ? (
            <div className="p-8 text-center text-[13px] text-[#9CA3AF]">No findings to display</div>
          ) : (
            <table className="w-full">
              <thead>
                <tr className="text-left text-[11px] text-[#6B7280] uppercase border-b border-[#E5E7EB] bg-[#F9FAFB]">
                  <th className="px-5 py-3 font-semibold w-24">Type</th>
                  <th className="px-4 py-3 font-semibold">Finding</th>
                  <th className="px-4 py-3 font-semibold w-32">Confidence</th>
                </tr>
              </thead>
              <tbody>
                {claims.map((claim) => (
                  <tr key={claim.id} className="border-b border-[#F3F4F6] hover:bg-[#F9FAFB]">
                    <td className="px-5 py-4">
                      <ClaimTypeBadge type={claim.type} />
                    </td>
                    <td className="px-4 py-4 text-[14px] text-[#1A1A2E]">{claim.text}</td>
                    <td className="px-4 py-4">
                      <ConfidenceBar confidence={claim.confidence} />
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          )}
        </div>
      </div>
    </div>
  );
}

function ClaimTypeBadge({ type }: { type: string }) {
  const config: Record<string, { label: string; bg: string; text: string }> = {
    FACT: { label: "FACT", bg: "bg-[#DCFCE7]", text: "text-[#16A34A]" },
    INFERENCE: { label: "INFERENCE", bg: "bg-[#DBEAFE]", text: "text-[#2563EB]" },
    QUALIFIED: { label: "QUALIFIED", bg: "bg-[#FEF3C7]", text: "text-[#D97706]" },
  };

  const { label, bg, text } = config[type] || {
    label: type.substring(0, 3).toUpperCase(),
    bg: "bg-[#F3F4F6]",
    text: "text-[#6B7280]",
  };

  return (
    <span className={`px-2 py-1 text-[10px] font-bold rounded ${bg} ${text}`}>
      {label}
    </span>
  );
}

function ConfidenceBar({ confidence }: { confidence?: number }) {
  const pct = confidence ? Math.round(confidence * 100) : 0;
  return (
    <div className="flex items-center gap-2">
      <div className="w-20 h-1.5 bg-[#E5E7EB] rounded-full overflow-hidden">
        <div className="h-full bg-[#00D4AA] rounded-full" style={{ width: `${pct}%` }} />
      </div>
      <span className="text-[12px] text-[#6B7280]">{pct}%</span>
    </div>
  );
}

function LoadingSpinner() {
  return (
    <div className="h-full flex items-center justify-center">
      <div className="w-8 h-8 border-2 border-[#00D4AA] border-t-transparent rounded-full animate-spin" />
    </div>
  );
}
