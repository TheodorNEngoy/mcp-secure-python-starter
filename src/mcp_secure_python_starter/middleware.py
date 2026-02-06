from __future__ import annotations

import os
from typing import Awaitable, Callable, Optional


class BodyTooLargeError(Exception):
    pass


def _get_header(scope, name: str) -> str:
    name_b = name.lower().encode("ascii")
    for k, v in scope.get("headers") or []:
        if k.lower() == name_b:
            try:
                return v.decode("utf-8")
            except Exception:
                return ""
    return ""


async def _send_json(send, status: int, body: str) -> None:
    await send(
        {
            "type": "http.response.start",
            "status": status,
            "headers": [(b"content-type", b"application/json")],
        }
    )
    await send({"type": "http.response.body", "body": body.encode("utf-8"), "more_body": False})


class MaxBodySizeMiddleware:
    def __init__(self, app, max_body_bytes: int) -> None:
        self.app = app
        self.max_body_bytes = int(max_body_bytes)

    async def __call__(self, scope, receive, send):
        if scope.get("type") != "http":
            return await self.app(scope, receive, send)

        # Fast fail on Content-Length when present.
        cl = _get_header(scope, "content-length")
        if cl:
            try:
                if int(cl) > self.max_body_bytes:
                    return await _send_json(send, 413, '{"detail":"Request body too large"}')
            except ValueError:
                pass

        received = 0

        async def limited_receive():
            nonlocal received
            msg = await receive()
            if msg.get("type") == "http.request":
                b = msg.get("body") or b""
                received += len(b)
                if received > self.max_body_bytes:
                    raise BodyTooLargeError()
            return msg

        try:
            return await self.app(scope, limited_receive, send)
        except BodyTooLargeError:
            return await _send_json(send, 413, '{"detail":"Request body too large"}')


class OptionalBearerAuthMiddleware:
    def __init__(self, app, token: Optional[str], exempt_paths: Optional[list[str]] = None) -> None:
        self.app = app
        self.token = token
        self.exempt_paths = set(exempt_paths or [])

    async def __call__(self, scope, receive, send):
        if not self.token:
            return await self.app(scope, receive, send)

        if scope.get("type") != "http":
            return await self.app(scope, receive, send)

        method = (scope.get("method") or "").upper()
        if method == "OPTIONS":
            return await self.app(scope, receive, send)

        path = scope.get("path") or ""
        if path in self.exempt_paths:
            return await self.app(scope, receive, send)

        auth = _get_header(scope, "authorization")
        expected = f"Bearer {self.token}"
        if auth != expected:
            return await _send_json(send, 401, '{"detail":"Unauthorized"}')

        return await self.app(scope, receive, send)


def env_int(name: str, default: int) -> int:
    v = os.getenv(name)
    if not v:
        return default
    try:
        return int(v)
    except ValueError:
        return default

