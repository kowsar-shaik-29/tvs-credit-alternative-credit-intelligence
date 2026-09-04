"""Main entry point for TVS Credit Alternative Credit Intelligence / NIRNAY API."""

import logging
import os
import sys
from contextlib import asynccontextmanager
from pathlib import Path
from fastapi import FastAPI, Request, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from fastapi.exceptions import RequestValidationError
from starlette.exceptions import HTTPException as StarletteHTTPException

# Ensure backend root is on sys.path
backend_dir = Path(__file__).resolve().parent
if str(backend_dir) not in sys.path:
    sys.path.insert(0, str(backend_dir))

from config.settings import settings
from app.api.routes import api_router
from app.services.model_service import model_service
from app.schemas.risk import ErrorResponse, ErrorDetail

# Configure structured logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S"
)
logger = logging.getLogger("tvs_credit.main")


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Lifespan event handler to load and verify ML artifacts once at startup."""
    logger.info("Initializing TVS Credit NIRNAY ML Engine...")
    try:
        model_service.load_artifacts()
        logger.info("TVS Credit NIRNAY ML Engine loaded successfully.")
    except Exception as e:
        logger.error(
            f"Failed to load model artifacts at startup: {e}. "
            "The service will run in degraded mode until artifacts are provided."
        )
    yield
    logger.info("Shutting down TVS Credit NIRNAY ML Engine...")


app = FastAPI(
    title="TVS Credit Alternative Credit Intelligence / NIRNAY API",
    description=(
        "Production REST API for alternative-credit risk assessment and intelligence. "
        "Evaluates applicant default risk, financial stability score, repayment capacity, "
        "and multi-tier approval recommendations using an Enhanced Random Forest model."
    ),
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc",
    openapi_url="/openapi.json",
    lifespan=lifespan
)

# CORS Configuration
logger.info(f"Configuring CORS with origins: {settings.cors_origins}")
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# Structured Error Handlers
@app.exception_handler(RequestValidationError)
async def validation_exception_handler(request: Request, exc: RequestValidationError):
    """Return clean, structured JSON errors for schema validation failures."""
    errors = exc.errors()
    first_error = errors[0] if errors else {}
    field = ".".join(str(loc) for loc in first_error.get("loc", []))
    msg = first_error.get("msg", "Invalid request parameter")
    error_message = f"Validation error at '{field}': {msg}"

    logger.warning(f"Validation failure: {error_message}")
    return JSONResponse(
        status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
        content=ErrorResponse(
            success=False,
            error=ErrorDetail(code="VALIDATION_ERROR", message=error_message)
        ).model_dump()
    )


@app.exception_handler(StarletteHTTPException)
async def http_exception_handler(request: Request, exc: StarletteHTTPException):
    """Return clean, structured JSON for HTTP exceptions without leaking paths."""
    code_map = {
        400: "BAD_REQUEST",
        404: "NOT_FOUND",
        422: "UNPROCESSABLE_ENTITY",
        500: "INTERNAL_SERVER_ERROR",
        503: "SERVICE_UNAVAILABLE"
    }
    code = code_map.get(exc.status_code, f"HTTP_{exc.status_code}")
    return JSONResponse(
        status_code=exc.status_code,
        content=ErrorResponse(
            success=False,
            error=ErrorDetail(code=code, message=str(exc.detail))
        ).model_dump()
    )


@app.exception_handler(Exception)
async def generic_exception_handler(request: Request, exc: Exception):
    """Catch-all for unhandled exceptions, hiding stack traces from clients."""
    logger.error(f"Unhandled server error: {exc}", exc_info=True)
    return JSONResponse(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        content=ErrorResponse(
            success=False,
            error=ErrorDetail(
                code="INTERNAL_SERVER_ERROR",
                message="An internal server error occurred while processing the request."
            )
        ).model_dump()
    )


# Include API Routes
app.include_router(api_router)


# Root health check redirect/convenience
@app.get("/", include_in_schema=False)
async def root():
    return {
        "service": "TVS Credit Alternative Credit Intelligence API",
        "version": "1.0.0",
        "docs": "/docs",
        "health": "/health"
    }


if __name__ == "__main__":
    import uvicorn
    # Support Cloud Run dynamic PORT variable
    port = int(os.environ.get("PORT", settings.PORT))
    host = os.environ.get("HOST", settings.HOST)
    uvicorn.run("main:app", host=host, port=port, reload=True)
