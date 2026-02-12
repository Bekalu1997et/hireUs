from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.core.config import settings


def create_application() -> FastAPI:
    """Create and configure the FastAPI application."""
    
    app = FastAPI(
        title=settings.app_name,
        debug=settings.debug,
        version="1.0.0",
    )
    
    # Configure CORS
    app.add_middleware(
        CORSMiddleware,
        allow_origins=settings.cors_origins,
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )
    
    # Register routers
    from app.modules.auth.router import router as auth_router
    app.include_router(auth_router, prefix="/api/auth", tags=["auth"])
    
    from app.modules.roles.router import router as roles_router
    app.include_router(roles_router, prefix="/api/roles", tags=["roles"])

    from app.modules.decisions.router import router as decisions_router
    app.include_router(decisions_router, prefix="/api/decisions", tags=["decisions"])

    from app.modules.evaluations.router import router as evaluations_router
    app.include_router(evaluations_router, prefix="/api/evaluations", tags=["evaluations"])

    from app.modules.interview_kits.router import router as interview_kits_router
    app.include_router(interview_kits_router, prefix="/api/interview-kits", tags=["interview-kits"])

    from app.modules.workflows.router import router as workflows_router
    app.include_router(workflows_router, prefix="/api/workflows", tags=["workflows"])

    from app.modules.organization.router import router as organization_router
    app.include_router(organization_router, prefix="/api", tags=["organization"])

    from app.modules.signals.router import router as signals_router
    app.include_router(signals_router, prefix="/api/signals", tags=["signals"])
    
    @app.get("/health")
    async def health_check():
        """Health check endpoint."""
        return {"status": "healthy", "app": settings.app_name}
    
    return app


app = create_application()


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "app.main:app",
        host="0.0.0.0",
        port=8000,
        reload=settings.debug,
    )
