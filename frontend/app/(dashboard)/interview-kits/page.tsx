"use client";

import React, { useState } from "react";
import Link from "next/link";
import { useQuery } from "@tanstack/react-query";
import { interviewKitApi } from "@/lib/api";
import { Button } from "@/components/ui/button";
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import { Input } from "@/components/ui/input";
import { Select } from "@/components/ui/select";
import {
  InterviewKit,
  InterviewKitListResponse,
} from "@/hooks/use-interview-kits";
import { Plus, Search, Clock, BookOpen } from "lucide-react";

export default function InterviewKitsPage() {
  const [search, setSearch] = useState("");
  const [interviewType, setInterviewType] = useState("");
  const [page, setPage] = useState(1);
  const limit = 12;

  const { data, isLoading, error } = useQuery({
    queryKey: ["interview-kits", { skip: (page - 1) * limit, limit, search, interview_type: interviewType }],
    queryFn: async () => {
      const response = await interviewKitApi.getAll({
        skip: (page - 1) * limit,
        limit,
        search: search || undefined,
        interview_type: interviewType || undefined,
      });
      return response as InterviewKitListResponse;
    },
  });

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

  if (isLoading) {
    return (
      <div className="container mx-auto py-8 px-4">
        <div className="flex items-center justify-between mb-8">
          <div>
            <h1 className="text-3xl font-bold">Interview Kits</h1>
            <p className="text-gray-600 mt-1">Manage your interview question banks and evaluation rubrics</p>
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
                <div className="h-4 bg-gray-200 rounded w-full mb-2" />
                <div className="h-4 bg-gray-200 rounded w-2/3" />
              </CardContent>
            </Card>
          ))}
        </div>
      </div>
    );
  }

  if (error) {
    return (
      <div className="container mx-auto py-8 px-4">
        <Card className="bg-red-50 border-red-200">
          <CardContent className="p-6 text-center">
            <p className="text-red-600">Failed to load interview kits. Please try again.</p>
          </CardContent>
        </Card>
      </div>
    );
  }

  return (
    <div className="container mx-auto py-8 px-4">
      {/* Header */}
      <div className="flex flex-col sm:flex-row items-start sm:items-center justify-between gap-4 mb-8">
        <div>
          <h1 className="text-3xl font-bold">Interview Kits</h1>
          <p className="text-gray-600 mt-1">
            {data?.total || 0} kits created | Generate structured interviews with AI
          </p>
        </div>
        <Link href="/interview-kits/create">
          <Button>
            <Plus className="w-4 h-4 mr-2" />
            Create Interview Kit
          </Button>
        </Link>
      </div>

      {/* Filters */}
      <div className="bg-gray-50 dark:bg-gray-800 rounded-lg p-4 mb-6">
        <div className="flex flex-col sm:flex-row gap-4">
          <div className="relative flex-1">
            <Search className="absolute left-3 top-1/2 transform -translate-y-1/2 text-gray-400 w-4 h-4" />
            <Input
              placeholder="Search interview kits..."
              value={search}
              onChange={(e) => setSearch(e.target.value)}
              className="pl-10"
            />
          </div>
          <Select
            options={[
              { value: "", label: "All Types" },
              { value: "coding", label: "Coding" },
              { value: "system_design", label: "System Design" },
              { value: "pm_case", label: "PM Case" },
              { value: "behavioral", label: "Behavioral" },
            ]}
            value={interviewType}
            onChange={(e) => setInterviewType(e.target.value)}
            className="w-full sm:w-48"
          />
        </div>
      </div>

      {/* Empty State */}
      {!data?.items.length && (
        <Card className="mb-6">
          <CardContent className="p-12 text-center">
            <BookOpen className="w-12 h-12 text-gray-400 mx-auto mb-4" />
            <h3 className="text-xl font-semibold mb-2">No Interview Kits Yet</h3>
            <p className="text-gray-600 mb-6 max-w-md mx-auto">
              Create your first interview kit to start generating structured interviews with AI assistance.
            </p>
            <Link href="/interview-kits/create">
              <Button>
                <Plus className="w-4 h-4 mr-2" />
                Create Your First Kit
              </Button>
            </Link>
          </CardContent>
        </Card>
      )}

      {/* Grid */}
      {data?.items && data.items.length > 0 && (
        <>
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
            {data.items.map((kit: InterviewKit) => (
              <Link key={kit.id} href={`/interview-kits/${kit.id}`}>
                <Card className="h-full hover:shadow-lg transition-shadow cursor-pointer">
                  <CardHeader>
                    <div className="flex items-start justify-between">
                      <div className="flex-1">
                        <CardTitle className="text-lg mb-1">{kit.title}</CardTitle>
                        <Badge className={getTypeColor(kit.type)}>
                          {formatType(kit.type)}
                        </Badge>
                      </div>
                    </div>
                    {kit.description && (
                      <CardDescription className="mt-2 line-clamp-2">
                        {kit.description}
                      </CardDescription>
                    )}
                  </CardHeader>
                  <CardContent>
                    <div className="flex items-center gap-4 text-sm text-gray-500">
                      <div className="flex items-center gap-1">
                        <Clock className="w-4 h-4" />
                        <span>{kit.estimated_duration_minutes} min</span>
                      </div>
                      <div className="flex items-center gap-1">
                        <BookOpen className="w-4 h-4" />
                        <span>{kit.questions?.length || 0} questions</span>
                      </div>
                    </div>
                    {kit.evaluation_rubric && kit.evaluation_rubric.length > 0 && (
                      <div className="mt-4 pt-4 border-t">
                        <p className="text-xs text-gray-500 mb-2">Evaluation Criteria:</p>
                        <div className="flex flex-wrap gap-1">
                          {kit.evaluation_rubric.slice(0, 3).map((criterion, idx) => (
                            <Badge key={idx} variant="outline" className="text-xs">
                              {criterion.name}
                            </Badge>
                          ))}
                          {kit.evaluation_rubric.length > 3 && (
                            <Badge variant="outline" className="text-xs">
                              +{kit.evaluation_rubric.length - 3} more
                            </Badge>
                          )}
                        </div>
                      </div>
                    )}
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
    </div>
  );
}

