"use client";

import { useMutation, useQuery, useQueryClient } from "@tanstack/react-query";
import { interviewKitApi } from "@/lib/api";
import { useState } from "react";

// Types
export interface RubricCriterion {
  name: string;
  description: string;
  max_score: number;
  weight: number;
}

export interface QuestionItem {
  question: string;
  type: string;
  duration_minutes: number;
  difficulty: string;
  notes?: string;
}

export interface AIGeneratedKit {
  title: string;
  problem_statement: string;
  evaluation_rubric: RubricCriterion[];
  red_flags: string[];
  good_answer_outline: string;
  questions: QuestionItem[];
  tips_for_interviewer?: string;
  suggested_duration_breakdown?: Record<string, number>;
}

export interface InterviewKit {
  id: string;
  organization_id: string;
  role_id?: string;
  title: string;
  type: string;
  description?: string;
  problem_statement?: string;
  evaluation_rubric: RubricCriterion[];
  red_flags: string[];
  good_answer_outline?: string;
  questions: QuestionItem[];
  estimated_duration_minutes: number;
  version: number;
  is_template: boolean;
  is_active: boolean;
  created_by?: string;
  created_at: string;
  updated_at: string;
  tips_for_interviewer?: string;
  suggested_duration_breakdown?: Record<string, number>;
}

export interface InterviewKitListResponse {
  items: InterviewKit[];
  total: number;
  page: number;
  page_size: number;
  total_pages: number;
}

export interface GenerateKitResponse {
  success: boolean;
  kit?: AIGeneratedKit;
  error?: string;
}

// Hook for fetching all interview kits
export function useInterviewKits(params?: {
  skip?: number;
  limit?: number;
  organization_id?: string;
  role_id?: string;
  interview_type?: string;
  is_active?: boolean;
  search?: string;
}) {
  return useQuery({
    queryKey: ["interview-kits", params],
    queryFn: async () => {
      const response = await interviewKitApi.getAll(params);
      return response as InterviewKitListResponse;
    },
  });
}

// Hook for fetching a single interview kit
export function useInterviewKit(id: string) {
  return useQuery({
    queryKey: ["interview-kit", id],
    queryFn: async () => {
      const response = await interviewKitApi.getById(id);
      return response as InterviewKit;
    },
    enabled: !!id,
  });
}

// Hook for generating an interview kit with AI
export function useGenerateInterviewKit() {
  return useMutation({
    mutationFn: async (data: {
      role_id?: string;
      role_title: string;
      seniority: string;
      stack?: string[];
      interview_type: string;
      competencies?: string[];
      duration_minutes?: number;
      additional_context?: string;
    }): Promise<GenerateKitResponse> => {
      const response = await interviewKitApi.generate(data);
      return response as GenerateKitResponse;
    },
  });
}

// Hook for creating an interview kit with AI-generated content
export function useCreateInterviewKitWithAI() {
  const queryClient = useQueryClient();
  
  return useMutation({
    mutationFn: async (data: {
      organization_id: string;
      role_id?: string;
      role_title: string;
      seniority: string;
      stack?: string[];
      interview_type: string;
      competencies?: string[];
      duration_minutes?: number;
      additional_context?: string;
    }): Promise<InterviewKit> => {
      const response = await interviewKitApi.createWithAI(data);
      return response as InterviewKit;
    },
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ["interview-kits"] });
    },
  });
}

// Hook for creating an interview kit manually
export function useCreateInterviewKit() {
  const queryClient = useQueryClient();
  
  return useMutation({
    mutationFn: async (data: {
      organization_id: string;
      role_id?: string;
      title: string;
      type: string;
      description?: string;
      problem_statement?: string;
      evaluation_rubric?: Record<string, unknown>[];
      red_flags?: string[];
      good_answer_outline?: string;
      questions?: Record<string, unknown>[];
      estimated_duration_minutes?: number;
      tips_for_interviewer?: string;
    }): Promise<InterviewKit> => {
      const response = await interviewKitApi.create(data);
      return response as InterviewKit;
    },
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ["interview-kits"] });
    },
  });
}

// Hook for updating an interview kit
export function useUpdateInterviewKit() {
  const queryClient = useQueryClient();
  
  return useMutation({
    mutationFn: async ({
      id,
      data,
    }: {
      id: string;
      data: Partial<{
        title: string;
        description: string;
        problem_statement: string;
        evaluation_rubric: Record<string, unknown>[];
        red_flags: string[];
        good_answer_outline: string;
        questions: Record<string, unknown>[];
        estimated_duration_minutes: number;
        tips_for_interviewer: string;
        is_active: boolean;
      }>;
    }): Promise<InterviewKit> => {
      const response = await interviewKitApi.update(id, data);
      return response as InterviewKit;
    },
    onSuccess: (data) => {
      queryClient.invalidateQueries({ queryKey: ["interview-kits"] });
      queryClient.invalidateQueries({ queryKey: ["interview-kit", data.id] });
    },
  });
}

// Hook for deleting an interview kit
export function useDeleteInterviewKit() {
  const queryClient = useQueryClient();
  
  return useMutation({
    mutationFn: async ({ id, hardDelete }: { id: string; hardDelete?: boolean }) => {
      await interviewKitApi.delete(id, hardDelete);
    },
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ["interview-kits"] });
    },
  });
}

// Hook for duplicating an interview kit
export function useDuplicateInterviewKit() {
  const queryClient = useQueryClient();
  
  return useMutation({
    mutationFn: async ({ id, newTitle }: { id: string; newTitle?: string }): Promise<InterviewKit> => {
      const response = await interviewKitApi.duplicate(id, newTitle);
      return response as InterviewKit;
    },
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ["interview-kits"] });
    },
  });
}

// Hook for regenerating an interview kit with AI
export function useRegenerateInterviewKit() {
  const queryClient = useQueryClient();
  
  return useMutation({
    mutationFn: async ({
      id,
      data,
    }: {
      id: string;
      data: {
        role_title: string;
        seniority: string;
        stack?: string[];
        interview_type: string;
        competencies?: string[];
        duration_minutes?: number;
        additional_context?: string;
      };
    }): Promise<GenerateKitResponse> => {
      const response = await interviewKitApi.regenerate(id, data);
      return response as GenerateKitResponse;
    },
    onSuccess: (data, variables) => {
      queryClient.invalidateQueries({ queryKey: ["interview-kits"] });
      queryClient.invalidateQueries({ queryKey: ["interview-kit", variables.id] });
    },
  });
}

// Hook for managing interview kit creation flow
export function useInterviewKitBuilder() {
  const [step, setStep] = useState<"form" | "preview" | "loading">("form");
  const [formData, setFormData] = useState<{
    role_title: string;
    seniority: string;
    stack: string[];
    interview_type: string;
    competencies: string[];
    duration_minutes: number;
    additional_context: string;
    organization_id: string;
    role_id?: string;
  } | null>(null);
  const [generatedKit, setGeneratedKit] = useState<AIGeneratedKit | null>(null);
  const [error, setError] = useState<string | null>(null);

  const generateMutation = useGenerateInterviewKit();
  const createMutation = useCreateInterviewKitWithAI();

  const handleFormSubmit = (data: typeof formData) => {
    setFormData(data);
    setError(null);
  };

  const handleGenerateKit = (data: typeof formData) => {
    if (!data) return;
    setFormData(data);
    setError(null);
    generateMutation.mutate(data, {
      onSuccess: (response) => {
        if (response.success && response.kit) {
          setGeneratedKit(response.kit);
          setStep("preview");
        } else {
          setError(response.error || "Failed to generate kit");
        }
      },
      onError: (err: Error) => {
        setError(err.message);
      },
    });
  };

  const handleAcceptKit = () => {
    if (!formData || !generatedKit) return;
    setError(null);
    createMutation.mutate(
      {
        organization_id: formData.organization_id,
        role_id: formData.role_id,
        role_title: formData.role_title,
        seniority: formData.seniority,
        stack: formData.stack,
        interview_type: formData.interview_type,
        competencies: formData.competencies,
        duration_minutes: formData.duration_minutes,
        additional_context: formData.additional_context,
      },
      {
        onError: (err: Error) => {
          setError(err.message);
        },
      }
    );
  };

  const handleRejectKit = () => {
    setStep("form");
    setGeneratedKit(null);
  };

  const reset = () => {
    setStep("form");
    setFormData(null);
    setGeneratedKit(null);
    setError(null);
  };

  return {
    step,
    setStep,
    formData,
    generatedKit,
    error,
    setError,
    generateMutation,
    createMutation,
    handleFormSubmit,
    handleGenerateKit,
    handleAcceptKit,
    handleRejectKit,
    reset,
    isGenerating: generateMutation.isPending,
    isCreating: createMutation.isPending,
  };
}

