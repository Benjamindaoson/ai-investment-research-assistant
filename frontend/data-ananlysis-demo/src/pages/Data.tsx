/**
 * Data Page - Data status
 */

import { useQuery } from "@tanstack/react-query";
import { dataApi } from "../api/client";

export function DataPage() {
  const { data, isLoading } = useQuery({
    queryKey: ["data-status"],
    queryFn: dataApi.status,
  });

  if (isLoading) {
    return <LoadingSpinner />;
  }

  if (!data) {
    return <ErrorMessage message="Failed to load data status" />;
  }

  const dataset = data.dataset;
  const dimensions = data.dimensions || [];
  const metrics = data.metrics || [];

  return (
    <div className="h-full overflow-y-auto p-6">
      <div className="max-w-5xl mx-auto">
        <div className="mb-6">
          <h1 className="text-[20px] font-semibold text-[#1A1A2E]">Data Status</h1>
          <p className="text-[14px] text-[#6B7280]">Dataset information and quality metrics</p>
        </div>

        {/* Snapshot Info */}
        <div className="bg-white rounded-xl border border-[#E5E7EB] overflow-hidden mb-6">
          <div className="px-5 py-4 border-b border-[#E5E7EB] flex items-center justify-between">
            <h2 className="text-[14px] font-semibold text-[#1A1A2E]">
              Snapshot: {dataset?.snapshot_id || 'Unknown'}
            </h2>
            <span className={`px-2.5 py-1 text-[12px] font-medium rounded ${
              dataset?.available ? "bg-[#DCFCE7] text-[#16A34A]" : "bg-[#FEF3C7] text-[#D97706]"
            }`}>
              {dataset?.available ? "LOADED" : "NOT LOADED"}
            </span>
          </div>
          <div className="p-5 grid grid-cols-2 md:grid-cols-4 gap-6">
            <InfoCell label="Status" value={dataset?.status || "—"} />
            <InfoCell label="Records" value={dataset?.measured_row_count?.toLocaleString() || "—"} />
            <InfoCell label="From" value={dataset?.measured_business_date_min || "—"} />
            <InfoCell label="Through" value={dataset?.measured_business_date_max || "—"} />
          </div>
        </div>

        {/* Quality Notes */}
        <div className="bg-white rounded-xl border border-[#E5E7EB] overflow-hidden mb-6">
          <div className="px-5 py-4 border-b border-[#E5E7EB]">
            <h2 className="text-[14px] font-semibold text-[#1A1A2E]">Data Quality Notes</h2>
          </div>
          <div className="p-5 space-y-3">
            <QualityNote type="success" text="20 exact duplicate records removed during curation" />
            <QualityNote type="warning" text="Cost/spread metrics available only from 2025-07-01 onward" />
            <QualityNote type="info" text="Negative values represent adjustments, not returns" />
            <QualityNote type="info" text="Historical naming preserved at transaction time" />
          </div>
        </div>

        {/* Metrics Table */}
        <div className="bg-white rounded-xl border border-[#E5E7EB] overflow-hidden">
          <div className="px-5 py-4 border-b border-[#E5E7EB]">
            <h2 className="text-[14px] font-semibold text-[#1A1A2E]">Available Metrics ({metrics.length})</h2>
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
                    <p className="text-[14px] font-medium text-[#1A1A2E]">{m.label || 'Unknown'}</p>
                    {m.description && <p className="text-[12px] text-[#9CA3AF]">{m.description}</p>}
                  </td>
                  <td className="px-4 py-3 text-[13px] text-[#6B7280]">{m.unit || "—"}</td>
                  <td className="px-4 py-3 text-[13px] text-[#9CA3AF]">{m.availability || "—"}</td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      </div>
    </div>
  );
}

function InfoCell({ label, value }: { label: string; value: string }) {
  return (
    <div>
      <p className="text-[11px] text-[#9CA3AF] uppercase mb-1">{label}</p>
      <p className="text-[14px] text-[#1A1A2E]">{value}</p>
    </div>
  );
}

function QualityNote({ type, text }: { type: "success" | "warning" | "info"; text: string }) {
  const icons = { success: "✓", warning: "⚠", info: "ℹ" };
  const colors = { success: "text-[#16A34A]", warning: "text-[#D97706]", info: "text-[#2563EB]" };

  return (
    <div className="flex items-start gap-3">
      <span className={colors[type]}>{icons[type]}</span>
      <p className="text-[13px] text-[#6B7280]">{text}</p>
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

function ErrorMessage({ message }: { message: string }) {
  return (
    <div className="h-full flex items-center justify-center">
      <div className="bg-white rounded-xl border border-[#E5E7EB] p-6">
        <p className="text-[14px] text-[#DC2626]">{message}</p>
      </div>
    </div>
  );
}
