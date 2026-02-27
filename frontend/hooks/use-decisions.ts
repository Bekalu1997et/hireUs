"use client";

import { useQuery, useMutation, useQueryClient } from "@tanstack/react-query";
import { decisionApi } from "@/lib/api";

// Types
export interface CandidateBrief {
  candidate_id: string;
  candidate_name: string;
  role_title: string;
  total_evaluations: number;
  overall_average: number;
  recommendation_breakdown: Record<string, number>;
  last_updated: string;
}

export interface DecisionBriefContent {
  generated_at: string;
  candidate: {
    name: string;
    role_applied: string;
    overall_score: number;
    total_evaluations: number;
    recommendation_breakdown: Record<string, number>;
  };
  strengths: Array<{
    category: string;
    description: string;
    evidence: string[];
    competency_scores: Record<string, number>;
  }>;
  risk_areas: Array<{
    category: string;
    description: string;
    severity: "low" | "medium" | "high";
    mitigation?: string;
    evidence: string[];
  }>;
  signal_gaps: Array<{
    competency: string;
    status: "missing" | "weak" | "conflicting";
    reason: string;
    recommendation: string;
    confidence_impact?: string;
  }>;
  interview_agreement: {
    level: "strong_agreement" | "moderate_agreement" | "mixed_opinions" | "conflicting_views";
    description: string;
    agreements: string[];
    disagreements: string[];
    confidence_score: number;
    evaluator_count: number;
  };
  suggested_decision: {
    decision: "strong_hire" | "hire" | "neutral" | "no_hire" | "strong_no_hire" | "defer";
    confidence: number;
    reasoning: string;
    key_factors: string[];
    risks_acknowledged: string[];
    next_steps: string[];
  };
  evaluation_ids: string[];
  model_used?: string;
  processing_time_ms?: number;
}

export interface DecisionBrief {
  id: string;
  candidate_id: string;
  candidate_name: string;
  role_title: string;
  organization_id: string;
  generated_by: string;
  generated_at: string;
  content: DecisionBriefContent;
}

export interface SignalAnalysis {
  candidate_id: string;
  candidate_name: string;
  total_evaluations: number;
  overall_signal_strength: "strong" | "moderate" | "weak" | "none";
  signal_gaps: Array<{
    competency: string;
    status: string;
    reason: string;
    recommendation: string;
    confidence_impact?: string;
  }>;
  interview_agreement: {
    level: string;
    description: string;
    agreements: string[];
    disagreements: string[];
    confidence_score: number;
    evaluator_count: number;
  };
  evaluation_stats: {
    overall_average: number;
    average_confidence: number;
    recommendation_counts: Record<string, number>;
  };
}

export interface EvaluationStats {
  total_evaluations: number;
  overall_average: number;
  competency_scores: Record<string, number>;
  confidence_scores: number[];
  average_confidence: number;
  recommendation_counts: Record<string, number>;
}

// Hook for generating a decision brief
export function useGenerateDecisionBrief() {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: async (params: {
      candidateId: string;
      organizationId: string;
      include_comparison?: boolean;
      comparison_candidate_ids?: string[];
      focus_areas?: string[];
      custom_prompt?: string;
    }) => {
      const response = await decisionApi.generateBrief(
        {
          candidate_id: params.candidateId,
          include_comparison: params.include_comparison,
          comparison_candidate_ids: params.comparison_candidate_ids,
          focus_areas: params.focus_areas,
          custom_prompt: params.custom_prompt,
        },
        params.organizationId
      );
      return response as DecisionBrief;
    },
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ["decisions"] });
      queryClient.invalidateQueries({ queryKey: ["candidate-briefs"] });
    },
  });
}

// Hook for getting a candidate's briefs
export function useCandidateBriefs(candidateId: string, organizationId: string) {
  return useQuery({
    queryKey: ["candidate-briefs", candidateId],
    queryFn: async () => {
      const response = await decisionApi.getCandidateBriefs(candidateId, organizationId);
      return response as {
        candidate_id: string;
        briefs: CandidateBrief[];
        count: number;
      };
    },
    enabled: !!candidateId && !!organizationId,
  });
}

// Hook for getting signal analysis for a candidate
export function useSignalAnalysis(candidateId: string) {
  return useQuery({
    queryKey: ["signal-analysis", candidateId],
    queryFn: async () => {
      const response = await decisionApi.getSignalAnalysis(candidateId);
      return response as SignalAnalysis;
    },
    enabled: !!candidateId,
  });
}

// Hook for getting evaluation statistics for a candidate
export function useCandidateDecisionStats(candidateId: string) {
  return useQuery({
    queryKey: ["candidate-decision-stats", candidateId],
    queryFn: async () => {
      const response = await decisionApi.getCandidateStats(candidateId);
      return response as {
        candidate_id: string;
        statistics: EvaluationStats;
      };
    },
    enabled: !!candidateId,
  });
}

// Hook for getting candidates eligible for decision briefs
export function useComparableCandidates(params: {
  organizationId: string;
  roleId?: string;
  minEvaluations?: number;
  skip?: number;
  limit?: number;
}) {
  return useQuery({
    queryKey: ["comparable-candidates", params],
    queryFn: async () => {
      const response = await decisionApi.getComparableCandidates({
        organization_id: params.organizationId,
        role_id: params.roleId,
        min_evaluations: params.minEvaluations,
        skip: params.skip,
        limit: params.limit,
      });
      return response as {
        candidates: Array<{
          id: string;
          full_name: string;
          email: string;
          status: string;
          role_id: string;
          role_title: string;
        }>;
        count: number;
        total: number;
        page: number;
        page_size: number;
        total_pages: number;
      };
    },
    enabled: !!params.organizationId,
  });
}

// Hook for getting decision summary
export function useDecisionSummary(params: {
  organizationId: string;
  roleId?: string;
  minEvaluations?: number;
  skip?: number;
  limit?: number;
}) {
  return useQuery({
    queryKey: ["decision-summary", params],
    queryFn: async () => {
      const response = await decisionApi.getDecisionSummary({
        organization_id: params.organizationId,
        role_id: params.roleId,
        min_evaluations: params.minEvaluations,
        skip: params.skip,
        limit: params.limit,
      });
      return response as {
        summary: {
          total_candidates: number;
          role_filter?: string;
          min_evaluations: number;
        };
        candidates: Array<{
          id: string;
          full_name: string;
          email: string;
          status: string;
          role_id: string;
          role_title: string;
        }>;
        pagination: {
          page: number;
          page_size: number;
          total_pages: number;
        };
      };
    },
    enabled: !!params.organizationId,
  });
}

// Hook for bulk generating decision briefs
export function useBulkGenerateBriefs() {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: async (params: {
      candidateIds: string[];
      organizationId: string;
    }) => {
      const response = await decisionApi.bulkGenerateBriefs(
        params.candidateIds,
        params.organizationId
      );
      return response as {
        successful: DecisionBrief[];
        failed: Array<{ candidate_id: string; error: string }>;
        total: number;
        success_count: number;
        failure_count: number;
      };
    },
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ["decisions"] });
      queryClient.invalidateQueries({ queryKey: ["candidate-briefs"] });
      queryClient.invalidateQueries({ queryKey: ["decision-summary"] });
    },
  });
}

