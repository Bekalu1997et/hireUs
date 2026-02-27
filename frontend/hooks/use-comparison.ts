"use client";

import { useQuery, useMutation, useQueryClient } from "@tanstack/react-query";
import { comparisonApi } from "@/lib/api";

// Types
export interface CompetencyComparison {
  competency: string;
  scores: Record<string, number>;
  average: number;
  std_deviation: number | null;
  min_score: number;
  max_score: number;
}

export interface CandidateSummary {
  id: string;
  name: string;
  email: string;
  role_id?: string;
  role_title?: string;
  status: string;
  current_stage?: string;
}

export interface CandidateScoreSummary {
  candidate_id: string;
  candidate_name: string;
  overall_average: number;
  total_evaluations: number;
  competency_scores: Record<string, number>;
  average_confidence: number;
  confidence_variance: number | null;
  recommendation_counts: Record<string, number>;
  dominant_recommendation?: string;
}

export interface SignalGap {
  competency: string;
  severity: string;
  description: string;
  recommendation: string;
}

export interface CandidateRanking {
  rank: number;
  candidate_id: string;
  candidate_name: string;
  score: number;
  improvement_areas: string[];
  strengths: string[];
}

export interface ComparisonResponse {
  compared_at: string;
  candidates_compared: number;
  candidates: CandidateSummary[];
  score_summaries: Record<string, CandidateScoreSummary>;
  competency_comparisons: CompetencyComparison[];
  rankings: {
    by_overall_score: Array<{
      rank: number;
      candidate_id: string;
      candidate_name: string;
      score: number;
    }>;
    by_confidence: Array<{
      rank: number;
      candidate_id: string;
      candidate_name: string;
      score: number;
    }>;
    by_recommendation: Array<{
      rank: number;
      candidate_id: string;
      candidate_name: string;
      score: number;
    }>;
    by_evaluation_count: Array<{
      rank: number;
      candidate_id: string;
      candidate_name: string;
      score: number;
    }>;
  };
  feedback_summary?: {
    overall: string;
    strengths_count: string;
    weaknesses_count: string;
    summaries_count: string;
  };
}

export interface SignalGapResponse {
  candidate_id: string;
  has_gaps: boolean;
  signal_gaps: SignalGap[];
  overall_signal_strength: string;
  recommendations: string[];
  analyzed_at: string;
}

export interface RankingResponse {
  criteria: string;
  direction: string;
  rankings: CandidateRanking[];
  generated_at: string;
}

export interface HeatmapData {
  competencies: string[];
  candidates: string[];
  data: Array<{
    competency: string;
    scores: Record<string, number>;
  }>;
  candidate_averages: Record<string, number>;
}

// Hook for comparing candidates
export function useCompareCandidates(params: {
  candidate_ids: string[];
  include_evaluations?: boolean;
  include_feedback_summary?: boolean;
}) {
  return useQuery({
    queryKey: ["comparison", params.candidate_ids],
    queryFn: async () => {
      const response = await comparisonApi.compare(params);
      return response as ComparisonResponse;
    },
    enabled: params.candidate_ids.length >= 2,
  });
}

// Hook for detecting signal gaps
export function useSignalGaps(params: {
  candidate_id: string;
  competency_threshold?: number;
  confidence_threshold?: number;
  variance_threshold?: number;
}) {
  return useQuery({
    queryKey: ["signal-gaps", params.candidate_id],
    queryFn: async () => {
      const response = await comparisonApi.detectSignalGaps(params);
      return response as SignalGapResponse;
    },
    enabled: !!params.candidate_id,
  });
}

// Hook for ranking candidates
export function useRankCandidates(params: {
  candidate_ids: string[];
  criteria?: string;
}) {
  return useQuery({
    queryKey: ["ranking", params.candidate_ids, params.criteria],
    queryFn: async () => {
      const response = await comparisonApi.rank(params);
      return response as RankingResponse;
    },
    enabled: params.candidate_ids.length >= 2,
  });
}

// Hook for getting heatmap data
export function useHeatmapData(candidateIds: string[]) {
  return useQuery({
    queryKey: ["heatmap", candidateIds],
    queryFn: async () => {
      const response = await comparisonApi.getHeatmap(candidateIds);
      return response as HeatmapData;
    },
    enabled: candidateIds.length >= 2,
  });
}

// Hook for getting comparable candidates for a role
export function useComparableCandidates(params: {
  roleId: string;
  minEvaluations?: number;
  skip?: number;
  limit?: number;
}) {
  return useQuery({
    queryKey: ["comparable-candidates", params],
    queryFn: async () => {
      const response = await comparisonApi.getRoleCandidates(params);
      return response as {
        candidates: Array<{
          id: string;
          name: string;
          email: string;
          status: string;
          role_title?: string;
        }>;
        count: number;
      };
    },
    enabled: !!params.roleId,
  });
}

// Hook for comparing all candidates in a role
export function useRoleComparison(roleId: string, statusFilter?: string[]) {
  return useQuery({
    queryKey: ["role-comparison", roleId, statusFilter],
    queryFn: async () => {
      const response = await comparisonApi.compareRoleCandidates(roleId, statusFilter);
      return response as {
        comparison_available: boolean;
        comparison?: ComparisonResponse;
        message?: string;
        candidates_found?: number;
      };
    },
    enabled: !!roleId,
  });
}

// Hook for getting a candidate's comparison summary
export function useCandidateComparisonSummary(candidateId: string) {
  return useQuery({
    queryKey: ["candidate-comparison-summary", candidateId],
    queryFn: async () => {
      const response = await comparisonApi.getSummary(candidateId);
      return response as {
        candidate: CandidateSummary;
        statistics: {
          total_evaluations: number;
          overall_average: number;
          competency_scores: Record<string, number>;
          confidence_scores: number[];
          recommendation_counts: Record<string, number>;
        };
        feedback: {
          strengths: string[];
          weaknesses: string[];
          summaries: string[];
          overall_themes: string[];
          total_feedback_count: number;
        };
        heatmap: HeatmapData;
      };
    },
    enabled: !!candidateId,
  });
}

// Mutation for batch comparison
export function useBatchComparison() {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: async (params: {
      candidate_ids: string[];
      max_candidates_per_comparison?: number;
      include_heatmap?: boolean;
    }) => {
      const response = await comparisonApi.batchCompare(params);
      return response as {
        total_candidates: number;
        total_chunks: number;
        chunks: Array<{
          chunk_index: number;
          candidates: CandidateSummary[];
          comparison: ComparisonResponse;
        }>;
        top_candidates: CandidateRanking[];
        generated_at: string;
      };
    },
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ["comparison"] });
      queryClient.invalidateQueries({ queryKey: ["heatmap"] });
      queryClient.invalidateQueries({ queryKey: ["ranking"] });
    },
  });
}

// Hook for managing comparison selection state
export function useComparisonSelection() {
  const [selectedIds, setSelectedIds] = React.useState<string[]>([]);
  const [maxSelection, setMaxSelection] = React.useState(10);

  const toggleCandidate = (id: string) => {
    setSelectedIds((prev) => {
      if (prev.includes(id)) {
        return prev.filter((i) => i !== id);
      }
      if (prev.length >= maxSelection) {
        return prev;
      }
      return [...prev, id];
    });
  };

  const selectAll = (ids: string[]) => {
    setSelectedIds(ids.slice(0, maxSelection));
  };

  const clearSelection = () => {
    setSelectedIds([]);
  };

  const isSelected = (id: string) => selectedIds.includes(id);

  const canSelectMore = selectedIds.length < maxSelection;

  return {
    selectedIds,
    toggleCandidate,
    selectAll,
    clearSelection,
    isSelected,
    canSelectMore,
    maxSelection,
    setMaxSelection,
    count: selectedIds.length,
    isEmpty: selectedIds.length === 0,
    hasMinimum: selectedIds.length >= 2,
  };
}

import React from "react";

