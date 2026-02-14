# Decision Brief Generator - Implementation TODO

## Backend Implementation

### 1. AI Schemas
- [x] Create `backend/app/modules/decisions/ai/schema.py`
  - [x] `DecisionBriefInput` - Input for generating decision brief
  - [x] `DecisionBriefOutput` - Structured output from AI
  - [x] `CandidateStrengths` sub-schema
  - [x] `RiskAreas` sub-schema
  - [x] `SignalGaps` sub-schema
  - [x] `InterviewAgreement` sub-schema
  - [x] `SuggestedDecision` sub-schema

### 2. AI Generator
- [x] Create `backend/app/modules/decisions/ai/decision_brief_generator.py`
  - [x] `DecisionBriefGenerator` class
  - [x] LLM prompt for generating structured briefs
  - [x] Method to generate candidate summary
  - [x] Method to identify strengths
  - [x] Method to identify risk areas
  - [x] Method to detect signal gaps
  - [x] Method to analyze interview agreement
  - [x] Method to generate suggested decision

### 3. Repository
- [x] Create `backend/app/modules/decisions/repository.py`
  - [x] `DecisionBriefRepository` class
  - [x] CRUD operations for candidate data
  - [x] Fetch evaluation data for candidates

### 4. Service
- [x] Create `backend/app/modules/decisions/service.py`
  - [x] `DecisionBriefService` class
  - [x] `generate_brief()` - Generate decision brief
  - [x] Signal gap detection

### 5. Router
- [x] Create `backend/app/modules/decisions/router.py`
  - [x] POST `/decisions/brief/generate` - Generate decision brief
  - [x] GET `/decisions/brief/{id}` - Get existing brief
  - [x] GET `/decisions/candidates/{candidate_id}/briefs` - Get candidate's briefs
  - [x] Additional endpoints for statistics and analysis

### 6. Main.py Update
- [x] Add decisions router to `backend/app/main.py`

## Frontend Implementation

### 7. API
- [x] Add decisionApi to `frontend/lib/api.ts`
  - [x] `generateBrief()` - Generate decision brief
  - [x] `getBrief()` - Get brief by ID
  - [x] `getCandidateBriefs()` - Get briefs for candidate
  - [x] Additional API methods

### 8. Hooks
- [x] Create `frontend/hooks/use-decisions.ts`
  - [x] `useGenerateDecisionBrief` - Mutation hook
  - [x] `useCandidateBriefs` - Query hook
  - [x] Additional hooks for statistics

### 9. Page
- [x] Create `frontend/app/decisions/page.tsx`
  - [x] Candidate selection
  - [x] Generate brief button
  - [x] Brief display components
  - [x] Strengths section
  - [x] Risk areas section
  - [x] Signal gaps section
  - [x] Interview agreement section
  - [x] Suggested decision section

### 10. Navigation Update
- [x] Update `frontend/app/layout.tsx`
  - [x] Add Decisions link to navigation

## COMPLETED ✅

The Decision Brief Generator module has been fully implemented with:
- Backend AI-powered decision brief generation
- Structured data analysis (strengths, risks, signal gaps, agreement)
- Frontend UI for generating and viewing decision briefs
- Full API integration


