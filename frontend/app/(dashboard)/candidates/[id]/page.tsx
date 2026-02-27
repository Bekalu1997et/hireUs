"use client";

import Link from "next/link";
import { useParams } from "next/navigation";
import { Button } from "@/components/ui/button";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { useCandidate } from "@/hooks/use-candidates";

export default function CandidateDetailPage() {
  const params = useParams<{ id: string }>();
  const candidateId = params?.id || null;
  const { data, isLoading, error } = useCandidate(candidateId);

  if (isLoading) {
    return <div className="container mx-auto py-8 px-4">Loading candidate...</div>;
  }

  if (error || !data) {
    return (
      <div className="container mx-auto py-8 px-4 space-y-4">
        <p className="text-red-600">Candidate not found.</p>
        <Link href="/candidates">
          <Button variant="outline">Back to Candidates</Button>
        </Link>
      </div>
    );
  }

  return (
    <div className="container mx-auto max-w-2xl py-8 px-4">
      <Card>
        <CardHeader>
          <CardTitle>{data.full_name}</CardTitle>
        </CardHeader>
        <CardContent className="space-y-2">
          <p>
            <span className="font-medium">Email:</span> {data.email}
          </p>
          <p>
            <span className="font-medium">Phone:</span> {data.phone || "-"}
          </p>
          <p>
            <span className="font-medium">Status:</span> {data.status}
          </p>
          <p>
            <span className="font-medium">Source:</span> {data.source || "-"}
          </p>
          <p>
            <span className="font-medium">Created:</span>{" "}
            {new Date(data.created_at).toLocaleString()}
          </p>
          <Link href="/candidates">
            <Button variant="outline" className="mt-4">
              Back to Candidates
            </Button>
          </Link>
        </CardContent>
      </Card>
    </div>
  );
}
