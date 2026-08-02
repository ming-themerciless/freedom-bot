"""Extension loading for the Discord adapter.

Startup used to log a failed extension and carry on. That leaves the bot
running in a shape nobody chose: if `ext.error_handler` is the extension that
failed, every unhandled command error falls back to Pycord's default handling
instead of the safe, ephemeral message this repository requires, and raw
exception text — Google errors, connection strings, another player's state —
reaches Discord. A missing game command is a smaller failure but the same kind:
players cannot tell "the command is broken" from "the command was removed", and
the bot looks healthy while it is not.

Every extension in `main.EXTENSIONS` is therefore required.
"""
from __future__ import annotations

import logging
from collections.abc import Iterable
from typing import Protocol

logger = logging.getLogger(__name__)


class SupportsExtensions(Protocol):
    def load_extension(self, name: str) -> object: ...


class ExtensionLoadError(RuntimeError):
    """A required extension did not load, so the bot must not start."""

    def __init__(self, extension: str) -> None:
        super().__init__(
            f"Required extension {extension!r} could not be loaded. "
            "Refusing to start a partially functional bot."
        )
        self.extension = extension


def load_required_extensions(
    bot: SupportsExtensions, extensions: Iterable[str]
) -> list[str]:
    """Load every extension, or raise on the first that fails.

    Raising on the first failure rather than collecting them keeps the process
    log short and unambiguous: the traceback that matters is the first one. It
    goes to the bot's own log, never to Discord.
    """
    loaded: list[str] = []
    for extension in extensions:
        try:
            bot.load_extension(extension)
        except Exception as error:
            logger.exception("Failed loading required extension: %s", extension)
            raise ExtensionLoadError(extension) from error
        loaded.append(extension)
    return loaded
