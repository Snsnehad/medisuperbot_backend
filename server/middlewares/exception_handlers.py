from fastapi import Request
from fastapi.responses import JSONResponse
from server.logger import logger


async def catch_exception_middleware(request: Request, call_next):
    try:
        return await call_next(request)
    except Exception as e:
        logger.exception("Unhandled exception caught by middleware")
        return JSONResponse(
            status_code=500,
            content={"detail": str(e)},
        )
