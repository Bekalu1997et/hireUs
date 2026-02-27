"use client";

import React from "react";
import { useQuery } from "@tanstack/react-query";
import { roleApi } from "@/lib/api";
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { Badge } from "@/components/ui/badge";
import { Skeleton } from "@/components/ui/skeleton";
import { ArrowLeft, Edit, Copy, Trash2, Plus } from "lucide-react";
import Link from "next/link";
import { useParams } from "next/navigation";

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

interface RoleDetail {
  id: string;
  title: string;
  slug: string;
  description: string | null;
  seniority: string | null;
  department: string | null;
  tech_stack: string[];
  core_competencies: { name: string; description: string; weight: string }[];
  interview_stages: { name: string; duration_minutes: number; description: string; interview_type: string }[];
  mission: string | null;
  must_have: MustHaveData;
  nice_to_have: NiceToHaveData;
  is_active: boolean;
  created_at: string;
  updated_at: string;
}

export default function RoleDetailPage() {
  const params = useParams();
  const roleId = params.id as string;

  const { data: role, isLoading, error, refetch } = useQuery<RoleDetail>({
    queryKey: ["role", roleId],
    queryFn: async () => {
      const response = await roleApi.getById(roleId);
      return response as RoleDetail;
    },
    enabled: !!roleId,
  });

  const getWeightBadgeVariant = (weight: string) => {
    switch (weight.toLowerCase()) {
      case "must-have":
        return "destructive" as const;
      case "nice-to-have":
        return "success" as const;
      default:
        return "secondary" as const;
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
      case "culture_fit":
        return "success" as const;
      default:
        return "secondary" as const;
    }
  };

  const formatArrayField = (field: string[] | undefined): React.ReactNode => {
    if (!field || !Array.isArray(field)) return null;
    return field.join(", ");
  };

  if (isLoading) {
    return (
      <div className="container mx-auto py-8 px-4">
        <div className="mb-8">
          <Skeleton className="h-8 w-32 mb-4" />
          <Skeleton className="h-10 w-1/2 mb-2" />
          <Skeleton className="h-6 w-1/3" />
        </div>
        <div className="space-y-6">
          <Skeleton className="h-48 w-full" />
          <Skeleton className="h-64 w-full" />
        </div>
      </div>
    );
  }

  if (error || !role) {
    return (
      <div className="container mx-auto py-8 px-4">
        <Card className="max-w-md mx-auto">
          <CardContent className="p-6 text-center">
            <p className="text-red-600 dark:text-red-400 mb-4">
              Error loading role. Please try again.
            </p>
            <Button variant="outline" onClick={() => refetch()}>
              Retry
            </Button>
          </CardContent>
        </Card>
      </div>
    );
  }

  return (
    <div className="container mx-auto py-8 px-4">
      {/* Header */}
      <div className="mb-8">
        <Link href="/roles">
          <Button variant="ghost" size="sm" className="mb-4">
            <ArrowLeft className="w-4 h-4 mr-2" />
            Back to Roles
          </Button>
        </Link>
        <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4">
          <div>
            <div className="flex items-center gap-3 mb-2">
              <h1 className="text-3xl font-bold">{role.title}</h1>
              {role.seniority && (
                <Badge variant="secondary">{role.seniority}</Badge>
              )}
              {!role.is_active && (
                <Badge variant="outline">Inactive</Badge>
              )}
            </div>
            {role.department && (
              <p className="text-gray-600 dark:text-gray-400">{role.department}</p>
            )}
          </div>
          <div className="flex gap-2">
            <Link href={`/roles/${role.id}/edit`}>
              <Button variant="outline" size="sm">
                <Edit className="w-4 h-4 mr-2" />
                Edit
              </Button>
            </Link>
            <Button variant="outline" size="sm">
              <Copy className="w-4 h-4 mr-2" />
              Duplicate
            </Button>
          </div>
        </div>
      </div>

      {/* Tech Stack */}
      {role.tech_stack.length > 0 && (
        <Card className="mb-6">
          <CardHeader>
            <CardTitle className="text-lg">Tech Stack</CardTitle>
          </CardHeader>
          <CardContent>
            <div className="flex flex-wrap gap-2">
              {role.tech_stack.map((tech) => (
                <Badge key={tech} variant="secondary">
                  {tech}
                </Badge>
              ))}
            </div>
          </CardContent>
        </Card>
      )}

      {/* Mission */}
      {role.mission && (
        <Card className="mb-6">
          <CardHeader>
            <CardTitle className="text-lg">Role Mission</CardTitle>
          </CardHeader>
          <CardContent>
            <p className="text-gray-700 dark:text-gray-300">{role.mission}</p>
          </CardContent>
        </Card>
      )}

      {/* Competencies */}
      {role.core_competencies.length > 0 && (
        <Card className="mb-6">
          <CardHeader>
            <CardTitle className="text-lg">Core Competencies</CardTitle>
            <CardDescription>
              Key competencies required for success in this role
            </CardDescription>
          </CardHeader>
          <CardContent>
            <div className="grid gap-4 md:grid-cols-2">
              {role.core_competencies.map((comp, index) => (
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
      )}

      {/* Requirements Grid */}
      <div className="grid md:grid-cols-2 gap-6 mb-6">
        {/* Must Have */}
        <Card>
          <CardHeader>
            <CardTitle className="text-lg">Must-Have Requirements</CardTitle>
          </CardHeader>
          <CardContent className="space-y-3">
            {role.must_have.technical_skills && (
              <div>
                <span className="font-medium">Technical Skills: </span>
                <span className="text-gray-600 dark:text-gray-400">
                  {formatArrayField(role.must_have.technical_skills)}
                </span>
              </div>
            )}
            {role.must_have.years_experience && (
              <div>
                <span className="font-medium">Experience: </span>
                <span className="text-gray-600 dark:text-gray-400">
                  {role.must_have.years_experience}
                </span>
              </div>
            )}
            {role.must_have.education && (
              <div>
                <span className="font-medium">Education: </span>
                <span className="text-gray-600 dark:text-gray-400">
                  {role.must_have.education}
                </span>
              </div>
            )}
            {role.must_have.key_experiences && (
              <div>
                <span className="font-medium">Key Experiences: </span>
                <span className="text-gray-600 dark:text-gray-400">
                  {formatArrayField(role.must_have.key_experiences)}
                </span>
              </div>
            )}
          </CardContent>
        </Card>

        {/* Nice to Have */}
        <Card>
          <CardHeader>
            <CardTitle className="text-lg">Nice-to-Have Qualifications</CardTitle>
          </CardHeader>
          <CardContent className="space-y-3">
            {role.nice_to_have.additional_skills && (
              <div>
                <span className="font-medium">Additional Skills: </span>
                <span className="text-gray-600 dark:text-gray-400">
                  {formatArrayField(role.nice_to_have.additional_skills)}
                </span>
              </div>
            )}
            {role.nice_to_have.preferred_experiences && (
              <div>
                <span className="font-medium">Preferred Experiences: </span>
                <span className="text-gray-600 dark:text-gray-400">
                  {formatArrayField(role.nice_to_have.preferred_experiences)}
                </span>
              </div>
            )}
            {role.nice_to_have.certifications && (
              <div>
                <span className="font-medium">Certifications: </span>
                <span className="text-gray-600 dark:text-gray-400">
                  {formatArrayField(role.nice_to_have.certifications)}
                </span>
              </div>
            )}
          </CardContent>
        </Card>
      </div>

      {/* Interview Stages */}
      {role.interview_stages.length > 0 && (
        <Card className="mb-6">
          <CardHeader>
            <CardTitle className="text-lg">Interview Stages</CardTitle>
            <CardDescription>
              Suggested interview flow for evaluating candidates
            </CardDescription>
          </CardHeader>
          <CardContent>
            <div className="space-y-4">
              {role.interview_stages.map((stage, index) => (
                <div key={index} className="border rounded-lg p-4">
                  <div className="flex justify-between items-start mb-2">
                    <div>
                      <h4 className="font-semibold">{stage.name}</h4>
                      <p className="text-sm text-gray-500">
                        {stage.duration_minutes} minutes
                      </p>
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
      )}

      {/* Quick Actions */}
      <Card>
        <CardHeader>
          <CardTitle className="text-lg">Quick Actions</CardTitle>
        </CardHeader>
        <CardContent>
          <div className="flex flex-wrap gap-3">
            <Link href={`/interview-kits/create?role_id=${role.id}`}>
              <Button variant="outline">
                <Plus className="w-4 h-4 mr-2" />
                Create Interview Kit
              </Button>
            </Link>
            <Link href={`/candidates/create?role_id=${role.id}`}>
              <Button variant="outline">
                <Plus className="w-4 h-4 mr-2" />
                Add Candidate
              </Button>
            </Link>
          </div>
        </CardContent>
      </Card>
    </div>
  );
}

