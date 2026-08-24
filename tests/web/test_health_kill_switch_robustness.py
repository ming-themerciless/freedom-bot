"""C35-04 / F-13: an unreadable kill switch degrades health, it does not break it.

Observed on the deployed portal: `/healthz` returned the safe error page with a
correlation id instead of a health report, because `Path.exists()` raises rather
than answering when the process cannot traverse the containing directory.

The endpoint's whole purpose is to answer while something is wrong.
"""

from __future__ import annotations

import errno
from pathlib import Path

import pytest

from application.web.startup import _kill_switch_absent


class _RaisingPath:
    """A path whose `exists()` fails the way a real one does."""

    def __init__(self, error: OSError) -> None:
        self._error = error

    def exists(self) -> bool:
        raise self._error


def test_a_readable_absent_switch_is_absent(tmp_path: Path):
    assert _kill_switch_absent(tmp_path / "kill-switch") is True


def test_a_readable_present_switch_is_present(tmp_path: Path):
    switch = tmp_path / "kill-switch"
    switch.write_text("")
    assert _kill_switch_absent(switch) is False


@pytest.mark.parametrize(
    "error",
    [
        PermissionError(errno.EACCES, "Permission denied"),
        OSError(errno.ENOTDIR, "Not a directory"),
        OSError(errno.ELOOP, "Too many levels of symbolic links"),
    ],
    ids=["permission-denied", "not-a-directory", "symlink-loop"],
)
def test_an_unreadable_switch_fails_the_check_rather_than_raising(error: OSError):
    """**Fails closed, and does not propagate.**

    Two assertions in one: the call returns rather than raising — which is what
    keeps the endpoint answering — and it returns `False`, because a process that
    cannot see the switch cannot honestly report that the switch is off.
    """
    assert _kill_switch_absent(_RaisingPath(error)) is False


def test_the_unguarded_implementation_would_fail_this(tmp_path: Path):
    """Falsification, kept as a test rather than a claim in a document.

    This is what the code did before C35-04: the exception escaped, and the
    endpoint became a 500. If this ever stops raising, the guard above has been
    made vacuous and this test says so.
    """
    raising = _RaisingPath(PermissionError(errno.EACCES, "Permission denied"))
    with pytest.raises(PermissionError):
        not raising.exists()  # noqa: B015 - the unguarded expression, exactly as it was


# ---------------------------------------------------------------------------
# R35-10: the same property, proved at the ASGI boundary
# ---------------------------------------------------------------------------
# The helper tests above prove the guard. These prove what an operator actually
# receives, which is the thing that was broken: a generic safe-error page with a
# correlation id, where a health report was needed.

import pytest as _pytest

from application.web import startup as _startup


@_pytest.mark.parametrize(
    "error", [PermissionError(13, "Permission denied"), OSError(20, "Not a directory")],
    ids=["permission-denied", "not-a-directory"],
)
async def test_healthz_degrades_rather_than_returning_the_error_page(
    client, monkeypatch, error
):
    """The endpoint answers, and answers honestly."""
    monkeypatch.setattr(
        _startup, "_kill_switch_absent", lambda _path: _kill_switch_absent(_RaisingPath(error))
    )

    response = await client.get("/healthz")

    assert response.status_code in (200, 503), (
        "health must answer its own contract, not the generic error page"
    )
    body = response.json()
    assert body["status"] == "degraded"
    assert body["checks"]["kill_switch"] is False


async def test_healthz_leaks_no_diagnostic_when_the_switch_is_unreadable(
    client, monkeypatch
):
    """VM-16 carries check names and booleans. It must not start carrying more."""
    monkeypatch.setattr(
        _startup,
        "_kill_switch_absent",
        lambda _path: _kill_switch_absent(
            _RaisingPath(PermissionError(13, "Permission denied"))
        ),
    )

    response = await client.get("/healthz")
    raw = response.text

    for leak in (
        "Permission denied", "PermissionError", "Traceback", "errno", "13",
        "kill-switch", "/srv", "Not a directory", "startup.py",
    ):
        assert leak not in raw, f"the response disclosed {leak!r}"

    body = response.json()
    assert set(body) == {"status", "checks", "version", "environment"}, (
        "the health response shape changed"
    )
    assert all(isinstance(value, bool) for value in body["checks"].values())


async def test_the_unguarded_implementation_would_have_broken_the_endpoint(
    client, monkeypatch
):
    """Falsification at the boundary, kept as a test.

    Restores the pre-C35-04 behaviour — the raw `not path.exists()` — and shows the
    endpoint stops answering its contract. If this ever passes, the guard has been
    removed and the regression above has gone quiet.
    """
    monkeypatch.setattr(
        _startup,
        "_kill_switch_absent",
        lambda _path: not _RaisingPath(PermissionError(13, "Permission denied")).exists(),
    )

    with _pytest.raises(Exception):
        await client.get("/healthz")
