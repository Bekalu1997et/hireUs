"use client";

import React, { useState } from "react";
import { useRouter } from "next/navigation";
import { useMutation } from "@tanstack/react-query";
import { roleApi } from "@/lib/api";
import { RoleForm } from "@/components/forms/role-form";
import { BlueprintPreview } from "@/components/forms/blueprint-preview";
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { ArrowLeft, Sparkles } from "lucide-react";
import Link from "next/link";

interface RoleFormData {
  title: string;
  seniority: string;
  department: string;
  tech_stack: string[];
  team_context: string;
}

interface BlueprintResponse {
  success: boolean;
  blueprint?: BlueprintData;
  error?: string;
}

interface BlueprintData {
  mission: string;
  competencies: { name: string; description: string; weight: string }[];
  must_have: Record<string, unknown>;
  nice_to_have: Record<string, unknown>;
  interview_stages: { name: string; duration_minutes: number; description: string; interview_type: string }[];
}

interface CreateRoleResponse {
  id: string;
  [key: string]: unknown;
}

export default function CreateRolePage() {
  const router = useRouter();
  const [step, setStep] = useState<"form" | "preview" | "loading">("form");
  const [formData, setFormData] = useState<RoleFormData | null>(null);
  const [blueprint, setBlueprint] = useState<BlueprintData | null>(null);
  const [error, setError] = useState<string | null>(null);

  // Generate blueprint mutation
  const generateMutation = useMutation({
    mutationFn: async (data: RoleFormData) => {
      const response = await roleApi.generateBlueprint({
        title: data.title,
        seniority: data.seniority,
        stack: data.tech_stack,
        team_context: data.team_context,
      });
      return response as BlueprintResponse;
    },
    onSuccess: (data) => {
      if (data.success && data.blueprint) {
        setBlueprint(data.blueprint);
        setStep("preview");
      } else {
        setError(data.error || "Failed to generate blueprint");
      }
    },
    onError: (err: Error) => {
      setError(err.message);
    },
  });

  // Create role mutation
  const createMutation = useMutation({
    mutationFn: async () => {
      if (!formData || !blueprint) return null;
      const response = await roleApi.createWithBlueprint({
        organization_id: "demo-org",
        title: formData.title,
        seniority: formData.seniority,
        stack: formData.tech_stack,
        team_context: formData.team_context,
      });
      return response as CreateRoleResponse;
    },
    onSuccess: (data) => {
      if (data && data.id) {
        router.push(`/roles/${data.id}`);
      }
    },
    onError: (err: Error) => {
      setError(err.message);
    },
  });

  const handleFormSubmit = (data: RoleFormData) => {
    setFormData(data);
    setError(null);
  };

  const handleGenerateBlueprint = (data: RoleFormData) => {
    setFormData(data);
    setError(null);
    generateMutation.mutate(data);
  };

  const handleAcceptBlueprint = () => {
    setError(null);
    createMutation.mutate();
  };

  const handleRejectBlueprint = () => {
    setStep("form");
  };

  return (
    <div className="container mx-auto py-8 px-4">
      {/* Header */}
      <div className="mb-8">
        <Link href="/roles" className="text-gray-600 hover:text-gray-900">
          <Button variant="ghost" size="sm" className="mb-4">
            <ArrowLeft className="w-4 h-4 mr-2" />
            Back to Roles
          </Button>
        </Link>
        <h1 className="text-3xl font-bold">Create Role Blueprint</h1>
        <p className="text-gray-600 dark:text-gray-400 mt-1">
          Define a new role with AI-powered assistance
        </p>
      </div>

      {/* Error Message */}
      {error && (
        <Card className="mb-6 bg-red-50 dark:bg-red-900/20 border-red-200">
          <CardContent className="p-4">
            <p className="text-red-600 dark:text-red-400">{error}</p>
          </CardContent>
        </Card>
      )}

      {/* Step 1: Form */}
      {step === "form" && (
        <div className="max-w-2xl">
          <RoleForm
            onSubmit={handleFormSubmit}
            onGenerateBlueprint={handleGenerateBlueprint}
            isLoading={createMutation.isPending}
            isGenerating={generateMutation.isPending}
          />
        </div>
      )}

      {/* Step 2: Preview */}
      {step === "preview" && blueprint && formData && (
        <div className="max-w-4xl">
          <Card className="mb-6 bg-blue-50 dark:bg-blue-900/20 border-blue-200">
            <CardContent className="p-4">
              <div className="flex items-center gap-3">
                <Sparkles className="w-5 h-5 text-blue-600" />
                <div>
                  <p className="font-medium text-blue-800">AI-Generated Blueprint Ready</p>
                  <p className="text-sm text-blue-600">Review and customize before creating</p>
                </div>
              </div>
            </CardContent>
          </Card>

          <BlueprintPreview
            mission={blueprint.mission}
            competencies={blueprint.competencies}
            must_have={blueprint.must_have}
            nice_to_have={blueprint.nice_to_have}
            interview_stages={blueprint.interview_stages}
            onAccept={handleAcceptBlueprint}
            onReject={handleRejectBlueprint}
            isLoading={createMutation.isPending}
          />
        </div>
      )}

      {/* Loading State */}
      {generateMutation.isPending && (
        <Card className="max-w-2xl mx-auto">
          <CardContent className="p-12 text-center">
            <div className="animate-spin w-8 h-8 border-4 border-primary border-t-transparent rounded-full mx-auto mb-4" />
            <h3 className="text-xl font-semibold mb-2">Generating Blueprint...</h3>
            <p className="text-gray-600">AI is analyzing your role requirements</p>
          </CardContent>
        </Card>
      )}
    </div>
  );
}

