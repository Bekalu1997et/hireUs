# Candidates Module

A FastAPI-based candidate management module for the HireUs recruitment platform. This module provides RESTful API endpoints for managing candidates within organizations, including CRUD operations, search, filtering, and statistics.

## Overview

The Candidates module is part of the HireUs backend architecture built with FastAPI and SQLAlchemy (async). It follows a layered architecture pattern with:

- **Router Layer**: Handles HTTP requests/responses
- **Service Layer**: Contains business logic
- **Repository Layer**: Manages database operations

## Features

- ✅ Create, read, update, and delete candidates
- ✅ Soft delete (deactivation) of candidates
- ✅ Search candidates by name, email, or company
- ✅ Filter candidates by role, workflow, active status, and source
- ✅ Pagination support for list endpoints
- ✅ Candidate statistics (total, active, inactive, by source, by role)
- ✅ Email existence check within an organization
- ✅ Candidate activation/deactivation

## Installation & Setup

### Prerequisites

- Python 3.10+
- PostgreSQL database
- FastAPI
- SQLAlchemy (async)

### Dependencies

Install the required dependencies:

```bash
pip install fastapi sqlalchemy asyncpg pydantic pydantic[email]
```

### Database Setup

The module uses SQLAlchemy async sessions. Ensure your database is configured in `app/db/session.py`:

```python
from app.db.session import get_db
```

### Register the Router

The candidate router is registered in `app/main.py`:

```python
from app.modules.candicates.router import router as candidates_router

app.include_router(candidates_router, prefix="/api/v1")
```

## API Endpoints

### Base Path
```
/candidates
```

### Endpoints Summary

| Method | Endpoint | Description |
|--------|----------|-------------|
| POST | `/candidates/` | Create a new candidate |
| GET | `/candidates/` | List candidates with filters and pagination |
| GET | `/candidates/search` | Search candidates by name, email, or company |
| GET | `/candidates/stats` | Get candidate statistics |
| GET | `/candidates/{candidate_id}` | Get a specific candidate |
| PUT | `/candidates/{candidate_id}` | Update a candidate |
| DELETE | `/candidates/{candidate_id}` | Soft delete a candidate |
| POST | `/candidates/{candidate_id}/activate` | Activate a candidate |
| POST | `/candidates/{candidate_id}/deactivate` | Deactivate a candidate |
| GET | `/candidates/check-email/{email}` | Check if email exists |

---

## Endpoint Details

### 1. Create Candidate

**POST** `/candidates/`

Creates a new candidate within an organization.

**Request Headers:**
- `Authorization`: Bearer token (required)

**Request Body:**
```json
{
  "email": "john.doe@example.com",
  "full_name": "John Doe",
  "phone": "+1234567890",
  "current_company": "Tech Corp",
  "current_position": "Software Engineer",
  "location": "San Francisco, CA",
  "linkedin_url": "https://linkedin.com/in/johndoe",
  "portfolio_url": "https://johndoe.dev",
  "resume_url": "https://example.com/resumes/johndoe.pdf",
  "source": "LinkedIn",
  "notes": "Excellent candidate with strong Python skills",
  "organization_id": "org-123-uuid",
  "role_id": "role-456-uuid",
  "workflow_id": "workflow-789-uuid",
  "metadata": {
    "referred_by": "Jane Smith",
    "priority": "high"
  }
}
```

**Response (201 Created):**
```json
{
  "id": "candidate-uuid",
  "email": "john.doe@example.com",
  "full_name": "John Doe",
  "phone": "+1234567890",
  "current_company": "Tech Corp",
  "current_position": "Software Engineer",
  "location": "San Francisco, CA",
  "linkedin_url": "https://linkedin.com/in/johndoe",
  "portfolio_url": "https://johndoe.dev",
  "resume_url": "https://example.com/resumes/johndoe.pdf",
  "source": "LinkedIn",
  "notes": "Excellent candidate with strong Python skills",
  "organization_id": "org-123-uuid",
  "role_id": "role-456-uuid",
  "workflow_id": "workflow-789-uuid",
  "metadata": {
    "referred_by": "Jane Smith",
    "priority": "high"
  },
  "is_active": true,
  "created_at": "2024-01-15T10:30:00Z",
  "updated_at": "2024-01-15T10:30:00Z"
}
```

**Error Responses:**
- `400 Bad Request`: Candidate with this email already exists
- `500 Internal Server Error`: Database or server error

---

### 2. List Candidates

**GET** `/candidates/`

Retrieves a paginated list of candidates with optional filters.

**Query Parameters:**
| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `organization_id` | string | Yes | Organization ID |
| `skip` | integer | No | Number of records to skip (default: 0) |
| `limit` | integer | No | Max records to return (default: 20, max: 100) |
| `role_id` | string | No | Filter by role ID |
| `workflow_id` | string | No | Filter by workflow ID |
| `is_active` | boolean | No | Filter by active status |
| `source` | string | No | Filter by source (e.g., "LinkedIn", "Referral") |

**Example Request:**
```
GET /candidates/?organization_id=org-123-uuid&skip=0&limit=20&role_id=role-456-uuid
```

**Response (200 OK):**
```json
{
  "candidates": [
    {
      "id": "candidate-uuid",
      "email": "john.doe@example.com",
      "full_name": "John Doe",
      "is_active": true,
      "source": "LinkedIn",
      ...
    }
  ],
  "total": 150,
  "skip": 0,
  "limit": 20
}
```

---

### 3. Search Candidates

**GET** `/candidates/search`

Searches candidates by name, email, or company.

**Query Parameters:**
| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `organization_id` | string | Yes | Organization ID |
| `query` | string | Yes | Search query (min 1 character) |
| `skip` | integer | No | Records to skip |
| `limit` | integer | No | Max records (default: 20, max: 100) |

**Example Request:**
```
GET /candidates/search?organization_id=org-123-uuid&query=john&limit=10
```

---

### 4. Get Candidate Statistics

**GET** `/candidates/stats`

Returns statistics about candidates in an organization.

**Query Parameters:**
| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `organization_id` | string | Yes | Organization ID |

**Response (200 OK):**
```json
{
  "total_candidates": 150,
  "active_candidates": 120,
  "inactive_candidates": 30,
  "by_source": {
    "LinkedIn": 50,
    "Referral": 30,
    "Direct": 40,
    "Indeed": 30
  },
  "by_role": {
    "role-uuid-1": 50,
    "role-uuid-2": 70,
    "role-uuid-3": 30
  }
}
```

---

### 5. Get Candidate by ID

**GET** `/candidates/{candidate_id}`

Retrieves a specific candidate by their ID.

**Path Parameters:**
| Parameter | Type | Description |
|-----------|------|-------------|
| `candidate_id` | string | The candidate's UUID |

**Response (200 OK):**
```json
{
  "id": "candidate-uuid",
  "email": "john.doe@example.com",
  "full_name": "John Doe",
  "is_active": true,
  ...
}
```

**Error Responses:**
- `404 Not Found`: Candidate not found

---

### 6. Update Candidate

**PUT** `/candidates/{candidate_id}`

Updates an existing candidate's information.

**Request Body:** (all fields optional)
```json
{
  "full_name": "John Updated Name",
  "current_position": "Senior Software Engineer",
  "location": "New York, NY"
}
```

**Response (200 OK):**
```json
{
  "id": "candidate-uuid",
  "email": "john.doe@example.com",
  "full_name": "John Updated Name",
  ...
}
```

---

### 7. Delete Candidate (Soft Delete)

**DELETE** `/candidates/{candidate_id}`

Soft deletes a candidate by setting `is_active` to `false`.

**Response:** `204 No Content`

---

### 8. Activate Candidate

**POST** `/candidates/{candidate_id}/activate`

Activates a previously deactivated candidate.

**Response (200 OK):**
```json
{
  "id": "candidate-uuid",
  "is_active": true,
  ...
}
```

---

### 9. Deactivate Candidate

**POST** `/candidates/{candidate_id}/deactivate`

Deactivates a candidate (soft delete).

**Response (200 OK):**
```json
{
  "id": "candidate-uuid",
  "is_active": false,
  ...
}
```

---

### 10. Check Email Exists

**GET** `/candidates/check-email/{email}`

Checks if a candidate with the given email exists in the organization.

**Path Parameters:**
| Parameter | Type | Description |
|-----------|------|-------------|
| `email` | string | Email to check |

**Query Parameters:**
| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `organization_id` | string | Yes | Organization ID |

**Response (200 OK):**
```json
{
  "exists": true
}
```

---

## Data Models

### Candidate Schema

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| `id` | string | Auto | Unique identifier (UUID) |
| `email` | EmailStr | Yes | Candidate's email address |
| `full_name` | string | Yes | Candidate's full name |
| `phone` | string | No | Phone number |
| `current_company` | string | No | Current employer |
| `current_position` | string | No | Current job title |
| `location` | string | No | Location |
| `linkedin_url` | string | No | LinkedIn profile URL |
| `portfolio_url` | string | No | Portfolio website URL |
| `resume_url` | string | No | Resume URL |
| `source` | string | No | Source (e.g., "LinkedIn", "Referral") |
| `notes` | string | No | Additional notes |
| `organization_id` | string | Yes | Organization UUID |
| `role_id` | string | No | Role UUID |
| `workflow_id` | string | No | Workflow UUID |
| `metadata` | dict | No | Custom metadata |
| `is_active` | boolean | Auto | Active status |
| `created_at` | datetime | Auto | Creation timestamp |
| `updated_at` | datetime | Auto | Last update timestamp |

---

## Usage Examples

### Python (using httpx)

```python
import httpx

BASE_URL = "http://localhost:8000/api/v1"
TOKEN = "your-jwt-token"

headers = {
    "Authorization": f"Bearer {TOKEN}",
    "Content-Type": "application/json"
}

# Create a candidate
candidate_data = {
    "email": "jane.doe@example.com",
    "full_name": "Jane Doe",
    "current_company": "Innovation Labs",
    "current_position": "Product Manager",
    "source": "Referral",
    "organization_id": "org-123-uuid"
}

response = httpx.post(
    f"{BASE_URL}/candidates/",
    json=candidate_data,
    headers=headers
)
print(response.json())

# List candidates with filters
params = {
    "organization_id": "org-123-uuid",
    "role_id": "role-456-uuid",
    "is_active": True,
    "skip": 0,
    "limit": 20
}

response = httpx.get(
    f"{BASE_URL}/candidates/",
    params=params,
    headers=headers
)
print(response.json())

# Search candidates
params = {
    "organization_id": "org-123-uuid",
    "query": "jane"
}

response = httpx.get(
    f"{BASE_URL}/candidates/search",
    params=params,
    headers=headers
)
print(response.json())
```

### cURL

```bash
# Create candidate
curl -X POST "http://localhost:8000/api/v1/candidates/" \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "email": "john.doe@example.com",
    "full_name": "John Doe",
    "organization_id": "org-123-uuid"
  }'

# List candidates
curl -X GET "http://localhost:8000/api/v1/candidates/?organization_id=org-123-uuid&limit=20" \
  -H "Authorization: Bearer YOUR_TOKEN"

# Get statistics
curl -X GET "http://localhost:8000/api/v1/candidates/stats?organization_id=org-123-uuid" \
  -H "Authorization: Bearer YOUR_TOKEN"
```

---

## Authentication

All endpoints require authentication using JWT tokens. Include the token in the `Authorization` header:

```
Authorization: Bearer <your-jwt-token>
```

The `get_current_active_user` dependency ensures:
- Valid JWT token is provided
- User is active and authorized

---

## Error Handling

The module uses standard HTTP status codes:

| Status Code | Description |
|-------------|-------------|
| 200 | Success |
| 201 | Created |
| 204 | No Content |
| 400 | Bad Request |
| 401 | Unauthorized |
| 404 | Not Found |
| 500 | Internal Server Error |

Error responses include a `detail` field with the error message:

```json
{
  "detail": "Candidate with this email already exists in the organization"
}
```

---

## File Structure

```
backend/app/modules/candicates/
├── __init__.py           # Package initialization
├── repository.py         # Database operations
├── router.py             # API route handlers
└── service.py            # Business logic
```

---

## Related Modules

- **Roles Module** (`app.modules.roles`): Job positions that candidates can apply to
- **Workflows Module** (`app.modules.workflows`): Candidate pipeline stages
- **Organizations Module** (`app.modules.organization`): Multi-tenant organization management
- **Auth Module** (`app.modules.auth`): Authentication and authorization

---

## Development Notes

### Async/Await Pattern

All database operations are asynchronous using SQLAlchemy async:

```python
async def get_candidates(self, ...):
    candidates = await self.repository.get_all(...)
    return candidates
```

### Soft Delete

The delete operation performs a soft delete by setting `is_active = False` instead of removing the record from the database.

### Email Uniqueness

Emails must be unique within an organization. The `create_candidate` service method validates this before creating a new record.

---

## License

This module is part of the HireUs platform. All rights reserved.
