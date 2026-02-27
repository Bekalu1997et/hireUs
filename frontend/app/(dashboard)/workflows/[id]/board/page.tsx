"use client";

import React, { useState } from "react";
import Link from "next/link";
import { useParams, useRouter } from "next/navigation";
import { useQuery, useMutation, useQueryClient } from "@tanstack/react-query";
import { Button } from "@/components/ui/button";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import {
  ArrowLeft,
  Plus,
  MoreHorizontal,
  ChevronRight,
  AlertCircle,
  CheckCircle,
  Calendar,
} from "lucide-react";
import { useWorkflow, useMoveCandidate, useValidateCandidateMove } from "@/hooks/use-workflows";

// Types for the Kanban board
interface Stage {
  id: string;
  name: string;
  order: number;
  description?: string;
  color: string;
  required_feedback_count: number;
}

interface Candidate {
  id: string;
  full_name: string;
  email: string;
  current_stage_id?: string;
  current_stage_name?: string;
  status: string;
  created_at: string;
}

interface CandidateWithFeedback extends Candidate {
  feedback_submitted_count: number;
  feedback_required_count: number;
}

interface WorkflowBoardPageProps {
  workflowId: string;
  stages: Stage[];
  candidates: CandidateWithFeedback[];
}

export default function WorkflowBoardPage() {
  const params = useParams();
  const router = useRouter();
  const queryClient = useQueryClient();
  const workflowId = params.id as string;

  const [selectedCandidate, setSelectedCandidate] = useState<CandidateWithFeedback | null>(null);
  const [targetStage, setTargetStage] = useState<string | null>(null);

  const { data: workflow, isLoading } = useWorkflow(workflowId);
  const moveCandidateMutation = useMoveCandidate();
  const validateMoveMutation = useValidateCandidateMove();

  // Demo candidates for display (in real app, these would come from the API)
  const [candidates, setCandidates] = useState<CandidateWithFeedback[]>([
    {
      id: "cand-1",
      full_name: "Alice Johnson",
      email: "alice@example.com",
      current_stage_id: "applied",
      current_stage_name: "Applied",
      status: "active",
      created_at: new Date().toISOString(),
      feedback_submitted_count: 0,
      feedback_required_count: 0,
    },
    {
      id: "cand-2",
      full_name: "Bob Smith",
      email: "bob@example.com",
      current_stage_id: "screening",
      current_stage_name: "Screening",
      status: "active",
      created_at: new Date().toISOString(),
      feedback_submitted_count: 0,
      feedback_required_count: 1,
    },
    {
      id: "cand-3",
      full_name: "Carol Williams",
      email: "carol@example.com",
      current_stage_id: "technical_1",
      current_stage_name: "Technical 1",
      status: "active",
      created_at: new Date().toISOString(),
      feedback_submitted_count: 1,
      feedback_required_count: 1,
    },
    {
      id: "cand-4",
      full_name: "David Brown",
      email: "david@example.com",
      current_stage_id: "decision",
      current_stage_name: "Decision",
      status: "active",
      created_at: new Date().toISOString(),
      feedback_submitted_count: 2,
      feedback_required_count: 2,
    },
  ]);

  const getCandidatesByStage = (stageId: string) => {
    return candidates.filter((c) => c.current_stage_id === stageId);
  };

  const handleMoveCandidate = async (candidate: CandidateWithFeedback, toStageId: string) => {
    const targetStage = workflow?.stages.find((s) => s.id === toStageId);

    // Check if move is allowed (feedback validation)
    if (candidate.feedback_required_count > candidate.feedback_submitted_count) {
      const proceed = window.confirm(
        `This candidate has incomplete feedback (${candidate.feedback_submitted_count}/${candidate.feedback_required_count}). ` +
        "Are you sure you want to move them anyway?"
      );
      if (!proceed) return;
    }

    // Update local state
    setCandidates((prev) =>
      prev.map((c) =>
        c.id === candidate.id
          ? {
              ...c,
              current_stage_id: toStageId,
              current_stage_name: targetStage?.name || toStageId,
            }
          : c
      )
    );

    // Call API (commented out for demo)
    // await moveCandidateMutation.mutateAsync({
    //   candidate_id: candidate.id,
    //   to_stage_id: toStageId,
    // });

    setSelectedCandidate(null);
  };

  const getInitials = (name: string) => {
    return name
      .split(" ")
      .map((n) => n[0])
      .join("")
      .toUpperCase()
      .slice(0, 2);
  };

  const getStageColor = (color: string) => {
    return color || "#6366f1";
  };

  if (isLoading) {
    return (
      <div className="container mx-auto py-8 px-4">
        <div className="flex items-center gap-4 mb-8">
          <Link href="/workflows">
            <Button variant="ghost" size="sm">
              <ArrowLeft className="w-4 h-4 mr-2" />
              Back
            </Button>
          </Link>
        </div>
        <div className="flex gap-4 overflow-x-auto pb-4">
          {[1, 2, 3, 4, 5].map((i) => (
            <div key={i} className="w-80 flex-shrink-0">
              <Card className="animate-pulse">
                <CardHeader>
                  <div className="h-6 bg-gray-200 rounded w-1/2" />
                </CardHeader>
                <CardContent className="space-y-3">
                  {[1, 2, 3].map((j) => (
                    <div key={j} className="h-24 bg-gray-200 rounded" />
                  ))}
                </CardContent>
              </Card>
            </div>
          ))}
        </div>
      </div>
    );
  }

  if (!workflow) {
    return (
      <div className="container mx-auto py-8 px-4">
        <Card className="bg-red-50 dark:bg-red-900/20">
          <CardContent className="p-6 text-center">
            <p className="text-red-600 dark:text-red-400">
              Failed to load workflow. Please try again.
            </p>
            <Link href="/workflows">
              <Button variant="outline" className="mt-4">
                <ArrowLeft className="w-4 h-4 mr-2" />
                Back to Workflows
              </Button>
            </Link>
          </CardContent>
        </Card>
      </div>
    );
  }

  const stages = workflow.stages || [];

  return (
    <div className="h-[calc(100vh-64px)] flex flex-col">
      {/* Header */}
      <div className="border-b bg-white dark:bg-gray-900 px-6 py-4">
        <div className="flex items-center justify-between">
          <div className="flex items-center gap-4">
            <Link href={`/workflows/${workflowId}`}>
              <Button variant="ghost" size="sm">
                <ArrowLeft className="w-4 h-4 mr-2" />
                Back
              </Button>
            </Link>
            <div>
              <h1 className="text-xl font-bold">{workflow.name}</h1>
              <p className="text-sm text-gray-500">
                {candidates.length} candidates in pipeline
              </p>
            </div>
          </div>
          <div className="flex items-center gap-2">
            <Button variant="outline" size="sm">
              <Calendar className="w-4 h-4 mr-2" />
              Schedule Interview
            </Button>
            <Link href="/candidates">
              <Button size="sm">
                <Plus className="w-4 h-4 mr-2" />
                Add Candidate
              </Button>
            </Link>
          </div>
        </div>
      </div>

      {/* Kanban Board */}
      <div className="flex-1 overflow-x-auto p-6 bg-gray-50 dark:bg-gray-950">
        <div className="flex gap-4 h-full">
          {stages.map((stage) => {
            const stageCandidates = getCandidatesByStage(stage.id);
            const color = getStageColor(stage.color);

            return (
              <div
                key={stage.id}
                className="w-80 flex-shrink-0 flex flex-col h-full"
              >
                {/* Stage Header */}
                <div
                  className="px-4 py-3 rounded-t-lg border-x border-t"
                  style={{
                    backgroundColor: `${color}10`,
                    borderColor: `${color}30`,
                  }}
                >
                  <div className="flex items-center justify-between">
                    <div className="flex items-center gap-2">
                      <div
                        className="w-3 h-3 rounded-full"
                        style={{ backgroundColor: color }}
                      />
                      <h3 className="font-semibold">{stage.name}</h3>
                      <Badge variant="secondary" className="text-xs">
                        {stageCandidates.length}
                      </Badge>
                    </div>
                    <Button variant="ghost" size="sm" className="h-8 w-8 p-0">
                      <MoreHorizontal className="w-4 h-4" />
                    </Button>
                  </div>
                  {stage.required_feedback_count > 0 && (
                    <p className="text-xs text-gray-500 mt-1">
                      {stage.required_feedback_count} feedback(s) required
                    </p>
                  )}
                </div>

                {/* Candidates List */}
                <div
                  className="flex-1 overflow-y-auto border-x border-b rounded-b-lg p-2 space-y-2"
                  style={{ borderColor: `${color}30` }}
                  onDragOver={(e) => e.preventDefault()}
                  onDrop={(e) => {
                    e.preventDefault();
                    if (selectedCandidate) {
                      handleMoveCandidate(selectedCandidate, stage.id);
                    }
                  }}
                >
                  {stageCandidates.length === 0 ? (
                    <div className="text-center py-8 text-gray-400 text-sm">
                      <p>No candidates</p>
                      <p className="text-xs">Drag candidates here or add new</p>
                    </div>
                  ) : (
                    stageCandidates.map((candidate) => (
                      <Card
                        key={candidate.id}
                        className={`cursor-pointer transition-all hover:shadow-md ${
                          selectedCandidate?.id === candidate.id
                            ? "ring-2 ring-blue-500"
                            : ""
                        }`}
                        draggable
                        onDragStart={() => setSelectedCandidate(candidate)}
                        onClick={() => setSelectedCandidate(candidate)}
                      >
                        <CardContent className="p-3">
                          <div className="flex items-start justify-between mb-2">
                            <div className="flex items-center gap-2">
                              <div className="w-8 h-8 rounded-full bg-gray-200 flex items-center justify-center text-xs font-medium">
                                {getInitials(candidate.full_name)}
                              </div>
                              <div>
                                <p className="font-medium text-sm">
                                  {candidate.full_name}
                                </p>
                                <p className="text-xs text-gray-500">
                                  {candidate.email}
                                </p>
                              </div>
                            </div>
                          </div>

                          {/* Feedback Status */}
                          {candidate.feedback_required_count > 0 && (
                            <div className="flex items-center gap-2 mt-2">
                              {candidate.feedback_submitted_count >=
                              candidate.feedback_required_count ? (
                                <div className="flex items-center gap-1 text-green-600 text-xs">
                                  <CheckCircle className="w-3 h-3" />
                                  <span>
                                    {candidate.feedback_submitted_count}/
                                    {candidate.feedback_required_count} feedback
                                  </span>
                                </div>
                              ) : (
                                <div className="flex items-center gap-1 text-amber-600 text-xs">
                                  <AlertCircle className="w-3 h-3" />
                                  <span>
                                    {candidate.feedback_submitted_count}/
                                    {candidate.feedback_required_count} feedback
                                  </span>
                                </div>
                              )}
                            </div>
                          )}

                          {/* Quick Move Actions (if selected) */}
                          {selectedCandidate?.id === candidate.id && (
                            <div className="flex flex-wrap gap-1 mt-3 pt-2 border-t">
                              {stages
                                .filter((s) => s.id !== stage.id)
                                .map((nextStage) => (
                                  <Button
                                    key={nextStage.id}
                                    variant="outline"
                                    size="sm"
                                    className="text-xs h-7"
                                    onClick={(e) => {
                                      e.stopPropagation();
                                      handleMoveCandidate(candidate, nextStage.id);
                                    }}
                                  >
                                    Move to {nextStage.name}
                                    <ChevronRight className="w-3 h-3 ml-1" />
                                  </Button>
                                ))}
                            </div>
                          )}
                        </CardContent>
                      </Card>
                    ))
                  )}
                </div>
              </div>
            );
          })}
        </div>
      </div>

      {/* Drag Preview */}
      {selectedCandidate && (
        <div className="fixed bottom-4 right-4 bg-white dark:bg-gray-800 rounded-lg shadow-lg p-4 border max-w-sm z-50">
          <div className="flex items-center gap-2 mb-2">
            <div className="w-2 h-2 rounded-full bg-blue-500 animate-pulse" />
            <span className="font-medium">Dragging: {selectedCandidate.full_name}</span>
          </div>
          <p className="text-sm text-gray-500">
            Drop on a stage to move the candidate there.
          </p>
          <Button
            variant="ghost"
            size="sm"
            className="mt-2 text-gray-500"
            onClick={() => setSelectedCandidate(null)}
          >
            Cancel
          </Button>
        </div>
      )}
    </div>
  );
}

