"use client";

import React, { useState } from "react";
import Link from "next/link";
import { Button } from "@/components/ui/button";
import { Card, CardContent, CardHeader, CardTitle, CardDescription } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import { Input } from "@/components/ui/input";
import { Separator } from "@/components/ui/separator";
import {
  FileText, Users, AlertTriangle, CheckCircle, Brain,
  TrendingUp, ChevronRight, RefreshCw, Sparkles,
  Target, ThumbsUp, ThumbsDown, AlertCircle, Info,
  ArrowRight, Search, Lightbulb
} from "lucide-react";
import {
  useGenerateDecisionBrief,
  useComparableCandidates,
  useSignalAnalysis,
  useCandidateDecisionStats,
  DecisionBrief,
  SignalAnalysis,
} from "@/hooks/use-decisions";

// Helper function to get score color
const getScoreColor = (score: number): string => {
  if (score >= 4.5) return "text-green-600 bg-green-50";
  if (score >= 3.5) return "text-blue-600 bg-blue-50";
  if (score >= 2.5) return "text-yellow-600 bg-yellow-50";
  if (score >= 1.5) return "text-orange-600 bg-orange-50";
  return "text-red-600 bg-red-50";
};

// Helper to get decision badge color
const getDecisionColor = (decision: string): string => {
  switch (decision) {
    case "strong_hire":
      return "bg-green-100 text-green-800 border-green-200";
    case "hire":
      return "bg-emerald-100 text-emerald-800 border-emerald-200";
    case "neutral":
      return "bg-gray-100 text-gray-800 border-gray-200";
    case "no_hire":
      return "bg-orange-100 text-orange-800 border-orange-200";
    case "strong_no_hire":
      return "bg-red-100 text-red-800 border-red-200";
    case "defer":
      return "bg-yellow-100 text-yellow-800 border-yellow-200";
    default:
      return "bg-gray-100 text-gray-800";
  }
};

// Helper to get signal strength color
const getSignalStrengthColor = (strength: string): string => {
  switch (strength) {
    case "strong":
      return "bg-green-500";
    case "moderate":
      return "bg-yellow-500";
    case "weak":
      return "bg-orange-500";
    case "none":
      return "bg-gray-400";
    default:
      return "bg-gray-400";
  }
};

// Candidate card component
const CandidateCard: React.FC<{
  candidate: {
    id: string;
    full_name: string;
    email: string;
    status: string;
    role_title: string;
  };
  isSelected: boolean;
  onSelect: () => void;
  disabled?: boolean;
}> = ({ candidate, isSelected, onSelect, disabled }) => {
  return (
    <Card
      className={`cursor-pointer transition-all hover:shadow-md ${
        isSelected ? "ring-2 ring-blue-500 shadow-lg" : "hover:border-blue-300"
      } ${disabled ? "opacity-50 cursor-not-allowed" : ""}`}
      onClick={disabled ? undefined : onSelect}
    >
      <CardContent className="p-4">
        <div className="flex items-start justify-between">
          <div>
            <h3 className="font-semibold text-lg">{candidate.full_name}</h3>
            <p className="text-sm text-gray-500">{candidate.email}</p>
            <div className="flex items-center gap-2 mt-2">
              <Badge variant="outline">{candidate.status}</Badge>
              <span className="text-xs text-gray-400">{candidate.role_title}</span>
            </div>
          </div>
          {isSelected && (
            <CheckCircle className="w-6 h-6 text-blue-500" />
          )}
        </div>
      </CardContent>
    </Card>
  );
};

// Strength item component
const StrengthItem: React.FC<{
  strength: {
    category: string;
    description: string;
    evidence: string[];
    competency_scores: Record<string, number>;
  };
}> = ({ strength }) => {
  return (
    <div className="border rounded-lg p-4 bg-green-50/50">
      <div className="flex items-start gap-3">
        <div className="p-2 bg-green-100 rounded-lg">
          <ThumbsUp className="w-5 h-5 text-green-600" />
        </div>
        <div className="flex-1">
          <h4 className="font-semibold text-green-800">{strength.category}</h4>
          <p className="text-sm text-gray-600 mt-1">{strength.description}</p>
          {strength.evidence && strength.evidence.length > 0 && (
            <div className="mt-2 flex flex-wrap gap-2">
              {strength.evidence.slice(0, 3).map((ev, idx) => (
                <Badge key={idx} variant="outline" className="text-xs">
                  {ev}
                </Badge>
              ))}
            </div>
          )}
          {Object.keys(strength.competency_scores).length > 0 && (
            <div className="mt-2 flex gap-2">
              {Object.entries(strength.competency_scores).map(([comp, score]) => (
                <span key={comp} className={`text-xs px-2 py-1 rounded ${getScoreColor(score)}`}>
                  {comp}: {score.toFixed(1)}
                </span>
              ))}
            </div>
          )}
        </div>
      </div>
    </div>
  );
};

// Risk area component
const RiskAreaItem: React.FC<{
  risk: {
    category: string;
    description: string;
    severity: "low" | "medium" | "high";
    mitigation?: string;
    evidence: string[];
  };
}> = ({ risk }) => {
  const severityColor = {
    low: "bg-blue-100 text-blue-800 border-blue-200",
    medium: "bg-yellow-100 text-yellow-800 border-yellow-200",
    high: "bg-red-100 text-red-800 border-red-200",
  };

  return (
    <div className="border rounded-lg p-4 bg-red-50/50">
      <div className="flex items-start gap-3">
        <div className="p-2 bg-red-100 rounded-lg">
          <AlertTriangle className="w-5 h-5 text-red-600" />
        </div>
        <div className="flex-1">
          <div className="flex items-center gap-2">
            <h4 className="font-semibold text-red-800">{risk.category}</h4>
            <Badge className={severityColor[risk.severity]}>
              {risk.severity}
            </Badge>
          </div>
          <p className="text-sm text-gray-600 mt-1">{risk.description}</p>
          {risk.mitigation && (
            <p className="text-sm text-blue-600 mt-2">
              <Lightbulb className="w-4 h-4 inline mr-1" />
              {risk.mitigation}
            </p>
          )}
        </div>
      </div>
    </div>
  );
};

// Signal gap component
const SignalGapItem: React.FC<{
  gap: {
    competency: string;
    status: string;
    reason: string;
    recommendation: string;
  };
}> = ({ gap }) => {
  const statusIcon = {
    missing: AlertCircle,
    weak: AlertTriangle,
    conflicting: Info,
  };

  const Icon = statusIcon[gap.status as keyof typeof statusIcon] || AlertCircle;
  const statusColor = {
    missing: "text-red-600 bg-red-50",
    weak: "text-yellow-600 bg-yellow-50",
    conflicting: "text-blue-600 bg-blue-50",
  };

  return (
    <div className="border rounded-lg p-4">
      <div className="flex items-start gap-3">
        <div className={`p-2 rounded-lg ${statusColor[gap.status as keyof typeof statusColor]}`}>
          <Icon className="w-5 h-5" />
        </div>
        <div className="flex-1">
          <h4 className="font-semibold">{gap.competency}</h4>
          <p className="text-sm text-gray-600 mt-1">{gap.reason}</p>
          <p className="text-sm text-blue-600 mt-2">
            <Target className="w-4 h-4 inline mr-1" />
            {gap.recommendation}
          </p>
        </div>
      </div>
    </div>
  );
};

// Decision brief display component
const DecisionBriefDisplay: React.FC<{
  brief: DecisionBrief;
}> = ({ brief }) => {
  const content = brief.content;

  return (
    <div className="space-y-6">
      {/* Header with candidate info */}
      <div className="flex items-center justify-between">
        <div>
          <h2 className="text-2xl font-bold">{content.candidate.name}</h2>
          <p className="text-gray-600">{content.candidate.role_applied}</p>
        </div>
        <div className="text-right">
          <p className="text-sm text-gray-500">
            Generated {new Date(content.generated_at).toLocaleDateString()}
          </p>
          {content.processing_time_ms && (
            <p className="text-xs text-gray-400">
              Processing time: {content.processing_time_ms}ms
            </p>
          )}
        </div>
      </div>

      {/* Stats Overview */}
      <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
        <Card>
          <CardContent className="p-4 text-center">
            <div className={`text-3xl font-bold ${getScoreColor(content.candidate.overall_score)} px-4 py-2 rounded-lg inline-block`}>
              {content.candidate.overall_score.toFixed(1)}
            </div>
            <p className="text-sm text-gray-500 mt-2">Overall Score</p>
          </CardContent>
        </Card>
        <Card>
          <CardContent className="p-4 text-center">
            <p className="text-3xl font-bold">{content.candidate.total_evaluations}</p>
            <p className="text-sm text-gray-500 mt-2">Evaluations</p>
          </CardContent>
        </Card>
        <Card>
          <CardContent className="p-4 text-center">
            <div className={`text-lg font-bold px-3 py-1 rounded-lg inline-block ${getDecisionColor(content.suggested_decision.decision)}`}>
              {content.suggested_decision.decision.replace("_", " ")}
            </div>
            <p className="text-sm text-gray-500 mt-2">Suggested Decision</p>
          </CardContent>
        </Card>
        <Card>
          <CardContent className="p-4 text-center">
            <div className={`w-12 h-12 rounded-full flex items-center justify-center mx-auto ${getSignalStrengthColor(content.interview_agreement.level.replace("strong_", "").replace("moderate_", "").replace("mixed_", "").replace("conflicting_", ""))}`}>
              <Brain className="w-6 h-6 text-white" />
            </div>
            <p className="text-sm text-gray-500 mt-2">
              {content.interview_agreement.evaluator_count} Evaluators
            </p>
          </CardContent>
        </Card>
      </div>

      <Separator />

      {/* Suggested Decision */}
      <Card className="border-2 border-primary/20">
        <CardHeader>
          <CardTitle className="flex items-center gap-2">
            <Sparkles className="w-5 h-5 text-primary" />
            AI Recommendation
          </CardTitle>
        </CardHeader>
        <CardContent>
          <div className="flex items-center justify-between mb-4">
            <div className={`text-2xl font-bold px-4 py-2 rounded-lg ${getDecisionColor(content.suggested_decision.decision)}`}>
              {content.suggested_decision.decision.replace("_", " ").toUpperCase()}
            </div>
            <div className="text-right">
              <p className="text-sm text-gray-500">Confidence</p>
              <p className="text-2xl font-bold">{(content.suggested_decision.confidence * 100).toFixed(0)}%</p>
            </div>
          </div>
          <p className="text-gray-700">{content.suggested_decision.reasoning}</p>
          
          {content.suggested_decision.key_factors.length > 0 && (
            <div className="mt-4">
              <h4 className="font-semibold mb-2">Key Factors:</h4>
              <ul className="list-disc list-inside space-y-1">
                {content.suggested_decision.key_factors.map((factor, idx) => (
                  <li key={idx} className="text-sm text-gray-600">{factor}</li>
                ))}
              </ul>
            </div>
          )}
          
          {content.suggested_decision.next_steps.length > 0 && (
            <div className="mt-4 p-4 bg-blue-50 rounded-lg">
              <h4 className="font-semibold text-blue-800 mb-2">Recommended Next Steps:</h4>
              <ul className="space-y-1">
                {content.suggested_decision.next_steps.map((step, idx) => (
                  <li key={idx} className="text-sm text-blue-700 flex items-center gap-2">
                    <ArrowRight className="w-4 h-4" />
                    {step}
                  </li>
                ))}
              </ul>
            </div>
          )}
        </CardContent>
      </Card>

      {/* Interview Agreement */}
      <Card>
        <CardHeader>
          <CardTitle className="flex items-center gap-2">
            <Users className="w-5 h-5" />
            Interview Agreement
          </CardTitle>
          <CardDescription>
            How well do interviewers agree on this candidate?
          </CardDescription>
        </CardHeader>
        <CardContent>
          <div className="flex items-center justify-between mb-4">
            <Badge className={getDecisionColor(content.interview_agreement.level.replace("_", " "))}>
              {content.interview_agreement.level.replace("_", " ")}
            </Badge>
            <p className="text-sm text-gray-500">
              Confidence Score: {(content.interview_agreement.confidence_score * 100).toFixed(0)}%
            </p>
          </div>
          <p className="text-gray-700">{content.interview_agreement.description}</p>
          
          {content.interview_agreement.agreements.length > 0 && (
            <div className="mt-4">
              <h4 className="font-semibold text-green-700 mb-2 flex items-center gap-2">
                <CheckCircle className="w-4 h-4" /> Areas of Agreement
              </h4>
              <div className="flex flex-wrap gap-2">
                {content.interview_agreement.agreements.map((ag, idx) => (
                  <Badge key={idx} variant="outline" className="bg-green-50">
                    {ag}
                  </Badge>
                ))}
              </div>
            </div>
          )}
          
          {content.interview_agreement.disagreements.length > 0 && (
            <div className="mt-4">
              <h4 className="font-semibold text-orange-700 mb-2 flex items-center gap-2">
                <AlertTriangle className="w-4 h-4" /> Areas of Disagreement
              </h4>
              <div className="flex flex-wrap gap-2">
                {content.interview_agreement.disagreements.map((dis, idx) => (
                  <Badge key={idx} variant="outline" className="bg-orange-50">
                    {dis}
                  </Badge>
                ))}
              </div>
            </div>
          )}
        </CardContent>
      </Card>

      <Separator />

      {/* Strengths */}
      {content.strengths.length > 0 && (
        <div>
          <h3 className="text-xl font-bold mb-4 flex items-center gap-2">
            <ThumbsUp className="w-6 h-6 text-green-600" />
            Candidate Strengths
          </h3>
          <div className="space-y-3">
            {content.strengths.map((strength, idx) => (
              <StrengthItem key={idx} strength={strength} />
            ))}
          </div>
        </div>
      )}

      {/* Risk Areas */}
      {content.risk_areas.length > 0 && (
        <div>
          <h3 className="text-xl font-bold mb-4 flex items-center gap-2">
            <AlertTriangle className="w-6 h-6 text-red-600" />
            Risk Areas
          </h3>
          <div className="space-y-3">
            {content.risk_areas.map((risk, idx) => (
              <RiskAreaItem key={idx} risk={risk} />
            ))}
          </div>
        </div>
      )}

      {/* Signal Gaps */}
      {content.signal_gaps.length > 0 && (
        <div>
          <h3 className="text-xl font-bold mb-4 flex items-center gap-2">
            <Brain className="w-6 h-6 text-purple-600" />
            Signal Gaps
          </h3>
          <p className="text-sm text-gray-600 mb-4">
            Areas where we need more information to make a confident decision
          </p>
          <div className="space-y-3">
            {content.signal_gaps.map((gap, idx) => (
              <SignalGapItem key={idx} gap={gap} />
            ))}
          </div>
        </div>
      )}
    </div>
  );
};

// Main page component
export default function DecisionsPage() {
  const [organizationId, setOrganizationId] = useState("");
  const [roleId, setRoleId] = useState("");
  const [selectedCandidateId, setSelectedCandidateId] = useState<string | null>(null);
  const [generatedBrief, setGeneratedBrief] = useState<DecisionBrief | null>(null);
  const [mounted, setMounted] = useState(false);

  React.useEffect(() => {
    setMounted(true);
  }, []);

  const {
    data: candidatesData,
    isLoading: loadingCandidates,
    refetch: refetchCandidates
  } = useComparableCandidates({
    organizationId,
    roleId,
    minEvaluations: 1,
  });

  const {
    mutate: generateBrief,
    isPending: generatingBrief,
  } = useGenerateDecisionBrief();

  const handleGenerateBrief = () => {
    if (!selectedCandidateId || !organizationId) return;

    generateBrief(
      {
        candidateId: selectedCandidateId,
        organizationId,
      },
      {
        onSuccess: (data) => {
          setGeneratedBrief(data);
        },
        onError: (error) => {
          console.error("Failed to generate brief:", error);
        },
      }
    );
  };

  if (!mounted) {
    return null;
  }

  return (
    <div className="container mx-auto py-8 px-4">
      {/* Header */}
      <div className="mb-8">
        <h1 className="text-3xl font-bold flex items-center gap-3">
          <FileText className="w-8 h-8" />
          Decision Brief Generator
        </h1>
        <p className="text-gray-600 mt-1">
          Generate AI-powered hiring decision briefs for candidates with sufficient evaluations
        </p>
      </div>

      {/* Input Section */}
      <Card className="mb-6">
        <CardHeader>
          <CardTitle>Configuration</CardTitle>
          <CardDescription>
            Enter your organization ID to load candidates with evaluations
          </CardDescription>
        </CardHeader>
        <CardContent>
          <div className="flex gap-4">
            <div className="flex-1">
              <label className="text-sm font-medium mb-2 block">Organization ID</label>
              <Input
                placeholder="Enter organization ID..."
                value={organizationId}
                onChange={(e) => setOrganizationId(e.target.value)}
              />
            </div>
            <div className="flex-1">
              <label className="text-sm font-medium mb-2 block">Role ID (Optional)</label>
              <Input
                placeholder="Filter by role..."
                value={roleId}
                onChange={(e) => setRoleId(e.target.value)}
              />
            </div>
            <div className="flex items-end">
              <Button variant="outline" onClick={() => refetchCandidates()}>
                <RefreshCw className="w-4 h-4 mr-2" />
                Load Candidates
              </Button>
            </div>
          </div>
        </CardContent>
      </Card>

      {/* Candidate Selection */}
      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        {/* Candidates List */}
        <div className="lg:col-span-1">
          <Card>
            <CardHeader>
              <CardTitle className="flex items-center gap-2">
                <Users className="w-5 h-5" />
                Candidates
              </CardTitle>
              <CardDescription>
                Select a candidate to generate a decision brief
              </CardDescription>
            </CardHeader>
            <CardContent>
              {loadingCandidates ? (
                <div className="space-y-3">
                  {[1, 2, 3].map((i) => (
                    <div key={i} className="h-24 bg-gray-100 rounded-lg animate-pulse" />
                  ))}
                </div>
              ) : candidatesData?.candidates && candidatesData.candidates.length > 0 ? (
                <div className="space-y-3">
                  {candidatesData.candidates.map((candidate) => (
                    <CandidateCard
                      key={candidate.id}
                      candidate={candidate}
                      isSelected={selectedCandidateId === candidate.id}
                      onSelect={() => {
                        setSelectedCandidateId(candidate.id);
                        setGeneratedBrief(null);
                      }}
                    />
                  ))}
                  {candidatesData.total > candidatesData.candidates.length && (
                    <p className="text-sm text-gray-500 text-center mt-4">
                      + {candidatesData.total - candidatesData.candidates.length} more candidates
                    </p>
                  )}
                </div>
              ) : (
                <div className="text-center py-8">
                  <Users className="w-12 h-12 text-gray-300 mx-auto mb-4" />
                  <p className="text-gray-500">
                    {organizationId
                      ? "No candidates with evaluations found"
                      : "Enter organization ID to load candidates"}
                  </p>
                </div>
              )}
            </CardContent>
          </Card>
        </div>

        {/* Decision Brief Display */}
        <div className="lg:col-span-2">
          {selectedCandidateId ? (
            <Card>
              <CardHeader>
                <CardTitle className="flex items-center justify-between">
                  <span className="flex items-center gap-2">
                    <FileText className="w-5 h-5" />
                    Decision Brief
                  </span>
                  {generatedBrief && (
                    <Badge variant="outline" className="bg-green-50">
                      Generated
                    </Badge>
                  )}
                </CardTitle>
                <CardDescription>
                  {generatedBrief
                    ? "Review the AI-generated decision brief below"
                    : "Click generate to create a decision brief for this candidate"}
                </CardDescription>
              </CardHeader>
              <CardContent>
                {!organizationId ? (
                  <div className="text-center py-8">
                    <AlertCircle className="w-12 h-12 text-yellow-500 mx-auto mb-4" />
                    <p className="text-gray-500">Enter organization ID to generate briefs</p>
                  </div>
                ) : generatingBrief ? (
                  <div className="text-center py-8">
                    <div className="animate-spin w-12 h-12 border-4 border-primary border-t-transparent rounded-full mx-auto mb-4" />
                    <p className="text-gray-500">Generating decision brief...</p>
                    <p className="text-sm text-gray-400 mt-2">
                      This may take a few seconds
                    </p>
                  </div>
                ) : generatedBrief ? (
                  <DecisionBriefDisplay brief={generatedBrief} />
                ) : (
                  <div className="text-center py-12">
                    <Sparkles className="w-16 h-16 text-gray-300 mx-auto mb-4" />
                    <h3 className="text-xl font-semibold mb-2">Ready to Generate</h3>
                    <p className="text-gray-500 mb-6">
                      Click the button below to generate a comprehensive decision brief
                    </p>
                    <Button size="lg" onClick={handleGenerateBrief}>
                      <Sparkles className="w-5 h-5 mr-2" />
                      Generate Decision Brief
                    </Button>
                  </div>
                )}
              </CardContent>
            </Card>
          ) : (
            <Card>
              <CardContent className="py-12 text-center">
                <FileText className="w-16 h-16 text-gray-300 mx-auto mb-4" />
                <h3 className="text-xl font-semibold mb-2">Select a Candidate</h3>
                <p className="text-gray-500">
                  Choose a candidate from the list to generate their decision brief
                </p>
              </CardContent>
            </Card>
          )}
        </div>
      </div>

      {/* Info Section */}
      <Card className="mt-6 bg-blue-50 border-blue-200">
        <CardContent className="p-6">
          <h3 className="font-semibold text-blue-800 mb-2 flex items-center gap-2">
            <Info className="w-5 h-5" />
            How Decision Briefs Work
          </h3>
          <div className="grid grid-cols-1 md:grid-cols-3 gap-4 text-sm text-blue-700">
            <div>
              <h4 className="font-medium">1. AI Analysis</h4>
              <p className="text-blue-600 mt-1">
                Our AI analyzes all submitted evaluations, scores, and feedback for the candidate
              </p>
            </div>
            <div>
              <h4 className="font-medium">2. Comprehensive Review</h4>
              <p className="text-blue-600 mt-1">
                Identifies strengths, risk areas, signal gaps, and interview agreement levels
              </p>
            </div>
            <div>
              <h4 className="font-medium">3. Smart Recommendation</h4>
              <p className="text-blue-600 mt-1">
                Provides evidence-based hiring recommendation with confidence score
              </p>
            </div>
          </div>
        </CardContent>
      </Card>
    </div>
  );
}

