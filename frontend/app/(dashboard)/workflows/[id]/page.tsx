"use client";

import React, { useState } from "react";
import Link from "next/link";
import { useParams, useRouter } from "next/navigation";
import { useQuery, useMutation, useQueryClient } from "@tanstack/react-query";
import { Button } from "@/components/ui/button";
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import { Textarea } from "@/components/ui/textarea";
import {
  ArrowLeft,
  Save,
  Plus,
  Trash2,
  GripVertical,
  Settings,
  Users,
  Check,
  Star,
  MoreVertical,
  Edit2,
  X,
} from "lucide-react";
import { useWorkflow, useUpdateWorkflow, useDeleteStage, useSetDefaultWorkflow } from "@/hooks/use-workflows";

interface Stage {
  id: string;
  name: string;
  order: number;
  description?: string;
  color: string;
  required_feedback_count: number;
  interview_types: string[];
}

export default function WorkflowDetailPage() {
  const params = useParams();
  const router = useRouter();
  const queryClient = useQueryClient();
  const workflowId = params.id as string;

  const [isEditing, setIsEditing] = useState(false);
  const [editedName, setEditedName] = useState("");
  const [editedDescription, setEditedDescription] = useState("");
  const [stages, setStages] = useState<Stage[]>([]);
  const [newStageName, setNewStageName] = useState("");

  const { data: workflow, isLoading, error } = useWorkflow(workflowId);

  const updateMutation = useUpdateWorkflow();
  const deleteStageMutation = useDeleteStage();
  const setDefaultMutation = useSetDefaultWorkflow();

  // Initialize edit state when workflow loads
  React.useEffect(() => {
    if (workflow) {
      setEditedName(workflow.name);
      setEditedDescription(workflow.description || "");
      setStages(workflow.stages as Stage[] || []);
    }
  }, [workflow]);

  const handleSave = async () => {
    await updateMutation.mutateAsync({
      id: workflowId,
      data: {
        name: editedName,
        description: editedDescription,
        stages: stages.map((stage, index) => ({
          ...stage,
          order: index,
        })),
      },
    });
    setIsEditing(false);
  };

  const handleCancel = () => {
    if (workflow) {
      setEditedName(workflow.name);
      setEditedDescription(workflow.description || "");
      setStages(workflow.stages as Stage[] || []);
    }
    setIsEditing(false);
  };

  const handleAddStage = async () => {
    if (!newStageName.trim()) return;

    const newStage: Stage = {
      id: `stage_${Date.now()}`,
      name: newStageName.trim(),
      order: stages.length,
      description: "",
      color: getRandomColor(),
      required_feedback_count: 0,
      interview_types: [],
    };

    setStages([...stages, newStage]);
    setNewStageName("");
  };

  const handleDeleteStage = async (stageId: string) => {
    if (stages.length <= 1) {
      alert("Cannot delete the last stage");
      return;
    }

    const updatedStages = stages.filter((s) => s.id !== stageId);
    // Reorder remaining stages
    const reorderedStages = updatedStages.map((stage, index) => ({
      ...stage,
      order: index,
    }));

    setStages(reorderedStages);

    // Also delete from server
    await deleteStageMutation.mutateAsync({ workflowId, stageId });
  };

  const handleSetDefault = async () => {
    await setDefaultMutation.mutateAsync({ id: workflowId });
  };

  const getRandomColor = () => {
    const colors = [
      "#6366f1", "#8b5cf6", "#06b6d4", "#10b981",
      "#f59e0b", "#ef4444", "#ec4899", "#14b8a6",
    ];
    return colors[Math.floor(Math.random() * colors.length)];
  };

  const updateStage = (stageId: string, updates: Partial<Stage>) => {
    setStages(stages.map((s) => (s.id === stageId ? { ...s, ...updates } : s)));
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
        <Card className="animate-pulse">
          <CardHeader>
            <div className="h-8 bg-gray-200 rounded w-1/3 mb-2" />
            <div className="h-4 bg-gray-200 rounded w-1/2" />
          </CardHeader>
          <CardContent>
            <div className="space-y-4">
              {[1, 2, 3, 4].map((i) => (
                <div key={i} className="h-24 bg-gray-200 rounded" />
              ))}
            </div>
          </CardContent>
        </Card>
      </div>
    );
  }

  if (error || !workflow) {
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

  return (
    <div className="container mx-auto py-8 px-4">
      {/* Header */}
      <div className="flex items-center gap-4 mb-8">
        <Link href="/workflows">
          <Button variant="ghost" size="sm">
            <ArrowLeft className="w-4 h-4 mr-2" />
            Back
          </Button>
        </Link>
        <div className="flex-1">
          {isEditing ? (
            <div className="flex items-center gap-4">
              <Input
                value={editedName}
                onChange={(e) => setEditedName(e.target.value)}
                className="text-2xl font-bold h-auto py-1"
                placeholder="Workflow name"
              />
            </div>
          ) : (
            <div className="flex items-center gap-3">
              <h1 className="text-2xl font-bold">{workflow.name}</h1>
              {workflow.is_default && (
                <Badge variant="default">
                  <Star className="w-3 h-3 mr-1" />
                  Default
                </Badge>
              )}
            </div>
          )}
          {workflow.description && !isEditing && (
            <p className="text-gray-600 dark:text-gray-400 mt-1">
              {workflow.description}
            </p>
          )}
        </div>
        <div className="flex items-center gap-2">
          {isEditing ? (
            <>
              <Button variant="outline" onClick={handleCancel}>
                <X className="w-4 h-4 mr-2" />
                Cancel
              </Button>
              <Button onClick={handleSave} disabled={updateMutation.isPending}>
                <Save className="w-4 h-4 mr-2" />
                {updateMutation.isPending ? "Saving..." : "Save"}
              </Button>
            </>
          ) : (
            <>
              {!workflow.is_default && (
                <Button variant="outline" onClick={handleSetDefault} disabled={setDefaultMutation.isPending}>
                  <Star className="w-4 h-4 mr-2" />
                  Set as Default
                </Button>
              )}
              <Button variant="outline" onClick={() => setIsEditing(true)}>
                <Edit2 className="w-4 h-4 mr-2" />
                Edit
              </Button>
              <Link href={`/workflows/${workflowId}/board`}>
                <Button>
                  <Users className="w-4 h-4 mr-2" />
                  View Board
                </Button>
              </Link>
            </>
          )}
        </div>
      </div>

      {/* Description Edit */}
      {isEditing && (
        <Card className="mb-6">
          <CardHeader>
            <CardTitle className="text-lg">Description</CardTitle>
          </CardHeader>
          <CardContent>
            <Textarea
              value={editedDescription}
              onChange={(e) => setEditedDescription(e.target.value)}
              placeholder="Describe this workflow..."
              rows={3}
            />
          </CardContent>
        </Card>
      )}

      {/* Stages */}
      <div className="mb-6">
        <div className="flex items-center justify-between mb-4">
          <h2 className="text-xl font-semibold">Stages</h2>
          <p className="text-sm text-gray-500">
            {stages.length} stages | Drag to reorder
          </p>
        </div>

        <div className="space-y-3">
          {stages.map((stage, index) => (
            <Card key={stage.id} className="relative">
              <CardContent className="p-4">
                <div className="flex items-start gap-4">
                  {/* Drag Handle */}
                  <div className="cursor-move text-gray-400 hover:text-gray-600 mt-1">
                    <GripVertical className="w-5 h-5" />
                  </div>

                  {/* Color Indicator */}
                  <div
                    className="w-3 h-full min-h-[60px] rounded"
                    style={{ backgroundColor: stage.color }}
                  />

                  {/* Stage Info */}
                  <div className="flex-1">
                    {isEditing ? (
                      <div className="space-y-3">
                        <Input
                          value={stage.name}
                          onChange={(e) => updateStage(stage.id, { name: e.target.value })}
                          placeholder="Stage name"
                        />
                        <Textarea
                          value={stage.description || ""}
                          onChange={(e) => updateStage(stage.id, { description: e.target.value })}
                          placeholder="Stage description..."
                          rows={2}
                        />
                        <div className="flex items-center gap-4">
                          <div>
                            <Label className="text-xs">Color</Label>
                            <Input
                              type="color"
                              value={stage.color}
                              onChange={(e) => updateStage(stage.id, { color: e.target.value })}
                              className="w-20 h-8 cursor-pointer"
                            />
                          </div>
                          <div>
                            <Label className="text-xs">Required Feedbacks</Label>
                            <Input
                              type="number"
                              min="0"
                              value={stage.required_feedback_count}
                              onChange={(e) =>
                                updateStage(stage.id, {
                                  required_feedback_count: parseInt(e.target.value) || 0,
                                })
                              }
                              className="w-24"
                            />
                          </div>
                        </div>
                      </div>
                    ) : (
                      <div>
                        <div className="flex items-center gap-2 mb-1">
                          <h3 className="font-semibold">{stage.name}</h3>
                          <Badge variant="outline" className="text-xs">
                            Stage {index + 1}
                          </Badge>
                        </div>
                        {stage.description && (
                          <p className="text-sm text-gray-600 dark:text-gray-400">
                            {stage.description}
                          </p>
                        )}
                        <div className="flex items-center gap-4 mt-2 text-xs text-gray-500">
                          {stage.required_feedback_count > 0 && (
                            <span>
                              {stage.required_feedback_count} feedback(s) required
                            </span>
                          )}
                          {workflow.candidates_count?.[stage.id] !== undefined && (
                            <span>
                              {workflow.candidates_count[stage.id]} candidate(s)
                            </span>
                          )}
                        </div>
                      </div>
                    )}
                  </div>

                  {/* Actions */}
                  {isEditing && (
                    <Button
                      variant="ghost"
                      size="sm"
                      onClick={() => handleDeleteStage(stage.id)}
                      disabled={stages.length <= 1}
                      className="text-red-500 hover:text-red-700 hover:bg-red-50"
                    >
                      <Trash2 className="w-4 h-4" />
                    </Button>
                  )}
                </div>
              </CardContent>
            </Card>
          ))}
        </div>

        {/* Add Stage */}
        {isEditing && (
          <Card className="mt-4 border-dashed">
            <CardContent className="p-4">
              <div className="flex items-center gap-4">
                <Input
                  value={newStageName}
                  onChange={(e) => setNewStageName(e.target.value)}
                  placeholder="New stage name..."
                  onKeyDown={(e) => {
                    if (e.key === "Enter") handleAddStage();
                  }}
                />
                <Button onClick={handleAddStage} disabled={!newStageName.trim()}>
                  <Plus className="w-4 h-4 mr-2" />
                  Add Stage
                </Button>
              </div>
            </CardContent>
          </Card>
        )}
      </div>

      {/* Quick Actions */}
      {!isEditing && (
        <Card>
          <CardHeader>
            <CardTitle className="text-lg">Quick Actions</CardTitle>
            <CardDescription>
              Common tasks for this workflow
            </CardDescription>
          </CardHeader>
          <CardContent>
            <div className="flex flex-wrap gap-3">
              <Link href={`/workflows/${workflowId}/board`}>
                <Button variant="outline">
                  <Users className="w-4 h-4 mr-2" />
                  Open Kanban Board
                </Button>
              </Link>
              <Button variant="outline" onClick={() => setIsEditing(true)}>
                <Settings className="w-4 h-4 mr-2" />
                Edit Workflow
              </Button>
              <Link href="/candidates">
                <Button variant="outline">
                  <Users className="w-4 h-4 mr-2" />
                  View Candidates
                </Button>
              </Link>
            </div>
          </CardContent>
        </Card>
      )}
    </div>
  );
}

