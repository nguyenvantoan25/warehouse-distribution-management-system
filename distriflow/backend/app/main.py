from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse
from fastapi.exceptions import RequestValidationError
from fastapi.middleware.cors import CORSMiddleware
from starlette.exceptions import HTTPException
from uuid import uuid4
from app.api.router import router as api_router
from fastapi import Depends
from sqlalchemy import text
from sqlalchemy.orm import Session
from sqlalchemy.exc import SQLAlchemyError
from app.core.database import get_db

app = FastAPI(title="DistriFlow API", version="0.2.0")
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://127.0.0.1:5173", "http://localhost:5173"],
    allow_credentials=True,
    allow_methods=["GET", "POST"],
    allow_headers=["Content-Type", "Idempotency-Key", "X-CSRF-Token"],
)
app.include_router(api_router)


@app.exception_handler(HTTPException)
async def http_error(request: Request, exc: HTTPException):
    error = exc.detail.get("error") if isinstance(exc.detail, dict) else None
    return JSONResponse(
        status_code=exc.status_code,
        content={
            "error": error
            or {
                "code": f"HTTP_{exc.status_code}",
                "message": str(exc.detail),
                "details": {},
            },
            "request_id": str(uuid4()),
        },
    )


@app.exception_handler(RequestValidationError)
async def validation_error(request: Request, exc: RequestValidationError):
    return JSONResponse(
        status_code=422,
        content={
            "error": {
                "code": "VALIDATION_ERROR",
                "message": "Dữ liệu đầu vào không hợp lệ",
                "details": {},
            },
            "request_id": str(uuid4()),
        },
    )


@app.get("/health")
def health():
    return {"status": "ok"}


@app.get("/health/ready")
def readiness(db: Session = Depends(get_db)):
    try:
        db.execute(text("SELECT 1"))
        return {"status": "ok", "database": db.get_bind().dialect.name}
    except SQLAlchemyError:
        raise HTTPException(503, "Database unavailable")
