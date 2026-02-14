# Migration Progress

## Completed Tasks

### Core LLM Module (`backend/app/core/llm/`)
- [x] `schema.py` - Added `InterviewType` enum and `get_gemini_client()` function

### Role AI Module (`backend/app/modules/roles/ai/`)
- [x] `__init__.py` - Module exports with `__all__`
- [x] `schema.py` - Role blueprint schemas (Competency, InterviewStage, RoleBlueprintInput, RoleBlueprintOutput)
- [x] `prompts.py` - Role blueprint prompt templates
- [x] `blueprint_generator.py` - `BlueprintGenerator` class with singleton

### Interview Kit AI Module (`backend/app/modules/interview_kits/ai/`)
- [x] `__init__.py` - Module exports with `__all__`
- [x] `schema.py` - Interview kit schemas (RubricCriterion, QuestionItem, InterviewKitInput, InterviewKitOutput)
- [x] `prompts.py` - Interview kit prompt templates with type-specific guidance
- [x] `kit_generator.py` - `KitGenerator` class with singleton

### Service Updates
- [x] `roles/service.py` - Updated imports to use new AI module locations
- [x] `interview_kits/service.py` - Updated imports to use new AI module locations

### Cleanup
- [x] Removed `backend/app/modules/ai/` directory

## Verification
- [x] No files import from the old AI module
- [x] New module structure in place
- [x] Imports verified working

