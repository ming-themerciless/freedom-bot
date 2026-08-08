"""Composition owns the artifact store's descriptor, and gives it back.

Security review S-B-2's remediation anchors the artifact store to a directory
file descriptor held for the life of the service. That is what stops a pathname
replacement redirecting a write — and it is also a resource with an owner and a
lifetime, which the review asked to be defined explicitly rather than left to
the garbage collector.

The composition root is that owner. These prove it: what it opens it closes, on
the success path and on every refusal after the store has anchored itself.

Nothing here connects to a database. `create_engine` does not open a connection,
and no test in this file issues a statement.

`build_application` walks the directories *above* the artifact root at startup
and refuses unless each is owned by `root` or this account. That is a fact about
the host, not about descriptor ownership, and on a host whose temporary directory
is owned by `nobody` it refused these tests before they reached their own
assertions (review finding 3). So they pass a `TrustedAncestors` bounded at
pytest's temporary root — the same real rule, walking only the directories the
test created. `test_the_production_composition_walks_to_the_filesystem_root`
holds the seam itself to account.
"""
from __future__ import annotations

import os
from pathlib import Path

import pytest

from adapters.artifacts.filesystem import TrustedAncestors
from adapters.http.composition import (
    ARTIFACT_ROOT_VARIABLE,
    ConfigurationError,
    build_application,
)

PRINCIPALS = f"foundry-the-guild|foundry:snapshot:submit|{'a' * 64}"


@pytest.fixture()
def ancestors(tmp_path_factory) -> TrustedAncestors:
    return TrustedAncestors(ceiling=tmp_path_factory.getbasetemp())


def environment(root: Path, **overrides: str) -> dict[str, str]:
    values = {
        ARTIFACT_ROOT_VARIABLE: str(root),
        "FREEDOM_SNAPSHOT_PRINCIPALS": PRINCIPALS,
        "APP_ENVIRONMENT": "test",
        "DATABASE_URL": "postgresql+psycopg:///freedom_test",
    }
    values.update(overrides)
    return values


def descriptors_under(root: Path) -> list[str]:
    """Descriptors this process holds on `root` or anything inside it."""
    held: list[str] = []
    for number in os.listdir("/proc/self/fd"):
        try:
            target = os.readlink(f"/proc/self/fd/{number}")
        except OSError:
            continue
        if target == str(root) or target.startswith(f"{root}/"):
            held.append(target)
    return held


def test_composition_holds_one_descriptor_and_dispose_returns_it(tmp_path, ancestors):
    root = tmp_path / "artifacts"

    composition = build_application(environment(root), ancestors=ancestors)

    assert descriptors_under(root) == [str(root)]
    composition.dispose()
    assert descriptors_under(root) == []


def test_a_refused_startup_after_anchoring_leaves_no_descriptor(tmp_path, ancestors):
    """A malformed origin list is refused *after* the store has proved itself
    ready, which is the ordering that could leak. A service supervised by
    systemd restarts on failure, so a leak here is a leak per restart."""
    root = tmp_path / "artifacts"

    for _ in range(3):
        with pytest.raises(Exception):
            build_application(
                environment(root, FREEDOM_SNAPSHOT_ALLOWED_ORIGINS="not-an-origin"),
                ancestors=ancestors,
            )
        assert descriptors_under(root) == []


def test_the_production_composition_walks_to_the_filesystem_root(tmp_path):
    """The seam above is a test seam, and this is what stops it becoming a
    deployment one: composed from configuration alone, the store gets the
    unbounded production walk. There is no environment variable that narrows it,
    which is asserted here rather than left as an intention."""
    root = tmp_path / "artifacts"
    environ = environment(root)
    assert not any("ANCESTOR" in name.upper() for name in environ)

    try:
        composition = build_application(environ)
    except ConfigurationError as refusal:
        # A host whose `/` or temporary directory is owned by a third account.
        # The walk reached them, which is the point being made.
        assert "root_ancestor_untrusted" in str(refusal)
        assert descriptors_under(root) == []
        return
    try:
        assert composition.artifacts.ancestors.ceiling is None
    finally:
        composition.dispose()


def test_an_unusable_root_is_refused_without_holding_it(tmp_path):
    root = tmp_path / "permissive"
    root.mkdir()
    root.chmod(0o755)

    with pytest.raises(ConfigurationError) as refusal:
        build_application(environment(root))

    assert "root_permissive" in str(refusal.value)
    # The reason, never the path (`docs/operations/…` §5.6).
    assert str(root) not in str(refusal.value)
    assert descriptors_under(root) == []
