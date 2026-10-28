from fastapi import FastAPI, Request
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse

from src.domain.exceptions.base import AppException


async def domain_exception_handler(request: Request, exc: AppException) -> JSONResponse:
    return JSONResponse(status_code=exc.http_status_code, content={"detail": exc.message})


async def request_validation_handler(request: Request, exc: RequestValidationError) -> JSONResponse:
    errors = [f"{' -> '.join(str(loc) for loc in e['loc'])}: {e['msg']}" for e in exc.errors()]
    return JSONResponse(status_code=422, content={"detail": "; ".join(errors)})


def register_exception_handlers(app: FastAPI) -> None:
    app.add_exception_handler(AppException, domain_exception_handler)  # type: ignore[arg-type]
    app.add_exception_handler(RequestValidationError, request_validation_handler)  # type: ignore[arg-type]
