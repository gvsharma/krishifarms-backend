from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

from app.core.config import settings
from app.core.exceptions import AppError
from app.modules.audit.router import router as audit_router
from app.modules.auth.router import router as auth_router
from app.modules.dashboard.router import router as dashboard_router
from app.modules.documents.router import router as documents_router
from app.modules.financial.router import router as financial_router
from app.modules.master_data.router import router as master_data_router
from app.modules.users.router import router as users_router

app = FastAPI(
    title=settings.app_name,
    version="0.1.0",
    docs_url="/docs" if settings.debug else None,
    redoc_url="/redoc" if settings.debug else None,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origin_list,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

api_v1 = FastAPI(title=f"{settings.app_name} API v1")
api_v1.include_router(auth_router)
api_v1.include_router(users_router)
api_v1.include_router(master_data_router)
api_v1.include_router(financial_router)
api_v1.include_router(documents_router)
api_v1.include_router(audit_router)
api_v1.include_router(dashboard_router)


@api_v1.exception_handler(AppError)
async def app_error_handler(_: Request, exc: AppError):
    return JSONResponse(
        status_code=exc.status_code,
        content={
            "success": False,
            "error": {
                "message": exc.message,
                "details": exc.details,
            },
        },
    )


@api_v1.exception_handler(Exception)
async def unhandled_error_handler(_: Request, exc: Exception):
    message = str(exc) if settings.debug else "Internal server error"
    return JSONResponse(
        status_code=500,
        content={"success": False, "error": {"message": message}},
    )


app.mount("/api/v1", api_v1)


@app.get("/")
def root():
    return {"app": settings.app_name, "version": "0.1.0", "api": "/api/v1", "docs": "/api/v1/docs"}
