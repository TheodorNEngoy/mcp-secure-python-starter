from __future__ import annotations

import os

import uvicorn


def main() -> None:
    host = os.getenv("HOST", "127.0.0.1")
    port = int(os.getenv("PORT", "8000"))
    reload = os.getenv("RELOAD", "0").strip() in ("1", "true", "yes", "y", "on")

    uvicorn.run("mcp_secure_python_starter.app:app", host=host, port=port, reload=reload)


if __name__ == "__main__":
    main()

