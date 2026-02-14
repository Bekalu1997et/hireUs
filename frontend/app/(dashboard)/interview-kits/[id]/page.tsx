"use client";

import React from "react";
import Link from "next/link";
import { useQuery } from "@tanstack/react-query";
import { interviewKitApi } from "@/lib/api";
import { Button } from "@/components/ui/button";
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import { ArrowLeft, Edit, Copy, Sparkles } from "lucide-react";
import { InterviewKit } from "@/hooks/use-interview-kits";

interface PageProps {
  params: Promise<{ id: string }>;
}

export default function InterviewKitDetailPage({ params }: PageProps) {
  const [kitId, setKitId] = React.useState<string>("");

  React.useEffect(() => {
    params.then((p) => setKitId(p.id));
  }, [params]);

  const { data: kit, isLoading, error } = useQuery({
    queryKey: ["interview-kit", kitId],
    queryFn: async () => {
      if (!kitId) return null;
      const response = await interviewKitApi.getById(kitId);
      return response as InterviewKit;
    },
    enabled: !!kitId,
  });

  if (isLoading) {
    return (
      <div className="container mx-auto py-8 px-4">
        <div className="mb-8">
          <Link href="/interview-kits">
            <Button variant="ghost" size="sm" className="mb-4">
              <ArrowLeft className="w-4 h-4 mr-2" />
              Back to Interview Kits
            </Button>
          </Link>
        </div>
        <Card className="animate-pulse">
          <CardHeader>
            <div className="h-8 bg-gray-200 rounded w-1/2 mb-2" />
            <div className="h-4 bg-gray-200 rounded w-1/4" />
          </CardHeader>
          <CardContent>
            <div className="space-y-4">
              <div className="h-4 bg-gray-200 rounded w-full" />
              <div className="h-4 bg-gray-200 rounded w-2/3" />
            </div>
          </CardContent>
        </Card>
      </div>
    );
  }

  if (error || !kit) {
    return (
      <div className="container mx-auto py-8 px-4">
        <Card className="bg-red-50 border-red-200">
          <CardContent className="p-6 text-center">
            <p className="text-red-600">Interview kit not found or failed to load.</p>
            <Link href="/interview-kits">
              <Button className="mt-4">Back to Interview Kits</Button>
            </Link>
          </CardContent>
        </Card>
      </div>
    );
  }

  const getTypeColor = (type: string) => {
    const colors: Record<string, string> = {
      coding: "bg-blue-100 text-blue-800",
      system_design: "bg-purple-100 text-purple-800",
      pm_case: "bg-orange-100 text-orange-800",
      behavioral: "bg-green-100 text-green-800",
    };
    return colors[type] || "bg-gray-100 text-gray-800";
  };

  const formatType = (type: string) => {
    return type.replace("_", " ").replace(/\b\w/g, (l) => l.toUpperCase());
  };

  return (
    <div className="container mx-auto py-8 px-4">
      {/* Header */}
      <div className="flex flex-col sm:flex-row items-start sm:items-center justify-between gap-4 mb-8">
        <div>
          <Link href="/interview-kits">
            <Button variant="ghost" size="sm" className="mb-4">
              <ArrowLeft className="w-4 h-4 mr-2" />
              Back to Interview Kits
            </Button>
          </Link>
          <h1 className="text-3xl font-bold">{kit.title}</h1>
          <div className="flex items-center gap-3 mt-2">
            <Badge className={getTypeColor(kit.type)}>{formatType(kit.type)}</Badge>
            <span className="text-gray-500 text-sm">v{kit.version}</span>
          </div>
        </div>
        <div className="flex gap-2">
          <Button variant="outline">
            <Copy className="w-4 h-4 mr-2" />
            Duplicate
          </Button>
          <Button variant="outline">
            <Sparkles className="w-4 h-4 mr-2" />
            Regenerate
          </Button>
          <Button>
            <Edit className="w-4 h-4 mr-2" />
            Edit
          </Button>
        </div>
      </div>

      {/* Quick Stats */}
      <div className="grid grid-cols-2 md:grid-cols-4 gap-4 mb-8">
        <Card>
          <CardContent className="p-4 flex items-center gap-3">
            <ClockIcon className="w-5 h-5 text-gray-400" />
            <div>
              <p className="text-2xl font-bold">{kit.estimated_duration_minutes}</p>
              <p className="text-xs text-gray-500">Minutes</p>
            </div>
          </CardContent>
        </Card>
        <Card>
          <CardContent className="p-4 flex items-center gap-3">
            <BookOpen className="w-5 h-5 text-gray-400" />
            <div>
              <p className="text-2xl font-bold">{kit.questions?.length || 0}</p>
              <p className="text-xs text-gray-500">Questions</p>
            </div>
          </CardContent>
        </Card>
        <Card>
          <CardContent className="p-4 flex items-center gap-3">
            <CheckCircleIcon className="w-5 h-5 text-gray-400" />
            <div>
              <p className="text-2xl font-bold">{kit.evaluation_rubric?.length || 0}</p>
              <p className="text-xs text-gray-500">Criteria</p>
            </div>
          </CardContent>
        </Card>
        <Card>
          <CardContent className="p-4 flex items-center gap-3">
            <WarningIcon className="w-5 h-5 text-red-400" />
            <div>
              <p className="text-2xl font-bold">{kit.red_flags?.length || 0}</p>
              <p className="text-xs text-gray-500">Red Flags</p>
            </div>
          </CardContent>
        </Card>
      </div>

      {/* Problem Statement */}
      {kit.problem_statement && (
        <Card className="mb-6">
          <CardHeader>
            <CardTitle>Problem Statement</CardTitle>
          </CardHeader>
          <CardContent>
            <p className="whitespace-pre-wrap">{kit.problem_statement}</p>
          </CardContent>
        </Card>
      )}

      {/* Evaluation Rubric */}
      {kit.evaluation_rubric && kit.evaluation_rubric.length > 0 && (
        <Card className="mb-6">
          <CardHeader>
            <CardTitle>Evaluation Rubric</CardTitle>
            <CardDescription>Criteria for scoring candidate performance</CardDescription>
          </CardHeader>
          <CardContent>
            <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
              {kit.evaluation_rubric.map((criterion, idx) => (
                <div key={idx} className="border rounded-lg p-4">
                  <div className="flex justify-between items-start mb-2">
                    <h4 className="font-medium">{criterion.name}</h4>
                    <Badge variant="outline">
                      Max: {criterion.max_score} | Weight: {criterion.weight}
                    </Badge>
                  </div>
                  <p className="text-sm text-gray-600">{criterion.description}</p>
                </div>
              ))}
            </div>
          </CardContent>
        </Card>
      )}

      {/* Red Flags */}
      {kit.red_flags && kit.red_flags.length > 0 && (
        <Card className="mb-6 border-red-200">
          <CardHeader>
            <CardTitle className="text-red-600">Red Flags</CardTitle>
            <CardDescription>Warning signs to watch for during the interview</CardDescription>
          </CardHeader>
          <CardContent>
            <ul className="list-disc list-inside space-y-2">
              {kit.red_flags.map((flag, idx) => (
                <li key={idx} className="text-sm">{flag}</li>
              ))}
            </ul>
          </CardContent>
        </Card>
      )}

      {/* Good Answer Outline */}
      {kit.good_answer_outline && (
        <Card className="mb-6">
          <CardHeader>
            <CardTitle>Good Answer Outline</CardTitle>
            <CardDescription>Key points a strong candidate should cover</CardDescription>
          </CardHeader>
          <CardContent>
            <p className="whitespace-pre-wrap">{kit.good_answer_outline}</p>
          </CardContent>
        </Card>
      )}

      {/* Questions */}
      {kit.questions && kit.questions.length > 0 && (
        <Card className="mb-6">
          <CardHeader>
            <CardTitle>Interview Questions</CardTitle>
            <CardDescription>Structured questions for the interview</CardDescription>
          </CardHeader>
          <CardContent className="space-y-4">
            {kit.questions.map((q, idx) => {
              const difficultyColors: Record<string, string> = {
                easy: "bg-green-100 text-green-800",
                medium: "bg-yellow-100 text-yellow-800",
                hard: "bg-red-100 text-red-800",
              };
              return (
                <div key={idx} className="border rounded-lg p-4">
                  <div className="flex justify-between items-start mb-2">
                    <div className="flex items-center gap-2">
                      <Badge variant="secondary">{idx + 1}</Badge>
                      <Badge variant="outline">{q.type}</Badge>
                    </div>
                    <div className="flex items-center gap-2">
                      <Badge className={difficultyColors[q.difficulty] || "bg-gray-100"}>
                        {q.difficulty}
                      </Badge>
                      <span className="text-sm text-gray-500">{q.duration_minutes} min</span>
                    </div>
                  </div>
                  <p className="text-sm mb-2">{q.question}</p>
                  {q.notes && (
                    <p className="text-xs text-gray-500 italic">Note: {q.notes}</p>
                  )}
                </div>
              );
            })}
          </CardContent>
        </Card>
      )}

      {/* Tips for Interviewer */}
      {kit.tips_for_interviewer && (
        <Card className="mb-6 bg-blue-50 dark:bg-blue-900/20 border-blue-200">
          <CardHeader>
            <CardTitle>Tips for Interviewer</CardTitle>
          </CardHeader>
          <CardContent>
            <p className="whitespace-pre-wrap">{kit.tips_for_interviewer}</p>
          </CardContent>
        </Card>
      )}
    </div>
  );
}

// Icons
function ClockIcon({ className }: { className?: string }) {
  return (
    <svg className={className} fill="none" stroke="currentColor" viewBox="0 0 24 24">
      <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 8v4l3 3m6-3a9 9 0 11-18 0 9 9 0 0118 0z" />
    </svg>
  );
}

function BookOpen({ className }: { className?: string }) {
  return (
    <svg className={className} fill="none" stroke="currentColor" viewBox="0 0 24 24">
      <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 6.253v13m0-13C10.832 5.477 9.246 5 7.5 5S4.168 5.477 3 6.253v13C4.168 18.477 5.754 18 7.5 18s3.332.477 4.5 1.253m0-13C13.168 5.477 14.754 5 16.5 5c1.747 0 3.332.477 4.5 1.253v13C19.832 18.477 18.247 18 16.5 18c-1.746 0-3.332.477-4.5 1.253" />
    </svg>
  );
}

function CheckCircleIcon({ className }: { className?: string }) {
  return (
    <svg className={className} fill="none" stroke="currentColor" viewBox="0 0 24 24">
      <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 12l2 2 4-4m6 2a9 9 0 11-18 0 9 9 0 0118 0z" />
    </svg>
  );
}

function WarningIcon({ className }: { className?: string }) {
  return (
    <svg className={className} fill="none" stroke="currentColor" viewBox="0 0 24 24">
      <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 9v2m0 4h.01m-6.938 4h13.856c1.54 0 2.502-1.667 1.732-3L13.732 4c-.77-1.333-2.694-1.333-3.464 0L3.34 16c-.77 1.333.192 3 1.732 3z" />
    </svg>
  );
}

