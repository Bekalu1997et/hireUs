"use client";

import { useQuery, useMutation, useQueryClient } from "@tanstack/react-query";
import { roleApi } from "@/lib/api";
import { useAuth } from "@/hooks/context/use-auth";
import { useState } from "react";

// Type definitions for role data
export interface RoleListItem {
  id: string;
  title: string;
  slug: string;
  seniority: string | null;
  department: string | null;
  tech_stack: string[];
  is_active: boolean;
  created_at: string;
  updated_at: string;
}

export interface RoleDetail {
  id: string;
  organization_id: string;
  title: string;
  slug: string;
  description: string | null;
  seniority: string | null;
  department: string | null;
  tech_stack: string[];
  core_competencies: {
    name: string;
    description: string;
    weight: string;
  }[];
  interview_stages: {
    name: string;
    duration_minutes: number;
    description: string;
    interview_type: string;
  }[];
  mission: string | null;
  must_have: Record<string, unknown>;
  nice_to_have: Record<string, unknown>;
  is_active: boolean;
  created_by: string | null;
  created_at: string;
  updated_at: string;
}

export interface RoleListResponse {
  items: RoleListItem[];
  total: number;
  page: number;
  page_size: number;
  total_pages: number;
}

export interface RoleFormData {
  title: string;
  seniority: string;
  department?: string;
  tech_stack?: string[];
  team_context?: string;
}

export interface BlueprintData {
  mission: string;
  competencies: {
    name: string;
    description: string;
    weight: string;
  }[];
  must_have: Record<string, unknown>;
  nice_to_have: Record<string, unknown>;
  interview_stages: {
    name: string;
    duration_minutes: number;
    description: string;
    interview_type: string;
  }[];
}

export interface UpdateRoleData {
  title?: string;
  seniority?: string;
  department?: string;
  tech_stack?: string[];
  description?: string;
  mission?: string;
  core_competencies?: Record<string, unknown>[];
  interview_stages?: Record<string, unknown>[];
  must_have?: Record<string, unknown>;
  nice_to_have?: Record<string, unknown>;
  is_active?: boolean;
}

// Hook for fetching all roles with optional filters
export function useRoles(filters?: {
  skip?: number;
  limit?: number;
  is_active?: boolean;
  search?: string;
}) {
  return useQuery<RoleListResponse>({
    queryKey: ["roles", filters],
    queryFn: async () => {
      const response = await roleApi.getAll(filters);
      return response as RoleListResponse;
    },
  });
}

// Hook for fetching a single role by ID
export function useRole(roleId: string | null) {
  return useQuery<RoleDetail>({
    queryKey: ["role", roleId],
    queryFn: async () => {
      if (!roleId) throw new Error("Role ID is required");
      const response = await roleApi.getById(roleId);
      return response as RoleDetail;
    },
    enabled: !!roleId,
  });
}

// Hook for creating a new role
export function useCreateRole() {
  const queryClient = useQueryClient();
  const { organizationId } = useAuth();

  return useMutation({
    mutationFn: async (data: RoleFormData) => {
      const response = await roleApi.create({
        organization_id: organizationId || "",
        title: data.title,
        seniority: data.seniority,
        department: data.department,
        tech_stack: data.tech_stack,
      });
      return response;
    },
    onSuccess: () => {
      void queryClient.invalidateQueries({ queryKey: ["roles"] });
    },
  });
}

// Hook for creating a role with AI-generated blueprint
export function useCreateRoleWithBlueprint() {
  const queryClient = useQueryClient();
  const { organizationId } = useAuth();

  return useMutation({
    mutationFn: async (data: RoleFormData) => {
      const response = await roleApi.createWithBlueprint({
        organization_id: organizationId || "",
        title: data.title,
        seniority: data.seniority,
        stack: data.tech_stack,
        team_context: data.team_context,
      });
      return response;
    },
    onSuccess: () => {
      void queryClient.invalidateQueries({ queryKey: ["roles"] });
    },
  });
}

// Hook for updating a role
export function useUpdateRole() {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: async (variables: { id: string; data: UpdateRoleData }) => {
      const response = await roleApi.update(variables.id, variables.data);
      return response;
    },
    onSuccess: (_data, variables) => {
      void queryClient.invalidateQueries({ queryKey: ["roles"] });
      void queryClient.invalidateQueries({ queryKey: ["role", (variables as { id: string }).id] });
    },
  });
}

// Hook for updating a role with AI-generated blueprint
export function useUpdateRoleWithBlueprint() {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: async (variables: { id: string; data: RoleFormData }) => {
      const response = await roleApi.updateWithBlueprint(variables.id, {
        title: variables.data.title,
        seniority: variables.data.seniority,
        stack: variables.data.tech_stack,
        team_context: variables.data.team_context,
      });
      return response;
    },
    onSuccess: (_data, variables) => {
      void queryClient.invalidateQueries({ queryKey: ["roles"] });
      void queryClient.invalidateQueries({ queryKey: ["role", (variables as { id: string }).id] });
    },
  });
}

// Hook for generating AI blueprint
export function useGenerateBlueprint() {
  return useMutation({
    mutationFn: async (data: RoleFormData) => {
      const response = await roleApi.generateBlueprint({
        title: data.title,
        seniority: data.seniority,
        stack: data.tech_stack,
        team_context: data.team_context,
      });
      return response;
    },
  });
}

// Hook for deleting a role
export function useDeleteRole() {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: async ({ id, hardDelete }: { id: string; hardDelete?: boolean }) => {
      const response = await roleApi.delete(id, hardDelete);
      return response;
    },
    onSuccess: () => {
      void queryClient.invalidateQueries({ queryKey: ["roles"] });
    },
  });
}

// Hook for duplicating a role
export function useDuplicateRole() {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: async ({ id, newTitle }: { id: string; newTitle?: string }) => {
      const response = await roleApi.duplicate(id, newTitle);
      return response;
    },
    onSuccess: () => {
      void queryClient.invalidateQueries({ queryKey: ["roles"] });
    },
  });
}

// Hook for deactivating a role
export function useDeactivateRole() {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: async (id: string) => {
      const response = await roleApi.deactivate(id);
      return response;
    },
    onSuccess: (_data: unknown, id: string) => {
      queryClient.invalidateQueries({ queryKey: ["roles"] });
      queryClient.invalidateQueries({ queryKey: ["role", id] });
    },
  });
}

// Hook for activating a role
export function useActivateRole() {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: async (id: string) => {
      const response = await roleApi.activate(id);
      return response;
    },
    onSuccess: (_data: unknown, id: string) => {
      void queryClient.invalidateQueries({ queryKey: ["roles"] });
      void queryClient.invalidateQueries({ queryKey: ["role", id] });
    },
  });
}

// Blueprint response type
interface BlueprintResponse {
  success: boolean;
  blueprint?: BlueprintData;
  error?: string;
}

// Composed hook for role creation with AI blueprint workflow
export function useCreateRoleWithAI() {
  const [step, setStep] = useState<"form" | "preview" | "loading" | "success" | "error">(
    "form"
  );
  const [formData, setFormData] = useState<RoleFormData | null>(null);
  const [blueprint, setBlueprint] = useState<BlueprintData | null>(null);
  const [error, setError] = useState<string | null>(null);

  const generateMutation = useGenerateBlueprint();
  const createMutation = useCreateRoleWithBlueprint();

  const handleFormSubmit = (data: RoleFormData) => {
    setFormData(data);
    setError(null);
  };

  const handleGenerateBlueprint = async (data: RoleFormData) => {
    setFormData(data);
    setError(null);
    setStep("loading");

    try {
      const result = await generateMutation.mutateAsync(data) as BlueprintResponse;
      if (result.success && result.blueprint) {
        setBlueprint(result.blueprint);
        setStep("preview");
      } else {
        setError(result.error || "Failed to generate blueprint");
        setStep("error");
      }
    } catch (err) {
      setError(err instanceof Error ? err.message : "An error occurred");
      setStep("error");
    }
  };

  const handleAcceptBlueprint = async () => {
    if (!formData || !blueprint) return;

    setStep("loading");
    try {
      await createMutation.mutateAsync(formData);
      setStep("success");
    } catch (err) {
      setError(err instanceof Error ? err.message : "Failed to create role");
      setStep("error");
    }
  };

  const handleRejectBlueprint = () => {
    setStep("form");
    setBlueprint(null);
  };

  const handleReset = () => {
    setStep("form");
    setFormData(null);
    setBlueprint(null);
    setError(null);
  };

  return {
    step,
    formData,
    blueprint,
    error,
    isGenerating: generateMutation.isPending,
    isCreating: createMutation.isPending,
    handleFormSubmit,
    handleGenerateBlueprint,
    handleAcceptBlueprint,
    handleRejectBlueprint,
    handleReset,
  };
}

