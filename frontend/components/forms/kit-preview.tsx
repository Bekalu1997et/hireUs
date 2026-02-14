"use client";

import React from "react";
import { Button } from "@/components/ui/button";
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import {
  AIGeneratedKit,
  RubricCriterion,
  QuestionItem,
} from "@/hooks/use-interview-kits";

interface KitPreviewProps {
  kit: AIGeneratedKit;
  onAccept: () => void;
  onReject: () => void;
  isLoading?: boolean;
}

interface RubricCardProps {
  criterion: RubricCriterion;
}

function RubricCard({ criterion }: RubricCardProps) {
  return (
    <div className="border rounded-lg p-4">
      <div className="flex justify-between items-start mb-2">
        <h4 className="font-medium">{criterion.name}</h4>
        <Badge variant="outline">
          Max: {criterion.max_score} | Weight: {criterion.weight}
        </Badge>
      </div>
      <p className="text-sm text-gray-600">{criterion.description}</p>
    </div>
  );
}

interface QuestionCardProps {
  question: QuestionItem;
  index: number;
}

function QuestionCard({ question, index }: QuestionCardProps) {
  const difficultyColors = {
    easy: "bg-green-100 text-green-800",
    medium: "bg-yellow-100 text-yellow-800",
    hard: "bg-red-100 text-red-800",
  };

  return (
    <div className="border rounded-lg p-4">
      <div className="flex justify-between items-start mb-2">
        <div className="flex items-center gap-2">
          <Badge variant="secondary">{index + 1}</Badge>
          <Badge variant="outline">{question.type}</Badge>
        </div>
        <div className="flex items-center gap-2">
          <Badge className={difficultyColors[question.difficulty as keyof typeof difficultyColors] || "bg-gray-100"}>
            {question.difficulty}
          </Badge>
          <span className="text-sm text-gray-500">{question.duration_minutes} min</span>
        </div>
      </div>
      <p className="text-sm mb-2">{question.question}</p>
      {question.notes && (
        <p className="text-xs text-gray-500 italic">Note: {question.notes}</p>
      )}
    </div>
  );
}

export function KitPreview({ kit, onAccept, onReject, isLoading }: KitPreviewProps) {
  return (
    <div className="space-y-6">
      {/* Header */}
      <Card className="bg-blue-50 dark:bg-blue-900/20 border-blue-200">
        <CardContent className="p-4">
          <div className="flex items-center gap-3">
            <div className="flex-shrink-0 w-10 h-10 bg-blue-100 rounded-full flex items-center justify-center">
              <svg
                className="w-6 h-6 text-blue-600"
                fill="none"
                stroke="currentColor"
                viewBox="0 0 24 24"
              >
                <path
                  strokeLinecap="round"
                  strokeLinejoin="round"
                  strokeWidth={2}
                  d="M9.663 17h4.673M12 3v1m6.364 1.636l-.707.707M21 12h-1M4 12H3m3.343-5.657l-.707-.707m2.828 9.9a5 5 0 117.072 0l-.548.547A3.374 3.374 0 0014 18.469V19a2 2 0 11-4 0v-.531c0-.895-.356-1.754-.988-2.386l-.548-.547z"
                />
              </svg>
            </div>
            <div>
              <p className="font-medium text-blue-800">AI-Generated Interview Kit Ready</p>
              <p className="text-sm text-blue-600">Review and customize before creating</p>
            </div>
          </div>
        </CardContent>
      </Card>

      {/* Title */}
      <div>
        <h2 className="text-2xl font-bold">{kit.title}</h2>
      </div>

      {/* Problem Statement */}
      <Card>
        <CardHeader>
          <CardTitle>Problem Statement</CardTitle>
        </CardHeader>
        <CardContent>
          <p className="whitespace-pre-wrap">{kit.problem_statement}</p>
        </CardContent>
      </Card>

      {/* Evaluation Rubric */}
      <Card>
        <CardHeader>
          <CardTitle>Evaluation Rubric</CardTitle>
          <CardDescription>
            Criteria for scoring candidate performance
          </CardDescription>
        </CardHeader>
        <CardContent>
          <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
            {kit.evaluation_rubric.map((criterion, index) => (
              <RubricCard key={index} criterion={criterion} />
            ))}
          </div>
        </CardContent>
      </Card>

      {/* Red Flags */}
      <Card>
        <CardHeader>
          <CardTitle className="text-red-600">Red Flags</CardTitle>
          <CardDescription>Warning signs to watch for during the interview</CardDescription>
        </CardHeader>
        <CardContent>
          <ul className="list-disc list-inside space-y-2">
            {kit.red_flags.map((flag, index) => (
              <li key={index} className="text-sm">
                {flag}
              </li>
            ))}
          </ul>
        </CardContent>
      </Card>

      {/* Good Answer Outline */}
      <Card>
        <CardHeader>
          <CardTitle>Good Answer Outline</CardTitle>
          <CardDescription>Key points a strong candidate should cover</CardDescription>
        </CardHeader>
        <CardContent>
          <p className="whitespace-pre-wrap">{kit.good_answer_outline}</p>
        </CardContent>
      </Card>

      {/* Questions */}
      <Card>
        <CardHeader>
          <CardTitle>Interview Questions</CardTitle>
          <CardDescription>
            Structured questions for the interview
          </CardDescription>
        </CardHeader>
        <CardContent className="space-y-4">
          {kit.questions.map((question, index) => (
            <QuestionCard key={index} question={question} index={index} />
          ))}
        </CardContent>
      </Card>

      {/* Tips for Interviewer */}
      {kit.tips_for_interviewer && (
        <Card>
          <CardHeader>
            <CardTitle>Tips for Interviewer</CardTitle>
          </CardHeader>
          <CardContent>
            <p className="whitespace-pre-wrap">{kit.tips_for_interviewer}</p>
          </CardContent>
        </Card>
      )}

      {/* Duration Breakdown */}
      {kit.suggested_duration_breakdown && (
        <Card>
          <CardHeader>
            <CardTitle>Suggested Duration Breakdown</CardTitle>
          </CardHeader>
          <CardContent>
            <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
              {Object.entries(kit.suggested_duration_breakdown).map(([section, minutes]) => (
                <div key={section} className="text-center p-4 border rounded-lg">
                  <p className="text-2xl font-bold">{minutes}</p>
                  <p className="text-sm text-gray-500 capitalize">{section.replace("_", " ")}</p>
                </div>
              ))}
            </div>
          </CardContent>
        </Card>
      )}

      {/* Actions */}
      <div className="flex flex-col sm:flex-row gap-3 justify-end pt-4">
        <Button variant="outline" onClick={onReject} disabled={isLoading}>
          Reject & Edit Manually
        </Button>
        <Button onClick={onAccept} disabled={isLoading}>
          {isLoading ? "Creating..." : "Accept & Create Kit"}
        </Button>
      </div>
    </div>
  );
}

