"use client";

import { useQuery, useMutation, useQueryClient } from "@tanstack/react-query";
import { candidateApi } from "@/lib/api";
import { useAuth } from "@/hooks/context/use-auth";

// Type definitions for candidate data
export interface Candidate {
  id: string;
  organization_id: string;
  first_name: string;
  last_name: string;
  email: string;
  phone: string | null;
  resume_url: string | null;
  linkedin_url: string | null;
  portfolio_url: string | null;
  role_id: string | null;
  status: string;
  source: string | null;
  notes: string | null;
  is_active: boolean;
  created_at: string;
  updated_at: string;
}

export interface CandidateListItem {
  id: string;
  first_name: string;
  last_name: string;
  email: string;
  phone: string | null;
  status: string;
  source: string | null;
  role_id: string | null;
  is_active: boolean;
  created_at: string;
  updated_at: string;
}

export interface CandidateListResponse {
  items: CandidateListItem[];
  total: number;
  skip: number;
  limit: number;
}

export interface CandidateFormData {
  first_name: string;
  last_name: string;
  email: string;
  phone?: string;
  resume_url?: string;
  linkedin_url?: string;
  portfolio_url?: string;
  role_id?: string;
  source?: string;
  notes?: string;
}

export interface CandidateAttachment {
  id: string;
  candidate_id: string;
  name: string;
  url: string;
  type: string;
  created_at: string;
}

export interface CandidateActivity {
  id: string;
  candidate_id: string;
  activity_type: string;
  description: string;
  metadata: Record<string, unknown> | null;
  created_at: string;
  created_by: string | null;
}

// Hook for fetching all candidates with optional filters
export function useCandidates(filters?: {
  skip?: number;
  limit?: number;
  organization_id?: string;
  role_id?: string;
  workflow_id?: string;
  stage_id?: string;
  status?: string;
  is_active?: boolean;
  search?: string;
}) {
  return useQuery<CandidateListResponse>({
    queryKey: ["candidates", filters],
    queryFn: async () => {
      const response = await candidateApi.getAll(filters);
      return response as CandidateListResponse;
    },
  });
}

// Hook for fetching a single candidate by ID
export function useCandidate(candidateId: string | null) {
  return useQuery<Candidate>({
    queryKey: ["candidate", candidateId],
    queryFn: async () => {
      if (!candidateId) throw new Error("Candidate ID is required");
      const response = await candidateApi.getById(candidateId);
      return response as Candidate;
    },
    enabled: !!candidateId,
  });
}

// Hook for creating a new candidate
export function useCreateCandidate() {
  const queryClient = useQueryClient();
  const { organizationId } = useAuth();

  return useMutation({
    mutationFn: async (data: CandidateFormData) => {
      const response = await candidateApi.create({
        organization_id: organizationId || "",
        ...data,
      });
      return response;
    },
    onSuccess: () => {
      void queryClient.invalidateQueries({ queryKey: ["candidates"] });
    },
  });
}

// Hook for updating a candidate
export function useUpdateCandidate() {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: async (variables: { id: string; data: Partial<CandidateFormData> }) => {
      const response = await candidateApi.update(variables.id, variables.data);
      return response;
    },
    onSuccess: (_data, variables) => {
      void queryClient.invalidateQueries({ queryKey: ["candidates"] });
      void queryClient.invalidateQueries({ queryKey: ["candidate", variables.id] });
    },
  });
}

// Hook for deleting a candidate
export function useDeleteCandidate() {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: async ({ id, hardDelete }: { id: string; hardDelete?: boolean }) => {
      const response = await candidateApi.delete(id, hardDelete);
      return response;
    },
    onSuccess: () => {
      void queryClient.invalidateQueries({ queryKey: ["candidates"] });
    },
  });
}

// Hook for assigning a candidate to a workflow stage
export function useAssignCandidateToStage() {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: async (variables: { candidateId: string; workflow_id: string; stage_id: string }) => {
      const response = await candidateApi.assignToStage(variables.candidateId, {
        workflow_id: variables.workflow_id,
        stage_id: variables.stage_id,
      });
      return response;
    },
    onSuccess: (_data, variables) => {
      void queryClient.invalidateQueries({ queryKey: ["candidate", variables.candidateId] });
      void queryClient.invalidateQueries({ queryKey: ["candidates"] });
    },
  });
}

// Hook for moving a candidate to a different stage
export function useMoveCandidateToStage() {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: async (variables: { candidateId: string; stage_id: string; notes?: string }) => {
      const response = await candidateApi.moveToStage(variables.candidateId, {
        stage_id: variables.stage_id,
        notes: variables.notes,
      });
      return response;
    },
    onSuccess: (_data, variables) => {
      void queryClient.invalidateQueries({ queryKey: ["candidate", variables.candidateId] });
      void queryClient.invalidateQueries({ queryKey: ["candidates"] });
    },
  });
}

// Hook for fetching candidate evaluations
export function useCandidateEvaluations(candidateId: string | null) {
  return useQuery({
    queryKey: ["candidate-evaluations", candidateId],
    queryFn: async () => {
      if (!candidateId) throw new Error("Candidate ID is required");
      const response = await candidateApi.getEvaluations(candidateId);
      return response;
    },
    enabled: !!candidateId,
  });
}

// Hook for fetching candidate attachments
export function useCandidateAttachments(candidateId: string | null) {
  return useQuery<CandidateAttachment[]>({
    queryKey: ["candidate-attachments", candidateId],
    queryFn: async () => {
      if (!candidateId) throw new Error("Candidate ID is required");
      const response = await candidateApi.getAttachments(candidateId);
      return response as CandidateAttachment[];
    },
    enabled: !!candidateId,
  });
}

// Hook for adding a candidate attachment
export function useAddCandidateAttachment() {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: async (variables: { candidateId: string; data: { name: string; url: string; type: string } }) => {
      const response = await candidateApi.addAttachment(variables.candidateId, variables.data);
      return response;
    },
    onSuccess: (_data, variables) => {
      void queryClient.invalidateQueries({ queryKey: ["candidate-attachments", variables.candidateId] });
    },
  });
}

// Hook for fetching candidate activities
export function useCandidateActivities(candidateId: string | null, params?: { skip?: number; limit?: number }) {
  return useQuery<CandidateActivity[]>({
    queryKey: ["candidate-activities", candidateId, params],
    queryFn: async () => {
      if (!candidateId) throw new Error("Candidate ID is required");
      const response = await candidateApi.getActivities(candidateId, params);
      return response as CandidateActivity[];
    },
    enabled: !!candidateId,
  });
}

// Hook for adding a candidate activity
export function useAddCandidateActivity() {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: async (variables: { 
      candidateId: string; 
      data: { 
        activity_type: string; 
        description: string; 
        metadata?: Record<string, unknown> 
      } 
    }) => {
      const response = await candidateApi.addActivity(variables.candidateId, variables.data);
      return response;
    },
    onSuccess: (_data, variables) => {
      void queryClient.invalidateQueries({ queryKey: ["candidate-activities", variables.candidateId] });
    },
  });
}

