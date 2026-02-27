"use client";

import React, { useState } from "react";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Textarea } from "@/components/ui/textarea";
import { Label } from "@/components/ui/label";
import { Select } from "@/components/ui/select";
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import { Card as UICard } from "@/components/ui/card";
import { Sparkles, AlertCircle, CheckCircle2 } from "lucide-react";

interface CompetencyScoreInputProps {
  competency: string;
  score: number;
  evidence: string;
  onScoreChange: (score: number) => void;
  onEvidenceChange: (evidence: string) => void;
  onSuggestEvidence: () => void;
  isSuggesting?: boolean;
  suggestedEvidence?: string;
}

function CompetencyScoreInput({
  competency,
  score,
  evidence,
  onScoreChange,
  onEvidenceChange,
  onSuggestEvidence,
  isSuggesting,
  suggestedEvidence,
}: CompetencyScoreInputProps) {
  const scoreLabels = {
    1: "Needs Improvement",
    2: "Below Expectations",
    3: "Meets Expectations",
    4: "Exceeds Expectations",
    5: "Outstanding",
  };

  const scoreColors = {
    1: "bg-red-100 text-red-800 border-red-200",
    2: "bg-orange-100 text-orange-800 border-orange-200",
    3: "bg-yellow-100 text-yellow-800 border-yellow-200",
    4: "bg-blue-100 text-blue-800 border-blue-200",
    5: "bg-green-100 text-green-800 border-green-200",
  };

  return (
    <div className="border rounded-lg p-4 space-y-4">
      <div className="flex items-center justify-between">
        <h4 className="font-medium text-lg">{competency}</h4>
        <Button
          type="button"
          variant="ghost"
          size="sm"
          onClick={onSuggestEvidence}
          disabled={isSuggesting}
        >
          <Sparkles className="w-4 h-4 mr-1" />
          {isSuggesting ? "Suggesting..." : "AI Suggest"}
        </Button>
      </div>

      {/* Score Slider */}
      <div className="space-y-2">
        <Label>Score: {score}/5 - {scoreLabels[score as keyof typeof scoreLabels]}</Label>
        <div className="flex gap-2">
          {[1, 2, 3, 4, 5].map((value) => (
            <button
              key={value}
              type="button"
              onClick={() => onScoreChange(value)}
              className={`flex-1 py-3 rounded-lg border-2 font-medium transition-all ${
                score === value
                  ? `${scoreColors[value as keyof typeof scoreColors]} border-current`
                  : "bg-gray-50 border-gray-200 hover:border-gray-300"
              }`}
            >
              {value}
            </button>
          ))}
        </div>
      </div>

      {/* Evidence */}
      <div className="space-y-2">
        <Label htmlFor={`evidence-${competency}`}>Evidence (required)</Label>
        <Textarea
          id={`evidence-${competency}`}
          placeholder="Describe specific examples or observations that support this score..."
          value={evidence}
          onChange={(e) => onEvidenceChange(e.target.value)}
          rows={3}
          className={!evidence.trim() ? "border-yellow-300 bg-yellow-50" : ""}
        />
        {!evidence.trim() && (
          <p className="text-sm text-yellow-600 flex items-center">
            <AlertCircle className="w-4 h-4 mr-1" />
            Evidence is required before submission
          </p>
        )}
      </div>

      {/* AI Suggestion */}
      {suggestedEvidence && (
        <div className="bg-blue-50 border border-blue-200 rounded-lg p-3">
          <div className="flex items-start gap-2">
            <Sparkles className="w-4 h-4 text-blue-600 mt-0.5" />
            <div className="space-y-2">
              <p className="text-sm font-medium text-blue-800">AI Suggestion</p>
              <p className="text-sm text-blue-700">{suggestedEvidence}</p>
              <Button
                type="button"
                size="sm"
                variant="outline"
                onClick={() => onEvidenceChange(suggestedEvidence)}
                className="bg-blue-100 hover:bg-blue-200"
              >
                Use This
              </Button>
            </div>
          </div>
        </div>
      )}
    </div>
  );
}

interface ScorecardFormProps {
  initialData?: {
    candidate_id: string;
    assignment_id?: string;
    competencies: string[];
    existingScores?: Record<string, { score: number; evidence?: string }>;
    confidence?: number;
    strengths?: string;
    weaknesses?: string;
    summary?: string;
    recommendation?: string;
  };
  onSubmit: (data: {
    candidate_id: string;
    assignment_id?: string;
    scores: Record<string, { competency: string; score: number; evidence: string }>;
    confidence: number;
    strengths: string;
    weaknesses: string;
    summary: string;
    recommendation: string;
  }) => void;
  onSaveDraft?: (data: {
    candidate_id: string;
    assignment_id?: string;
    scores: Record<string, { competency: string; score: number; evidence: string }>;
    confidence: number;
    strengths: string;
    weaknesses: string;
    summary: string;
    recommendation: string;
  }) => void;
  isLoading?: boolean;
  isSaving?: boolean;
  isSubmitting?: boolean;
  onImproveFeedback?: (target: string) => void;
  isImproving?: boolean;
  improvementSuggestion?: {
    field: string;
    original: string;
    improved: string;
  };
  candidateName?: string;
}

export function ScorecardForm({
  initialData,
  onSubmit,
  onSaveDraft,
  isLoading,
  isSaving,
  isSubmitting,
  onImproveFeedback,
  isImproving,
  improvementSuggestion,
  candidateName,
}: ScorecardFormProps) {
  const [scores, setScores] = useState<Record<string, { score: number; evidence: string }>>(() => {
    if (initialData?.existingScores) {
      const normalized: Record<string, { score: number; evidence: string }> = {};
      Object.entries(initialData.existingScores).forEach(([key, value]) => {
        normalized[key] = { score: value.score, evidence: value.evidence || "" };
      });
      return normalized;
    }
    // Initialize with competencies
    const initial: Record<string, { score: number; evidence: string }> = {};
    (initialData?.competencies || []).forEach((comp) => {
      initial[comp] = { score: 3, evidence: "" };
    });
    return initial;
  });

  const [confidence, setConfidence] = useState(initialData?.confidence || 3);
  const [strengths, setStrengths] = useState(initialData?.strengths || "");
  const [weaknesses, setWeaknesses] = useState(initialData?.weaknesses || "");
  const [summary, setSummary] = useState(initialData?.summary || "");
  const [recommendation, setRecommendation] = useState(initialData?.recommendation || "neutral");
  const [suggestedEvidence, setSuggestedEvidence] = useState<Record<string, string>>({});
  const [activeSuggestion, setActiveSuggestion] = useState<string | null>(null);

  const handleScoreChange = (competency: string, score: number) => {
    setScores((prev) => ({
      ...prev,
      [competency]: { ...prev[competency], score },
    }));
  };

  const handleEvidenceChange = (competency: string, evidence: string) => {
    setScores((prev) => ({
      ...prev,
      [competency]: { ...prev[competency], evidence },
    }));
  };

  const handleSuggestEvidence = (competency: string) => {
    setActiveSuggestion(competency);
    onImproveFeedback?.(competency);
  };

  // Update suggested evidence when suggestion changes
  React.useEffect(() => {
    if (improvementSuggestion && improvementSuggestion.field === activeSuggestion) {
      setSuggestedEvidence((prev) => ({
        ...prev,
        [activeSuggestion]: improvementSuggestion.improved,
      }));
    }
  }, [improvementSuggestion, activeSuggestion]);

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();

    // Validate
    const hasEmptyEvidence = Object.values(scores).some((s) => !s.evidence.trim());
    if (hasEmptyEvidence) {
      alert("Please provide evidence for all competencies before submitting.");
      return;
    }

    const scoresData: Record<string, { competency: string; score: number; evidence: string }> = {};
    Object.entries(scores).forEach(([key, value]) => {
      scoresData[key] = {
        competency: key,
        score: value.score,
        evidence: value.evidence,
      };
    });

    onSubmit({
      candidate_id: initialData?.candidate_id || "",
      assignment_id: initialData?.assignment_id,
      scores: scoresData,
      confidence,
      strengths,
      weaknesses,
      summary,
      recommendation,
    });
  };

  const handleSaveDraft = () => {
    const scoresData: Record<string, { competency: string; score: number; evidence: string }> = {};
    Object.entries(scores).forEach(([key, value]) => {
      scoresData[key] = {
        competency: key,
        score: value.score,
        evidence: value.evidence,
      };
    });

    onSaveDraft?.({
      candidate_id: initialData?.candidate_id || "",
      assignment_id: initialData?.assignment_id,
      scores: scoresData,
      confidence,
      strengths,
      weaknesses,
      summary,
      recommendation,
    });
  };

  const recommendationOptions = [
    { value: "strong_no_hire", label: "Strong No Hire" },
    { value: "no_hire", label: "No Hire" },
    { value: "neutral", label: "Neutral" },
    { value: "hire", label: "Hire" },
    { value: "strong_hire", label: "Strong Hire" },
  ];

  const confidenceOptions = [
    { value: "1", label: "1 - Very Uncertain" },
    { value: "2", label: "2 - Somewhat Uncertain" },
    { value: "3", label: "3 - Moderate Confidence" },
    { value: "4", label: "4 - Pretty Confident" },
    { value: "5", label: "5 - Very Confident" },
  ];

  // Calculate completion status
  const completedScores = Object.values(scores).filter((s) => s.evidence.trim()).length;
  const totalScores = Object.keys(scores).length;

  if (isLoading) {
    return (
      <div className="space-y-6 animate-pulse">
        <div className="h-8 bg-gray-200 rounded w-1/4" />
        <div className="space-y-4">
          {[1, 2, 3].map((i) => (
            <div key={i} className="border rounded-lg p-4">
              <div className="h-6 bg-gray-200 rounded w-1/3 mb-4" />
              <div className="h-10 bg-gray-200 rounded" />
            </div>
          ))}
        </div>
      </div>
    );
  }

  return (
    <form onSubmit={handleSubmit} className="space-y-8">
      {/* Header */}
      <div className="flex items-center justify-between">
        <div>
          <h2 className="text-2xl font-bold">Interview Scorecard</h2>
          {candidateName && (
            <p className="text-gray-600">Candidate: {candidateName}</p>
          )}
        </div>
        <div className="flex items-center gap-2">
          <Badge variant="outline" className="text-sm">
            {completedScores}/{totalScores} competencies scored
          </Badge>
        </div>
      </div>

      {/* Competency Scores */}
      <Card>
        <CardHeader>
          <CardTitle>Competency Evaluation</CardTitle>
          <CardDescription>
            Rate each competency and provide specific evidence supporting your score
          </CardDescription>
        </CardHeader>
        <CardContent className="space-y-6">
          {Object.keys(scores).map((competency) => (
            <CompetencyScoreInput
              key={competency}
              competency={competency}
              score={scores[competency].score}
              evidence={scores[competency].evidence}
              onScoreChange={(score) => handleScoreChange(competency, score)}
              onEvidenceChange={(evidence) => handleEvidenceChange(competency, evidence)}
              onSuggestEvidence={() => handleSuggestEvidence(competency)}
              isSuggesting={isImproving && activeSuggestion === competency}
              suggestedEvidence={suggestedEvidence[competency]}
            />
          ))}
        </CardContent>
      </Card>

      {/* Confidence Level */}
      <Card>
        <CardHeader>
          <CardTitle>Interviewer Confidence</CardTitle>
          <CardDescription>
            How confident are you in this evaluation based on the interview?
          </CardDescription>
        </CardHeader>
        <CardContent>
          <Select
            options={confidenceOptions}
            value={String(confidence)}
            onChange={(e) => setConfidence(parseInt(e.target.value))}
          />
          <div className="mt-4 p-4 bg-gray-50 rounded-lg">
            <p className="text-sm text-gray-600">
              <strong>Tip:</strong> Lower confidence may indicate the candidate showed mixed signals
              or you need more information. Consider flagging this candidate for a follow-up interview.
            </p>
          </div>
        </CardContent>
      </Card>

      {/* Written Feedback */}
      <Card>
        <CardHeader>
          <div className="flex items-center justify-between">
            <div>
              <CardTitle>Written Feedback</CardTitle>
              <CardDescription>
                Provide constructive feedback for the hiring team
              </CardDescription>
            </div>
            <Button
              type="button"
              variant="outline"
              size="sm"
              onClick={() => onImproveFeedback?.("all")}
              disabled={isImproving}
            >
              <Sparkles className="w-4 h-4 mr-1" />
              {isImproving ? "Improving..." : "✨ Improve All with AI"}
            </Button>
          </div>
        </CardHeader>
        <CardContent className="space-y-6">
          {/* Strengths */}
          <div className="space-y-2">
            <div className="flex items-center justify-between">
              <Label htmlFor="strengths">Strengths</Label>
              <Button
                type="button"
                variant="ghost"
                size="sm"
                onClick={() => onImproveFeedback?.("strengths")}
                disabled={isImproving || !strengths}
              >
                <Sparkles className="w-3 h-3 mr-1" />
                Improve
              </Button>
            </div>
            <Textarea
              id="strengths"
              placeholder="What are the candidate's key strengths observed during the interview?"
              value={strengths}
              onChange={(e) => setStrengths(e.target.value)}
              rows={4}
            />
          </div>

          {/* Weaknesses */}
          <div className="space-y-2">
            <div className="flex items-center justify-between">
              <Label htmlFor="weaknesses">Areas for Improvement</Label>
              <Button
                type="button"
                variant="ghost"
                size="sm"
                onClick={() => onImproveFeedback?.("weaknesses")}
                disabled={isImproving || !weaknesses}
              >
                <Sparkles className="w-3 h-3 mr-1" />
                Improve
              </Button>
            </div>
            <Textarea
              id="weaknesses"
              placeholder="What are the areas where the candidate could improve?"
              value={weaknesses}
              onChange={(e) => setWeaknesses(e.target.value)}
              rows={4}
            />
          </div>

          {/* Summary */}
          <div className="space-y-2">
            <div className="flex items-center justify-between">
              <Label htmlFor="summary">Overall Summary</Label>
              <Button
                type="button"
                variant="ghost"
                size="sm"
                onClick={() => onImproveFeedback?.("summary")}
                disabled={isImproving || !summary}
              >
                <Sparkles className="w-3 h-3 mr-1" />
                Improve
              </Button>
            </div>
            <Textarea
              id="summary"
              placeholder="Provide an overall summary of the candidate's performance..."
              value={summary}
              onChange={(e) => setSummary(e.target.value)}
              rows={4}
            />
          </div>

          {/* AI Improvement Suggestion Display */}
          {improvementSuggestion && (
            <div className="bg-green-50 border border-green-200 rounded-lg p-4">
              <div className="flex items-start gap-3">
                <Sparkles className="w-5 h-5 text-green-600 mt-0.5" />
                <div className="flex-1 space-y-2">
                  <div className="flex items-center justify-between">
                    <p className="font-medium text-green-800">
                      AI Improvement for {improvementSuggestion.field}
                    </p>
                    <div className="flex gap-2">
                      <Button
                        type="button"
                        size="sm"
                        variant="outline"
                        onClick={() => {
                          if (improvementSuggestion.field === "strengths") setStrengths(improvementSuggestion.improved);
                          if (improvementSuggestion.field === "weaknesses") setWeaknesses(improvementSuggestion.improved);
                          if (improvementSuggestion.field === "summary") setSummary(improvementSuggestion.improved);
                          if (improvementSuggestion.field === "all") {
                            setStrengths(improvementSuggestion.improved);
                          }
                        }}
                      >
                        Accept
                      </Button>
                      <Button type="button" size="sm" variant="ghost">
                        Dismiss
                      </Button>
                    </div>
                  </div>
                  <div className="grid grid-cols-2 gap-4 text-sm">
                    <div>
                      <p className="text-green-700 font-medium">Original:</p>
                      <p className="text-green-600">{improvementSuggestion.original}</p>
                    </div>
                    <div>
                      <p className="text-green-700 font-medium">Improved:</p>
                      <p className="text-green-600">{improvementSuggestion.improved}</p>
                    </div>
                  </div>
                </div>
              </div>
            </div>
          )}
        </CardContent>
      </Card>

      {/* Recommendation */}
      <Card>
        <CardHeader>
          <CardTitle>Hiring Recommendation</CardTitle>
          <CardDescription>
            Based on the evaluation, what is your recommendation?
          </CardDescription>
        </CardHeader>
        <CardContent>
          <Select
            options={recommendationOptions}
            value={recommendation}
            onChange={(e) => setRecommendation(e.target.value)}
          />

          <div className="mt-6 p-4 bg-gray-50 rounded-lg">
            <h4 className="font-medium mb-2">Recommendation Guide:</h4>
            <ul className="text-sm text-gray-600 space-y-1">
              <li><strong>Strong No Hire:</strong> Clear concerns, would not recommend</li>
              <li><strong>No Hire:</strong> Does not meet requirements</li>
              <li><strong>Neutral:</strong> Meets basic requirements, but not outstanding</li>
              <li><strong>Hire:</strong> Strong candidate, recommend hiring</li>
              <li><strong>Strong Hire:</strong> Exceptional candidate, highly recommend</li>
            </ul>
          </div>
        </CardContent>
      </Card>

      {/* Validation Summary */}
      <UICard className="bg-gray-50">
        <CardContent className="p-4">
          <h4 className="font-medium mb-3">Submission Checklist:</h4>
          <div className="space-y-2">
            <div className="flex items-center gap-2">
              {completedScores === totalScores ? (
                <CheckCircle2 className="w-5 h-5 text-green-600" />
              ) : (
                <AlertCircle className="w-5 h-5 text-yellow-600" />
              )}
              <span>
                {completedScores}/{totalScores} competencies with evidence ({completedScores === totalScores ? "Ready" : "Missing evidence"})
              </span>
            </div>
            <div className="flex items-center gap-2">
              {strengths.trim() ? (
                <CheckCircle2 className="w-5 h-5 text-green-600" />
              ) : (
                <AlertCircle className="w-5 h-5 text-yellow-600" />
              )}
              <span>Strengths {strengths.trim() ? "provided" : "missing"}</span>
            </div>
            <div className="flex items-center gap-2">
              {weaknesses.trim() ? (
                <CheckCircle2 className="w-5 h-5 text-green-600" />
              ) : (
                <AlertCircle className="w-5 h-5 text-yellow-600" />
              )}
              <span>Areas for improvement {weaknesses.trim() ? "provided" : "missing"}</span>
            </div>
            <div className="flex items-center gap-2">
              {summary.trim() ? (
                <CheckCircle2 className="w-5 h-5 text-green-600" />
              ) : (
                <AlertCircle className="w-5 h-5 text-yellow-600" />
              )}
              <span>Summary {summary.trim() ? "provided" : "missing"}</span>
            </div>
          </div>
        </CardContent>
      </UICard>

      {/* Actions */}
      <div className="flex flex-col sm:flex-row gap-3 justify-end">
        {onSaveDraft && (
          <Button
            type="button"
            variant="outline"
            onClick={handleSaveDraft}
            disabled={isSaving}
          >
            {isSaving ? "Saving..." : "Save Draft"}
          </Button>
        )}
        <Button type="submit" disabled={isSubmitting}>
          {isSubmitting ? "Submitting..." : "Submit Evaluation"}
        </Button>
      </div>
    </form>
  );
}

