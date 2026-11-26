
import logging

from fastapi import FastAPI, Request

from fastapi.exceptions import RequestValidationError

from fastapi.responses import JSONResponse

from sqlalchemy.exc import (
    IntegrityError,
    OperationalError,
    SQLAlchemyError
)


logger = logging.getLogger(__name__)


def register_exception_handlers(app: FastAPI):

    # Invalid request data
    @app.exception_handler(RequestValidationError)
    async def validation_handler(
        request: Request,
        exc: RequestValidationError
    ):

        errors = []

        for error in exc.errors():

            errors.append({
                "loc": list(error["loc"]),
                "msg": error["msg"]
            })

        return JSONResponse(
            status_code=422,
            content={"detail": errors}
        )


    # Database constraint violations
    @app.exception_handler(IntegrityError)
    async def integrity_handler(
        request: Request,
        exc: IntegrityError
    ):

        diagnostics = getattr(
            exc.orig,
            "diag",
            None
        )

        constraint = getattr(
            diagnostics,
            "constraint_name",
            None
        )

        # Duplicate email at database level
        if constraint == "uq_students_email":

            return JSONResponse(
                status_code=409,
                content={
                    "detail": "This email is already registered"
                }
            )

        # Known database validation constraints
        if constraint in {
            "ck_students_mobile",
            "ck_students_course",
            "ck_students_name",
            "ck_students_email_lowercase"
        }:

            return JSONResponse(
                status_code=422,
                content={
                    "detail": "Student data violates validation rules"
                }
            )

        logger.error(
            "Database integrity error",
            exc_info=exc
        )

        return JSONResponse(
            status_code=500,
            content={
                "detail": "Unable to complete database operation"
            }
        )


    # Database connection or operational errors
    @app.exception_handler(OperationalError)
    async def operational_handler(
        request: Request,
        exc: OperationalError
    ):

        logger.error(
            "Database operational error",
            exc_info=exc
        )

        return JSONResponse(
            status_code=503,
            content={
                "detail": "Database temporarily unavailable"
            }
        )


    # Other SQLAlchemy errors
    @app.exception_handler(SQLAlchemyError)
    async def database_handler(
        request: Request,
        exc: SQLAlchemyError
    ):

        logger.error(
            "Database error",
            exc_info=exc
        )

        return JSONResponse(
            status_code=500,
            content={
                "detail": "A database error occurred"
            }
        )


    # Unexpected application errors
    @app.exception_handler(Exception)
    async def general_handler(
        request: Request,
        exc: Exception
    ):

        logger.error(
            "Unexpected application error",
            exc_info=exc
        )

        return JSONResponse(
            status_code=500,
            content={
                "detail": "An unexpected server error occurred"
            }
        )
