"use client";

import { useQuery, useMutation, useQueryClient } from "@tanstack/react-query";
import { workflowApi, Workflow, WorkflowStage, WorkflowTemplateResponse } from "@/lib/workflow-api";

// Type definitions
export interface WorkflowListItem {
  id: string;
  name: string;
  description?: string;
  stages: WorkflowStage[];
  is_default: boolean;
  is_active: boolean;
  created_at: string;
}

export interface WorkflowListResponse {
  items: WorkflowListItem[];
  total: number;
  page: number;
  page_size: number;
  total_pages: number;
}

export interface WorkflowDetail {
  id: string;
  organization_id: string;
  name: string;
  description?: string;
  stages: WorkflowStage[];
  is_default: boolean;
  is_active: boolean;
  candidates_count?: Record<string, number>;
  created_at: string;
  updated_at: string;
}

export interface CreateWorkflowData {
  organization_id: string;
  name: string;
  description?: string;
  stages?: WorkflowStage[];
  is_default?: boolean;
}

export interface UpdateWorkflowData {
  name?: string;
  description?: string;
  stages?: WorkflowStage[];
  is_default?: boolean;
  is_active?: boolean;
}

export interface MoveCandidateData {
  candidate_id: string;
  to_stage_id: string;
  reason?: string;
  skip_feedback_check?: boolean;
}

export interface StageTransitionResult {
  success: boolean;
  candidate_id: string;
  from_stage?: string;
  to_stage: string;
  message: string;
  blocked_reason?: string;
}

export interface CanMoveCandidateResponse {
  can_move: boolean;
  candidate_id: string;
  current_stage_id?: string;
  required_feedbacks: number;
  submitted_feedbacks: number;
  missing_feedbacks: string[];
  blocked_reason?: string;
}

export interface FeedbackStatusResponse {
  candidate_id: string;
  candidate_name: string;
  current_stage_id?: string;
  current_stage_name?: string;
  total_required_feedbacks: number;
  total_submitted_feedbacks: number;
  is_blocked: boolean;
  blocked_reason?: string;
}

// Hook for fetching all workflows
export function useWorkflows(filters?: {
  skip?: number;
  limit?: number;
}) {
  return useQuery<WorkflowListResponse>({
    queryKey: ["workflows", filters],
    queryFn: async () => {
      const response = await workflowApi.getAll(filters);
      return response as WorkflowListResponse;
    },
  });
}

// Hook for fetching a single workflow by ID
export function useWorkflow(workflowId: string | null) {
  return useQuery<WorkflowDetail>({
    queryKey: ["workflow", workflowId],
    queryFn: async () => {
      if (!workflowId) throw new Error("Workflow ID is required");
      const response = await workflowApi.getById(workflowId);
      return response as WorkflowDetail;
    },
    enabled: !!workflowId,
  });
}

// Hook for fetching default workflow
export function useDefaultWorkflow() {
  return useQuery<Workflow>({
    queryKey: ["defaultWorkflow"],
    queryFn: async () => {
      const response = await workflowApi.getDefault();
      return response as Workflow;
    },
  });
}

// Hook for fetching workflow template
export function useWorkflowTemplate() {
  return useQuery<WorkflowTemplateResponse>({
    queryKey: ["workflowTemplate"],
    queryFn: async () => {
      const response = await workflowApi.getTemplate();
      return response;
    },
  });
}

// Hook for fetching workflow stats
export function useWorkflowStats(workflowId: string | null) {
  return useQuery({
    queryKey: ["workflowStats", workflowId],
    queryFn: async () => {
      if (!workflowId) throw new Error("Workflow ID is required");
      const response = await workflowApi.getStats(workflowId);
      return response;
    },
    enabled: !!workflowId,
  });
}

// Hook for validating candidate move
export function useValidateCandidateMove() {
  return useMutation({
    mutationFn: async ({
      candidateId,
      targetStageId,
    }: {
      candidateId: string;
      targetStageId: string;
    }) => {
      const response = await workflowApi.validateMove(candidateId, targetStageId);
      return response as CanMoveCandidateResponse;
    },
  });
}

// Hook for fetching candidate feedback status
export function useCandidateFeedbackStatus(candidateId: string | null) {
  return useQuery<FeedbackStatusResponse>({
    queryKey: ["feedbackStatus", candidateId],
    queryFn: async () => {
      if (!candidateId) throw new Error("Candidate ID is required");
      const response = await workflowApi.getFeedbackStatus(candidateId);
      return response as FeedbackStatusResponse;
    },
    enabled: !!candidateId,
  });
}

// Hook for creating a workflow
export function useCreateWorkflow() {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: async (data: CreateWorkflowData) => {
      const response = await workflowApi.create(data);
      return response;
    },
    onSuccess: () => {
      void queryClient.invalidateQueries({ queryKey: ["workflows"] });
      void queryClient.invalidateQueries({ queryKey: ["defaultWorkflow"] });
    },
  });
}

// Hook for creating a default workflow
export function useCreateDefaultWorkflow() {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: async (organizationId?: string) => {
      const response = await workflowApi.createDefault(organizationId);
      return response;
    },
    onSuccess: () => {
      void queryClient.invalidateQueries({ queryKey: ["workflows"] });
      void queryClient.invalidateQueries({ queryKey: ["defaultWorkflow"] });
    },
  });
}

// Hook for updating a workflow
export function useUpdateWorkflow() {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: async (variables: { id: string; data: UpdateWorkflowData }) => {
      const response = await workflowApi.update(variables.id, variables.data);
      return response;
    },
    onSuccess: (_data, variables) => {
      void queryClient.invalidateQueries({ queryKey: ["workflows"] });
      void queryClient.invalidateQueries({ queryKey: ["workflow", variables.id] });
    },
  });
}

// Hook for deleting a workflow
export function useDeleteWorkflow() {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: async ({ id, hardDelete }: { id: string; hardDelete?: boolean }) => {
      const response = await workflowApi.delete(id, hardDelete);
      return response;
    },
    onSuccess: () => {
      void queryClient.invalidateQueries({ queryKey: ["workflows"] });
    },
  });
}

// Hook for setting workflow as default
export function useSetDefaultWorkflow() {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: async ({ id, organizationId }: { id: string; organizationId?: string }) => {
      const response = await workflowApi.setDefault(id, organizationId);
      return response;
    },
    onSuccess: () => {
      void queryClient.invalidateQueries({ queryKey: ["workflows"] });
      void queryClient.invalidateQueries({ queryKey: ["defaultWorkflow"] });
    },
  });
}

// Hook for moving a candidate
export function useMoveCandidate() {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: async (data: MoveCandidateData) => {
      const response = await workflowApi.moveCandidate(data);
      return response as StageTransitionResult;
    },
    onSuccess: (_data, variables) => {
      void queryClient.invalidateQueries({ queryKey: ["feedbackStatus", variables.candidate_id] });
    },
  });
}

// Hook for adding a stage
export function useAddStage() {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: async ({
      workflowId,
      stageData,
    }: {
      workflowId: string;
      stageData: Record<string, unknown>;
    }) => {
      const response = await workflowApi.addStage(workflowId, stageData);
      return response;
    },
    onSuccess: (_data, variables) => {
      void queryClient.invalidateQueries({ queryKey: ["workflow", variables.workflowId] });
      void queryClient.invalidateQueries({ queryKey: ["workflows"] });
    },
  });
}

// Hook for updating a stage
export function useUpdateStage() {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: async ({
      workflowId,
      stageId,
      stageData,
    }: {
      workflowId: string;
      stageId: string;
      stageData: Record<string, unknown>;
    }) => {
      const response = await workflowApi.updateStage(workflowId, stageId, stageData);
      return response;
    },
    onSuccess: (_data, variables) => {
      void queryClient.invalidateQueries({ queryKey: ["workflow", variables.workflowId] });
      void queryClient.invalidateQueries({ queryKey: ["workflows"] });
    },
  });
}

// Hook for deleting a stage
export function useDeleteStage() {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: async ({
      workflowId,
      stageId,
    }: {
      workflowId: string;
      stageId: string;
    }) => {
      const response = await workflowApi.deleteStage(workflowId, stageId);
      return response;
    },
    onSuccess: (_data, variables) => {
      void queryClient.invalidateQueries({ queryKey: ["workflow", variables.workflowId] });
      void queryClient.invalidateQueries({ queryKey: ["workflows"] });
    },
  });
}

// Hook for reordering stages
export function useReorderStages() {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: async ({
      workflowId,
      stageOrders,
    }: {
      workflowId: string;
      stageOrders: { id: string; order: number }[];
    }) => {
      const response = await workflowApi.reorderStages(workflowId, stageOrders);
      return response;
    },
    onSuccess: (_data, variables) => {
      void queryClient.invalidateQueries({ queryKey: ["workflow", variables.workflowId] });
      void queryClient.invalidateQueries({ queryKey: ["workflows"] });
    },
  });
}

// Composed hook for workflow creation with template
export function useCreateWorkflowWithTemplate() {
  const queryClient = useQueryClient();
  const templateQuery = useWorkflowTemplate();
  const createMutation = useCreateWorkflow();

  const handleCreateWithTemplate = async (data: {
    organization_id: string;
    name: string;
    description?: string;
  }) => {
    if (!templateQuery.data?.stages) {
      throw new Error("Template not loaded");
    }

    return createMutation.mutateAsync({
      ...data,
      stages: templateQuery.data.stages,
      is_default: true,
    });
  };

  return {
    template: templateQuery.data,
    isLoading: templateQuery.isLoading || createMutation.isPending,
    error: templateQuery.error || createMutation.error,
    createWithTemplate: handleCreateWithTemplate,
    isCreating: createMutation.isPending,
  };
}

