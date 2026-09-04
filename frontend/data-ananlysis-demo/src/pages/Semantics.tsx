/**
 * Semantics Page - Metric and dimension definitions
 */

import { useQuery } from "@tanstack/react-query";
import { semanticApi } from "../api/client";

export function SemanticsPage() {
  const { data, isLoading } = useQuery({
    queryKey: ["semantic"],
    queryFn: semanticApi.get,
  });

  if (isLoading) {
    return <LoadingSpinner />;
  }

  if (!data || data.status === "unavailable") {
    return (
      <div className="h-full flex items-center justify-center">
        <div className="bg-white rounded-xl border border-[#E5E7EB] p-6 text-center">
          <p className="text-[14px] text-[#DC2626] mb-2">Semantic package not available</p>
          <p className="text-[12px] text-[#9CA3AF]">Build the semantic package to enable this feature</p>
        </div>
      </div>
    );
  }

  const metrics = data.metrics || [];
  const dimensions = data.dimensions || [];

  return (
    <div className="h-full overflow-y-auto p-6">
      <div className="max-w-5xl mx-auto">
        <div className="mb-6">
          <h1 className="text-[20px] font-semibold text-[#1A1A2E]">Semantic Explorer</h1>
          <p className="text-[14px] text-[#6B7280]">Browse metric definitions and dimensions</p>
        </div>

        {/* Metrics */}
        <div className="bg-white rounded-xl border border-[#E5E7EB] overflow-hidden mb-6">
          <div className="px-5 py-4 border-b border-[#E5E7EB]">
            <h2 className="text-[14px] font-semibold text-[#1A1A2E]">Metrics ({metrics.length})</h2>
          </div>
          <table className="w-full">
            <thead>
              <tr className="text-left text-[11px] text-[#6B7280] uppercase border-b border-[#E5E7EB] bg-[#F9FAFB]">
                <th className="px-5 py-3 font-semibold">Metric</th>
                <th className="px-4 py-3 font-semibold w-28">Unit</th>
                <th className="px-4 py-3 font-semibold">Availability</th>
              </tr>
            </thead>
            <tbody>
              {metrics.map((m) => (
                <tr key={m.id} className="border-b border-[#F3F4F6] hover:bg-[#F9FAFB]">
                  <td className="px-5 py-3">
                    <p className="text-[14px] font-medium text-[#1A1A2E]">{m.label}</p>
                    {m.description && <p className="text-[12px] text-[#9CA3AF]">{m.description}</p>}
                  </td>
                  <td className="px-4 py-3 text-[13px] text-[#6B7280]">{m.unit || "—"}</td>
                  <td className="px-4 py-3 text-[13px] text-[#9CA3AF]">{m.availability || "—"}</td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>

        {/* Dimensions */}
        <div className="bg-white rounded-xl border border-[#E5E7EB] overflow-hidden">
          <div className="px-5 py-4 border-b border-[#E5E7EB]">
            <h2 className="text-[14px] font-semibold text-[#1A1A2E]">Dimensions ({dimensions.length})</h2>
          </div>
          <div className="p-5">
            <div className="flex flex-wrap gap-2">
              {dimensions.map((d) => (
                <span key={d.id} className="px-3 py-1.5 text-[13px] bg-[#F5F5F5] text-[#1A1A2E] rounded-lg">
                  {d.label}
                </span>
              ))}
            </div>
          </div>
        </div>
      </div>
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
