from contextlib import asynccontextmanager

from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware

from app.api.routes import router
from app.config import get_settings
from app.logging_util import configure_logging
from app.services.factory import get_services

settings = get_settings()
configure_logging()


@asynccontextmanager
async def lifespan(_: FastAPI):
    get_services()
    yield


app = FastAPI(
    title="VeriChron AI",
    version="1.1.0",
    description="Bitemporal Governance & Audit Intelligence",
    lifespan=lifespan,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origin_list + ["http://127.0.0.1:3000", "http://frontend:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(router, prefix="/api")
from app.openclaw.tools_http import router as openclaw_tools_router

app.include_router(openclaw_tools_router, prefix="/api/internal/openclaw/tools")


@app.middleware("http")
async def request_id_mw(request: Request, call_next):
    from uuid import uuid4

    rid = request.headers.get("x-request-id") or uuid4().hex[:12]
    response = await call_next(request)
    response.headers["x-request-id"] = rid
    return response


@app.get("/")
def root():
    return {"name": "VeriChron AI", "tagline": "Bitemporal Governance & Audit Intelligence"}
