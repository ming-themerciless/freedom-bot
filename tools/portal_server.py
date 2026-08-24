"""Operator entry point: build the portal for an ASGI server.

    ./venv-web/bin/python -m uvicorn tools.portal_server:application --factory

`create_app()` deliberately takes **exactly one** configuration authority — a
settings graph or a composition built from one — and refuses to be called with
neither, because a factory that silently read the environment would be a second
authority nothing could require to agree with the first. That refusal is correct,
and it means an ASGI server's `--factory` cannot call `create_app` directly: the
server calls it with no arguments.

This module is the missing half-line, and it lives in `tools/` because that is
where operator entry points live (`.agents/AGENTS.md`, repository map). It adds
no route, no view model, no dependency and no behaviour; it reads the environment
once, exactly as `tools.freedom_worker` does, and names which of the two
processes is reading so S-11 has its subject.

Authored 2026-08-23 by P3.5. It exists because the deployment step needed it, and
nothing before P3.5 ever started this process from a unit file.
"""

from __future__ import annotations

import os

from fastapi import FastAPI

from adapters.web.app import create_app
from application.web.config import ProcessRole, WebSettings


def application() -> FastAPI:
    """The ASGI application, built from this process's environment.

    A `ConfigurationError` here is deliberately allowed to propagate: it names
    every problem it found, and a supervisor restarting a process that cannot be
    configured is the intended outcome, not a caught exception and a half-built
    portal.
    """
    return create_app(
        WebSettings.from_environment(os.environ, process=ProcessRole.WEB)
    )


__all__ = ["application"]
