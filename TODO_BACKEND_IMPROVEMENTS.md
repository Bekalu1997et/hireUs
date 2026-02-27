# TODO: Backend Improvements Plan

## Phase 1: Fix Test Fixtures (Auth) ✅ COMPLETED
- [x] Fix test_user fixture to properly extract token from registration response
- [x] Fix auth_headers fixture to ensure proper token extraction
- [x] Added database and API test fixtures in conftest.py

## Phase 2: Add Unit Tests ✅ COMPLETED
- [x] Add unit tests for roles module (schemas, validation)
- [x] Add unit tests for workflows module (schemas, transitions)
- [x] Add unit tests for interview_kits module (schemas)
- [x] Existing tests: calculators, utils, security

## Phase 3: Fix Auth Issues ✅ COMPLETED
- [x] Fix hardcoded SECRET_KEY in config.py - use secure random fallback + env var
- [x] Add password validation enforcement in UserCreate schema
- [x] Add rate limiting config options

## Phase 4: Code Quality Improvements ✅ COMPLETED
- [x] Improved input validation in schemas (password validation)
- [x] CORS already properly configured for frontend integration

## Phase 5: Integration Readiness ✅ COMPLETED
- [x] Backend configured for frontend integration (CORS)
- [x] API endpoints ready
- [x] All test files created and ready to run

