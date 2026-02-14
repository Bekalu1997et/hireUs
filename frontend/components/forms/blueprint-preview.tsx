"use client";

import React from "react";
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { Badge } from "@/components/ui/badge";
import { CheckCircle, XCircle, Clock, Users, Code, MessageSquare } from "lucide-react";

interface Competency {
  name: string;
  description: string;
  weight: string;
}

interface InterviewStage {
  name: string;
  duration_minutes: number;
  description: string;
  interview_type: string;
}

interface MustHaveData {
  technical_skills?: string[];
  years_experience?: string;
  education?: string;
  key_experiences?: string[];
}

interface NiceToHaveData {
  additional_skills?: string[];
  preferred_experiences?: string[];
  certifications?: string[];
}

interface BlueprintPreviewProps {
  mission: string;
  competencies: Competency[];
  must_have: MustHaveData;
  nice_to_have: NiceToHaveData;
  interview_stages: InterviewStage[];
  onAccept: () => void;
  onReject: () => void;
  isLoading?: boolean;
}

export function BlueprintPreview({
  mission,
  competencies,
  must_have,
  nice_to_have,
  interview_stages,
  onAccept,
  onReject,
  isLoading = false,
}: BlueprintPreviewProps) {
  const getWeightBadgeVariant = (weight: string) => {
    switch (weight.toLowerCase()) {
      case "must-have":
        return "destructive" as const;
      case "nice-to-have":
        return "secondary" as const;
      default:
        return "outline" as const;
    }
  };

  const getStageIcon = (type: string) => {
    switch (type.toLowerCase()) {
      case "coding":
        return <Code className="w-4 h-4" />;
      case "system_design":
        return <Users className="w-4 h-4" />;
      case "behavioral":
        return <MessageSquare className="w-4 h-4" />;
      default:
        return <Clock className="w-4 h-4" />;
    }
  };

  const getStageBadgeVariant = (type: string) => {
    switch (type.toLowerCase()) {
      case "coding":
        return "default" as const;
      case "system_design":
        return "secondary" as const;
      case "behavioral":
        return "outline" as const;
      default:
        return "secondary" as const;
    }
  };

  const formatArrayField = (field: string[] | undefined): React.ReactNode => {
    if (!field || !Array.isArray(field)) return null;
    return field.join(", ");
  };

  return (
    <div className="space-y-6">
      {/* Mission */}
      <Card>
        <CardHeader>
          <CardTitle className="text-lg">Role Mission</CardTitle>
          <CardDescription>
            The core purpose and responsibilities of this role
          </CardDescription>
        </CardHeader>
        <CardContent>
          <p className="text-gray-700 dark:text-gray-300 leading-relaxed">
            {mission}
          </p>
        </CardContent>
      </Card>

      {/* Competencies */}
      <Card>
        <CardHeader>
          <CardTitle className="text-lg">Core Competencies</CardTitle>
          <CardDescription>
            Key skills and abilities required for success
          </CardDescription>
        </CardHeader>
        <CardContent>
          <div className="grid gap-4 md:grid-cols-2">
            {competencies.map((comp, index) => (
              <div key={index} className="border rounded-lg p-4">
                <div className="flex justify-between items-start mb-2">
                  <h4 className="font-semibold">{comp.name}</h4>
                  <Badge variant={getWeightBadgeVariant(comp.weight)}>
                    {comp.weight}
                  </Badge>
                </div>
                <p className="text-sm text-gray-600 dark:text-gray-400">
                  {comp.description}
                </p>
              </div>
            ))}
          </div>
        </CardContent>
      </Card>

      {/* Requirements */}
      <div className="grid md:grid-cols-2 gap-6">
        {/* Must Have */}
        <Card>
          <CardHeader>
            <CardTitle className="text-lg flex items-center gap-2">
              <CheckCircle className="w-5 h-5 text-green-600" />
              Must-Have Requirements
            </CardTitle>
          </CardHeader>
          <CardContent className="space-y-3">
            {must_have.technical_skills && (
              <div>
                <span className="font-medium">Technical Skills: </span>
                <span className="text-gray-600 dark:text-gray-400">
                  {formatArrayField(must_have.technical_skills)}
                </span>
              </div>
            )}
            {must_have.years_experience && (
              <div>
                <span className="font-medium">Experience: </span>
                <span className="text-gray-600 dark:text-gray-400">
                  {must_have.years_experience}
                </span>
              </div>
            )}
            {must_have.education && (
              <div>
                <span className="font-medium">Education: </span>
                <span className="text-gray-600 dark:text-gray-400">
                  {must_have.education}
                </span>
              </div>
            )}
            {must_have.key_experiences && (
              <div>
                <span className="font-medium">Key Experiences: </span>
                <span className="text-gray-600 dark:text-gray-400">
                  {formatArrayField(must_have.key_experiences)}
                </span>
              </div>
            )}
          </CardContent>
        </Card>

        {/* Nice to Have */}
        <Card>
          <CardHeader>
            <CardTitle className="text-lg flex items-center gap-2">
              <XCircle className="w-5 h-5 text-blue-600" />
              Nice-to-Have Qualifications
            </CardTitle>
          </CardHeader>
          <CardContent className="space-y-3">
            {nice_to_have.additional_skills && (
              <div>
                <span className="font-medium">Additional Skills: </span>
                <span className="text-gray-600 dark:text-gray-400">
                  {formatArrayField(nice_to_have.additional_skills)}
                </span>
              </div>
            )}
            {nice_to_have.preferred_experiences && (
              <div>
                <span className="font-medium">Preferred Experiences: </span>
                <span className="text-gray-600 dark:text-gray-400">
                  {formatArrayField(nice_to_have.preferred_experiences)}
                </span>
              </div>
            )}
            {nice_to_have.certifications && (
              <div>
                <span className="font-medium">Certifications: </span>
                <span className="text-gray-600 dark:text-gray-400">
                  {formatArrayField(nice_to_have.certifications)}
                </span>
              </div>
            )}
          </CardContent>
        </Card>
      </div>

      {/* Interview Stages */}
      <Card>
        <CardHeader>
          <CardTitle className="text-lg">Interview Stages</CardTitle>
          <CardDescription>
            Suggested interview flow for evaluating candidates
          </CardDescription>
        </CardHeader>
        <CardContent>
          <div className="space-y-4">
            {interview_stages.map((stage, index) => (
              <div key={index} className="border rounded-lg p-4">
                <div className="flex justify-between items-start mb-2">
                  <div className="flex items-center gap-3">
                    {getStageIcon(stage.interview_type)}
                    <div>
                      <h4 className="font-semibold">{stage.name}</h4>
                      <p className="text-sm text-gray-500">
                        {stage.duration_minutes} minutes
                      </p>
                    </div>
                  </div>
                  <Badge variant={getStageBadgeVariant(stage.interview_type)}>
                    {stage.interview_type.replace("_", " ")}
                  </Badge>
                </div>
                <p className="text-sm text-gray-600 dark:text-gray-400">
                  {stage.description}
                </p>
              </div>
            ))}
          </div>
        </CardContent>
      </Card>

      {/* Actions */}
      <div className="flex flex-col sm:flex-row gap-3 justify-end">
        <Button
          variant="outline"
          onClick={onReject}
          disabled={isLoading}
        >
          <XCircle className="w-4 h-4 mr-2" />
          Regenerate
        </Button>
        <Button
          onClick={onAccept}
          disabled={isLoading}
        >
          <CheckCircle className="w-4 h-4 mr-2" />
          {isLoading ? "Creating Role..." : "Create Role"}
        </Button>
      </div>
    </div>
  );
}

