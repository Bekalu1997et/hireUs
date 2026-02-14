"use client";

import React from "react";
import Link from "next/link";
import { useQuery } from "@tanstack/react-query";
import { evaluationApi } from "@/lib/api";
import { Button } from "@/components/ui/button";
import { Card, CardContent } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import { Select } from "@/components/ui/select";
import { Input } from "@/components/ui/input";
import { 
  Plus, Search, FileText, User, Star, 
  CheckCircle, Clock, ArrowRight
} from "lucide-react";
import { Scorecard } from "@/hooks/use-evaluations";

interface PageProps {
  searchParams: Promise<{ [key: string]: string | string[] | undefined }>;
}

export default function EvaluationsPage({ searchParams }: PageProps) {
  const [params, setParams] = React.useState({
    is_submitted: "",
    is_draft: "",
    search: "",
  });
  const [mounted, setMounted] = React.useState(false);

  React.useEffect(() => {
    setMounted(true);
  }, []);

  const { data: evaluationsData, isLoading, error } = useQuery({
    queryKey: ["evaluations", params],
    queryFn: async () => {
      const queryParams: Record<string, unknown> = {};
      if (params.is_submitted) queryParams.is_submitted = params.is_submitted === "true";
      if (params.is_draft) queryParams.is_draft = params.is_draft === "true";
      if (params.search) queryParams.search = params.search;
      
      const response = await evaluationApi.getAll(queryParams);
      return response;
    },
  });

  const { data: myDraftsData } = useQuery({
    queryKey: ["my-drafts"],
    queryFn: async () => {
      const response = await evaluationApi.getMyDrafts();
      return response as Scorecard[];
    },
  });

  if (!mounted) {
    return null;
  }

  const myDrafts = myDraftsData || [];

  const getStatusBadge = (scorecard: Scorecard) => {
    if (scorecard.is_draft) {
      return <span className="inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium bg-yellow-100 text-yellow-800">Draft</span>;
    }
    if (scorecard.is_submitted) {
      return <span className="inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium bg-green-100 text-green-800">Submitted</span>;
    }
    return <span className="inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium bg-gray-100 text-gray-800">Pending</span>;
  };

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

  const calculateAverageScore = (scores: Record<string, unknown>) => {
    const values = Object.values(scores);
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

  const evaluationsListData = evaluationsData as { items?: Scorecard[]; total?: number; total_pages?: number } | undefined;
  const evaluationsItems = evaluationsListData?.items || [];

  return (
    <div className="container mx-auto py-8 px-4">
      {/* Header */}
      <div className="flex flex-col sm:flex-row items-start sm:items-center justify-between gap-4 mb-8">
        <div>
          <h1 className="text-3xl font-bold">Interview Evaluations</h1>
          <p className="text-gray-600 mt-1">
            View and manage interview scorecards and feedback
          </p>
        </div>
        <div className="flex gap-2">
          <Link href="/evaluations/create">
            <Button>
              <Plus className="w-4 h-4 mr-2" />
              New Evaluation
            </Button>
          </Link>
        </div>
      </div>

      {/* Draft Alert */}
      {myDrafts.length > 0 && (
        <Card className="mb-6 bg-yellow-50 border-yellow-200">
          <CardContent className="p-4">
            <div className="flex items-center gap-3">
              <Clock className="w-5 h-5 text-yellow-600" />
              <div className="flex-1">
                <p className="font-medium text-yellow-800">
                  You have {myDrafts.length} draft evaluation(s) pending submission
                </p>
              </div>
              <Link href="/?filter=drafts">
                <Button variant="outline" size="sm">
                  View Drafts
                </Button>
              </Link>
            </div>
          </CardContent>
        </Card>
      )}

      {/* Filters */}
      <Card className="mb-6">
        <CardContent className="p-4">
          <div className="flex flex-col sm:flex-row gap-4">
            <div className="flex-1">
              <div className="relative">
                <Search className="w-4 h-4 absolute left-3 top-1/2 transform -translate-y-1/2 text-gray-400" />
                <Input
                  placeholder="Search evaluations..."
                  className="pl-10"
                  value={params.search}
                  onChange={(e) => setParams((prev) => ({ ...prev, search: e.target.value }))}
                />
              </div>
            </div>
            <Select
              options={[
                { value: "", label: "All Status" },
                { value: "draft", label: "Drafts" },
                { value: "submitted", label: "Submitted" },
              ]}
              value={params.is_draft}
              onChange={(e) => setParams((prev) => ({ 
                ...prev, 
                is_draft: e.target.value,
                is_submitted: e.target.value === "submitted" ? "true" : e.target.value === "draft" ? "" : ""
              }))}
              className="w-full sm:w-40"
            />
          </div>
        </CardContent>
      </Card>

      {/* Stats */}
      <div className="grid grid-cols-2 md:grid-cols-4 gap-4 mb-6">
        <Card>
          <CardContent className="p-4 flex items-center gap-3">
            <FileText className="w-5 h-5 text-gray-400" />
            <div>
              <p className="text-2xl font-bold">
                {evaluationsListData?.total || 0}
              </p>
              <p className="text-xs text-gray-500">Total Evaluations</p>
            </div>
          </CardContent>
        </Card>
        <Card>
          <CardContent className="p-4 flex items-center gap-3">
            <Clock className="w-5 h-5 text-yellow-500" />
            <div>
              <p className="text-2xl font-bold">
                {myDrafts.length}
              </p>
              <p className="text-xs text-gray-500">Drafts</p>
            </div>
          </CardContent>
        </Card>
        <Card>
          <CardContent className="p-4 flex items-center gap-3">
            <CheckCircle className="w-5 h-5 text-green-500" />
            <div>
              <p className="text-2xl font-bold">
                {evaluationsItems.filter((s) => s.is_submitted).length}
              </p>
              <p className="text-xs text-gray-500">Submitted</p>
            </div>
          </CardContent>
        </Card>
        <Card>
          <CardContent className="p-4 flex items-center gap-3">
            <Star className="w-5 h-5 text-blue-500" />
            <div>
              <p className="text-2xl font-bold">-</p>
              <p className="text-xs text-gray-500">Avg Score</p>
            </div>
          </CardContent>
        </Card>
      </div>

      {/* Evaluations List */}
      {isLoading ? (
        <div className="space-y-4">
          {[1, 2, 3].map((i) => (
            <Card key={i} className="animate-pulse">
              <CardContent className="p-6">
                <div className="h-6 bg-gray-200 rounded w-1/4 mb-4" />
                <div className="h-4 bg-gray-200 rounded w-1/2" />
              </CardContent>
            </Card>
          ))}
        </div>
      ) : error ? (
        <Card className="bg-red-50 border-red-200">
          <CardContent className="p-6 text-center">
            <p className="text-red-600">Failed to load evaluations.</p>
          </CardContent>
        </Card>
      ) : evaluationsItems.length === 0 ? (
        <Card>
          <CardContent className="p-12 text-center">
            <FileText className="w-12 h-12 text-gray-300 mx-auto mb-4" />
            <h3 className="text-xl font-semibold mb-2">No Evaluations Yet</h3>
            <p className="text-gray-600 mb-6">
              Start by creating your first interview evaluation
            </p>
            <Link href="/evaluations/create">
              <Button>
                <Plus className="w-4 h-4 mr-2" />
                Create Evaluation
              </Button>
            </Link>
          </CardContent>
        </Card>
      ) : (
        <div className="space-y-4">
          {evaluationsItems.map((scorecard) => {
            const avgScore = calculateAverageScore(scorecard.scores);
            return (
              <Card key={scorecard.id} className="hover:shadow-md transition-shadow">
                <CardContent className="p-6">
                  <div className="flex flex-col md:flex-row md:items-center justify-between gap-4">
                    <div className="flex-1">
                      <div className="flex items-center gap-3 mb-2">
                        {getStatusBadge(scorecard)}
                        <Badge className={getRecommendationColor(scorecard.recommendation)}>
                          {formatRecommendation(scorecard.recommendation)}
                        </Badge>
                      </div>
                      <div className="flex items-center gap-6 text-sm text-gray-600">
                        <div className="flex items-center gap-1">
                          <User className="w-4 h-4" />
                          <span>ID: {scorecard.candidate_id.slice(0, 8)}...</span>
                        </div>
                        <div className="flex items-center gap-1">
                          <Star className="w-4 h-4" />
                          <span>Avg: {avgScore}/5</span>
                        </div>
                        <div className="flex items-center gap-1">
                          <Clock className="w-4 h-4" />
                          <span>{new Date(scorecard.created_at).toLocaleDateString()}</span>
                        </div>
                      </div>
                    </div>
                    <div className="flex items-center gap-2">
                      <Link href={`/evaluations/${scorecard.id}`}>
                        <Button variant="outline" size="sm">
                          View Details
                          <ArrowRight className="w-4 h-4 ml-1" />
                        </Button>
                      </Link>
                    </div>
                  </div>
                </CardContent>
              </Card>
            );
          })}
        </div>
      )}

      {/* Pagination */}
      {(evaluationsListData?.total_pages || 0) > 1 && (
        <div className="mt-6 flex justify-center gap-2">
          <Button variant="outline" disabled>Previous</Button>
          <Button variant="outline" disabled>Next</Button>
        </div>
      )}
    </div>
  );
}

