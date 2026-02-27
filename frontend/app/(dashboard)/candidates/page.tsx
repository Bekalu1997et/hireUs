"use client";

import React from "react";
import { useQuery } from "@tanstack/react-query";
import { candidateApi } from "@/lib/api";
import { useAuth } from "@/hooks/context/use-auth";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Card, CardContent } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import { Skeleton } from "@/components/ui/skeleton";
import { Plus, Search, Filter, Mail, Phone } from "lucide-react";
import Link from "next/link";

interface CandidateListItem {
  id: string;
  full_name: string;
  email: string;
  phone: string | null;
  status: string;
  source: string | null;
  role_id: string | null;
  is_active: boolean;
  created_at: string;
  updated_at: string;
}

interface CandidateListResponse {
  candidates: CandidateListItem[];
  total: number;
  skip: number;
  limit: number;
}

type BadgeVariant = "default" | "secondary" | "destructive" | "outline" | "success";

const getStatusBadgeVariant = (status: string): BadgeVariant => {
  switch (status.toLowerCase()) {
    case "new":
      return "default";
    case "screening":
      return "secondary";
    case "interview":
      return "outline";
    case "offer":
      return "success";
    case "hired":
      return "success";
    case "rejected":
      return "destructive";
    case "withdrawn":
      return "destructive";
    default:
      return "secondary";
  }
};

export default function CandidatesPage() {
  const { organizationId } = useAuth();
  const { data, isLoading, error, refetch } = useQuery<CandidateListResponse>({
    queryKey: ["candidates", organizationId],
    queryFn: async () => {
      const response = await candidateApi.getAll({
        limit: 50,
        organization_id: organizationId || undefined,
      });
      return response as CandidateListResponse;
    },
    enabled: !!organizationId,
  });

  return (
    <div className="container mx-auto py-8 px-4">
      <div className="flex flex-col sm:flex-row justify-between items-start sm:items-center gap-4 mb-8">
        <div>
          <h1 className="text-3xl font-bold">Candidates</h1>
          <p className="text-gray-600 dark:text-gray-400 mt-1">
            Manage and track your candidates
          </p>
        </div>
        <Link href="/candidates/create">
          <Button>
            <Plus className="w-4 h-4 mr-2" />
            Add Candidate
          </Button>
        </Link>
      </div>

      {/* Filters */}
      <div className="flex gap-4 mb-6">
        <div className="relative flex-1">
          <Search className="absolute left-3 top-1/2 transform -translate-y-1/2 text-gray-400 w-4 h-4" />
          <Input
            type="text"
            placeholder="Search candidates..."
            className="pl-10"
          />
        </div>
        <Button variant="outline">
          <Filter className="w-4 h-4 mr-2" />
          Filters
        </Button>
      </div>

      {/* Candidates List */}
      {!organizationId ? (
        <Card className="bg-yellow-50">
          <CardContent className="p-6 text-center">
            <p className="text-yellow-800">
              No organization is associated with your account yet.
            </p>
          </CardContent>
        </Card>
      ) : isLoading ? (
        <div className="space-y-4">
          {[1, 2, 3].map((i) => (
            <Card key={i}>
              <CardContent className="p-6">
                <div className="space-y-3">
                  <Skeleton className="h-6 w-1/3" />
                  <Skeleton className="h-4 w-1/2" />
                  <Skeleton className="h-4 w-1/4" />
                </div>
              </CardContent>
            </Card>
          ))}
        </div>
      ) : error ? (
        <Card className="bg-red-50 dark:bg-red-900/20">
          <CardContent className="p-6 text-center">
            <p className="text-red-600 dark:text-red-400">
              Error loading candidates. Please try again.
            </p>
            <Button variant="outline" className="mt-4" onClick={() => refetch()}>
              Retry
            </Button>
          </CardContent>
        </Card>
      ) : data?.candidates.length === 0 ? (
        <Card>
          <CardContent className="p-12 text-center">
            <h3 className="text-xl font-semibold mb-2">No candidates yet</h3>
            <p className="text-gray-600 dark:text-gray-400 mb-6">
              Get started by adding your first candidate
            </p>
            <Link href="/candidates/create">
              <Button>
                <Plus className="w-4 h-4 mr-2" />
                Add Candidate
              </Button>
            </Link>
          </CardContent>
        </Card>
      ) : (
        <div className="grid gap-4">
          {data?.candidates.map((candidate) => (
            <Link key={candidate.id} href={`/candidates/${candidate.id}`}>
              <Card className="hover:shadow-md transition-shadow cursor-pointer">
                <CardContent className="p-6">
                  <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4">
                    <div className="flex-1">
                      <div className="flex items-center gap-3 mb-2">
                        <h3 className="text-xl font-semibold">
                          {candidate.full_name}
                        </h3>
                        {candidate.status && (
                          <Badge variant={getStatusBadgeVariant(candidate.status)}>
                            {candidate.status}
                          </Badge>
                        )}
                        {!candidate.is_active && (
                          <Badge variant="outline">Inactive</Badge>
                        )}
                      </div>
                      
                      {/* Contact Info */}
                      <div className="flex flex-wrap gap-4 mb-2 text-sm text-gray-600 dark:text-gray-400">
                        <div className="flex items-center gap-1">
                          <Mail className="w-4 h-4" />
                          {candidate.email}
                        </div>
                        {candidate.phone && (
                          <div className="flex items-center gap-1">
                            <Phone className="w-4 h-4" />
                            {candidate.phone}
                          </div>
                        )}
                      </div>

                      {/* Source */}
                      {candidate.source && (
                        <p className="text-sm text-gray-500">
                          Source: {candidate.source}
                        </p>
                      )}
                    </div>
                    <Button variant="outline" size="sm">
                      View Details
                    </Button>
                  </div>
                </CardContent>
              </Card>
            </Link>
          ))}
        </div>
      )}

      {/* Pagination Info */}
      {data && data.candidates.length > 0 && (
        <div className="mt-6 text-center text-sm text-gray-600 dark:text-gray-400">
          Showing {data.candidates.length} of {data.total} candidates
        </div>
      )}
    </div>
  );
}
