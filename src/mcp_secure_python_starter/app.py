from __future__ import annotations

import os

from mcp.server.fastmcp import FastMCP
from starlette.applications import Starlette
from starlette.middleware import Middleware
from starlette.middleware.cors import CORSMiddleware
from starlette.responses import JSONResponse
from starlette.routing import Route

from .middleware import MaxBodySizeMiddleware, OptionalBearerAuthMiddleware, env_int


def _parse_csv_env(name: str, default: list[str]) -> list[str]:
    raw = os.getenv(name)
    if raw is None:
        return default
    vals = [s.strip() for s in raw.split(",")]
    vals = [s for s in vals if s]
    return vals


def _parse_bool_env(name: str, default: bool) -> bool:
    raw = os.getenv(name)
    if raw is None:
        return default
    return raw.strip().lower() in ("1", "true", "yes", "y", "on")


mcp = FastMCP(os.getenv("MCP_SERVER_NAME", "mcp-secure-python-starter"))


@mcp.tool()
def add(a: int, b: int) -> int:
    """Add two integers."""

    return a + b


async def healthz(request):
    return JSONResponse({"ok": True})


ALLOW_ORIGINS = _parse_csv_env(
    "MCP_CORS_ALLOW_ORIGINS",
    default=["http://localhost:3000", "http://127.0.0.1:3000"],
)
ALLOW_CREDENTIALS = _parse_bool_env("MCP_CORS_ALLOW_CREDENTIALS", default=False)
MAX_BODY_BYTES = env_int("MCP_MAX_BODY_BYTES", 256 * 1024)
AUTH_TOKEN = os.getenv("MCP_AUTH_TOKEN") or None

app = Starlette(
    routes=[Route("/healthz", healthz)],
    middleware=[
        # Outer-most: ensures preflight works and CORS headers are set even on 401/413 responses.
        Middleware(
            CORSMiddleware,
            allow_origins=ALLOW_ORIGINS,
            allow_credentials=ALLOW_CREDENTIALS,
            allow_methods=["GET", "POST", "DELETE"],
            allow_headers=["*"],
            expose_headers=["Mcp-Session-Id"],
        ),
        Middleware(OptionalBearerAuthMiddleware, token=AUTH_TOKEN, exempt_paths=["/healthz"]),
        Middleware(MaxBodySizeMiddleware, max_body_bytes=MAX_BODY_BYTES),
    ],
)

app.mount("/mcp", mcp.streamable_http_app())

