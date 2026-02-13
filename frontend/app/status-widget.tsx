"use client";

import { useEffect, useState } from "react";

type Health = {
  status?: string;
  app?: string;
};

export default function StatusWidget() {
  const [health, setHealth] = useState<Health | null>(null);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    const base = process.env.NEXT_PUBLIC_API_BASE || "http://127.0.0.1:8000";
    fetch(`${base}/health`)
      .then((res) => res.json())
      .then((data) => setHealth(data))
      .catch((err) => setError(err?.message || "Unable to reach backend"));
  }, []);

  if (error) {
    return <div>Backend status: unavailable</div>;
  }

  if (!health) {
    return <div>Backend status: checking...</div>;
  }

  return (
    <div>
      Backend status: {health.status || "unknown"}{" "}
      {health.app ? `(${health.app})` : ""}
    </div>
  );
}
