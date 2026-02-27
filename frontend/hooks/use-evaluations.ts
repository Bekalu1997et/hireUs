
+-"use client";

import { useMutation, useQuery, useQueryClient } from "@tanstack/react-query";
import { evaluationApi } from "@/lib/api";

// Types
export interface CompetencyScore {
  competency: string;
  score: number;
  evidence?: string;
  notes?: string;
}

export interface Scorecard {
  id: string;
  candidate_id: string;
  interviewer_id: string;
  assignment_id?: string;
  scores: Record<string, CompetencyScore | number>;
  confidence: number;
  strengths?: string;
  weaknesses?: string;
  summary?: string;
  recommendation: string;
  evidence: Record<string, string>;
  ai_suggestions?: string;
  is_draft: boolean;
  is_submitted: boolean;
  submitted_at?: string;
  created_at: string;
  updated_at: string;
}

export interface ScorecardListResponse {
  items: Scorecard[];
  total: number;
  page: number;
  page_size: number;
  total_pages: number;
}

export interface ScorecardSummary {
  id: string;
  candidate_id: string;
  candidate_name?: string;
  interviewer_id: string;
  average_score: number;
  recommendation: string;
  is_submitted: boolean;
  submitted_at?: string;
  created_at: string;
}

export interface CandidateScorecardsResponse {
  candidate_id: string;
  candidate_name?: string;
  scorecards: ScorecardSummary[];
  total_scorecards: number;
  average_score: number;
}

export interface ValidationResult {
  is_valid: boolean;
  missing_competencies: string[];
  missing_evidence: string[];
  low_confidence_warning: boolean;
  messages: string[];
}

export interface FeedbackImproveResponse {
  success: boolean;
  improved_text?: string;
  suggestions?: Array<{
    field: string;
    original: string;
    improved: string;
    explanation?: string;
  }>;
  error?: string;
}

// Hook for fetching all scorecards
export function useScorecards(params?: {
  organization_id?: string;
  role_id?: string;
  candidate_id?: string;
  interviewer_id?: string;
  is_submitted?: boolean;
  is_draft?: boolean;
  skip?: number;
  limit?: number;
}) {
  return useQuery({
    queryKey: ["evaluations", params],
    queryFn: async () => {
      const response = await evaluationApi.getAll(params);
      return response as ScorecardListResponse;
    },
  });
}

// Hook for fetching my drafts
export function useMyDrafts(params?: {
  skip?: number;
  limit?: number;
}) {
  return useQuery({
    queryKey: ["my-drafts", params],
    queryFn: async () => {
      const response = await evaluationApi.getMyDrafts(params);
      return response as Scorecard[];
    },
  });
}

// Hook for fetching a single scorecard
export function useScorecard(id: string) {
  return useQuery({
    queryKey: ["evaluation", id],
    queryFn: async () => {
      const response = await evaluationApi.getById(id);
      return response as Scorecard;
    },
    enabled: !!id,
  });
}

// Hook for creating a scorecard
export function useCreateScorecard() {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: async (data: {
      candidate_id: string;
      assignment_id?: string;
      scores: Record<string, unknown>;
      confidence: number;
      strengths?: string;
      weaknesses?: string;
      summary?: string;
      recommendation: string;
      is_draft?: boolean;
    }): Promise<Scorecard> => {
      const response = await evaluationApi.create(data);
      return response as Scorecard;
    },
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ["evaluations"] });
      queryClient.invalidateQueries({ queryKey: ["my-drafts"] });
    },
  });
}

// Hook for updating a scorecard
export function useUpdateScorecard() {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: async ({
      id,
      data,
    }: {
      id: string;
      data: Partial<{
        scores: Record<string, unknown>;
        confidence: number;
        strengths: string;
        weaknesses: string;
        summary: string;
        recommendation: string;
        is_draft: boolean;
      }>;
    }): Promise<Scorecard> => {
      const response = await evaluationApi.update(id, data);
      return response as Scorecard;
    },
    onSuccess: (data) => {
      queryClient.invalidateQueries({ queryKey: ["evaluations"] });
      queryClient.invalidateQueries({ queryKey: ["my-drafts"] });
      queryClient.invalidateQueries({ queryKey: ["evaluation", data.id] });
    },
  });
}

// Hook for deleting a scorecard
export function useDeleteScorecard() {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: async ({ id, hardDelete }: { id: string; hardDelete?: boolean }) => {
      await evaluationApi.delete(id, hardDelete);
    },
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ["evaluations"] });
      queryClient.invalidateQueries({ queryKey: ["my-drafts"] });
    },
  });
}

// Hook for submitting a scorecard
export function useSubmitScorecard() {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: async ({
      id,
      validateFirst,
    }: {
      id: string;
      validateFirst?: boolean;
    }): Promise<{
      success: boolean;
      message: string;
      submitted_at?: string;
    }> => {
      const response = await evaluationApi.submit(id, validateFirst);
      return response as { success: boolean; message: string; submitted_at?: string };
    },
    onSuccess: (data, variables) => {
      queryClient.invalidateQueries({ queryKey: ["evaluations"] });
      queryClient.invalidateQueries({ queryKey: ["my-drafts"] });
      queryClient.invalidateQueries({ queryKey: ["evaluation", variables.id] });
    },
  });
}

// Hook for validating a scorecard
export function useValidateScorecard(id: string) {
  return useQuery({
    queryKey: ["validation", id],
    queryFn: async () => {
      const response = await evaluationApi.validate(id);
      return response as ValidationResult;
    },
    enabled: !!id,
  });
}

// Hook for candidate scorecards
export function useCandidateScorecards(
  candidateId: string,
  submittedOnly?: boolean
) {
  return useQuery({
    queryKey: ["candidate-scorecards", candidateId],
    queryFn: async () => {
      const response = await evaluationApi.getCandidateScorecards(candidateId, submittedOnly);
      return response as CandidateScorecardsResponse;
    },
    enabled: !!candidateId,
  });
}

// Hook for candidate evaluation stats
export function useCandidateStats(candidateId: string) {
  return useQuery({
    queryKey: ["candidate-stats", candidateId],
    queryFn: async () => {
      const response = await evaluationApi.getCandidateStats(candidateId);
      return response as Record<string, unknown>;
    },
    enabled: !!candidateId,
  });
}

// Hook for AI feedback improvement
export function useImproveFeedback() {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: async ({
      id,
      target,
      context,
    }: {
      id: string;
      target: string;
      context?: string;
    }): Promise<FeedbackImproveResponse> => {
      const response = await evaluationApi.improveFeedback(id, { target, context });
      return response as FeedbackImproveResponse;
    },
    onSuccess: (data, variables) => {
      queryClient.invalidateQueries({ queryKey: ["evaluation", variables.id] });
    },
  });
}

// Hook for suggesting evidence
export function useSuggestEvidence() {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: async ({
      id,
      competency,
    }: {
      id: string;
      competency: string;
    }): Promise<{
      success: boolean;
      suggested_evidence?: string;
      what_to_look_for?: string[];
      red_flags?: string[];
      positive_signs?: string[];
      error?: string;
    }> => {
      const response = await evaluationApi.suggestEvidence(id, competency);
      return response as {
        success: boolean;
        suggested_evidence?: string;
        what_to_look_for?: string[];
        red_flags?: string[];
        positive_signs?: string[];
        error?: string;
      };
    },
    onSuccess: (data, variables) => {
      queryClient.invalidateQueries({ queryKey: ["evaluation", variables.id] });
    },
  });
}

// Hook for generating summary
export function useGenerateSummary() {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: async (id: string): Promise<{
      generated_summary: string;
    }> => {
      const response = await evaluationApi.generateSummary(id);
      return response as { generated_summary: string };
    },
    onSuccess: (data, id) => {
      queryClient.invalidateQueries({ queryKey: ["evaluation", id] });
    },
  });
}

// Hook for assignment feedback status
export function useAssignmentFeedbackStatus(assignmentId: string) {
  return useQuery({
    queryKey: ["assignment-feedback-status", assignmentId],
    queryFn: async () => {
      const response = await evaluationApi.getAssignmentFeedbackStatus(assignmentId);
      return response as {
        exists: boolean;
        feedback_required: boolean;
        feedback_submitted: boolean;
        feedback_id?: string;
        message: string;
      };
    },
    enabled: !!assignmentId,
  });
}

// Hook for managing scorecard creation flow
export function useScorecardBuilder() {
  const [step, setStep] = useState<"form" | "scoring" | "review" | "loading">("form");
  const [formData, setFormData] = useState<{
    candidate_id: string;
    assignment_id?: string;
    scores: Record<string, { competency: string; score: number; evidence?: string }>;
    confidence: number;
    strengths?: string;
    weaknesses?: string;
    summary?: string;
    recommendation: string;
  } | null>(null);
  const [error, setError] = useState<string | null>(null);

  const createMutation = useCreateScorecard();
  const updateMutation = useUpdateScorecard();
  const submitMutation = useSubmitScorecard();

  const handleFormSubmit = (data: typeof formData) => {
    setFormData(data);
    setError(null);
    setStep("scoring");
  };

  const handleScoringComplete = (data: typeof formData) => {
    setFormData((prev) => (prev ? { ...prev, ...data } : data));
    setStep("review");
  };

  const handleSubmit = async () => {
    if (!formData) return;
    setError(null);

    try {
      // Create the scorecard
      const scorecard = await createMutation.mutateAsync({
        candidate_id: formData.candidate_id,
        assignment_id: formData.assignment_id,
        scores: formData.scores,
        confidence: formData.confidence,
        strengths: formData.strengths,
        weaknesses: formData.weaknesses,
        summary: formData.summary,
        recommendation: formData.recommendation,
        is_draft: false,
      });

      setStep("loading");
    } catch (err) {
      setError(err instanceof Error ? err.message : 'An unexpected error occurred');
    }
  };

  const handleSaveDraft = async () => {
    if (!formData) return;
    setError(null);

    try {
      const scorecard = await createMutation.mutateAsync({
        candidate_id: formData.candidate_id,
        assignment_id: formData.assignment_id,
        scores: formData.scores,
        confidence: formData.confidence,
        strengths: formData.strengths,
        weaknesses: formData.weaknesses,
        summary: formData.summary,
        recommendation: formData.recommendation,
        is_draft: true,
      });

      return scorecard;
    } catch (err) {
      setError(err instanceof Error ? err.message : 'An unexpected error occurred');
      return null;
    }
  };

  const reset = () => {
    setStep("form");
    setFormData(null);
    setError(null);
  };

  return {
    step,
    setStep,
    formData,
    error,
    setError,
    createMutation,
    updateMutation,
    submitMutation,
    handleFormSubmit,
    handleScoringComplete,
    handleSubmit,
    handleSaveDraft,
    reset,
    isCreating: createMutation.isPending,
    isUpdating: updateMutation.isPending,
    isSubmitting: submitMutation.isPending,
  };
}

import { useState } from "react";

