"use client";

import React, { useState } from "react";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Textarea } from "@/components/ui/textarea";
import { Label } from "@/components/ui/label";
import { Select } from "@/components/ui/select";
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";

interface FormData {
  role_title: string;
  seniority: string;
  stack: string[];
  interview_type: string;
  competencies: string[];
  duration_minutes: number;
  additional_context: string;
  organization_id: string;
  role_id?: string;
}

interface TechStackInputProps {
  techStack: string[];
  onChange: (stack: string[]) => void;
}

function TechStackInput({ techStack, onChange }: TechStackInputProps) {
  const [input, setInput] = useState("");

  const handleKeyDown = (e: React.KeyboardEvent) => {
    if (e.key === "Enter" || e.key === ",") {
      e.preventDefault();
      const value = input.trim();
      if (value && !techStack.includes(value)) {
        onChange([...techStack, value]);
      }
      setInput("");
    }
  };

  const removeTech = (tech: string) => {
    onChange(techStack.filter((t) => t !== tech));
  };

  return (
    <div className="space-y-2">
      <Label htmlFor="tech-stack">Tech Stack</Label>
      <Input
        id="tech-stack"
        placeholder="Type and press Enter (e.g., Python, React)"
        value={input}
        onChange={(e) => setInput(e.target.value)}
        onKeyDown={handleKeyDown}
      />
      {techStack.length > 0 && (
        <div className="flex flex-wrap gap-2 mt-2">
          {techStack.map((tech) => (
            <Badge
              key={tech}
              variant="secondary"
              className="cursor-pointer"
              onClick={() => removeTech(tech)}
            >
              {tech} ×
            </Badge>
          ))}
        </div>
      )}
    </div>
  );
}

interface CompetenciesInputProps {
  competencies: string[];
  onChange: (competencies: string[]) => void;
}

function CompetenciesInput({ competencies, onChange }: CompetenciesInputProps) {
  const [input, setInput] = useState("");

  const handleKeyDown = (e: React.KeyboardEvent) => {
    if (e.key === "Enter" || e.key === ",") {
      e.preventDefault();
      const value = input.trim();
      if (value && !competencies.includes(value)) {
        onChange([...competencies, value]);
      }
      setInput("");
    }
  };

  const removeCompetency = (comp: string) => {
    onChange(competencies.filter((c) => c !== comp));
  };

  return (
    <div className="space-y-2">
      <Label htmlFor="competencies">Core Competencies to Evaluate</Label>
      <Input
        id="competencies"
        placeholder="Type and press Enter (e.g., System Design, Python)"
        value={input}
        onChange={(e) => setInput(e.target.value)}
        onKeyDown={handleKeyDown}
      />
      <p className="text-sm text-gray-500">
        Add key competencies from the role blueprint
      </p>
      {competencies.length > 0 && (
        <div className="flex flex-wrap gap-2 mt-2">
          {competencies.map((comp) => (
            <Badge
              key={comp}
              variant="outline"
              className="cursor-pointer"
              onClick={() => removeCompetency(comp)}
            >
              {comp} ×
            </Badge>
          ))}
        </div>
      )}
    </div>
  );
}

interface InterviewKitFormProps {
  initialData?: Partial<FormData>;
  onSubmit: (data: FormData) => void;
  onGenerateKit?: (data: FormData) => void;
  isLoading?: boolean;
  isGenerating?: boolean;
  submitLabel?: string;
  showGenerateButton?: boolean;
  organizationId: string;
  roles?: Array<{ id: string; title: string }>;
}

export function InterviewKitForm({
  initialData = {},
  onSubmit,
  onGenerateKit,
  isLoading = false,
  isGenerating = false,
  submitLabel = "Create Kit",
  showGenerateButton = true,
  organizationId,
  roles = [],
}: InterviewKitFormProps) {
  const [formData, setFormData] = useState<FormData>({
    role_title: initialData.role_title || "",
    seniority: initialData.seniority || "",
    stack: initialData.stack || [],
    interview_type: initialData.interview_type || "",
    competencies: initialData.competencies || [],
    duration_minutes: initialData.duration_minutes || 60,
    additional_context: initialData.additional_context || "",
    organization_id: organizationId,
    role_id: initialData.role_id,
  });

  const handleChange = (field: keyof FormData, value: string | string[] | number) => {
    setFormData((prev) => ({ ...prev, [field]: value }));
  };

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    onSubmit(formData);
  };

  const handleGenerate = () => {
    if (onGenerateKit) {
      onGenerateKit(formData);
    }
  };

  const seniorityOptions = [
    { value: "", label: "Select seniority" },
    { value: "junior", label: "Junior" },
    { value: "mid", label: "Mid-Level" },
    { value: "senior", label: "Senior" },
    { value: "lead", label: "Lead" },
    { value: "principal", label: "Principal" },
    { value: "director", label: "Director" },
  ];

  const interviewTypeOptions = [
    { value: "", label: "Select interview type" },
    { value: "coding", label: "Coding" },
    { value: "system_design", label: "System Design" },
    { value: "pm_case", label: "PM Case" },
    { value: "behavioral", label: "Behavioral" },
  ];

  const durationOptions = [
    { value: "30", label: "30 minutes" },
    { value: "45", label: "45 minutes" },
    { value: "60", label: "60 minutes" },
    { value: "90", label: "90 minutes" },
    { value: "120", label: "120 minutes" },
  ];

  return (
    <form onSubmit={handleSubmit} className="space-y-6">
      <Card>
        <CardHeader>
          <CardTitle>Interview Details</CardTitle>
          <CardDescription>
            Configure the interview parameters for AI-generated content
          </CardDescription>
        </CardHeader>
        <CardContent className="space-y-4">
          {/* Role Selection */}
          {roles.length > 0 && (
            <div className="space-y-2">
              <Label htmlFor="role_id">Select Existing Role (Optional)</Label>
              <Select
                id="role_id"
                options={[
                  { value: "", label: "Select a role" },
                  ...roles.map((role) => ({ value: role.id, label: role.title })),
                ]}
                value={formData.role_id || ""}
                onChange={(e) => handleChange("role_id", e.target.value)}
              />
            </div>
          )}

          <div className="space-y-2">
            <Label htmlFor="role_title">Job Title *</Label>
            <Input
              id="role_title"
              placeholder="e.g., Senior Python Backend Engineer"
              value={formData.role_title}
              onChange={(e) => handleChange("role_title", e.target.value)}
              required
            />
          </div>

          <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
            <div className="space-y-2">
              <Label htmlFor="seniority">Seniority *</Label>
              <Select
                id="seniority"
                options={seniorityOptions}
                value={formData.seniority}
                onChange={(e) => handleChange("seniority", e.target.value)}
                required
              />
            </div>

            <div className="space-y-2">
              <Label htmlFor="interview_type">Interview Type *</Label>
              <Select
                id="interview_type"
                options={interviewTypeOptions}
                value={formData.interview_type}
                onChange={(e) => handleChange("interview_type", e.target.value)}
                required
              />
            </div>
          </div>

          <TechStackInput
            techStack={formData.stack}
            onChange={(stack) => handleChange("stack", stack)}
          />

          <CompetenciesInput
            competencies={formData.competencies}
            onChange={(competencies) => handleChange("competencies", competencies)}
          />

          <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
            <div className="space-y-2">
              <Label htmlFor="duration_minutes">Duration *</Label>
              <Select
                id="duration_minutes"
                options={durationOptions}
                value={String(formData.duration_minutes)}
                onChange={(e) => handleChange("duration_minutes", parseInt(e.target.value))}
                required
              />
            </div>
          </div>

          <div className="space-y-2">
            <Label htmlFor="additional_context">Additional Context</Label>
            <Textarea
              id="additional_context"
              placeholder="Any specific requirements or context for the interview..."
              value={formData.additional_context}
              onChange={(e) => handleChange("additional_context", e.target.value)}
              rows={4}
            />
          </div>
        </CardContent>
      </Card>

      <div className="flex flex-col sm:flex-row gap-3 justify-end">
        {showGenerateButton && onGenerateKit && (
          <Button
            type="button"
            variant="outline"
            onClick={handleGenerate}
            disabled={
              isGenerating ||
              !formData.role_title ||
              !formData.seniority ||
              !formData.interview_type
            }
          >
            {isGenerating ? "Generating..." : "✨ Generate with AI"}
          </Button>
        )}
        <Button
          type="submit"
          disabled={
            isLoading ||
            !formData.role_title ||
            !formData.seniority ||
            !formData.interview_type
          }
        >
          {isLoading ? "Creating..." : submitLabel}
        </Button>
      </div>
    </form>
  );
}

