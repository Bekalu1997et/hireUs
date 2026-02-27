"use client";

import Link from "next/link";
import { useAuth } from "@/hooks/context/use-auth";
import { Button } from "@/components/ui/button";
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";
import { Sparkles, Users, ClipboardList, BarChart3 } from "lucide-react";

export default function HomePage() {
  const { isAuthenticated, isLoading } = useAuth();

  return (
    <div className="min-h-screen">
      {/* Hero Section */}
      <section className="bg-gradient-to-b from-blue-50 to-white dark:from-blue-950 dark:to-background py-20">
        <div className="container mx-auto px-4 text-center">
          <h1 className="text-5xl font-bold mb-6 bg-gradient-to-r from-blue-600 to-purple-600 bg-clip-text text-transparent">
            HireUs
          </h1>
          <p className="text-xl text-gray-600 dark:text-gray-400 max-w-2xl mx-auto mb-8">
            AI-Powered Hiring Platform for Founders. Define roles, build interview kits,
            and make data-driven hiring decisions.
          </p>
          <div className="flex justify-center gap-4">
            {isLoading ? (
              <Button size="lg" disabled>Loading...</Button>
            ) : isAuthenticated ? (
              <Link href="/dashboard">
                <Button size="lg">
                  <Sparkles className="w-4 h-4 mr-2" />
                  Go to Dashboard
                </Button>
              </Link>
            ) : (
              <>
                <Link href="/auth/login">
                  <Button size="lg">
                    Sign In
                  </Button>
                </Link>
                <Link href="/auth/register">
                  <Button variant="outline" size="lg">
                    Create Account
                  </Button>
                </Link>
              </>
            )}
          </div>
        </div>
      </section>

      {/* Features Section */}
      <section className="py-20">
        <div className="container mx-auto px-4">
          <h2 className="text-3xl font-bold text-center mb-12">
            Everything You Need to Hire Better
          </h2>
          <div className="grid md:grid-cols-2 lg:grid-cols-4 gap-6">
            <Card>
              <CardHeader>
                <Sparkles className="w-10 h-10 text-blue-600 mb-2" />
                <CardTitle>Role Blueprints</CardTitle>
                <CardDescription>
                  AI-powered role definition with competencies and requirements
                </CardDescription>
              </CardHeader>
            </Card>

            <Card>
              <CardHeader>
                <ClipboardList className="w-10 h-10 text-green-600 mb-2" />
                <CardTitle>Interview Kits</CardTitle>
                <CardDescription>
                  Structured interview questions and evaluation rubrics
                </CardDescription>
              </CardHeader>
            </Card>

            <Card>
              <CardHeader>
                <Users className="w-10 h-10 text-purple-600 mb-2" />
                <CardTitle>Scorecards</CardTitle>
                <CardDescription>
                  Consistent, competency-based candidate evaluations
                </CardDescription>
              </CardHeader>
            </Card>

            <Card>
              <CardHeader>
                <BarChart3 className="w-10 h-10 text-orange-600 mb-2" />
                <CardTitle>Hiring Intelligence</CardTitle>
                <CardDescription>
                  Data-driven insights for better hiring decisions
                </CardDescription>
              </CardHeader>
            </Card>
          </div>
        </div>
      </section>

      {/* Quick Start Section */}
      <section className="py-20 bg-gray-50 dark:bg-gray-900">
        <div className="container mx-auto px-4 text-center">
          <h2 className="text-3xl font-bold mb-6">Get Started in Minutes</h2>
          <p className="text-gray-600 dark:text-gray-400 max-w-xl mx-auto mb-8">
            Create your first role blueprint with AI assistance. Define competencies,
            interview stages, and requirements automatically.
          </p>
          {isAuthenticated ? (
            <Link href="/dashboard">
              <Button size="lg">
                Go to Dashboard
              </Button>
            </Link>
          ) : (
            <Link href="/auth/register">
              <Button size="lg">
                Start Hiring Better Today
              </Button>
            </Link>
          )}
        </div>
      </section>

      {/* Footer */}
      <footer className="border-t py-8">
        <div className="container mx-auto px-4 text-center text-sm text-gray-600 dark:text-gray-400">
          <p>© 2024 HireUs. AI-Powered Hiring Platform.</p>
        </div>
      </footer>
    </div>
  );
}

