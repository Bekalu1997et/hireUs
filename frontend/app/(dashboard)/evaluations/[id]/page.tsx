"use client";

import React from "react";
import Link from "next/link";
import { useQuery, useMutation, useQueryClient } from "@tanstack/react-query";
import { evaluationApi } from "@/lib/api";
import { Button } from "@/components/ui/button";
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import { ScorecardForm } from "@/components/forms/scorecard-form";
import { 
  ArrowLeft, Edit, Save, Send, Sparkles, 
  AlertCircle, CheckCircle, Clock, Star, User 
} from "lucide-react";
import { 
  Scorecard, 
  useScorecard, 
  useUpdateScorecard, 
  useSubmitScorecard, 
  useImproveFeedback,
  useValidateScorecard,
  ValidationResult
} from "@/hooks/use-evaluations";

interface PageProps {
  params: Promise<{ id: string }>;
}

export default function EvaluationDetailPage({ params }: PageProps) {
  const [evaluationId, setEvaluationId] = React.useState<string>("");
  const [isEditing, setIsEditing] = React.useState(false);
  const [improvementTarget, setImprovementTarget] = React.useState<string | null>(null);
  const queryClient = useQueryClient();

  React.useEffect(() => {
    params.then((p) => setEvaluationId(p.id));
  }, [params]);

  const { data: scorecard, isLoading, error } = useScorecard(evaluationId);
  const { data: validation } = useValidateScorecard(evaluationId);

  const updateMutation = useUpdateScorecard();
  const submitMutation = useSubmitScorecard();
  const improveMutation = useImproveFeedback();

  const handleImproveFeedback = (target: string) => {
    setImprovementTarget(target);
    improveMutation.mutate(
      { id: evaluationId, target },
      {
        onSuccess: () => {
          queryClient.invalidateQueries({ queryKey: ["evaluation", evaluationId] });
        },
      }
    );
  };

  const handleUpdate = async (data: {
    candidate_id: string;
    assignment_id?: string;
    scores: Record<string, { competency: string; score: number; evidence: string }>;
    confidence: number;
    strengths: string;
    weaknesses: string;
    summary: string;
    recommendation: string;
  }) => {
    const scoresRecord: Record<string, unknown> = {};
    Object.entries(data.scores).forEach(([key, value]) => {
      scoresRecord[key] = {
        competency: value.competency,
        score: value.score,
        evidence: value.evidence,
      };
    });

    await updateMutation.mutateAsync({
      id: evaluationId,
      data: {
        scores: scoresRecord,
        confidence: data.confidence,
        strengths: data.strengths,
        weaknesses: data.weaknesses,
        summary: data.summary,
        recommendation: data.recommendation,
      },
    });
    setIsEditing(false);
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
    const scoresRecord: Record<string, unknown> = {};
    Object.entries(data.scores).forEach(([key, value]) => {
      scoresRecord[key] = {
        competency: value.competency,
        score: value.score,
        evidence: value.evidence,
      };
    });

    await updateMutation.mutateAsync({
      id: evaluationId,
      data: {
        scores: scoresRecord,
        confidence: data.confidence,
        strengths: data.strengths,
        weaknesses: data.weaknesses,
        summary: data.summary,
        recommendation: data.recommendation,
        is_draft: true,
      },
    });
  };

  const handleSubmit = async () => {
    await submitMutation.mutateAsync({ id: evaluationId, validateFirst: true });
  };

  if (isLoading) {
    return (
      <div className="container mx-auto py-8 px-4">
        <div className="mb-8">
          <Link href="/evaluations">
            <Button variant="ghost" size="sm" className="mb-4">
              <ArrowLeft className="w-4 h-4 mr-2" />
              Back to Evaluations
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

  if (error || !scorecard) {
    return (
      <div className="container mx-auto py-8 px-4">
        <Link href="/evaluations">
          <Button variant="ghost" size="sm" className="mb-4">
            <ArrowLeft className="w-4 h-4 mr-2" />
            Back to Evaluations
          </Button>
        </Link>
        <Card className="bg-red-50 border-red-200">
          <CardContent className="p-6 text-center">
            <p className="text-red-600">Evaluation not found or failed to load.</p>
          </CardContent>
        </Card>
      </div>
    );
  }

  const getRecommendationColor = (rec: string) => {
    const colors: Record<string, string> = {
      strong_hire: "bg-green-100 text-green-800",
      hire: "bg-blue-100 text-blue-800",
      neutral: "bg-gray-100 text-gray-800",
      no_hire: "bg-orange-100 text-orange-800",
      strong_no_hire: "bg-red-100 text-red-800",
    };
    return colors[rec] || "bg-gray-100 text-gray-800";
  };

  const formatRecommendation = (rec: string) => {
    return rec.replace(/_/g, " ").replace(/\b\w/g, (l) => l.toUpperCase());
  };

  const calculateAverageScore = () => {
    const values = Object.values(scorecard.scores);
    if (values.length === 0) return "0.0";
    
    let total = 0;
    let count = 0;
    
    values.forEach((v) => {
      if (typeof v === "number") {
        total += v;
        count++;
      } else if (typeof v === "object" && v !== null && "score" in v) {
        total += (v as { score: number }).score;
        count++;
      }
    });
    
    return count > 0 ? (total / count).toFixed(1) : "0.0";
  };

  const competencies = Object.keys(scorecard.scores).map((key) => {
    const scoreData = scorecard.scores[key];
    let score = 3;
    let evidence = "";
    
    if (typeof scoreData === "object" && scoreData !== null) {
      score = (scoreData as { score: number }).score || 3;
      evidence = (scoreData as { evidence?: string }).evidence || "";
    } else if (typeof scoreData === "number") {
      score = scoreData;
    }
    
    return {
      competency: key,
      score,
      evidence,
    };
  });

  // Get AI suggestion if available
  const getAISuggestion = () => {
    if (!improveMutation.data?.suggestions || improveMutation.data.suggestions.length === 0) {
      return undefined;
    }
    return improveMutation.data.suggestions[0];
  };

  return (
    <div className="container mx-auto py-8 px-4">
      {/* Header */}
      <div className="flex flex-col sm:flex-row items-start sm:items-center justify-between gap-4 mb-8">
        <div>
          <Link href="/evaluations">
            <Button variant="ghost" size="sm" className="mb-4">
              <ArrowLeft className="w-4 h-4 mr-2" />
              Back to Evaluations
            </Button>
          </Link>
          <div className="flex items-center gap-3">
            <h1 className="text-3xl font-bold">Interview Evaluation</h1>
            {scorecard.is_draft && (
              <Badge className="bg-yellow-100 text-yellow-800">Draft</Badge>
            )}
            {scorecard.is_submitted && (
              <Badge className="bg-green-100 text-green-800">Submitted</Badge>
            )}
          </div>
        </div>
        <div className="flex gap-2">
          {!isEditing && scorecard.is_draft && (
            <>
              <Button variant="outline" onClick={() => setIsEditing(true)}>
                <Edit className="w-4 h-4 mr-2" />
                Edit
              </Button>
              <Button onClick={handleSubmit} disabled={submitMutation.isPending}>
                <Send className="w-4 h-4 mr-2" />
                {submitMutation.isPending ? "Submitting..." : "Submit"}
              </Button>
            </>
          )}
        </div>
      </div>

      {/* Validation Messages */}
      {validation && !validation.is_valid && scorecard.is_draft && (
        <Card className="mb-6 bg-yellow-50 border-yellow-200">
          <CardContent className="p-4">
            <div className="flex items-start gap-3">
              <AlertCircle className="w-5 h-5 text-yellow-600 mt-0.5" />
              <div>
                <h4 className="font-medium text-yellow-800">Submission Requirements</h4>
                <ul className="text-sm text-yellow-700 mt-2 space-y-1">
                  {validation.messages.map((msg, i) => (
                    <li key={i}>• {msg}</li>
                  ))}
                  {validation.missing_evidence.length > 0 && (
                    <li>
                      Missing evidence for: {validation.missing_evidence.join(", ")}
                    </li>
                  )}
                </ul>
              </div>
            </div>
          </CardContent>
        </Card>
      )}

      {/* Success Message */}
      {submitMutation.isSuccess && (
        <Card className="mb-6 bg-green-50 border-green-200">
          <CardContent className="p-4">
            <div className="flex items-center gap-3">
              <CheckCircle className="w-5 h-5 text-green-600" />
              <div>
                <p className="font-medium text-green-800">
                  Evaluation submitted successfully!
                </p>
              </div>
            </div>
          </CardContent>
        </Card>
      )}

      {/* View Mode */}
      {!isEditing ? (
        <div className="space-y-6">
          {/* Quick Stats */}
          <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
            <Card>
              <CardContent className="p-4 flex items-center gap-3">
                <Star className="w-5 h-5 text-yellow-500" />
                <div>
                  <p className="text-2xl font-bold">{calculateAverageScore()}</p>
                  <p className="text-xs text-gray-500">Avg Score</p>
                </div>
              </CardContent>
            </Card>
            <Card>
              <CardContent className="p-4 flex items-center gap-3">
                <User className="w-5 h-5 text-gray-400" />
                <div>
                  <p className="text-2xl font-bold">{competencies.length}</p>
                  <p className="text-xs text-gray-500">Competencies</p>
                </div>
              </CardContent>
            </Card>
            <Card>
              <CardContent className="p-4 flex items-center gap-3">
                <Clock className="w-5 h-5 text-blue-500" />
                <div>
                  <p className="text-2xl font-bold">{scorecard.confidence}/5</p>
                  <p className="text-xs text-gray-500">Confidence</p>
                </div>
              </CardContent>
            </Card>
            <Card>
              <CardContent className="p-4 flex items-center gap-3">
                <Badge className={`${getRecommendationColor(scorecard.recommendation)} text-sm px-3 py-1`}>
                  {formatRecommendation(scorecard.recommendation)}
                </Badge>
                <div>
                  <p className="text-xs text-gray-500">Recommendation</p>
                </div>
              </CardContent>
            </Card>
          </div>

          {/* Competency Scores */}
          <Card>
            <CardHeader>
              <CardTitle>Competency Evaluation</CardTitle>
              <CardDescription>
                Scores and evidence for each competency
              </CardDescription>
            </CardHeader>
            <CardContent className="space-y-4">
              {competencies.map((comp) => (
                <div key={comp.competency} className="border rounded-lg p-4">
                  <div className="flex items-center justify-between mb-3">
                    <h4 className="font-medium">{comp.competency}</h4>
                    <div className="flex items-center gap-1">
                      {[1, 2, 3, 4, 5].map((score) => (
                        <Star
                          key={score}
                          className={`w-4 h-4 ${
                            score <= comp.score
                              ? "text-yellow-500 fill-yellow-500"
                              : "text-gray-300"
                          }`}
                        />
                      ))}
                      <span className="ml-2 text-sm font-medium">{comp.score}/5</span>
                    </div>
                  </div>
                  <p className="text-sm text-gray-700">{comp.evidence}</p>
                </div>
              ))}
            </CardContent>
          </Card>

          {/* Written Feedback */}
          <Card>
            <CardHeader>
              <CardTitle>Written Feedback</CardTitle>
            </CardHeader>
            <CardContent className="space-y-6">
              {scorecard.strengths && (
                <div>
                  <h4 className="font-medium mb-2 text-green-700">Strengths</h4>
                  <p className="text-gray-700 whitespace-pre-wrap">{scorecard.strengths}</p>
                </div>
              )}
              {scorecard.weaknesses && (
                <div>
                  <h4 className="font-medium mb-2 text-orange-700">Areas for Improvement</h4>
                  <p className="text-gray-700 whitespace-pre-wrap">{scorecard.weaknesses}</p>
                </div>
              )}
              {scorecard.summary && (
                <div>
                  <h4 className="font-medium mb-2">Overall Summary</h4>
                  <p className="text-gray-700 whitespace-pre-wrap">{scorecard.summary}</p>
                </div>
              )}
            </CardContent>
          </Card>

          {/* Metadata */}
          <Card>
            <CardContent className="p-4 text-sm text-gray-500">
              <div className="flex flex-wrap gap-4">
                <span>Created: {new Date(scorecard.created_at).toLocaleString()}</span>
                <span>Updated: {new Date(scorecard.updated_at).toLocaleString()}</span>
                {scorecard.submitted_at && (
                  <span>Submitted: {new Date(scorecard.submitted_at).toLocaleString()}</span>
                )}
              </div>
            </CardContent>
          </Card>
        </div>
      ) : (
        /* Edit Mode */
        <ScorecardForm
          initialData={{
            candidate_id: scorecard.candidate_id,
            assignment_id: scorecard.assignment_id,
            competencies: competencies.map((c) => c.competency),
            existingScores: competencies.reduce((acc, c) => {
              acc[c.competency] = { score: c.score, evidence: c.evidence };
              return acc;
            }, {} as Record<string, { score: number; evidence: string }>),
            confidence: scorecard.confidence,
            strengths: scorecard.strengths || "",
            weaknesses: scorecard.weaknesses || "",
            summary: scorecard.summary || "",
            recommendation: scorecard.recommendation,
          }}
          onSubmit={handleUpdate}
          onSaveDraft={handleSaveDraft}
          isSaving={updateMutation.isPending}
          onImproveFeedback={handleImproveFeedback}
          isImproving={improveMutation.isPending}
          improvementSuggestion={getAISuggestion()}
        />
      )}
    </div>
  );
}

