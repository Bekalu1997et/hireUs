# HireUs API Reference

Complete API reference for the HireUs platform. All API endpoints are prefixed with `/api/v1`.

## Base URL

```
http://localhost:8000/api/v1
```

## Interactive Documentation

- **Swagger UI**: http://localhost:8000/api/docs
- **ReDoc**: http://localhost:8000/api/redoc

---

## Table of Contents

- [Authentication](#authentication)
- [Roles](#roles)
- [Interview Kits](#interview-kits)
- [Workflows](#workflows)
- [Evaluations](#evaluations)
- [Comparison](#comparison)
- [Decisions](#decisions)
- [Candidates](#candidates)
- [Organizations](#organizations)

---

## Authentication

### Login

Authenticate user and receive access token.

**Endpoint:** `POST /auth/login/json`

**Request:**
```json
{
  "email": "user@example.com",
  "password": "password123"
}
```

**Response:**
```json
{
  "access_token": "eyJhbGciOiJIUzI1NiIs...",
  "refresh_token": "eyJhbGciOiJIUzI1NiIs...",
  "token_type": "bearer"
}
```

### Register

Register a new user account.

**Endpoint:** `POST /auth/register`

**Request:**
```json
{
  "email": "user@example.com",
  "password": "password123",
  "confirm_password": "password123",
  "full_name": "John Doe"
}
```

### Get Current User

Get authenticated user profile.

**Endpoint:** `GET /auth/me`

**Headers:**
```
Authorization: Bearer {access_token}
```

### Refresh Token

Refresh access token using refresh token.

**Endpoint:** `POST /auth/refresh`

**Request:**
```json
{
  "refresh_token": "eyJhbGciOiJIUzI1NiIs..."
}
```

---

## Roles

Manage job roles and position requirements.

### List Roles

**Endpoint:** `GET /roles/`

**Query Parameters:**
| Parameter | Type | Description |
|-----------|------|-------------|
| `skip` | int | Number of records to skip |
| `limit` | int | Maximum records to return |
| `is_active` | bool | Filter by active status |
| `search` | str | Search by title |

**Response:**
```json
{
  "data": [
    {
      "id": "uuid",
      "organization_id": "uuid",
      "title": "Senior Python Developer",
      "seniority": "senior",
      "department": "Engineering",
      "tech_stack": ["Python", "FastAPI", "PostgreSQL"],
      "core_competencies": [...],
      "mission": "Lead backend development...",
      "is_active": true,
      "created_at": "2024-01-01T00:00:00Z"
    }
  ],
  "total": 10
}
```

### Create Role

**Endpoint:** `POST /roles/`

**Request:**
```json
{
  "organization_id": "uuid",
  "title": "Senior Python Developer",
  "seniority": "senior",
  "department": "Engineering",
  "tech_stack": ["Python", "FastAPI"]
}
```

### Get Role by ID

**Endpoint:** `GET /roles/{role_id}`

### Update Role

**Endpoint:** `PUT /roles/{role_id}`

**Request:**
```json
{
  "title": "Lead Python Developer",
  "seniority": "lead",
  "core_competencies": [
    {"name": "System Design", "weight": 0.3},
    {"name": "Code Quality", "weight": 0.2}
  ]
}
```

### Delete Role

**Endpoint:** `DELETE /roles/{role_id}`

### AI: Generate Blueprint

Generate role requirements using AI.

**Endpoint:** `POST /roles/blueprint/generate`

**Request:**
```json
{
  "title": "Senior Python Developer",
  "seniority": "senior",
  "stack": ["Python", "FastAPI", "PostgreSQL"],
  "team_context": "Small team of 5 engineers"
}
```

**Response:**
```json
{
  "mission": "Lead backend architecture...",
  "core_competencies": [
    {"name": "Python Proficiency", "weight": 0.25},
    {"name": "System Design", "weight": 0.2}
  ],
  "must_have": {
    "skills": ["Python", "SQL"],
    "experience": "5+ years"
  },
  "nice_to_have": ["AWS", "Docker"]
}
```

### AI: Create Role with Blueprint

**Endpoint:** `POST /roles/blueprint/create`

---

## Interview Kits

Manage interview questions, rubrics, and evaluation criteria.

### List Interview Kits

**Endpoint:** `GET /interview-kits/`

**Query Parameters:**
| Parameter | Type | Description |
|-----------|------|-------------|
| `skip` | int | Pagination skip |
| `limit` | int | Pagination limit |
| `organization_id` | uuid | Filter by org |
| `role_id` | uuid | Filter by role |
| `interview_type` | str | Filter by type (coding, system_design, pm_case, behavioral) |
| `search` | str | Search query |

### Create Interview Kit

**Endpoint:** `POST /interview-kits/`

**Request:**
```json
{
  "organization_id": "uuid",
  "role_id": "uuid",
  "title": "Python Technical Interview",
  "type": "coding",
  "description": "Technical assessment for Python developers",
  "problem_statement": "Implement a rate limiter",
  "evaluation_rubric": [
    {"competency": "Code Quality", "max_score": 5},
    {"competency": "Problem Solving", "max_score": 5}
  ],
  "red_flags": ["No testing", "No error handling"],
  "estimated_duration_minutes": 60
}
```

### AI: Generate Interview Kit

Generate interview kit using AI.

**Endpoint:** `POST /interview-kits/generate`

**Request:**
```json
{
  "role_title": "Senior Python Developer",
  "seniority": "senior",
  "stack": ["Python", "FastAPI"],
  "interview_type": "coding",
  "competencies": ["Problem Solving", "System Design"],
  "duration_minutes": 60
}
```

### AI: Create with AI

Create and generate interview kit in one step.

**Endpoint:** `POST /interview-kits/create-with-ai`

### Get Kit Questions

**Endpoint:** `GET /interview-kits/{kit_id}/questions`

---

## Workflows

Manage candidate pipeline workflows.

### List Workflows

**Endpoint:** `GET /workflows/`

### Create Workflow

**Endpoint:** `POST /workflows/`

**Request:**
```json
{
  "organization_id": "uuid",
  "name": "Standard Engineering Pipeline",
  "description": "Default hiring pipeline",
  "stages": [
    {"id": "applied", "name": "Applied", "order": 1},
    {"id": "screening", "name": "Screening", "order": 2},
    {"id": "technical", "name": "Technical", "order": 3},
    {"id": "decision", "name": "Decision", "order": 4}
  ],
  "is_default": true
}
```

### Get Workflow by ID

**Endpoint:** `GET /workflows/{workflow_id}`

### Update Workflow

**Endpoint:** `PUT /workflows/{workflow_id}`

### Delete Workflow

**Endpoint:** `DELETE /workflows/{workflow_id}`

### Get Workflow Board

Get candidates in workflow stages.

**Endpoint:** `GET /workflows/{workflow_id}/board`

**Response:**
```json
{
  "stages": [
    {
      "id": "applied",
      "name": "Applied",
      "candidates": [
        {
          "id": "uuid",
          "name": "John Doe",
          "email": "john@example.com",
          "applied_at": "2024-01-01T00:00:00Z"
        }
      ]
    }
  ]
}
```

---

## Evaluations

Manage structured scorecards and interview feedback.

### List Evaluations

**Endpoint:** `GET /evaluations/`

**Query Parameters:**
| Parameter | Type | Description |
|-----------|------|-------------|
| `organization_id` | uuid | Filter by org |
| `role_id` | uuid | Filter by role |
| `candidate_id` | uuid | Filter by candidate |
| `is_submitted` | bool | Filter by submission status |
| `is_draft` | bool | Filter by draft status |

### Create Evaluation

**Endpoint:** `POST /evaluations/`

**Request:**
```json
{
  "candidate_id": "uuid",
  "assignment_id": "uuid",
  "scores": {
    "Problem Solving": 4,
    "Technical Skills": 5,
    "Communication": 3
  },
  "confidence": 4,
  "strengths": "Excellent problem-solving approach",
  "weaknesses": "Could improve on system design",
  "summary": "Strong candidate overall",
  "recommendation": "hire"
}
```

### Update Evaluation

**Endpoint:** `PUT /evaluations/{evaluation_id}`

### Submit Evaluation

Submit evaluation (required before candidate can progress).

**Endpoint:** `POST /evaluations/{evaluation_id}/submit`

**Query Parameters:**
| Parameter | Type | Description |
|-----------|------|-------------|
| `validate_first` | bool | Validate before submitting |

### Validate Evaluation

Check if evaluation is valid for submission.

**Endpoint:** `GET /evaluations/{evaluation_id}/validate`

### Get Candidate Scorecards

Get all evaluations for a candidate.

**Endpoint:** `GET /evaluations/candidates/{candidate_id}`

**Query Parameters:**
| Parameter | Type | Description |
|-----------|------|-------------|
| `submitted_only` | bool | Only submitted evaluations |

### Get Candidate Stats

Get aggregated statistics for a candidate.

**Endpoint:** `GET /evaluations/candidates/{candidate_id}/stats`

**Response:**
```json
{
  "total_evaluations": 3,
  "submitted_count": 2,
  "average_score": 4.2,
  "average_confidence": 3.8,
  "recommendations": {
    "hire": 2,
    "neutral": 1
  }
}
```

### AI: Improve Feedback

Improve feedback clarity using AI.

**Endpoint:** `POST /evaluations/{evaluation_id}/improve-feedback`

**Request:**
```json
{
  "target": "strengths",
  "context": "Make feedback more specific"
}
```

### AI: Generate Summary

Generate evaluation summary using AI.

**Endpoint:** `POST /evaluations/{evaluation_id}/generate-summary`

---

## Comparison

Compare candidates side-by-side.

### Compare Candidates

**Endpoint:** `POST /comparison/compare`

**Request:**
```json
{
  "candidate_ids": ["uuid1", "uuid2", "uuid3"],
  "include_evaluations": true,
  "include_feedback_summary": true
}
```

**Response:**
```json
{
  "candidates": [
    {
      "id": "uuid",
      "name": "John Doe",
      "average_score": 4.2,
      "competency_scores": {
        "Problem Solving": 4,
        "Technical Skills": 5
      },
      "confidence": 4.0,
      "feedback_count": 3
    }
  ],
  "comparison": {
    "overall_leader": "uuid1",
    "score_differences": {...}
  }
}
```

### Detect Signal Gaps

Identify weak areas in candidate evaluations.

**Endpoint:** `POST /comparison/signal-gaps`

**Request:**
```json
{
  "candidate_id": "uuid",
  "competency_threshold": 3.0,
  "confidence_threshold": 3.0,
  "variance_threshold": 1.5
}
```

**Response:**
```json
{
  "gaps": [
    {
      "competency": "System Design",
      "issue": "No evaluation found",
      "severity": "high",
      "recommendation": "Schedule system design interview"
    }
  ]
}
```

### Get Heatmap Data

Get competency heatmap for multiple candidates.

**Endpoint:** `GET /comparison/heatmap`

**Query Parameters:**
```
?candidate_ids=uuid1&candidate_ids=uuid2&candidate_ids=uuid3
```

### Rank Candidates

Rank candidates by criteria.

**Endpoint:** `GET /comparison/rank`

**Query Parameters:**
```
?candidate_ids=uuid1&candidate_ids=uuid2&criteria=overall_score
```

---

## Decisions

AI-powered hiring decision support.

### Generate Decision Brief

Generate comprehensive hiring brief for a candidate.

**Endpoint:** `POST /decisions/brief/generate`

**Query Parameters:**
```
?organization_id=uuid
```

**Request:**
```json
{
  "candidate_id": "uuid",
  "include_comparison": true,
  "comparison_candidate_ids": ["uuid1", "uuid2"],
  "focus_areas": ["technical skills", "team fit"]
}
```

**Response:**
```json
{
  "id": "uuid",
  "candidate_id": "uuid",
  "summary": "Strong technical candidate...",
  "strengths": [
    "Excellent problem-solving skills",
    "Strong Python proficiency"
  ],
  "risk_areas": [
    "Limited system design experience"
  ],
  "signal_gaps": [
    "No behavioral interview completed"
  ],
  "interview_agreement": 0.85,
  "recommendation": "hire",
  "recommendation_explanation": "Overall strong fit..."
}
```

### Get Candidate Briefs

Get all briefs for a candidate.

**Endpoint:** `GET /decisions/candidates/{candidate_id}/briefs`

**Query Parameters:**
```
?organization_id=uuid
```

### Get Signal Analysis

Get signal analysis for a candidate.

**Endpoint:** `GET /decisions/candidates/{candidate_id}/signal-analysis`

### Get Decision Summary

Get decision summaries across organization.

**Endpoint:** `GET /decisions/summary`

**Query Parameters:**
| Parameter | Type | Description |
|-----------|------|-------------|
| `organization_id` | uuid | Required |
| `role_id` | uuid | Filter by role |
| `min_evaluations` | int | Minimum evaluations |

---

## Candidates

Manage job candidates.

### List Candidates

**Endpoint:** `GET /candidates/`

**Query Parameters:**
| Parameter | Type | Description |
|-----------|------|-------------|
| `skip` | int | Pagination skip |
| `limit` | int | Pagination limit |
| `organization_id` | uuid | Filter by org |
| `role_id` | uuid | Filter by role |
| `workflow_id` | uuid | Filter by workflow |
| `stage_id` | str | Filter by stage |
| `status` | str | Filter by status |
| `search` | str | Search query |

### Create Candidate

**Endpoint:** `POST /candidates/`

**Request:**
```json
{
  "organization_id": "uuid",
  "first_name": "John",
  "last_name": "Doe",
  "email": "john@example.com",
  "phone": "+1234567890",
  "role_id": "uuid",
  "source": "linkedin",
  "resume_url": "https://..."
}
```

### Get Candidate by ID

**Endpoint:** `GET /candidates/{candidate_id}`

### Update Candidate

**Endpoint:** `PUT /candidates/{candidate_id}`

### Delete Candidate

**Endpoint:** `DELETE /candidates/{candidate_id}`

### Assign to Stage

Assign candidate to workflow stage.

**Endpoint:** `POST /candidates/{candidate_id}/assign-stage`

**Request:**
```json
{
  "workflow_id": "uuid",
  "stage_id": "technical"
}
```

### Move to Stage

Move candidate to different stage.

**Endpoint:** `POST /candidates/{candidate_id}/move-stage`

**Request:**
```json
{
  "stage_id": "decision",
  "notes": "Completed all technical interviews"
}
```

### Get Candidate Evaluations

Get all evaluations for a candidate.

**Endpoint:** `GET /candidates/{candidate_id}/evaluations`

### Get Candidate Activities

Get activity history for a candidate.

**Endpoint:** `GET /candidates/{candidate_id}/activities`

### Add Activity

Add activity note to candidate.

**Endpoint:** `POST /candidates/{candidate_id}/activities`

**Request:**
```json
{
  "activity_type": "note",
  "description": "Follow-up call scheduled",
  "metadata": {"call_time": "2024-01-15T10:00:00Z"}
}
```

---

## Organizations

Manage organizations (multi-tenant).

### List Organizations

**Endpoint:** `GET /organizations/`

### Create Organization

**Endpoint:** `POST /organizations/`

**Request:**
```json
{
  "name": "Acme Corp",
  "description": "Technology company",
  "website": "https://acme.com",
  "industry": "Technology",
  "size": "11-50",
  "location": "San Francisco, CA"
}
```

### Get Organization

**Endpoint:** `GET /organizations/{organization_id}`

### Update Organization

**Endpoint:** `PUT /organizations/{organization_id}`

### Delete Organization

**Endpoint:** `DELETE /organizations/{organization_id}`

### Get Organization Stats

Get statistics for organization.

**Endpoint:** `GET /organizations/stats`

**Query Parameters:**
```
?organization_id=uuid
```

### Get Organization Members

**Endpoint:** `GET /organizations/{organization_id}/members`

### Add Member

**Endpoint:** `POST /organizations/{organization_id}/members`

**Request:**
```json
{
  "user_id": "uuid",
  "role": "admin"
}
```

### Remove Member

**Endpoint:** `DELETE /organizations/{organization_id}/members/{user_id}`

---

## Error Responses

All endpoints may return error responses in the following format:

### 400 Bad Request
```json
{
  "detail": "Validation error message"
}
```

### 401 Unauthorized
```json
{
  "detail": "Not authenticated"
}
```

### 403 Forbidden
```json
{
  "detail": "Insufficient permissions"
}
```

### 404 Not Found
```json
{
  "detail": "Resource not found"
}
```

### 422 Validation Error
```json
{
  "detail": [
    {
      "loc": ["body", "email"],
      "msg": "field required",
      "type": "missing"
    }
  ]
}
```

### 500 Internal Server Error
```json
{
  "detail": "Internal server error"
}
```

---

## Rate Limits

| Endpoint | Limit |
|----------|-------|
| Authentication | 10 requests/minute |
| AI Endpoints | 20 requests/minute |
| Other Endends | 100 requests/minute |

---

## Pagination

List endpoints support pagination with the following response format:

```json
{
  "data": [...],
  "total": 100,
  "skip": 0,
  "limit": 20
}
```

Query parameters:
- `skip`: Number of records to skip (default: 0)
- `limit`: Maximum records to return (default: 20, max: 100)

