"use client";

import React, { useState } from "react";
import { useRouter } from "next/navigation";
import { useMutation, useQuery } from "@tanstack/react-query";
import { interviewKitApi, roleApi } from "@/lib/api";
import { InterviewKitForm } from "@/components/forms/interview-kit-form";
import { KitPreview } from "@/components/forms/kit-preview";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { AIGeneratedKit, InterviewKit } from "@/hooks/use-interview-kits";
import { ArrowLeft, Sparkles } from "lucide-react";
import Link from "next/link";

interface GenerateResponse {
  success: boolean;
  kit?: AIGeneratedKit;
  error?: string;
}

interface CreateResponse {
  id: string;
  [key: string]: unknown;
}

interface Role {
  id: string;
  title: string;
}

export default function CreateInterviewKitPage() {
  const router = useRouter();
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

  // Fetch roles for the dropdown
  const { data: rolesData } = useQuery({
    queryKey: ["roles"],
    queryFn: async () => {
      const response = await roleApi.getAll({ is_active: true });
      return response as { items: Role[] };
    },
  });

  // Generate kit mutation
  const generateMutation = useMutation({
    mutationFn: async (data: typeof formData) => {
      if (!data) throw new Error("No form data");
      const response = await interviewKitApi.generate({
        role_id: data.role_id,
        role_title: data.role_title,
        seniority: data.seniority,
        stack: data.stack,
        interview_type: data.interview_type,
        competencies: data.competencies,
        duration_minutes: data.duration_minutes,
        additional_context: data.additional_context,
      });
      return response as GenerateResponse;
    },
    onSuccess: (data) => {
      if (data.success && data.kit) {
        setGeneratedKit(data.kit);
        setStep("preview");
      } else {
        setError(data.error || "Failed to generate kit");
      }
    },
    onError: (err: Error) => {
      setError(err.message);
    },
  });

  // Create kit mutation
  const createMutation = useMutation({
    mutationFn: async () => {
      if (!formData || !generatedKit) return null;
      const response = await interviewKitApi.createWithAI({
        organization_id: formData.organization_id,
        role_id: formData.role_id,
        role_title: formData.role_title,
        seniority: formData.seniority,
        stack: formData.stack,
        interview_type: formData.interview_type,
        competencies: formData.competencies,
        duration_minutes: formData.duration_minutes,
        additional_context: formData.additional_context,
      });
      return response as InterviewKit;
    },
    onSuccess: (data) => {
      if (data && data.id) {
        router.push(`/interview-kits/${data.id}`);
      }
    },
    onError: (err: Error) => {
      setError(err.message);
    },
  });

  const handleFormSubmit = (data: typeof formData) => {
    setFormData(data);
    setError(null);
  };

  const handleGenerateKit = (data: typeof formData) => {
    setFormData(data);
    setError(null);
    generateMutation.mutate(data);
  };

  const handleAcceptKit = () => {
    setError(null);
    createMutation.mutate();
  };

  const handleRejectKit = () => {
    setStep("form");
  };

  return (
    <div className="container mx-auto py-8 px-4">
      {/* Header */}
      <div className="mb-8">
        <Link href="/interview-kits" className="text-gray-600 hover:text-gray-900">
          <Button variant="ghost" size="sm" className="mb-4">
            <ArrowLeft className="w-4 h-4 mr-2" />
            Back to Interview Kits
          </Button>
        </Link>
        <h1 className="text-3xl font-bold">Create Interview Kit</h1>
        <p className="text-gray-600 dark:text-gray-400 mt-1">
          Generate structured interview questions and evaluation rubrics with AI assistance
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
          <InterviewKitForm
            onSubmit={handleFormSubmit}
            onGenerateKit={handleGenerateKit}
            isLoading={createMutation.isPending}
            isGenerating={generateMutation.isPending}
            organizationId="demo-org"
            roles={rolesData?.items || []}
          />
        </div>
      )}

      {/* Step 2: Preview */}
      {step === "preview" && generatedKit && formData && (
        <div className="max-w-4xl">
          <KitPreview
            kit={generatedKit}
            onAccept={handleAcceptKit}
            onReject={handleRejectKit}
            isLoading={createMutation.isPending}
          />
        </div>
      )}

      {/* Loading State */}
      {generateMutation.isPending && (
        <Card className="max-w-2xl mx-auto">
          <CardContent className="p-12 text-center">
            <div className="animate-spin w-8 h-8 border-4 border-primary border-t-transparent rounded-full mx-auto mb-4" />
            <h3 className="text-xl font-semibold mb-2">Generating Interview Kit...</h3>
            <p className="text-gray-600">AI is creating questions and evaluation criteria</p>
          </CardContent>
        </Card>
      )}
    </div>
  );
}

