# Structured Scorecards Implementation - TODO

## Backend Implementation

### 1. Pydantic Schemas
- [x] Create evaluation schemas in `backend/app/schemas/evaluation.py`
  - `ScorecardCreate` - Schema for creating scorecards
  - `ScorecardUpdate` - Schema for updating scorecards
  - `ScorecardResponse` - Response schema
  - `ScorecardListResponse` - Paginated list response
  - `CompetencyScore` - Individual competency score schema
  - `FeedbackRefineRequest/Response` - AI feedback improvement schemas

### 2. Repository Layer
- [x] Implement database operations in `backend/app/modules/evaluations/repository.py`
  - CRUD operations for feedbacks/scorecards
  - Get feedback by candidate_id, interviewer_id, assignment_id
  - List feedbacks with filters

### 3. Service Layer
- [x] Implement business logic in `backend/app/modules/evaluations/service.py`
  - Create/update/submit scorecards
  - Validate competencies against role requirements
  - AI feedback improvement integration

### 4. AI Feedback Refiner
- [x] Implement Gemini integration in `backend/app/modules/evaluations/ai/feedback_refiner.py`
  - Use existing GeminiLLM client
  - Improve feedback clarity endpoint
  - Suggest evidence for weak areas

### 5. Router/Endpoints
- [x] Add API endpoints in `backend/app/modules/evaluations/router.py`
  - POST /evaluations - Create scorecard
  - GET /evaluations/ - List scorecards
  - GET /evaluations/{id} - Get scorecard
  - PUT /evaluations/{id} - Update scorecard
  - POST /evaluations/{id}/submit - Submit scorecard
  - POST /evaluations/{id}/improve-feedback - AI enhancement
  - GET /evaluations/candidates/{id} - Get candidate scorecards

### 6. Main Application
- [x] Include evaluations router in `backend/app/main.py`

---

## Frontend Implementation

### 1. API Client
- [x] Add evaluation API endpoints in `frontend/lib/api.ts`

### 2. React Query Hooks
- [x] Create hooks in `frontend/hooks/use-evaluations.ts`
  - useScorecards, useScorecard
  - useCreateScorecard, useUpdateScorecard
  - useSubmitScorecard
  - useImproveFeedback (AI)

### 3. Scorecard Form Component
- [x] Create `frontend/components/forms/scorecard-form.tsx`
  - Competency list with 1-5 scoring
  - Evidence text areas
  - Confidence slider
  - Recommendation dropdown
  - Strengths/weaknesses text areas
  - Submit button with validation

### 4. Feedback Refiner Component
- [x] Create `frontend/components/forms/scorecard-form.tsx` (integrated)
  - "Improve Clarity" button
  - Show AI suggestions
  - Accept/reject AI suggestions

### 5. Evaluation Pages
- [x] Create `frontend/app/evaluations/page.tsx` - List all evaluations
- [x] Create `frontend/app/evaluations/[id]/page.tsx` - View/edit evaluation
- [x] Create `frontend/app/evaluations/create/page.tsx` - Create new evaluation

### 6. Layout/Navigation
- [ ] Add evaluations to navigation in `frontend/app/layout.tsx` (optional - can be added manually)

---

## Testing
- [ ] Write backend tests for evaluation endpoints
- [ ] Test AI feedback improvement functionality
- [ ] Test frontend components

---

## Features from FEATURES.md
- ✅ Competency-based scoring (1-5 scale)
- ✅ Required written evidence
- ✅ Confidence score
- ✅ "Improve feedback clarity" AI button using Gemini
- ✅ Submit-before-view rule

