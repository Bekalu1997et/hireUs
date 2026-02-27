"use client";

import React from "react";
import { useQuery } from "@tanstack/react-query";
import { roleApi } from "@/lib/api";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Card, CardContent } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import { Skeleton } from "@/components/ui/skeleton";
import { Plus, Search, Filter } from "lucide-react";
import Link from "next/link";

interface RoleListItem {
  id: string;
  title: string;
  slug: string;
  seniority: string | null;
  department: string | null;
  tech_stack: string[];
  is_active: boolean;
  created_at: string;
}

interface RoleListResponse {
  items: RoleListItem[];
  total: number;
  page: number;
  page_size: number;
  total_pages: number;
}

type BadgeVariant = "default" | "secondary" | "destructive" | "outline" | "success";

const getSeniorityBadgeVariant = (seniority: string): BadgeVariant => {
  switch (seniority.toLowerCase()) {
    case "intern":
      return "outline";
    case "junior":
      return "secondary";
    case "mid":
      return "default";
    case "senior":
      return "default";
    case "lead":
      return "secondary";
    case "principal":
      return "secondary";
    case "director":
      return "destructive";
    case "vp":
      return "destructive";
    default:
      return "secondary";
  }
};

export default function RolesPage() {
  const { data, isLoading, error, refetch } = useQuery<RoleListResponse>({
    queryKey: ["roles"],
    queryFn: async () => {
      const response = await roleApi.getAll({ limit: 50 });
      return response as RoleListResponse;
    },
  });

  // Helper function to get error message
  const getErrorMessage = (err: unknown): string => {
    if (err instanceof Error) return err.message;
    return "Error loading roles. Please try again.";
  };

  return (
    <div className="container mx-auto py-8 px-4">
      <div className="flex flex-col sm:flex-row justify-between items-start sm:items-center gap-4 mb-8">
        <div>
          <h1 className="text-3xl font-bold">Role Blueprints</h1>
          <p className="text-gray-600 dark:text-gray-400 mt-1">
            Define and manage your role requirements
          </p>
        </div>
        <Link href="/roles/create">
          <Button>
            <Plus className="w-4 h-4 mr-2" />
            Create Role
          </Button>
        </Link>
      </div>

      {/* Filters */}
      <div className="flex gap-4 mb-6">
        <div className="relative flex-1">
          <Search className="absolute left-3 top-1/2 transform -translate-y-1/2 text-gray-400 w-4 h-4" />
          <Input
            type="text"
            placeholder="Search roles..."
            className="pl-10"
          />
        </div>
        <Button variant="outline">
          <Filter className="w-4 h-4 mr-2" />
          Filters
        </Button>
      </div>

      {/* Role List */}
      {isLoading ? (
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
              Error loading roles. Please try again.
            </p>
            <Button variant="outline" className="mt-4" onClick={() => refetch()}>
              Retry
            </Button>
          </CardContent>
        </Card>
      ) : data?.items.length === 0 ? (
        <Card>
          <CardContent className="p-12 text-center">
            <h3 className="text-xl font-semibold mb-2">No roles yet</h3>
            <p className="text-gray-600 dark:text-gray-400 mb-6">
              Get started by creating your first role blueprint
            </p>
            <Link href="/roles/create">
              <Button>
                <Plus className="w-4 h-4 mr-2" />
                Create Role
              </Button>
            </Link>
          </CardContent>
        </Card>
      ) : (
        <div className="grid gap-4">
          {data?.items.map((role) => (
            <Link key={role.id} href={`/roles/${role.id}`}>
              <Card className="hover:shadow-md transition-shadow cursor-pointer">
                <CardContent className="p-6">
                  <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4">
                    <div className="flex-1">
                      <div className="flex items-center gap-3 mb-2">
                        <h3 className="text-xl font-semibold">{role.title}</h3>
                        {role.seniority && (
                          <Badge variant={getSeniorityBadgeVariant(role.seniority)}>
                            {role.seniority}
                          </Badge>
                        )}
                        {!role.is_active && (
                          <Badge variant="outline">Inactive</Badge>
                        )}
                      </div>
                      {role.department && (
                        <p className="text-gray-600 dark:text-gray-400 mb-2">
                          {role.department}
                        </p>
                      )}
                      {role.tech_stack.length > 0 && (
                        <div className="flex flex-wrap gap-2">
                          {role.tech_stack.slice(0, 5).map((tech) => (
                            <Badge key={tech} variant="secondary">
                              {tech}
                            </Badge>
                          ))}
                          {role.tech_stack.length > 5 && (
                            <Badge variant="secondary">
                              +{role.tech_stack.length - 5} more
                            </Badge>
                          )}
                        </div>
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
      {data && data.items.length > 0 && (
        <div className="mt-6 text-center text-sm text-gray-600 dark:text-gray-400">
          Showing {data.items.length} of {data.total} roles
        </div>
      )}
    </div>
  );
}

