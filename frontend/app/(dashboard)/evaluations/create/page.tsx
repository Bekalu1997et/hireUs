"use client";

import React, { useState } from "react";
import { useRouter, useSearchParams } from "next/navigation";
import { useQuery } from "@tanstack/react-query";
import { roleApi } from "@/lib/api";
import { Button } from "@/components/ui/button";
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import { Select } from "@/components/ui/select";
import { ArrowLeft, User, Plus, X } from "lucide-react";
import Link from "next/link";
import { ScorecardForm } from "@/components/forms/scorecard-form";
import { useCreateScorecard } from "@/hooks/use-evaluations";

// Mock candidate type for demo
interface Candidate {
  id: string;
  full_name: string;
  email: string;
}

interface RoleCoreCompetency {
  competency?: string;
  name?: string;
}

interface Role {
  id: string;
  title: string;
  core_competencies?: RoleCoreCompetency[] | string[];
}

export default function CreateEvaluationPage() {
  const router = useRouter();
  const searchParams = useSearchParams();
  const candidateIdParam = searchParams.get("candidate_id");

  const [selectedCandidateId, setSelectedCandidateId] = useState<string>(candidateIdParam || "");
  const [selectedRoleId, setSelectedRoleId] = useState<string>("");
  const [competencies, setCompetencies] = useState<string[]>([]);
  const [customCompetency, setCustomCompetency] = useState("");
  const [error, setError] = useState<string | null>(null);

  // For demo purposes, we'll use mock data
  // In production, these would come from the API
  const [candidates] = useState<Candidate[]>([
    { id: "demo-candidate-1", full_name: "John Doe", email: "john@example.com" },
    { id: "demo-candidate-2", full_name: "Jane Smith", email: "jane@example.com" },
  ]);

  // Fetch role if selected
  const { data: roleData } = useQuery({
    queryKey: ["role", selectedRoleId],
    queryFn: async () => {
      if (!selectedRoleId) return null;
      const response = await roleApi.getById(selectedRoleId);
      return response as Role;
    },
    enabled: !!selectedRoleId,
  });

  // Update competencies when role is selected
  React.useEffect(() => {
    if (roleData?.core_competencies && Array.isArray(roleData.core_competencies)) {
      const comps = roleData.core_competencies.map((c): string => {
        if (typeof c === "string") return c;
        return (c as RoleCoreCompetency).competency || (c as RoleCoreCompetency).name || "";
      }).filter((c): c is string => c !== "");
      
      if (comps.length > 0 && competencies.length === 0) {
        setCompetencies(comps);
      }
    }
  }, [roleData, competencies.length]);

  const createMutation = useCreateScorecard();

  const handleAddCompetency = () => {
    if (customCompetency.trim() && !competencies.includes(customCompetency.trim())) {
      setCompetencies([...competencies, customCompetency.trim()]);
      setCustomCompetency("");
    }
  };

  const handleRemoveCompetency = (comp: string) => {
    setCompetencies(competencies.filter((c) => c !== comp));
  };

  const handleSubmit = async (data: {
    candidate_id: string;
    assignment_id?: string;
    scores: Record<string, { competency: string; score: number; evidence: string }>;
    confidence: number;
    strengths: string;
    weaknesses: string;
    summary: string;
    recommendation: string;
  }) => {
    setError(null);

    try {
      const scorecard = await createMutation.mutateAsync({
        candidate_id: data.candidate_id,
        assignment_id: data.assignment_id,
        scores: data.scores,
        confidence: data.confidence,
        strengths: data.strengths,
        weaknesses: data.weaknesses,
        summary: data.summary,
        recommendation: data.recommendation,
        is_draft: false,
      });

      router.push(`/evaluations/${scorecard.id}`);
    } catch (err: unknown) {
      const errorMessage = err instanceof Error ? err.message : "Failed to create evaluation";
      setError(errorMessage);
    }
  };

  const handleSaveDraft = async (data: {
    candidate_id: string;
    assignment_id?: string;
    scores: Record<string, { competency: string; score: number; evidence: string }>;
    confidence: number;
    strengths: string;
    weaknesses: string;
    summary: string;
    recommendation: string;
  }) => {
    setError(null);

    try {
      const scorecard = await createMutation.mutateAsync({
        candidate_id: data.candidate_id,
        assignment_id: data.assignment_id,
        scores: data.scores,
        confidence: data.confidence,
        strengths: data.strengths,
        weaknesses: data.weaknesses,
        summary: data.summary,
        recommendation: data.recommendation,
        is_draft: true,
      });

      router.push(`/evaluations/${scorecard.id}`);
    } catch (err: unknown) {
      const errorMessage = err instanceof Error ? err.message : "Failed to save draft";
      setError(errorMessage);
    }
  };

  const commonCompetencies = [
    "Technical Skills",
    "Problem Solving",
    "Communication",
    "System Design",
    "Code Quality",
    "Team Collaboration",
    "Leadership",
    "Product Thinking",
    "Analytical Skills",
    "Creativity",
    "Time Management",
    "Attention to Detail",
  ];

  return (
    <div className="container mx-auto py-8 px-4">
      {/* Header */}
      <div className="mb-8">
        <Link href="/evaluations">
          <Button variant="ghost" size="sm" className="mb-4">
            <ArrowLeft className="w-4 h-4 mr-2" />
            Back to Evaluations
          </Button>
        </Link>
        <h1 className="text-3xl font-bold">Create Evaluation</h1>
        <p className="text-gray-600 mt-1">
          Set up a new interview scorecard
        </p>
      </div>

      {/* Error Message */}
      {error && (
        <Card className="mb-6 bg-red-50 border-red-200">
          <CardContent className="p-4">
            <p className="text-red-600">{error}</p>
          </CardContent>
        </Card>
      )}

      {/* Step 1: Setup */}
      {!selectedCandidateId ? (
        <div className="max-w-2xl">
          <Card>
            <CardHeader>
              <CardTitle>Select Candidate</CardTitle>
              <CardDescription>
                Choose the candidate you want to evaluate
              </CardDescription>
            </CardHeader>
            <CardContent>
              <div className="space-y-4">
                <div className="space-y-2">
                  <Label htmlFor="candidate">Candidate</Label>
                  <Select
                    id="candidate"
                    options={[
                      { value: "", label: "Select a candidate" },
                      ...candidates.map((c) => ({ 
                        value: c.id, 
                        label: `${c.full_name} (${c.email})` 
                      })),
                    ]}
                    value={selectedCandidateId}
                    onChange={(e) => setSelectedCandidateId(e.target.value)}
                  />
                </div>
              </div>
            </CardContent>
          </Card>

          {selectedCandidateId && (
            <Card className="mt-6">
              <CardHeader>
                <CardTitle>Competencies to Evaluate</CardTitle>
                <CardDescription>
                  Select or add competencies based on the role requirements
                </CardDescription>
              </CardHeader>
              <CardContent className="space-y-6">
                {/* Role Selection */}
                <div className="space-y-2">
                  <Label htmlFor="role">Role (Optional)</Label>
                  <p className="text-sm text-gray-500 mb-2">
                    Selecting a role will auto-populate its core competencies
                  </p>
                  <Input
                    id="role"
                    placeholder="Enter role ID (for demo, leave empty to manually add competencies)"
                    value={selectedRoleId}
                    onChange={(e) => setSelectedRoleId(e.target.value)}
                  />
                </div>

                {/* Quick Add Competencies */}
                <div className="space-y-2">
                  <Label>Quick Add Competencies</Label>
                  <div className="flex flex-wrap gap-2">
                    {commonCompetencies.map((comp) => (
                      <Button
                        key={comp}
                        type="button"
                        variant={competencies.includes(comp) ? "secondary" : "outline"}
                        size="sm"
                        onClick={() => {
                          if (!competencies.includes(comp)) {
                            setCompetencies([...competencies, comp]);
                          }
                        }}
                        disabled={competencies.includes(comp)}
                      >
                        {comp}
                      </Button>
                    ))}
                  </div>
                </div>

                {/* Custom Competency */}
                <div className="space-y-2">
                  <Label htmlFor="custom">Add Custom Competency</Label>
                  <div className="flex gap-2">
                    <Input
                      id="custom"
                      placeholder="e.g., Machine Learning"
                      value={customCompetency}
                      onChange={(e) => setCustomCompetency(e.target.value)}
                      onKeyDown={(e) => {
                        if (e.key === "Enter") {
                          e.preventDefault();
                          handleAddCompetency();
                        }
                      }}
                    />
                    <Button type="button" onClick={handleAddCompetency}>
                      <Plus className="w-4 h-4" />
                    </Button>
                  </div>
                </div>

                {/* Selected Competencies */}
                <div className="space-y-2">
                  <Label>
                    Selected Competencies ({competencies.length})
                  </Label>
                  {competencies.length === 0 ? (
                    <p className="text-sm text-gray-500 italic">
                      Add at least one competency to continue
                    </p>
                  ) : (
                    <div className="flex flex-wrap gap-2">
                      {competencies.map((comp) => (
                        <span
                          key={comp}
                          className="inline-flex items-center gap-1 px-3 py-1 bg-blue-100 text-blue-800 rounded-full text-sm"
                        >
                          {comp}
                          <button
                            type="button"
                            onClick={() => handleRemoveCompetency(comp)}
                            className="hover:text-blue-900"
                          >
                            <X className="w-3 h-3" />
                          </button>
                        </span>
                      ))}
                    </div>
                  )}
                </div>

                {/* Continue Button */}
                <Button
                  className="w-full"
                  disabled={competencies.length === 0}
                  onClick={() => {
                    // Just continue, the form will use the candidate_id
                  }}
                >
                  Continue to Scorecard
                </Button>
              </CardContent>
            </Card>
          )}
        </div>
      ) : (
        /* Step 2: Scorecard Form */
        <div className="max-w-4xl">
          {/* Selected Info */}
          <Card className="mb-6">
            <CardContent className="p-4">
              <div className="flex items-center justify-between">
                <div className="flex items-center gap-4">
                  <div className="w-10 h-10 bg-blue-100 rounded-full flex items-center justify-center">
                    <User className="w-5 h-5 text-blue-600" />
                  </div>
                  <div>
                    <p className="font-medium">
                      {candidates.find((c) => c.id === selectedCandidateId)?.full_name || "Unknown Candidate"}
                    </p>
                    <p className="text-sm text-gray-500">
                      {competencies.length} competencies selected
                    </p>
                  </div>
                </div>
                <Button
                  variant="ghost"
                  size="sm"
                  onClick={() => setSelectedCandidateId("")}
                >
                  Change
                </Button>
              </div>
            </CardContent>
          </Card>

          {/* Scorecard Form */}
          <ScorecardForm
            initialData={{
              candidate_id: selectedCandidateId,
              competencies: competencies,
            }}
            onSubmit={handleSubmit}
            onSaveDraft={handleSaveDraft}
            isLoading={createMutation.isPending}
            candidateName={candidates.find((c) => c.id === selectedCandidateId)?.full_name}
          />
        </div>
      )}
    </div>
  );
}

