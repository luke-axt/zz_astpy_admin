from contextlib import asynccontextmanager

from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse

from .db import init_db
from .openai_client import close_client
from .routers import openai, anthropic


@asynccontextmanager
async def lifespan(app: FastAPI):
    await init_db()
    yield
    await close_client()


app = FastAPI(
    title="AI Gateway",
    description="Team internal AI API Gateway",
    version="0.1.0",
    lifespan=lifespan,
)


@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    return JSONResponse(
        status_code=500,
        content={
            "error": {
                "message": str(exc),
                "type": "internal_error",
                "code": 500,
            }
        },
    )


app.include_router(openai.router, prefix="/openai")
app.include_router(anthropic.router, prefix="/anthropic")
