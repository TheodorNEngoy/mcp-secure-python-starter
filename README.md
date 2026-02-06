# mcp-secure-python-starter

Secure-by-default Python starter for Model Context Protocol (MCP) servers.

What this template prioritizes:

- CORS **allowlist** (no wildcard origins)
- Request body size limits
- Optional bearer token auth
- CI gate with `mcp-safety-scanner`

## Quickstart

Prereqs: Python 3.10+.

```bash
python -m venv .venv
source .venv/bin/activate
pip install -U pip
pip install -e .

# run
python -m mcp_secure_python_starter
```

The MCP endpoint is mounted at `http://127.0.0.1:8000/mcp`.

## Configuration

Copy `.env.example` to `.env` and edit as needed.

Key env vars:

- `MCP_CORS_ALLOW_ORIGINS`: comma-separated origin allowlist
- `MCP_MAX_BODY_BYTES`: request size limit (default: 256KiB)
- `MCP_AUTH_TOKEN`: if set, requires `Authorization: Bearer ...`

## Why These Defaults

Most real-world MCP incidents come from “easy” mistakes:

- wildcard CORS (`*`) on authenticated endpoints
- reflecting `Origin` without allowlist validation
- exposing shell/file capabilities with weak input validation

This repo is meant to make the safe path the easy path.

