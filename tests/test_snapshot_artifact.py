"""Ingestion refuses before it parses, and identifies before it refuses."""
from __future__ import annotations

import hashlib

import pytest

from application.foundry.artifact import (
    DEFAULT_MAX_BYTES,
    IngestionLimits,
    SnapshotArtifact,
    SnapshotRejected,
    ingest_bytes,
    read_artifact,
    safe_artifact_name,
)
from domain.foundry import SnapshotChecksum
from tests import foundry_fixtures as fx


def payload() -> bytes:
    return fx.encode(fx.bundle())


def test_checksum_is_the_sha256_of_the_original_bytes():
    data = payload()

    artifact = ingest_bytes(data)

    assert artifact.checksum.hex_digest == hashlib.sha256(data).hexdigest()
    assert artifact.raw_bytes() == data
    assert artifact.size_bytes == len(data)


def test_one_changed_byte_is_a_different_snapshot():
    original = ingest_bytes(payload())
    tampered = ingest_bytes(
        fx.tamper(payload(), find=b"Brightlantern", replace=b"Brightlantexn")
    )

    assert original.checksum != tampered.checksum
    # Identity is the whole digest, never a prefix.
    assert original.checksum.hex_digest != tampered.checksum.hex_digest


def test_verify_refuses_bytes_that_no_longer_hash_to_the_recorded_checksum():
    artifact = SnapshotArtifact(
        b'{"a":1}', SnapshotChecksum.of(b'{"a":2}')
    )

    with pytest.raises(SnapshotRejected) as refusal:
        artifact.verify()

    assert refusal.value.code == "checksum_mismatch"


def test_a_refusal_after_hashing_still_names_the_artifact():
    # Everything after the checksum step can name which bytes were refused, so
    # an audit record of a refusal is about a specific artifact.
    with pytest.raises(SnapshotRejected) as refusal:
        ingest_bytes(b'{"a": ' + b"[" * 100 + b"]" * 100 + b"}")

    assert refusal.value.code == "excessive_nesting"
    assert refusal.value.checksum is not None


def test_an_empty_artifact_is_refused():
    with pytest.raises(SnapshotRejected) as refusal:
        ingest_bytes(b"")

    assert refusal.value.code == "empty_artifact"


def test_an_oversized_artifact_is_refused_without_being_parsed():
    with pytest.raises(SnapshotRejected) as refusal:
        ingest_bytes(payload(), limits=IngestionLimits(max_bytes=16))

    assert refusal.value.code == "artifact_too_large"
    # No checksum: the bytes were never taken in.
    assert refusal.value.checksum is None


@pytest.mark.parametrize(
    ("data", "description"),
    [
        (b"PK\x03\x04rest of a zip", "zip"),
        (b"\x1f\x8b\x08gzipped", "gzip"),
        (b"BZh9bzipped", "bzip2"),
        (b"\xfd7zXZ\x00xz", "xz"),
        (b"7z\xbc\xaf\x27\x1c7zip", "7-zip"),
        (b"Rar!\x1a\x07rar", "rar"),
        (b"\x7fELF\x02\x01", "elf"),
        (b"MZ\x90\x00exe", "dos"),
        (b"#!/bin/sh\necho hi\n", "script"),
        (b"%PDF-1.7", "pdf"),
        (b"\x89PNG\r\n\x1a\n", "png"),
        (b"SQLite format 3\x00", "sqlite"),
        (b"\x00" * 512 + b"ustar\x0000" + b"\x00" * 100, "tar"),
    ],
)
def test_archives_and_executables_are_refused_unopened(data, description):
    with pytest.raises(SnapshotRejected) as refusal:
        ingest_bytes(data)

    assert refusal.value.code in {"unsupported_container", "binary_artifact"}


def test_a_byte_order_mark_is_refused_because_it_changes_the_identity():
    with pytest.raises(SnapshotRejected) as refusal:
        ingest_bytes(b"\xef\xbb\xbf" + payload())

    assert refusal.value.code == "byte_order_mark"


def test_invalid_utf8_is_refused_without_echoing_the_bytes():
    with pytest.raises(SnapshotRejected) as refusal:
        ingest_bytes(b'{"name": "\xff\xfe"}')

    assert refusal.value.code == "invalid_encoding"
    assert "\\xff" not in str(refusal.value)


def test_excessive_nesting_is_refused_by_scanning_not_by_parsing():
    deep = b'{"a":' + b'{"a":' * 200 + b"1" + b"}" * 200 + b"}"

    with pytest.raises(SnapshotRejected) as refusal:
        ingest_bytes(deep, limits=IngestionLimits(max_depth=64))

    assert refusal.value.code == "excessive_nesting"


def test_a_brace_inside_a_string_is_not_structure():
    document = fx.bundle(actors=(fx.actor(name="Testcharacter {of} Braces"),))

    artifact = ingest_bytes(fx.encode(document), limits=IngestionLimits(max_depth=8))

    assert artifact.size_bytes > 0


@pytest.mark.parametrize(
    "data",
    [b'{"a": 1', b'{"a": 1}}', b'{"a": "unterminated'],
)
def test_unbalanced_structure_is_refused_before_parsing(data):
    with pytest.raises(SnapshotRejected) as refusal:
        ingest_bytes(data)

    assert refusal.value.code == "malformed_json"


@pytest.mark.parametrize(
    "name",
    [
        "../escape.json",
        "/absolute/snapshot.json",
        "dir/snapshot.json",
        "dir\\snapshot.json",
        "snapshot.json.exe",
        "snapshot.tar.gz",
        ".hidden.json",
        "snapshot",
        "snap\x00shot.json",
        "s" * 200 + ".json",
    ],
)
def test_path_bearing_and_unsafe_names_are_refused_not_sanitised(name):
    with pytest.raises(SnapshotRejected) as refusal:
        safe_artifact_name(name)

    assert refusal.value.code == "unsafe_artifact_name"


def test_a_plain_name_is_accepted_and_recorded():
    artifact = ingest_bytes(payload(), source_name="the-guild-2026-08-02.json")

    assert artifact.source_name == "the-guild-2026-08-02.json"


def test_reading_from_disk_applies_the_same_bounds(tmp_path):
    path = tmp_path / "snapshot.json"
    path.write_bytes(payload())

    artifact = read_artifact(path)

    assert artifact.checksum == ingest_bytes(payload()).checksum


def test_reading_an_oversized_file_refuses_on_the_stat_not_the_read(tmp_path):
    path = tmp_path / "snapshot.json"
    path.write_bytes(payload())

    with pytest.raises(SnapshotRejected) as refusal:
        read_artifact(path, limits=IngestionLimits(max_bytes=8))

    assert refusal.value.code == "artifact_too_large"


def test_reading_a_missing_file_reports_no_path_detail(tmp_path):
    with pytest.raises(SnapshotRejected) as refusal:
        read_artifact(tmp_path / "absent.json")

    assert refusal.value.code == "artifact_unreadable"
    assert str(tmp_path) not in str(refusal.value)


def test_repr_never_renders_artifact_content():
    artifact = ingest_bytes(payload())

    rendered = repr(artifact)

    assert "Brightlantern" not in rendered
    assert artifact.checksum.short in rendered


def test_the_default_bound_is_documented_and_positive():
    assert DEFAULT_MAX_BYTES == 64 * 1024 * 1024

    with pytest.raises(ValueError):
        IngestionLimits(max_bytes=0)


def test_the_accepted_contract_limits_are_unchanged():
    """The bounds are inherited from the accepted export contract, exactly.

    They are a security control, and relaxing one while reorganising something
    else is the way a bound quietly grows. Changing any value here requires a
    §0.2 change-control entry against `docs/rules/foundry-export-contract.md`
    first — this test is what makes that a deliberate act rather than a diff
    nobody noticed.
    """
    from application.foundry.artifact import DEFAULT_MAX_DEPTH
    from application.foundry.parser import BundleLimits

    assert DEFAULT_MAX_BYTES == 64 * 1024 * 1024  # contract §1
    assert DEFAULT_MAX_DEPTH == 64  # contract §1

    limits = BundleLimits()
    assert limits.max_actors == 500  # contract §2.6
    assert limits.max_folders == 64  # contract §2.5
    assert limits.max_selected_folders == 8  # contract §2.5
    assert limits.max_items_per_actor == 4000  # contract §2.6


def test_the_contract_document_states_the_same_limits():
    """The prose a maintainer approved and the numbers in force must agree."""
    from pathlib import Path

    contract = (
        Path(__file__).resolve().parents[1]
        / "docs"
        / "rules"
        / "foundry-export-contract.md"
    ).read_text(encoding="utf-8")

    assert "64 MiB" in contract
    assert "**64**" in contract  # nesting depth
    assert "≤ 500" in contract  # actors
