"use client";

import React, { useState } from "react";
import Link from "next/link";
import { useQuery } from "@tanstack/react-query";
import { workflowApi, Workflow } from "@/lib/workflow-api";
import { Button } from "@/components/ui/button";
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import { Input } from "@/components/ui/input";
import {
  Workflow as WorkflowIcon,
  Plus,
  Search,
  Settings,
  MoreVertical,
  Check,
  Star,
  Users,
} from "lucide-react";

interface WorkflowListItem {
  id: string;
  name: string;
  description?: string;
  stages: {
    id: string;
    name: string;
    order: number;
    color: string;
  }[];
  is_default: boolean;
  is_active: boolean;
  created_at: string;
}

interface WorkflowListResponse {
  items: WorkflowListItem[];
  total: number;
  page: number;
  page_size: number;
  total_pages: number;
}

export default function WorkflowsPage() {
  const [search, setSearch] = useState("");
  const [page, setPage] = useState(1);
  const limit = 10;

  const { data, isLoading, error, refetch } = useQuery<WorkflowListResponse>({
    queryKey: ["workflows", { skip: (page - 1) * limit, limit }],
    queryFn: async () => {
      const response = await workflowApi.getAll({ skip: (page - 1) * limit, limit });
      return response as WorkflowListResponse;
    },
  });

  const { data: defaultWorkflow } = useQuery({
    queryKey: ["defaultWorkflow"],
    queryFn: async () => {
      const response = await workflowApi.getDefault();
      return response as Workflow;
    },
  });

  const getStageColor = (color: string) => {
    return color || "#6366f1";
  };

  if (isLoading) {
    return (
      <div className="container mx-auto py-8 px-4">
        <div className="flex items-center justify-between mb-8">
          <div>
            <h1 className="text-3xl font-bold">Hiring Workflows</h1>
            <p className="text-gray-600 mt-1">Manage your hiring pipelines</p>
          </div>
        </div>
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
          {[...Array(6)].map((_, i) => (
            <Card key={i} className="animate-pulse">
              <CardHeader>
                <div className="h-6 bg-gray-200 rounded w-3/4 mb-2" />
                <div className="h-4 bg-gray-200 rounded w-1/2" />
              </CardHeader>
              <CardContent>
                <div className="flex gap-1 mb-4">
                  {[...Array(4)].map((_, j) => (
                    <div key={j} className="h-6 w-12 rounded bg-gray-200" />
                  ))}
                </div>
                <div className="h-4 bg-gray-200 rounded w-full" />
              </CardContent>
            </Card>
          ))}
        </div>
      </div>
    );
  }

  return (
    <div className="container mx-auto py-8 px-4">
      {/* Header */}
      <div className="flex flex-col sm:flex-row items-start sm:items-center justify-between gap-4 mb-8">
        <div>
          <h1 className="text-3xl font-bold">Hiring Workflows</h1>
          <p className="text-gray-600 mt-1">
            {data?.total || 0} workflows created | Manage your hiring pipelines
          </p>
        </div>
        <Link href="/workflows/create">
          <Button>
            <Plus className="w-4 h-4 mr-2" />
            Create Workflow
          </Button>
        </Link>
      </div>

      {/* Search */}
      <div className="mb-6">
        <div className="relative">
          <Search className="absolute left-3 top-1/2 transform -translate-y-1/2 text-gray-400 w-4 h-4" />
          <Input
            placeholder="Search workflows..."
            value={search}
            onChange={(e) => setSearch(e.target.value)}
            className="pl-10"
          />
        </div>
      </div>

      {/* Empty State */}
      {!data?.items.length && (
        <Card className="mb-6">
          <CardContent className="p-12 text-center">
            <WorkflowIcon className="w-12 h-12 text-gray-400 mx-auto mb-4" />
            <h3 className="text-xl font-semibold mb-2">No Workflows Yet</h3>
            <p className="text-gray-600 mb-6 max-w-md mx-auto">
              Create your first hiring workflow to start managing candidates through your pipeline.
            </p>
            <Link href="/workflows/create">
              <Button>
                <Plus className="w-4 h-4 mr-2" />
                Create Your First Workflow
              </Button>
            </Link>
          </CardContent>
        </Card>
      )}

      {/* Workflow Grid */}
      {data?.items && data.items.length > 0 && (
        <>
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
            {data.items.map((workflow) => (
              <Link key={workflow.id} href={`/workflows/${workflow.id}`}>
                <Card className="h-full hover:shadow-lg transition-shadow cursor-pointer">
                  <CardHeader>
                    <div className="flex items-start justify-between">
                      <div className="flex-1">
                        <div className="flex items-center gap-2">
                          <CardTitle className="text-lg">{workflow.name}</CardTitle>
                          {workflow.is_default && (
                            <Badge variant="default" className="text-xs">
                              <Star className="w-3 h-3 mr-1" />
                              Default
                            </Badge>
                          )}
                        </div>
                        {workflow.description && (
                          <CardDescription className="mt-1 line-clamp-2">
                            {workflow.description}
                          </CardDescription>
                        )}
                      </div>
                      <Button variant="ghost" size="sm" className="ml-2">
                        <MoreVertical className="w-4 h-4" />
                      </Button>
                    </div>
                  </CardHeader>
                  <CardContent>
                    {/* Stages Preview */}
                    <div className="mb-4">
                      <p className="text-xs text-gray-500 mb-2">Stages:</p>
                      <div className="flex flex-wrap gap-1">
                        {workflow.stages.slice(0, 6).map((stage, idx) => (
                          <Badge
                            key={stage.id || idx}
                            style={{
                              backgroundColor: `${getStageColor(stage.color)}20`,
                              color: getStageColor(stage.color),
                              borderColor: getStageColor(stage.color),
                            }}
                            variant="outline"
                            className="text-xs"
                          >
                            {stage.name}
                          </Badge>
                        ))}
                        {workflow.stages.length > 6 && (
                          <Badge variant="outline" className="text-xs">
                            +{workflow.stages.length - 6} more
                          </Badge>
                        )}
                      </div>
                    </div>

                    {/* Stats */}
                    <div className="flex items-center gap-4 text-sm text-gray-500">
                      <div className="flex items-center gap-1">
                        <WorkflowIcon className="w-4 h-4" />
                        <span>{workflow.stages.length} stages</span>
                      </div>
                      {workflow.is_default && (
                        <div className="flex items-center gap-1">
                          <Check className="w-4 h-4 text-green-500" />
                          <span>Active</span>
                        </div>
                      )}
                    </div>
                  </CardContent>
                </Card>
              </Link>
            ))}
          </div>

          {/* Pagination */}
          {data.total_pages > 1 && (
            <div className="flex items-center justify-center gap-2 mt-8">
              <Button
                variant="outline"
                size="sm"
                onClick={() => setPage(p => Math.max(1, p - 1))}
                disabled={page === 1}
              >
                Previous
              </Button>
              <span className="text-sm text-gray-600">
                Page {page} of {data.total_pages}
              </span>
              <Button
                variant="outline"
                size="sm"
                onClick={() => setPage(p => Math.min(data.total_pages, p + 1))}
                disabled={page === data.total_pages}
              >
                Next
              </Button>
            </div>
          )}
        </>
      )}

      {/* Default Workflow Info */}
      {defaultWorkflow && (
        <div className="mt-8 p-4 bg-blue-50 dark:bg-blue-900/20 rounded-lg">
          <div className="flex items-center gap-2 mb-2">
            <Star className="w-4 h-4 text-blue-500" />
            <h3 className="font-semibold">Default Workflow</h3>
          </div>
          <p className="text-sm text-gray-600 dark:text-gray-400">
            Your default workflow is <strong>{defaultWorkflow.name}</strong> with{" "}
            {defaultWorkflow.stages?.length || 0} stages. This workflow will be used for
            new candidates by default.
          </p>
          <Link href={`/workflows/${defaultWorkflow.id}`}>
            <Button variant="outline" size="sm" className="mt-2">
              <Settings className="w-4 h-4 mr-2" />
              Manage Default Workflow
            </Button>
          </Link>
        </div>
      )}
    </div>
  );
}

