# Candidate Comparison Module Implementation

## Overview
Implementation of Module 5 - Candidate Comparison View for HireUs platform.

## Features
- Side-by-side competency scores comparison
- Average score calculation
- Standard deviation computation
- Interviewer confidence average
- Competency heatmap visualization
- Confidence variance analysis
- Written feedback summary
- Signal gap detection
- Candidate rankings

## Backend Implementation
- [x] Create comparison schemas (`schemas.py`)
- [x] Create comparison repository (`repository.py`)
- [x] Create statistical calculators (`calculators.py`)
- [x] Create comparison service (`service.py`)
- [x] Create comparison router (`router.py`)
- [x] Register router in main.py

## Frontend Implementation
- [x] Create comparison API endpoints (`lib/api.ts`)
- [x] Create comparison hooks (`hooks/use-comparison.ts`)
- [x] Create comparison page (`app/comparison/page.tsx`)

## API Endpoints
- `POST /comparison/compare` - Compare candidates side-by-side
- `POST /comparison/signal-gaps` - Detect signal gaps
- `GET /comparison/rank` - Rank candidates
- `POST /comparison/batch` - Batch compare many candidates
- `GET /comparison/heatmap` - Get heatmap data
- `GET /comparison/summary/{candidate_id}` - Get candidate summary
- `GET /comparison/role/{role_id}/candidates` - Get comparable candidates
- `GET /comparison/role/{role_id}/comparison` - Compare role candidates

## Testing
- [ ] Test API endpoints
- [ ] Test frontend integration
- [ ] Verify calculations accuracy

## Progress
Started: 2024
Status: Completed


