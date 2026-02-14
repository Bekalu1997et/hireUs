# HireUs Coding Guidelines

## Big Picture Architecture
- **Backend**: FastAPI modular architecture located in [backend/app/modules/](backend/app/modules/).
  - **Pattern**: `Router` -> `Service` -> `Repository` (optional but preferred).
  - **Data Layer**: SQLAlchemy for ORM [backend/app/db/models.py](backend/app/db/models.py), Pydantic for schemas [backend/app/schemas/](backend/app/schemas/).
  - **AI Integration**: Logic resides in `ai/` subdirectories within modules (e.g., [backend/app/modules/roles/ai/](backend/app/modules/roles/ai/)).
- **Frontend**: Next.js 14 App Router in [frontend/app/](frontend/app/).
  - **API Client**: Axios-based client in [frontend/lib/api.ts](frontend/lib/api.ts).
  - **State Management**: TanStack Query (React Query) hooks in [frontend/hooks/](frontend/hooks/) (e.g., `use-roles.ts`).
  - **UI**: Tailwind CSS with Shadcn/UI components in [frontend/components/ui/](frontend/components/ui/).

## Project Conventions
- **Naming**:
  - Backend: PascalCase for classes (`RoleService`), snake_case for methods and variables.
  - Frontend: camelCase for hooks and variables.
- **IDs**: Use string-based UUIDs for primary keys.
- **Caveat**: The "candidates" module is currently named `candicates` in [backend/app/modules/candicates/](backend/app/modules/candicates/). Preserve this spelling when modifying existing code in that path.

## Critical Workflows
- **Running Locally**:
  - Backend: `cd backend && uvicorn app.main:app --reload`
  - Frontend: `cd frontend && npm run dev`
  - Full Stack: `docker-compose up`
- **Migrations**: Use Alembic: `alembic revision --autogenerate -m "message"` and `alembic upgrade head`.
- **Testing**: Run backend tests with `pytest` in `backend/`. See fixtures in [backend/app/tests/conftest.py](backend/app/tests/conftest.py).

## Implementation Patterns
### Adding a new Backend Endpoint
1. Define Pydantic schemas in [backend/app/schemas/](backend/app/schemas/).
2. (Optional) Create `Repository` class in module for DB queries.
3. Create `Service` class for business logic.
4. Define `Router` and include it in [backend/app/main.py](backend/app/main.py).

### Creating a Frontend Feature
1. Add API methods to `roleApi` or equivalent in [frontend/lib/api.ts](frontend/lib/api.ts).
2. Create a custom hook in [frontend/hooks/](frontend/hooks/) using `useQuery` or `useMutation`.
3. Implement the UI in [frontend/app/](frontend/app/) using shared components.

## Integration Points
- **LLMs**: Core LLM providers (Gemini, GPT) are abstracted in [backend/app/core/llm/](backend/app/core/llm/).
- **Auth**: JWT-based. Protect routes with `get_current_active_user` in backend and `protected-route.tsx` in frontend.
