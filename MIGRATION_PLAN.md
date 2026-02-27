# AI Code Migration Plan

## Objective
Migrate AI code from `backend/app/modules/ai/` to proper module locations and split into separate generators for better maintainability.

## Files to Create/Update

### 1. Core LLM Module (`backend/app/core/llm/`)

#### `backend/app/core/llm/schema.py`
- Add `InterviewType` enum (shared enum for all AI modules)
- Add `get_gemini_client()` function

### 2. Role AI Module (`backend/app/modules/roles/ai/`)

#### `backend/app/modules/roles/ai/__init__.py`
- Export role-specific schemas and generators

#### `backend/app/modules/roles/ai/schema.py`
- `RoleBlueprintInput`
- `Competency`
- `InterviewStage`
- `RoleBlueprintOutput`

#### `backend/app/modules/roles/ai/prompts.py`
- Role blueprint prompt template

#### `backend/app/modules/roles/ai/blueprint_generator.py`
- `BlueprintGenerator` class (split from GeminiClient)
- `get_blueprint_generator()` singleton

### 3. Interview Kit AI Module (`backend/app/modules/interview_kits/ai/`)

#### `backend/app/modules/interview_kits/ai/__init__.py`
- Export kit-specific schemas and generators

#### `backend/app/modules/interview_kits/ai/schema.py`
- `RubricCriterion`
- `QuestionItem`
- `InterviewKitInput`
- `InterviewKitOutput`

#### `backend/app/modules/interview_kits/ai/prompts.py`
- Interview kit prompt template

#### `backend/app/modules/interview_kits/ai/kit_generator.py`
- `KitGenerator` class (split from GeminiClient)
- `get_kit_generator()` singleton

### 4. Update Service Imports

#### `backend/app/modules/roles/service.py`
- Update imports to use new locations
- Use `get_blueprint_generator()` instead of `get_gemini_client()`

#### `backend/app/modules/interview_kits/service.py`
- Update imports to use new locations
- Use `get_kit_generator()` instead of `get_gemini_client()`

### 5. Cleanup

- Remove `backend/app/modules/ai/` directory (after verifying no other imports)

## Migration Order

1. ✅ Create core LLM schema with shared types
2. ✅ Create Role AI module files
3. ✅ Create Interview Kit AI module files
4. ✅ Update roles/service.py imports
5. ✅ Update interview_kits/service.py imports
6. ✅ Remove old AI module

## Verification Steps

1. Run tests to ensure functionality is preserved
2. Verify no import errors in the services
3. Test AI generation endpoints

