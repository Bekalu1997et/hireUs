"use client";

import React, { useState } from "react";
import Link from "next/link";
import { useQuery } from "@tanstack/react-query";
import { comparisonApi } from "@/lib/api";
import { Button } from "@/components/ui/button";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import { Select } from "@/components/ui/select";
import { Input } from "@/components/ui/input";
import {
  Users, BarChart3, TrendingUp, AlertTriangle,
  CheckCircle, Search, ArrowRight, Trophy,
  Target, Brain, Zap
} from "lucide-react";
import {
  useCompareCandidates,
  useSignalGaps,
  useComparableCandidates,
  useComparisonSelection,
  ComparisonResponse,
  CandidateSummary,
  CandidateScoreSummary,
  CompetencyComparison,
} from "@/hooks/use-comparison";

// Helper function to get score color
const getScoreColor = (score: number): string => {
  if (score >= 4.5) return "bg-green-500";
  if (score >= 3.5) return "bg-blue-500";
  if (score >= 2.5) return "bg-yellow-500";
  if (score >= 1.5) return "bg-orange-500";
  return "bg-red-500";
};

// Score badge component
const ScoreBadge: React.FC<{ score: number; label?: string }> = ({ score, label }) => (
  <div className="flex flex-col items-center">
    <div className={`w-14 h-14 rounded-full flex items-center justify-center text-white text-xl font-bold ${getScoreColor(score)}`}>
      {score.toFixed(1)}
    </div>
    {label && <span className="text-xs text-gray-500 mt-1">{label}</span>}
  </div>
);

// Competency heatmap cell
const HeatmapCell: React.FC<{ score: number }> = ({ score }) => {
  return (
    <div
      className={`w-full h-12 flex items-center justify-center rounded text-sm font-medium transition-all ${getScoreColor(score)}`}
      style={{ opacity: Math.max(score / 5, 0.3) }}
    >
      {score.toFixed(1)}
    </div>
  );
};

// Signal gap item component
const SignalGapItem: React.FC<{ candidateId: string }> = ({ candidateId }) => {
  const { data: signalGaps } = useSignalGaps({ candidate_id: candidateId });

  if (!signalGaps) {
    return <div className="animate-pulse h-20 bg-gray-100 rounded" />;
  }

  return (
    <div className="border rounded-lg p-4">
      <div className="flex items-center justify-between mb-3">
        <Badge
          className={
            signalGaps.overall_signal_strength === "strong" ? "bg-green-100 text-green-800" :
            signalGaps.overall_signal_strength === "moderate" ? "bg-yellow-100 text-yellow-800" :
            signalGaps.overall_signal_strength === "weak" ? "bg-orange-100 text-orange-800" :
            "bg-gray-100 text-gray-800"
          }
        >
          {signalGaps.overall_signal_strength || "Unknown"} signal
        </Badge>
      </div>

      {signalGaps.has_gaps ? (
        <div className="space-y-2">
          {signalGaps.signal_gaps.map((gap, idx) => (
            <div key={idx} className="flex items-start gap-2 text-sm">
              <AlertTriangle className={`w-4 h-4 mt-0.5 flex-shrink-0 ${
                gap.severity === "high" ? "text-red-500" :
                gap.severity === "medium" ? "text-yellow-500" :
                "text-blue-500"
              }`} />
              <div>
                <p className="font-medium">{gap.competency}</p>
                <p className="text-gray-600">{gap.recommendation}</p>
              </div>
            </div>
          ))}
        </div>
      ) : (
        <p className="text-sm text-green-600 flex items-center gap-2">
          <CheckCircle className="w-4 h-4" />
          No signal gaps detected
        </p>
      )}
    </div>
  );
};

// Signal gaps panel component
const SignalGapsPanel: React.FC<{
  candidates: CandidateSummary[];
}> = ({ candidates }) => {
  return (
    <Card>
      <CardHeader>
        <CardTitle className="flex items-center gap-2">
          <Brain className="w-5 h-5" />
          Signal Analysis
        </CardTitle>
      </CardHeader>
      <CardContent>
        <div className="space-y-4">
          {candidates.map(candidate => (
            <SignalGapItem key={candidate.id} candidateId={candidate.id} />
          ))}
        </div>
      </CardContent>
    </Card>
  );
};

// Candidate card component
const CandidateCard: React.FC<{
  candidate: CandidateSummary;
  isSelected: boolean;
  onToggle: () => void;
}> = ({ candidate, isSelected, onToggle }) => {
  return (
    <Card
      className={`cursor-pointer transition-all hover:shadow-lg ${
        isSelected ? "ring-2 ring-blue-500 shadow-lg" : "hover:border-blue-300"
      }`}
      onClick={onToggle}
    >
      <CardContent className="p-4">
        <div className="flex items-start justify-between mb-4">
          <div>
            <h3 className="font-semibold text-lg">{candidate.name}</h3>
            <p className="text-sm text-gray-500">{candidate.email}</p>
            <Badge variant="outline" className="mt-2">{candidate.status}</Badge>
          </div>
          {isSelected && (
            <CheckCircle className="w-6 h-6 text-blue-500" />
          )}
        </div>
      </CardContent>
    </Card>
  );
};

// Comparison table component
const ComparisonTable: React.FC<{
  comparison: ComparisonResponse;
}> = ({ comparison }) => {
  if (!comparison.competency_comparisons.length) {
    return (
      <Card>
        <CardContent className="p-8 text-center">
          <BarChart3 className="w-12 h-12 text-gray-300 mx-auto mb-4" />
          <p className="text-gray-500">No competency data available for comparison</p>
        </CardContent>
      </Card>
    );
  }

  return (
    <Card>
      <CardHeader>
        <CardTitle className="flex items-center gap-2">
          <Target className="w-5 h-5" />
          Competency Comparison
        </CardTitle>
      </CardHeader>
      <CardContent>
        <div className="overflow-x-auto">
          <table className="w-full">
            <thead>
              <tr className="border-b">
                <th className="text-left p-3 font-medium text-gray-600">Competency</th>
                {comparison.candidates.map(c => (
                  <th key={c.id} className="text-center p-3 font-medium text-gray-600 min-w-[100px]">
                    {c.name}
                  </th>
                ))}
                <th className="text-center p-3 font-medium text-gray-600">Avg</th>
                <th className="text-center p-3 font-medium text-gray-600">Std Dev</th>
              </tr>
            </thead>
            <tbody>
              {comparison.competency_comparisons.map(comp => (
                <tr key={comp.competency} className="border-b last:border-0">
                  <td className="p-3 font-medium">{comp.competency}</td>
                  {comparison.candidates.map(c => {
                    const score = comp.scores[c.id] || 0;
                    return (
                      <td key={c.id} className="p-2">
                        <HeatmapCell score={score} />
                      </td>
                    );
                  })}
                  <td className="p-3 text-center">
                    <span className="font-semibold">{comp.average.toFixed(1)}</span>
                  </td>
                  <td className="p-3 text-center text-gray-500">
                    {comp.std_deviation?.toFixed(2) || "-"}
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      </CardContent>
    </Card>
  );
};

// Rankings card component
const RankingsCard: React.FC<{
  rankings: ComparisonResponse["rankings"];
  candidates: CandidateSummary[];
}> = ({ rankings, candidates }) => {
  const [criteria, setCriteria] = useState<"by_overall_score" | "by_confidence">("by_overall_score");

  const rankingList = rankings[criteria];
  const candidateMap = new Map(candidates.map(c => [c.id, c]));

  const getRankColor = (rank: number): string => {
    if (rank === 1) return "bg-yellow-400 text-yellow-900";
    if (rank === 2) return "bg-gray-300 text-gray-700";
    if (rank === 3) return "bg-orange-300 text-orange-900";
    return "bg-gray-200 text-gray-600";
  };

  return (
    <Card>
      <CardHeader>
        <div className="flex items-center justify-between">
          <CardTitle className="flex items-center gap-2">
            <Trophy className="w-5 h-5" />
            Rankings
          </CardTitle>
          <Select
            options={[
              { value: "by_overall_score", label: "Overall Score" },
              { value: "by_confidence", label: "Confidence" },
            ]}
            value={criteria}
            onChange={(e) => setCriteria(e.target.value as typeof criteria)}
            className="w-40"
          />
        </div>
      </CardHeader>
      <CardContent>
        <div className="space-y-3">
          {rankingList.slice(0, 5).map((item) => {
            const candidate = candidateMap.get(item.candidate_id);
            return (
              <div
                key={item.candidate_id}
                className="flex items-center gap-4 p-3 rounded-lg bg-gray-50"
              >
                <div className={`w-8 h-8 rounded-full flex items-center justify-center font-bold ${getRankColor(item.rank)}`}>
                  {item.rank}
                </div>
                <div className="flex-1">
                  <p className="font-medium">{candidate?.name || "Unknown"}</p>
                  <p className="text-sm text-gray-500">{candidate?.status}</p>
                </div>
                <ScoreBadge score={item.score} />
              </div>
            );
          })}
        </div>
      </CardContent>
    </Card>
  );
};

// Main page component
export default function ComparisonPage() {
  const [roleId, setRoleId] = useState("");
  const [mounted, setMounted] = useState(false);

  React.useEffect(() => {
    setMounted(true);
  }, []);

  const {
    selectedIds,
    toggleCandidate,
    isSelected,
    count,
    hasMinimum,
    clearSelection,
    selectAll
  } = useComparisonSelection();

  const { data: roleCandidates, isLoading: loadingCandidates } = useComparableCandidates({
    roleId,
    minEvaluations: 1,
  });

  const {
    data: comparison,
    isLoading: loadingComparison,
    refetch: refetchComparison
  } = useCompareCandidates({
    candidate_ids: selectedIds,
    include_evaluations: true,
    include_feedback_summary: true,
  });

  const handleCompare = () => {
    if (selectedIds.length >= 2) {
      refetchComparison();
    }
  };

  if (!mounted) {
    return null;
  }

  return (
    <div className="container mx-auto py-8 px-4">
      {/* Header */}
      <div className="mb-8">
        <h1 className="text-3xl font-bold">Candidate Comparison</h1>
        <p className="text-gray-600 mt-1">
          Compare candidates side-by-side with detailed score analysis
        </p>
      </div>

      {/* Selection Panel */}
      <Card className="mb-6">
        <CardHeader>
          <CardTitle className="flex items-center gap-2">
            <Users className="w-5 h-5" />
            Select Candidates
          </CardTitle>
        </CardHeader>
        <CardContent>
          <div className="flex gap-4 mb-4">
            <div className="flex-1">
              <Input
                placeholder="Enter role ID to load candidates..."
                value={roleId}
                onChange={(e) => setRoleId(e.target.value)}
              />
            </div>
            {roleCandidates?.candidates && (
              <Button
                variant="outline"
                onClick={() => selectAll(roleCandidates.candidates.map(c => c.id))}
              >
                Select All ({roleCandidates.count})
              </Button>
            )}
            {selectedIds.length > 0 && (
              <Button variant="outline" onClick={clearSelection}>
                Clear ({count})
              </Button>
            )}
          </div>

          {loadingCandidates ? (
            <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
              {[1, 2, 3].map(i => (
                <div key={i} className="h-48 bg-gray-100 rounded-lg animate-pulse" />
              ))}
            </div>
          ) : roleCandidates?.candidates && roleCandidates.candidates.length > 0 ? (
            <>
              <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
                {roleCandidates.candidates.map(candidate => (
                  <CandidateCard
                    key={candidate.id}
                    candidate={candidate}
                    isSelected={isSelected(candidate.id)}
                    onToggle={() => toggleCandidate(candidate.id)}
                  />
                ))}
              </div>

              {selectedIds.length >= 2 && (
                <div className="mt-6 flex justify-center">
                  <Button size="lg" onClick={handleCompare}>
                    <BarChart3 className="w-5 h-5 mr-2" />
                    Compare {selectedIds.length} Candidates
                  </Button>
                </div>
              )}
            </>
          ) : (
            <div className="text-center py-12">
              <Users className="w-12 h-12 text-gray-300 mx-auto mb-4" />
              <h3 className="text-xl font-semibold mb-2">No Candidates Found</h3>
              <p className="text-gray-600">
                Enter a role ID to load candidates with evaluations
              </p>
            </div>
          )}
        </CardContent>
      </Card>

      {/* Comparison Results */}
      {loadingComparison ? (
        <div className="space-y-6">
          <Card>
            <CardContent className="p-8">
              <div className="animate-pulse space-y-4">
                <div className="h-8 bg-gray-200 rounded w-1/4" />
                <div className="h-64 bg-gray-100 rounded" />
              </div>
            </CardContent>
          </Card>
        </div>
      ) : comparison ? (
        <div className="space-y-6">
          {/* Summary Stats */}
          <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
            <Card>
              <CardContent className="p-4 flex items-center gap-3">
                <Users className="w-8 h-8 text-blue-500" />
                <div>
                  <p className="text-2xl font-bold">{comparison.candidates_compared}</p>
                  <p className="text-xs text-gray-500">Candidates</p>
                </div>
              </CardContent>
            </Card>
            <Card>
              <CardContent className="p-4 flex items-center gap-3">
                <TrendingUp className="w-8 h-8 text-green-500" />
                <div>
                  <p className="text-2xl font-bold">
                    {comparison.competency_comparisons.length}
                  </p>
                  <p className="text-xs text-gray-500">Competencies</p>
                </div>
              </CardContent>
            </Card>
            <Card>
              <CardContent className="p-4 flex items-center gap-3">
                <Zap className="w-8 h-8 text-yellow-500" />
                <div>
                  <p className="text-2xl font-bold">
                    {comparison.rankings.by_overall_score[0]?.score.toFixed(1) || "-"}
                  </p>
                  <p className="text-xs text-gray-500">Top Score</p>
                </div>
              </CardContent>
            </Card>
            <Card>
              <CardContent className="p-4 flex items-center gap-3">
                <Brain className="w-8 h-8 text-purple-500" />
                <div>
                  <p className="text-2xl font-bold">
                    {comparison.feedback_summary?.strengths_count || "0"}
                  </p>
                  <p className="text-xs text-gray-500">Feedback Items</p>
                </div>
              </CardContent>
            </Card>
          </div>

          {/* Comparison Table */}
          <ComparisonTable comparison={comparison} />

          {/* Rankings */}
          <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
            <RankingsCard
              rankings={comparison.rankings}
              candidates={comparison.candidates}
            />
            <SignalGapsPanel candidates={comparison.candidates} />
          </div>

          {/* Feedback Summary */}
          {comparison.feedback_summary && (
            <Card>
              <CardHeader>
                <CardTitle className="flex items-center gap-2">
                  <Target className="w-5 h-5" />
                  Feedback Summary
                </CardTitle>
              </CardHeader>
              <CardContent>
                <p className="text-gray-700">{comparison.feedback_summary.overall}</p>
              </CardContent>
            </Card>
          )}
        </div>
      ) : null}
    </div>
  );
}

