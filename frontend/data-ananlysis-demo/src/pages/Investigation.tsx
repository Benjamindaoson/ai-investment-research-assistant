/**
 * Investigation Page - Hypothesis testing
 */

import { useParams } from "react-router-dom";
import { useQuery } from "@tanstack/react-query";
import { analysisApi } from "../api/client";

export function InvestigationPage() {
  const { taskId } = useParams<{ taskId: string }>();

  const { data, isLoading } = useQuery({
    queryKey: ["investigation", taskId],
    queryFn: () => analysisApi.investigation(taskId!),
    enabled: !!taskId,
  });

  if (isLoading) {
    return <LoadingSpinner />;
  }

  const hypotheses = data?.hypotheses || [];
  const observations = data?.observations || [];
  const contributions = data?.contributions || [];

  return (
    <div className="h-full overflow-y-auto p-6">
      <div className="max-w-6xl mx-auto">
        <h2 className="text-[18px] font-semibold text-[#1A1A2E] mb-6">Investigation</h2>

        <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
          {/* Hypotheses */}
          <div className="bg-white rounded-xl border border-[#E5E7EB] overflow-hidden">
            <div className="px-5 py-4 border-b border-[#E5E7EB]">
              <h3 className="text-[14px] font-semibold text-[#1A1A2E]">Hypotheses</h3>
            </div>
            <div className="p-5">
              {hypotheses.length === 0 ? (
                <p className="text-[13px] text-[#9CA3AF]">No hypotheses yet</p>
              ) : (
                <div className="space-y-3">
                  {hypotheses.map((h) => (
                    <div key={h.id} className="flex items-start gap-3">
                      <StatusIcon status={h.status} />
                      <p className="text-[13px] text-[#6B7280]">{typeof h.text === 'string' ? h.text : 'Hypothesis data'}</p>
                    </div>
                  ))}
                </div>
              )}
            </div>
          </div>

          {/* Observations */}
          <div className="bg-white rounded-xl border border-[#E5E7EB] overflow-hidden">
            <div className="px-5 py-4 border-b border-[#E5E7EB]">
              <h3 className="text-[14px] font-semibold text-[#1A1A2E]">Observations</h3>
            </div>
            <div className="p-5">
              {observations.length === 0 ? (
                <p className="text-[13px] text-[#9CA3AF]">No observations yet</p>
              ) : (
                <div className="space-y-3">
                  {observations.map((o) => (
                    <p key={o.id} className="text-[13px] text-[#6B7280]">{typeof o.text === 'string' ? o.text : 'Observation data'}</p>
                  ))}
                </div>
              )}
            </div>
          </div>

          {/* Contributions */}
          <div className="bg-white rounded-xl border border-[#E5E7EB] overflow-hidden">
            <div className="px-5 py-4 border-b border-[#E5E7EB]">
              <h3 className="text-[14px] font-semibold text-[#1A1A2E]">Top Contributors</h3>
            </div>
            <div className="p-5">
              {contributions.length === 0 ? (
                <p className="text-[13px] text-[#9CA3AF]">No data yet</p>
              ) : (
                <div className="space-y-2">
                  {contributions.slice(0, 8).map((c, i) => {
                    const label = typeof c.label === 'string' ? c.label : (typeof c.dimension === 'string' ? c.dimension : 'Unknown');
                    const value = typeof c.value === 'number' ? c.value : 0;
                    return (
                      <div key={i} className="flex items-center justify-between py-2 border-b border-[#F3F4F6] last:border-0">
                        <span className="text-[13px] text-[#6B7280] truncate flex-1 mr-2">{label}</span>
                        <span className={`text-[13px] font-medium ${value < 0 ? "text-[#DC2626]" : "text-[#16A34A]"}`}>
                          {value > 0 ? "+" : ""}{value.toFixed(1)}%
                        </span>
                      </div>
                    );
                  })}
                </div>
              )}
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}

function StatusIcon({ status }: { status: string }) {
  const colors: Record<string, string> = {
    proposed: "text-[#9CA3AF]",
    testing: "text-[#2563EB]",
    supported: "text-[#16A34A]",
    rejected: "text-[#DC2626]",
  };

  return (
    <span className={`text-[14px] font-bold ${colors[status] || colors.proposed}`}>
      {status === "supported" ? "✓" : status === "rejected" ? "✗" : "○"}
    </span>
  );
}

function LoadingSpinner() {
  return (
    <div className="h-full flex items-center justify-center">
      <div className="w-8 h-8 border-2 border-[#00D4AA] border-t-transparent rounded-full animate-spin" />
    </div>
  );
}
