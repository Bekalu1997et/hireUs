"use client";

import React, { useState } from "react";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Textarea } from "@/components/ui/textarea";
import { Label } from "@/components/ui/label";
import { Select } from "@/components/ui/select";
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";

interface RoleFormData {
  title: string;
  seniority: string;
  department: string;
  tech_stack: string[];
  team_context: string;
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
            <Badge key={tech} variant="secondary" className="cursor-pointer" onClick={() => removeTech(tech)}>
              {tech} ×
            </Badge>
          ))}
        </div>
      )}
    </div>
  );
}

interface RoleFormProps {
  initialData?: Partial<RoleFormData>;
  onSubmit: (data: RoleFormData) => void;
  onGenerateBlueprint?: (data: RoleFormData) => void;
  isLoading?: boolean;
  isGenerating?: boolean;
  submitLabel?: string;
  showGenerateButton?: boolean;
}

export function RoleForm({
  initialData = {},
  onSubmit,
  onGenerateBlueprint,
  isLoading = false,
  isGenerating = false,
  submitLabel = "Create Role",
  showGenerateButton = true,
}: RoleFormProps) {
  const [formData, setFormData] = useState<RoleFormData>({
    title: initialData.title || "",
    seniority: initialData.seniority || "",
    department: initialData.department || "",
    tech_stack: initialData.tech_stack || [],
    team_context: initialData.team_context || "",
  });

  const handleChange = (field: keyof RoleFormData, value: string | string[]) => {
    setFormData((prev) => ({ ...prev, [field]: value }));
  };

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    onSubmit(formData);
  };

  const handleGenerate = () => {
    if (onGenerateBlueprint) {
      onGenerateBlueprint(formData);
    }
  };

  const seniorityOptions = [
    { value: "", label: "Select seniority" },
    { value: "intern", label: "Intern" },
    { value: "junior", label: "Junior" },
    { value: "mid", label: "Mid-Level" },
    { value: "senior", label: "Senior" },
    { value: "lead", label: "Lead" },
    { value: "principal", label: "Principal" },
    { value: "director", label: "Director" },
    { value: "vp", label: "VP" },
  ];

  return (
    <form onSubmit={handleSubmit} className="space-y-6">
      <Card>
        <CardHeader>
          <CardTitle>Role Details</CardTitle>
          <CardDescription>Enter the basic information for this role</CardDescription>
        </CardHeader>
        <CardContent className="space-y-4">
          <div className="space-y-2">
            <Label htmlFor="title">Job Title *</Label>
            <Input
              id="title"
              placeholder="e.g., Senior Python Backend Engineer"
              value={formData.title}
              onChange={(e) => handleChange("title", e.target.value)}
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
              <Label htmlFor="department">Department</Label>
              <Input
                id="department"
                placeholder="e.g., Engineering"
                value={formData.department}
                onChange={(e) => handleChange("department", e.target.value)}
              />
            </div>
          </div>

          <TechStackInput
            techStack={formData.tech_stack}
            onChange={(stack) => handleChange("tech_stack", stack)}
          />

          <div className="space-y-2">
            <Label htmlFor="team_context">Team Context</Label>
            <Textarea
              id="team_context"
              placeholder="Describe the team, product, and any specific context that would help define this role..."
              value={formData.team_context}
              onChange={(e) => handleChange("team_context", e.target.value)}
              rows={4}
            />
          </div>
        </CardContent>
      </Card>

      <div className="flex flex-col sm:flex-row gap-3 justify-end">
        {showGenerateButton && onGenerateBlueprint && (
          <Button
            type="button"
            variant="outline"
            onClick={handleGenerate}
            disabled={isGenerating || !formData.title || !formData.seniority}
          >
            {isGenerating ? "Generating..." : "✨ Generate with AI"}
          </Button>
        )}
        <Button type="submit" disabled={isLoading || !formData.title || !formData.seniority}>
          {isLoading ? "Creating..." : submitLabel}
        </Button>
      </div>
    </form>
  );
}
