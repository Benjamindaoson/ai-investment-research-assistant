/**
 * NewAnalysis Page - Create new analysis
 */

import { useState } from "react";
import { useNavigate } from "react-router-dom";
import { useMutation, useQueryClient } from "@tanstack/react-query";
import { analysisApi, ApiError } from "../api/client";

export function NewAnalysisPage() {
  const navigate = useNavigate();
  const queryClient = useQueryClient();
  const [question, setQuestion] = useState("");
  const [isSubmitting, setIsSubmitting] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const createMutation = useMutation({
    mutationFn: (q: string) => analysisApi.create({ question: q }),
    onSuccess: (data) => {
      queryClient.invalidateQueries({ queryKey: ["analyses"] });
      navigate(`/analyses/${data.id}`);
    },
    onError: (err: ApiError) => {
      setError(err.message || "Failed to create analysis");
      setIsSubmitting(false);
    },
  });

  const handleSubmit = () => {
    if (!question.trim()) return;
    setError(null);
    setIsSubmitting(true);
    createMutation.mutate(question.trim());
  };

  return (
    <div className="h-full overflow-y-auto p-6">
      <div className="max-w-2xl mx-auto">
        <div className="flex items-center justify-between mb-6">
          <h1 className="text-[20px] font-semibold text-[#1A1A2E]">New Analysis</h1>
          <button
            onClick={() => navigate("/today")}
            className="text-[13px] text-[#6B7280] hover:text-[#1A1A2E]"
          >
            Cancel
          </button>
        </div>

        <div className="bg-white rounded-xl border border-[#E5E7EB] p-6">
          <label className="text-[12px] font-semibold text-[#6B7280] uppercase tracking-wide block mb-2">
            Business Question
          </label>
          <textarea
            value={question}
            onChange={(e) => setQuestion(e.target.value)}
            placeholder="e.g., Why did July sales drop compared to June?"
            rows={4}
            disabled={isSubmitting}
            className="w-full text-[14px] text-[#1A1A2E] placeholder-[#9CA3AF] resize-none outline-none border border-[#E5E7EB] rounded-lg p-3 focus:border-[#00D4AA] focus:ring-2 focus:ring-[#00D4AA]/20 disabled:opacity-50"
          />

          {error && (
            <div className="mt-4 p-3 bg-[#FEE2E2] border border-[#FECACA] rounded-lg text-[13px] text-[#DC2626]">
              {error}
            </div>
          )}

          <div className="flex items-center justify-between mt-6 pt-4 border-t border-[#E5E7EB]">
            <span className="text-[12px] text-[#9CA3AF]">
              Press Enter to submit
            </span>
            <button
              onClick={handleSubmit}
              disabled={!question.trim() || isSubmitting}
              className="px-6 py-2.5 bg-[#00D4AA] text-white text-[14px] font-medium rounded-lg hover:bg-[#00B894] disabled:opacity-50 disabled:cursor-not-allowed transition-all"
            >
              {isSubmitting ? "Creating..." : "Start Analysis"}
            </button>
          </div>
        </div>
      </div>
    </div>
  );
}
