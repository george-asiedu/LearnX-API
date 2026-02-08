from fastapi import Request, status
from fastapi.responses import JSONResponse
from app.config.log import log
from app.utils.exceptions import APIException


async def global_exception_handler(request: Request, exc: Exception):
    # Default values for unhandled exceptions
    status_code = status.HTTP_500_INTERNAL_SERVER_ERROR
    message = 'An unexpected error occurred.'
    detail = None

    # Handle custom APIException
    if isinstance(exc, APIException):
        status_code = exc.status_code
        message = exc.message
        detail = exc.detail
        log.warning(f"API Error: {message} | Status: {status_code}")

    # Handle Database or other system errors
    else:
        log.error(f"Unhandled System Error: {str(exc)}", exc_info=True)
        if hasattr(exc, 'detail'):
            message = exc.detail

    return JSONResponse(
        status_code=status_code,
        content={
            "status": "error",
            "message": message,
            "detail": detail,
            "path": request.url.path,
        }
    )