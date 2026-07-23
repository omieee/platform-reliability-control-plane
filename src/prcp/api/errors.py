from http import HTTPStatus
from typing import cast

from fastapi import FastAPI, Request
from fastapi.exceptions import RequestValidationError
from pydantic import BaseModel
from starlette.exceptions import HTTPException as StarletteHTTPException
from starlette.responses import JSONResponse
from starlette.types import ExceptionHandler

from prcp.exceptions import PRCPError


class ValidationIssue(BaseModel):
    field: str
    message: str


class ErrorOut(BaseModel):
    type: str
    title: str
    status: int
    detail: str
    instance: str
    errors: list[ValidationIssue] | None = None


async def prcp_error_handler(
    request: Request,
    exc: PRCPError,
) -> JSONResponse:
    error = ErrorOut(
        type=exc.error_type,
        title=exc.title,
        status=exc.status,
        detail=exc.detail,
        instance=request.url.path,
    )

    return JSONResponse(
        status_code=exc.status,
        content=error.model_dump(mode="json", exclude_none=True),
    )


async def validation_error_handler(
    request: Request,
    exc: RequestValidationError,
) -> JSONResponse:
    validation_issues = [
        ValidationIssue(
            field=".".join(str(part) for part in error["loc"]),
            message=error["msg"],
        )
        for error in exc.errors()
    ]

    error = ErrorOut(
        type="urn:prcp:error:validation-failed",
        title="Validation failed",
        status=422,
        detail="One or more request fields are invalid.",
        instance=request.url.path,
        errors=validation_issues,
    )

    return JSONResponse(
        status_code=422,
        content=error.model_dump(mode="json", exclude_none=True),
    )


async def http_exception_handler(
    request: Request,
    exc: StarletteHTTPException,
) -> JSONResponse:
    error = ErrorOut(
        type=f"urn:prcp:error:http-{exc.status_code}",
        title=HTTPStatus(exc.status_code).phrase,
        status=exc.status_code,
        detail=str(exc.detail),
        instance=request.url.path,
    )

    return JSONResponse(
        status_code=exc.status_code,
        content=error.model_dump(mode="json", exclude_none=True),
    )


def register_error_handlers(app: FastAPI) -> None:
    app.add_exception_handler(PRCPError, cast(ExceptionHandler, prcp_error_handler))
    app.add_exception_handler(
        RequestValidationError,
        cast(ExceptionHandler, validation_error_handler),
    )
    app.add_exception_handler(
        StarletteHTTPException,
        cast(ExceptionHandler, http_exception_handler),
    )
