"use client";

import { useState } from "react";
import { useAuth } from "../auth-context";

const API_BASE = process.env.NEXT_PUBLIC_API_BASE || "http://127.0.0.1:8000";

async function apiFetch(path: string, options: RequestInit = {}) {
  const res = await fetch(`${API_BASE}${path}`, {
    headers: {
      "Content-Type": "application/json",
      ...(options.headers || {})
    },
    ...options
  });
  const text = await res.text();
  let json: any = null;
  try {
    json = text ? JSON.parse(text) : null;
  } catch {
    json = text;
  }
  return { status: res.status, body: json };
}

export default function ConsolePage() {
  const { token, setToken, clearToken } = useAuth();
  const [lastAction, setLastAction] = useState("Idle");
  const [lastStatus, setLastStatus] = useState<number | null>(null);
  const [lastMessage, setLastMessage] = useState<string>("");
  const [loading, setLoading] = useState(false);
  const [orgId, setOrgId] = useState("1");
  const [roleId, setRoleId] = useState("1");
  const [kitId, setKitId] = useState("1");
  const [workflowId, setWorkflowId] = useState("1");
  const [evaluationId, setEvaluationId] = useState("1");
  const [decisionId, setDecisionId] = useState("1");
  const [candidateId, setCandidateId] = useState("1");
  const [inviteToken, setInviteToken] = useState("");
  const [registerForm, setRegisterForm] = useState({
    email: "founder@example.com",
    password: "StrongPass123",
    full_name: "Founder User",
    organization_name: "HireUs",
    organization_domain: "hireus"
  });
  const [loginForm, setLoginForm] = useState({
    email: "founder@example.com",
    password: "StrongPass123"
  });

  const authHeader = token ? { Authorization: `Bearer ${token}` } : {};

  const run = async (
    label: string,
    fn: () => Promise<{ status: number; body?: any }>
  ) => {
    setLastAction(label);
    setLoading(true);
    const res = await fn();
    setLastStatus(res.status);
    const detail =
      res.body?.detail ||
      res.body?.message ||
      (res.status >= 200 && res.status < 300 ? "Success" : "Request failed");
    setLastMessage(typeof detail === "string" ? detail : "Response received");
    setLoading(false);
  };

  return (
    <div className="page">
      <div className="container">
        <nav className="nav">
          <div className="brand">
            <span className="dot" />
            HireUs Console
          </div>
          <div className="cta">
            <a className="btn ghost" href="/">
              Home
            </a>
            <a className="btn ghost" href="/welcome">
              Welcome
            </a>
          </div>
        </nav>

        <section className="section fade-in">
          <h2>Authentication</h2>
          <p className="muted">
            Register or login. Tokens are saved automatically.
          </p>
          <div className="console-grid">
            <div className="card">
              <h3>Register Founder</h3>
              <div className="muted">Creates org + founder account.</div>
              <input
                style={{ width: "100%", padding: "10px", borderRadius: "10px", marginBottom: "8px" }}
                placeholder="email"
                value={registerForm.email}
                onChange={(e) => setRegisterForm({ ...registerForm, email: e.target.value })}
              />
              <input
                style={{ width: "100%", padding: "10px", borderRadius: "10px", marginBottom: "8px" }}
                placeholder="password"
                type="password"
                value={registerForm.password}
                onChange={(e) => setRegisterForm({ ...registerForm, password: e.target.value })}
              />
              <input
                style={{ width: "100%", padding: "10px", borderRadius: "10px", marginBottom: "8px" }}
                placeholder="full name"
                value={registerForm.full_name}
                onChange={(e) => setRegisterForm({ ...registerForm, full_name: e.target.value })}
              />
              <input
                style={{ width: "100%", padding: "10px", borderRadius: "10px", marginBottom: "8px" }}
                placeholder="organization name"
                value={registerForm.organization_name}
                onChange={(e) => setRegisterForm({ ...registerForm, organization_name: e.target.value })}
              />
              <input
                style={{ width: "100%", padding: "10px", borderRadius: "10px", marginBottom: "8px" }}
                placeholder="organization domain"
                value={registerForm.organization_domain}
                onChange={(e) => setRegisterForm({ ...registerForm, organization_domain: e.target.value })}
              />
            <button
              className="btn primary"
              onClick={async () => {
                  await run("Register Founder", async () => {
                    const result = await apiFetch("/api/auth/register", {
                      method: "POST",
                      body: JSON.stringify(registerForm)
                    });
                    if (result.body?.access_token) setToken(result.body.access_token);
                    return result;
                  });
                }}
            >
              Register + Save Token
            </button>
            </div>

            <div className="card">
              <h3>Login Founder</h3>
              <div className="muted">Use existing founder credentials.</div>
              <input
                style={{ width: "100%", padding: "10px", borderRadius: "10px", marginBottom: "8px" }}
                placeholder="email"
                value={loginForm.email}
                onChange={(e) => setLoginForm({ ...loginForm, email: e.target.value })}
              />
              <input
                style={{ width: "100%", padding: "10px", borderRadius: "10px", marginBottom: "8px" }}
                placeholder="password"
                type="password"
                value={loginForm.password}
                onChange={(e) => setLoginForm({ ...loginForm, password: e.target.value })}
              />
            <button
              className="btn primary"
              onClick={async () => {
                  await run("Login Founder", async () => {
                    const result = await apiFetch("/api/auth/login", {
                      method: "POST",
                      body: JSON.stringify(loginForm)
                    });
                    if (result.body?.access_token) setToken(result.body.access_token);
                    return result;
                  });
                }}
            >
              Login + Save Token
            </button>
            </div>

            <div className="card">
              <h3>Session</h3>
              <div style={{ marginBottom: "8px" }}>
                Token status: {token ? "Active" : "None"}
              </div>
              <button
                className="btn ghost"
                onClick={async () =>
                  run("Get Me", async () =>
                    apiFetch("/api/auth/me", { headers: authHeader })
                  )
                }
              >
                Get Me
              </button>
              <button className="btn ghost" onClick={clearToken}>
                Clear Token
              </button>
            </div>
          </div>
        </section>

        <section className="section fade-in">
          <h2>Organization</h2>
          <p className="muted">Manage org settings and invites.</p>
          <div className="console-grid">
            <input
              className="card"
              value={orgId}
              onChange={(e) => setOrgId(e.target.value)}
              placeholder="org_id"
            />
            <button
              className="btn ghost"
              onClick={async () =>
                run("Get Organization", async () =>
                  apiFetch(`/api/organizations/${orgId}`, { headers: authHeader })
                )
              }
            >
              Get Organization
            </button>
            <button
              className="btn ghost"
              onClick={async () =>
                run("Update Organization", async () =>
                  apiFetch(`/api/organizations/${orgId}`, {
                    method: "PUT",
                    headers: authHeader,
                    body: JSON.stringify({ name: "HireUs Labs" })
                  })
                )
              }
            >
              Update Organization
            </button>
            <button
              className="btn ghost"
              onClick={async () =>
                run("Invite Interviewer", async () =>
                  apiFetch("/api/auth/invite", {
                    method: "POST",
                    headers: authHeader,
                    body: JSON.stringify({
                      email: "interviewer@example.com",
                      full_name: "Interviewer One"
                    })
                  })
                )
              }
            >
              Invite Interviewer
            </button>
            <input
              className="card"
              value={inviteToken}
              onChange={(e) => setInviteToken(e.target.value)}
              placeholder="invite token"
            />
            <button
              className="btn ghost"
              onClick={async () =>
                run("Accept Invite", async () =>
                  apiFetch("/api/auth/accept-invite", {
                    method: "POST",
                    body: JSON.stringify({
                      token: inviteToken,
                      password: "StrongPass123"
                    })
                  })
                )
              }
            >
              Accept Invite
            </button>
          </div>
        </section>

        <section className="section fade-in">
          <h2>Roles</h2>
          <p className="muted">Define competencies and evaluation criteria.</p>
          <div className="console-grid">
            <button
              className="btn primary"
              onClick={async () =>
                run("Create Role", async () =>
                  apiFetch("/api/roles", {
                    method: "POST",
                    headers: authHeader,
                    body: JSON.stringify({
                      title: "Backend Engineer",
                      description: "Build APIs",
                      seniority_level: "senior",
                      competencies: [
                        { name: "Python", description: "Python skills", weight: 0.5 },
                        { name: "System Design", description: "Design skills", weight: 0.5 }
                      ]
                    })
                  })
                )
              }
            >
              Create Role
            </button>
            <input
              className="card"
              value={roleId}
              onChange={(e) => setRoleId(e.target.value)}
              placeholder="role_id"
            />
            <button
              className="btn ghost"
              onClick={async () =>
                run("Get Role", async () =>
                  apiFetch(`/api/roles/${roleId}`, { headers: authHeader })
                )
              }
            >
              Get Role
            </button>
            <button
              className="btn ghost"
              onClick={async () =>
                run("List Roles", async () =>
                  apiFetch("/api/roles", { headers: authHeader })
                )
              }
            >
              List Roles
            </button>
            <button
              className="btn ghost"
              onClick={async () =>
                run("Update Role", async () =>
                  apiFetch(`/api/roles/${roleId}`, {
                    method: "PUT",
                    headers: authHeader,
                    body: JSON.stringify({ title: "Staff Backend Engineer" })
                  })
                )
              }
            >
              Update Role
            </button>
            <button
              className="btn ghost"
              onClick={async () =>
                run("Delete Role", async () =>
                  apiFetch(`/api/roles/${roleId}`, {
                    method: "DELETE",
                    headers: authHeader
                  })
                )
              }
            >
              Delete Role
            </button>
          </div>
        </section>

        <section className="section fade-in">
          <h2>Interview Kits</h2>
          <p className="muted">Generate AI questions + rubrics.</p>
          <div className="console-grid">
            <button
              className="btn primary"
              onClick={async () =>
                run("Generate Kit", async () =>
                  apiFetch("/api/interview-kits/generate", {
                    method: "POST",
                    headers: authHeader,
                    body: JSON.stringify({ role_id: Number(roleId) })
                  })
                )
              }
            >
              Generate Kit
            </button>
            <input
              className="card"
              value={kitId}
              onChange={(e) => setKitId(e.target.value)}
              placeholder="kit_id"
            />
            <button
              className="btn ghost"
              onClick={async () =>
                run("Get Kit", async () =>
                  apiFetch(`/api/interview-kits/${kitId}`, { headers: authHeader })
                )
              }
            >
              Get Kit
            </button>
            <button
              className="btn ghost"
              onClick={async () =>
                run("List Kits", async () =>
                  apiFetch(`/api/interview-kits/role/${roleId}`, { headers: authHeader })
                )
              }
            >
              List Kits for Role
            </button>
          </div>
        </section>

        <section className="section fade-in">
          <h2>Workflows</h2>
          <p className="muted">Create candidate pipelines and stages.</p>
          <div className="console-grid">
            <button
              className="btn primary"
              onClick={async () =>
                run("Create Workflow", async () =>
                  apiFetch("/api/workflows", {
                    method: "POST",
                    headers: authHeader,
                    body: JSON.stringify({
                      candidate: { full_name: "Candidate A", email: "candidate@example.com" },
                      role_id: Number(roleId),
                      stages: [{ interviewer_id: 2, stage_order: 1 }]
                    })
                  })
                )
              }
            >
              Create Workflow
            </button>
            <input
              className="card"
              value={workflowId}
              onChange={(e) => setWorkflowId(e.target.value)}
              placeholder="workflow_id"
            />
            <button
              className="btn ghost"
              onClick={async () =>
                run("Get Workflow", async () =>
                  apiFetch(`/api/workflows/${workflowId}`, { headers: authHeader })
                )
              }
            >
              Get Workflow
            </button>
            <button
              className="btn ghost"
              onClick={async () =>
                run("List Workflows", async () =>
                  apiFetch("/api/workflows", { headers: authHeader })
                )
              }
            >
              List Workflows
            </button>
            <button
              className="btn ghost"
              onClick={async () =>
                run("Update Stages", async () =>
                  apiFetch(`/api/workflows/${workflowId}/stages`, {
                    method: "PUT",
                    headers: authHeader,
                    body: JSON.stringify({
                      stages: [{ id: 1, interviewer_id: 2 }]
                    })
                  })
                )
              }
            >
              Update Stages
            </button>
            <button
              className="btn ghost"
              onClick={async () =>
                run("Reopen Workflow", async () =>
                  apiFetch(`/api/workflows/${workflowId}/reopen`, {
                    method: "POST",
                    headers: authHeader,
                    body: JSON.stringify({ reason: "Re-evaluate candidate" })
                  })
                )
              }
            >
              Reopen Workflow
            </button>
            <button
              className="btn ghost"
              onClick={async () =>
                run("Update Notes", async () =>
                  apiFetch(`/api/workflows/${workflowId}/notes`, {
                    method: "PATCH",
                    headers: authHeader,
                    body: JSON.stringify({ notes: "Candidate showed strong system design." })
                  })
                )
              }
            >
              Update Notes
            </button>
          </div>
        </section>

        <section className="section fade-in">
          <h2>Evaluations</h2>
          <p className="muted">Interviewers submit scorecards.</p>
          <div className="console-grid">
            <button
              className="btn primary"
              onClick={async () =>
                run("Submit Evaluation", async () =>
                  apiFetch("/api/evaluations", {
                    method: "POST",
                    headers: authHeader,
                    body: JSON.stringify({
                      workflow_id: Number(workflowId),
                      workflow_stage_id: 1,
                      notes: "Good depth",
                      scores: [
                        { competency_id: 1, score: 4 },
                        { competency_id: 2, score: 3 }
                      ]
                    })
                  })
                )
              }
            >
              Submit Evaluation
            </button>
            <input
              className="card"
              value={evaluationId}
              onChange={(e) => setEvaluationId(e.target.value)}
              placeholder="evaluation_id"
            />
            <button
              className="btn ghost"
              onClick={async () =>
                run("Get Evaluation", async () =>
                  apiFetch(`/api/evaluations/${evaluationId}`, { headers: authHeader })
                )
              }
            >
              Get Evaluation
            </button>
            <button
              className="btn ghost"
              onClick={async () =>
                run("List Evaluations", async () =>
                  apiFetch(`/api/evaluations/workflow/${workflowId}`, { headers: authHeader })
                )
              }
            >
              List Evaluations
            </button>
          </div>
        </section>

        <section className="section fade-in">
          <h2>Signals</h2>
          <p className="muted">Aggregate scores for a candidate.</p>
          <div className="console-grid">
            <input
              className="card"
              value={candidateId}
              onChange={(e) => setCandidateId(e.target.value)}
              placeholder="candidate_id"
            />
            <button
              className="btn ghost"
              onClick={async () =>
                run("Get Signals", async () =>
                  apiFetch(`/api/signals/candidate/${candidateId}/role/${roleId}`, {
                    headers: authHeader
                  })
                )
              }
            >
              Get Signals
            </button>
          </div>
        </section>

        <section className="section fade-in">
          <h2>Decisions</h2>
          <p className="muted">Generate AI brief and record final decision.</p>
          <div className="console-grid">
            <button
              className="btn primary"
              onClick={async () =>
                run("Generate Brief", async () =>
                  apiFetch("/api/decisions/generate-brief", {
                    method: "POST",
                    headers: authHeader,
                    body: JSON.stringify({ workflow_id: Number(workflowId) })
                  })
                )
              }
            >
              Generate Brief
            </button>
            <button
              className="btn ghost"
              onClick={async () =>
                run("Record Decision", async () =>
                  apiFetch("/api/decisions", {
                    method: "POST",
                    headers: authHeader,
                    body: JSON.stringify({
                      workflow_id: Number(workflowId),
                      outcome: "hire",
                      summary: "Strong candidate",
                      strengths: "System design",
                      concerns: "None",
                      recommendation: "Recommend hiring"
                    })
                  })
                )
              }
            >
              Record Decision
            </button>
            <input
              className="card"
              value={decisionId}
              onChange={(e) => setDecisionId(e.target.value)}
              placeholder="decision_id"
            />
            <button
              className="btn ghost"
              onClick={async () =>
                run("Get Decision", async () =>
                  apiFetch(`/api/decisions/${decisionId}`, { headers: authHeader })
                )
              }
            >
              Get Decision
            </button>
            <button
              className="btn ghost"
              onClick={async () =>
                run("Get Decision by Workflow", async () =>
                  apiFetch(`/api/decisions/workflow/${workflowId}`, { headers: authHeader })
                )
              }
            >
              Get Decision by Workflow
            </button>
          </div>
        </section>

        <section className="section fade-in">
          <h2>Status</h2>
          <div className="card">
            <div className={`status-pill ${lastStatus && lastStatus >= 400 ? "error" : ""}`}>
              {loading ? "Working..." : `${lastAction} • ${lastStatus ? `HTTP ${lastStatus}` : "No requests yet"}`}
            </div>
            <div style={{ marginTop: "10px", color: "var(--muted)" }}>
              {lastMessage}
            </div>
          </div>
        </section>
      </div>
    </div>
  );
}
