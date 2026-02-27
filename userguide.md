# HireUs User Guide

## Overview
HireUs is a structured hiring platform that helps startups run consistent technical interviews. It guides teams through role definition, interview kit generation, workflow management, evaluations, signal aggregation, and final decisions. The system emphasizes repeatable processes, clear scoring, and traceability.

## User Types

### Founder
**Purpose**: Owns hiring strategy and final decisions.

**Why this is needed**: Founders are accountable for hiring quality and speed. The platform gives them a repeatable system for decisions based on structured data rather than gut feel.

**Key responsibilities**:
- Create the organization and manage the team.
- Define roles and competencies.
- Generate interview kits with AI.
- Create and manage candidate workflows.
- Review evaluations and signals.
- Generate decision briefs and record final decisions.
- Reopen workflows when a decision must be revised.

### Interviewer
**Purpose**: Conducts interviews and provides structured evaluations.

**Why this is needed**: Interviewers need clarity on what to evaluate and how to score candidates consistently. The platform provides structured kits and scorecards to reduce bias and variance.

**Key responsibilities**:
- Review interview questions and rubrics.
- Submit evaluations with competency scores and notes.
- Contribute evidence used for final decisions.

### Administrator (Optional)
**Purpose**: Manages system configuration and user access.

**Why this is needed**: Some teams separate admin tasks from hiring decisions. This role can manage organizations and users without influencing decision data.

**Key responsibilities**:
- Manage org settings and invitations.
- Assist with onboarding and access.

## Core Concepts

### Role and Competencies
A role defines the job and the competencies required for success. Competencies have weights that sum to 1.0. This drives both interview questions and evaluation scoring.

### Interview Kit
An interview kit is AI-generated and maps questions to competencies. Each question includes an evaluation rubric.

### Workflow
A workflow represents a candidate’s interview process. It includes ordered stages, each assigned to an interviewer.

### Evaluation
An evaluation is a structured scorecard. Interviewers score each competency and provide notes. All competencies must be scored.

### Signals
Signals aggregate evaluations into average competency scores and an overall weighted score.

### Decision Brief
A decision brief is AI-generated and summarizes evaluation data into strengths, concerns, and a recommendation.

### Final Decision
The founder records the final decision. Once recorded, the workflow is locked to protect integrity. It can be reopened with a reason if needed.

## User Journeys

### Founder Journey
1. Register and create an organization.
2. Invite interviewers to the team.
3. Create a role with competencies and weights.
4. Generate an interview kit for the role.
5. Create a workflow for a candidate and assign interviewers to stages.
6. Review evaluations as they arrive.
7. View aggregated signals for the candidate.
8. Generate a decision brief.
9. Record the final decision.

### Interviewer Journey
1. Join the organization via invitation.
2. Access assigned workflow stages.
3. Use the interview kit to conduct interviews.
4. Submit a structured evaluation with scores and notes.

## When to Use Each Feature

### Role Definition
Use when opening a new position or updating hiring criteria. It ensures every interview is aligned to the same competency model.

### Interview Kit Generation
Use after defining a role. It provides consistent questions and rubrics across interviewers.

### Workflow Creation
Use when a candidate enters the interview process. It enforces staged progression and assignment.

### Evaluation Submission
Use immediately after an interview. It ensures consistent scoring and captures evidence.

### Signals Aggregation
Use when comparing candidates or validating consistency across interviews. It summarizes signal quality.

### Decision Brief
Use after evaluations are complete. It provides a structured summary and recommendation.

### Final Decision
Use once the hiring team has enough signal. Locks the workflow for integrity.

### Reopen Workflow
Use only when a decision needs correction. Requires a reason and is auditable.

## Data Integrity and Trust

- All evaluations require full competency coverage.
- Workflow stages must follow the defined order.
- Decisions lock workflows to prevent silent modifications.
- Audit logs capture key mutations for accountability.

## Common Questions

**Can I edit a workflow after a decision?**
No. Workflows are locked after a decision. Founders can reopen with a reason if needed.

**Can interviewers change role definitions?**
No. Role creation and editing are founder-only actions.

**Can I use Ollama instead of OpenAI?**
Yes. The system falls back to Ollama when OpenAI is unavailable.

## API Endpoints Summary

### Authentication
- `POST /api/auth/register`
- `POST /api/auth/login`
- `GET /api/auth/me`

### Organization
- `GET /api/organizations/{org_id}`
- `PUT /api/organizations/{org_id}`
- `POST /api/auth/invite`
- `POST /api/auth/accept-invite`

### Roles
- `POST /api/roles`
- `GET /api/roles/{role_id}`
- `GET /api/roles`
- `PUT /api/roles/{role_id}`
- `DELETE /api/roles/{role_id}`

### Interview Kits
- `POST /api/interview-kits/generate`
- `GET /api/interview-kits/{kit_id}`
- `GET /api/interview-kits/role/{role_id}`

### Workflows
- `POST /api/workflows`
- `GET /api/workflows/{workflow_id}`
- `GET /api/workflows`
- `PUT /api/workflows/{workflow_id}/stages`
- `POST /api/workflows/{workflow_id}/reopen`
- `PATCH /api/workflows/{workflow_id}/notes`

### Evaluations
- `POST /api/evaluations`
- `GET /api/evaluations/{evaluation_id}`
- `GET /api/evaluations/workflow/{workflow_id}`

### Signals
- `GET /api/signals/candidate/{candidate_id}/role/{role_id}`

### Decisions
- `POST /api/decisions/generate-brief`
- `POST /api/decisions`
- `GET /api/decisions/{decision_id}`
- `GET /api/decisions/workflow/{workflow_id}`

## cURL Test Guide (By Role and Status)

Set environment variables:
```bash
export API=http://127.0.0.1:8000
```

### Authentication (Public)
1. Register Founder (201)
```bash
curl -s -X POST "$API/api/auth/register" \
  -H "Content-Type: application/json" \
  -d '{
    "email": "founder@example.com",
    "password": "StrongPass123",
    "full_name": "Founder User",
    "organization_name": "HireUs",
    "organization_domain": "hireus"
  }'
```

2. Login (200)
```bash
curl -s -X POST "$API/api/auth/login" \
  -H "Content-Type: application/json" \
  -d '{
    "email": "founder@example.com",
    "password": "StrongPass123"
  }'
```

3. Get current user (200)  
Role: Founder or Interviewer
```bash
export FOUNDER_TOKEN="PASTE_TOKEN"
curl -s -X GET "$API/api/auth/me" \
  -H "Authorization: Bearer $FOUNDER_TOKEN"
```

### Organization (Founder)
4. Get organization (200)
```bash
export ORG_ID=1
curl -s -X GET "$API/api/organizations/$ORG_ID" \
  -H "Authorization: Bearer $FOUNDER_TOKEN"
```

5. Update organization (200)
```bash
curl -s -X PUT "$API/api/organizations/$ORG_ID" \
  -H "Authorization: Bearer $FOUNDER_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"name":"HireUs Labs"}'
```

6. Invite interviewer (201)  
Role: Founder
```bash
curl -s -X POST "$API/api/auth/invite" \
  -H "Authorization: Bearer $FOUNDER_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "email":"interviewer@example.com",
    "full_name":"Interviewer One"
  }'
```

7. Accept invite (200)  
Role: Interviewer
```bash
export INVITE_TOKEN="PASTE_INVITE_TOKEN"
curl -s -X POST "$API/api/auth/accept-invite" \
  -H "Content-Type: application/json" \
  -d '{
    "token":"'"$INVITE_TOKEN"'",
    "password":"StrongPass123"
  }'
```

### Roles (Founder)
8. Create role (201)
```bash
curl -s -X POST "$API/api/roles" \
  -H "Authorization: Bearer $FOUNDER_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "title":"Backend Engineer",
    "description":"Build APIs",
    "seniority_level":"senior",
    "competencies":[
      {"name":"Python","description":"Python skills","weight":0.5},
      {"name":"System Design","description":"Design skills","weight":0.5}
    ]
  }'
```

9. Get role (200)
```bash
export ROLE_ID=1
curl -s -X GET "$API/api/roles/$ROLE_ID" \
  -H "Authorization: Bearer $FOUNDER_TOKEN"
```

10. List roles (200)
```bash
curl -s -X GET "$API/api/roles" \
  -H "Authorization: Bearer $FOUNDER_TOKEN"
```

11. Update role (200)
```bash
curl -s -X PUT "$API/api/roles/$ROLE_ID" \
  -H "Authorization: Bearer $FOUNDER_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"title":"Staff Backend Engineer"}'
```

12. Delete role (204)
```bash
curl -s -X DELETE "$API/api/roles/$ROLE_ID" \
  -H "Authorization: Bearer $FOUNDER_TOKEN"
```

### Interview Kits (Founder)
13. Generate interview kit (201)
```bash
curl -s -X POST "$API/api/interview-kits/generate" \
  -H "Authorization: Bearer $FOUNDER_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"role_id":1}'
```

14. Get interview kit (200)
```bash
export KIT_ID=1
curl -s -X GET "$API/api/interview-kits/$KIT_ID" \
  -H "Authorization: Bearer $FOUNDER_TOKEN"
```

15. List kits for role (200)
```bash
curl -s -X GET "$API/api/interview-kits/role/$ROLE_ID" \
  -H "Authorization: Bearer $FOUNDER_TOKEN"
```

### Workflows (Founder)
16. Create workflow (201)
```bash
curl -s -X POST "$API/api/workflows" \
  -H "Authorization: Bearer $FOUNDER_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "candidate":{"full_name":"Candidate A","email":"candidate@example.com"},
    "role_id":1,
    "stages":[
      {"interviewer_id":2,"stage_order":1}
    ]
  }'
```

17. Get workflow (200)  
Role: Founder or Interviewer
```bash
export WORKFLOW_ID=1
curl -s -X GET "$API/api/workflows/$WORKFLOW_ID" \
  -H "Authorization: Bearer $FOUNDER_TOKEN"
```

18. List workflows (200)
```bash
curl -s -X GET "$API/api/workflows" \
  -H "Authorization: Bearer $FOUNDER_TOKEN"
```

19. Update workflow stages (200)  
Role: Founder
```bash
curl -s -X PUT "$API/api/workflows/$WORKFLOW_ID/stages" \
  -H "Authorization: Bearer $FOUNDER_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "stages":[
      {"id":1,"interviewer_id":2}
    ]
  }'
```

20. Reopen workflow (200)  
Role: Founder
```bash
curl -s -X POST "$API/api/workflows/$WORKFLOW_ID/reopen" \
  -H "Authorization: Bearer $FOUNDER_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"reason":"Re-evaluate new evidence"}'
```

21. Update workflow notes (200)  
Role: Founder or Interviewer
```bash
curl -s -X PATCH "$API/api/workflows/$WORKFLOW_ID/notes" \
  -H "Authorization: Bearer $FOUNDER_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"notes":"Candidate showed strong system design."}'
```

### Evaluations (Interviewer)
22. Submit evaluation (201)
```bash
export INTERVIEWER_TOKEN="PASTE_INTERVIEWER_TOKEN"
curl -s -X POST "$API/api/evaluations" \
  -H "Authorization: Bearer $INTERVIEWER_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "workflow_id":1,
    "workflow_stage_id":1,
    "notes":"Good depth",
    "scores":[
      {"competency_id":1,"score":4},
      {"competency_id":2,"score":3}
    ]
  }'
```

23. Get evaluation (200)
```bash
export EVALUATION_ID=1
curl -s -X GET "$API/api/evaluations/$EVALUATION_ID" \
  -H "Authorization: Bearer $FOUNDER_TOKEN"
```

24. List evaluations for workflow (200)
```bash
curl -s -X GET "$API/api/evaluations/workflow/$WORKFLOW_ID" \
  -H "Authorization: Bearer $FOUNDER_TOKEN"
```

### Signals (Founder)
25. Get signals (200)
```bash
export CANDIDATE_ID=1
curl -s -X GET "$API/api/signals/candidate/$CANDIDATE_ID/role/$ROLE_ID" \
  -H "Authorization: Bearer $FOUNDER_TOKEN"
```

### Decisions (Founder)
26. Generate decision brief (200)
```bash
curl -s -X POST "$API/api/decisions/generate-brief" \
  -H "Authorization: Bearer $FOUNDER_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"workflow_id":1}'
```

27. Record decision (201)
```bash
curl -s -X POST "$API/api/decisions" \
  -H "Authorization: Bearer $FOUNDER_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "workflow_id":1,
    "outcome":"hire",
    "summary":"Strong candidate",
    "strengths":"System design",
    "concerns":"None",
    "recommendation":"Recommend hiring"
  }'
```

28. Get decision (200)
```bash
export DECISION_ID=1
curl -s -X GET "$API/api/decisions/$DECISION_ID" \
  -H "Authorization: Bearer $FOUNDER_TOKEN"
```

29. Get decision by workflow (200)
```bash
curl -s -X GET "$API/api/decisions/workflow/$WORKFLOW_ID" \
  -H "Authorization: Bearer $FOUNDER_TOKEN"
```
