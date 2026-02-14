"use client";

import React from "react";
import { useAuth } from "@/hooks/context/use-auth";
import { Card, CardContent } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { Skeleton } from "@/components/ui/skeleton";
import { 
  Users, 
  Sparkles, 
  ClipboardList, 
  FileText, 
  GitBranch,
  TrendingUp,
  Brain,
  ArrowRight
} from "lucide-react";
import Link from "next/link";

export default function DashboardPage() {
  const { user, isLoading } = useAuth();

  if (isLoading) {
    return (
      <div className="space-y-6">
        <Skeleton className="h-12 w-64" />
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
          {[1, 2, 3, 4].map((i) => (
            <Skeleton key={i} className="h-32" />
          ))}
        </div>
      </div>
    );
  }

  const stats = [
    {
      title: "Active Roles",
      value: "12",
      icon: Sparkles,
      color: "bg-blue-500",
      href: "/roles",
    },
    {
      title: "Candidates",
      value: "48",
      icon: Users,
      color: "bg-green-500",
      href: "/candidates",
    },
    {
      title: "Interview Kits",
      value: "24",
      icon: ClipboardList,
      color: "bg-purple-500",
      href: "/interview-kits",
    },
    {
      title: "Evaluations",
      value: "156",
      icon: FileText,
      color: "bg-orange-500",
      href: "/evaluations",
    },
  ];

  const features = [
    {
      title: "Role Blueprints",
      description: "Create AI-powered role definitions with competencies and requirements",
      icon: Sparkles,
      href: "/roles",
    },
    {
      title: "Candidates",
      description: "Manage and track your candidates through the hiring pipeline",
      icon: Users,
      href: "/candidates",
    },
    {
      title: "Interview Kits",
      description: "Build structured interview questions and evaluation rubrics",
      icon: ClipboardList,
      href: "/interview-kits",
    },
    {
      title: "Scorecards",
      description: "Conduct consistent, competency-based candidate evaluations",
      icon: FileText,
      href: "/evaluations",
    },
    {
      title: "Workflows",
      description: "Design and manage your hiring pipelines",
      icon: GitBranch,
      href: "/workflows",
    },
    {
      title: "Comparison",
      description: "Compare candidates side-by-side with detailed analysis",
      icon: TrendingUp,
      href: "/comparison",
    },
    {
      title: "Decisions",
      description: "Generate AI-powered hiring decision briefs",
      icon: Brain,
      href: "/decisions",
    },
  ];

  return (
    <div className="space-y-8">
      {/* Welcome Section */}
      <div>
        <h1 className="text-3xl font-bold">
          Welcome back, {user?.full_name || "User"} 👋
        </h1>
        <p className="text-gray-600 mt-1">
          Here's what's happening with your hiring pipeline today.
        </p>
      </div>

      {/* Stats Grid */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
        {stats.map((stat) => (
          <Link key={stat.title} href={stat.href}>
            <Card className="hover:shadow-lg transition-shadow cursor-pointer">
              <CardContent className="p-6">
                <div className="flex items-center justify-between">
                  <div>
                    <p className="text-sm text-gray-500">{stat.title}</p>
                    <p className="text-3xl font-bold mt-1">{stat.value}</p>
                  </div>
                  <div className={`w-12 h-12 rounded-lg ${stat.color} flex items-center justify-center`}>
                    <stat.icon className="w-6 h-6 text-white" />
                  </div>
                </div>
              </CardContent>
            </Card>
          </Link>
        ))}
      </div>

      {/* Quick Actions */}
      <div>
        <h2 className="text-xl font-semibold mb-4">Quick Actions</h2>
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
          {features.slice(0, 6).map((feature) => (
            <Link key={feature.title} href={feature.href}>
              <Card className="hover:shadow-lg transition-shadow cursor-pointer h-full">
                <CardContent className="p-6">
                  <div className="flex items-start gap-4">
                    <div className="w-10 h-10 rounded-lg bg-blue-50 flex items-center justify-center flex-shrink-0">
                      <feature.icon className="w-5 h-5 text-blue-600" />
                    </div>
                    <div className="flex-1">
                      <h3 className="font-medium">{feature.title}</h3>
                      <p className="text-sm text-gray-500 mt-1 line-clamp-2">
                        {feature.description}
                      </p>
                    </div>
                    <ArrowRight className="w-4 h-4 text-gray-400 flex-shrink-0" />
                  </div>
                </CardContent>
              </Card>
            </Link>
          ))}
        </div>
      </div>

      {/* Recent Activity Placeholder */}
      <div>
        <h2 className="text-xl font-semibold mb-4">Recent Activity</h2>
        <Card>
          <CardContent className="p-6">
            <div className="text-center py-8">
              <p className="text-gray-500">No recent activity to show</p>
              <p className="text-sm text-gray-400 mt-1">
                Start by creating a role or adding a candidate
              </p>
              <div className="flex justify-center gap-4 mt-4">
                <Link href="/roles/create">
                  <Button variant="outline">
                    <Sparkles className="w-4 h-4 mr-2" />
                    Create Role
                  </Button>
                </Link>
                <Link href="/candidates">
                  <Button variant="outline">
                    <Users className="w-4 h-4 mr-2" />
                    View Candidates
                  </Button>
                </Link>
              </div>
            </div>
          </CardContent>
        </Card>
      </div>
    </div>
  );
}

