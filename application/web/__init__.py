"""The Freedom Blades web portal's application layer.

This package is imported by the `freedom-web` process and **never** by the
Discord bot. It deliberately does not import the bot's root `config.py`: that
module calls `sys.exit()` on a missing variable, which is fine for a bot and
wrong for a web process under a supervisor (topology §5). The web process builds
its configuration through `application.web.config.WebSettings.from_environment`,
which raises a typed error listing every problem instead.

`tests/test_web_configuration.py::test_the_web_module_graph_excludes_the_bot_config`
(startup refusal S-13) keeps that separation true rather than intended.
"""
from __future__ import annotations

#: The application version reported by `/healthz` (VM-16). It names the delivery
#: package rather than a release tag, because Phase 3 has not deployed one.
WEB_APPLICATION_VERSION = "phase-3-p3.1"

__all__ = ["WEB_APPLICATION_VERSION"]
