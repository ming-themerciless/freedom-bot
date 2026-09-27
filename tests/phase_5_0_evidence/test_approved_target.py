"""The approved target: exactly Peter Duscha's values, and a one-field deviation
refused in every field.

Target assignment is the first item of the authorization draft's required
sequence, and the failure mode it guards against is not *"someone points the
harness at production"* — the path guards in `targets.py` already refuse that. It
is the quieter one: a rebuilt host, a second evidence root, a `p5-1` beside the
`p5-0`, a target that is right in six fields and wrong in the seventh. Those all
pass every structural guard in the package, and none of them is the target
anybody confirmed.
"""
from __future__ import annotations

import pytest

from tools.phase_5_0_evidence.approved_target import (
    APPROVED_TARGET,
    APPROVED_TARGET_FACTS,
    COMPARED_TARGET_FIELDS,
    CONFIRMATION_TOKEN,
    TARGET_IDENTITY_DIGEST,
    require_approved_target,
    target_deviations,
)
from tools.phase_5_0_evidence.errors import TargetRefused
from tools.phase_5_0_evidence.targets import DisposableTarget


def test_the_canonical_target_carries_exactly_the_approved_facts() -> None:
    assert APPROVED_TARGET.host == "oracle-test"
    assert APPROVED_TARGET.root_path == "/var/lib/fb-evidence-p5-0"
    assert APPROVED_TARGET.database_name == "fb_evidence_p5_0"
    assert APPROVED_TARGET.postgres_socket_directory == "/var/run/postgresql"
    assert APPROVED_TARGET.postgres_config_directory == "/etc/postgresql/16/main"
    assert APPROVED_TARGET.confirmed_disposable is True


def test_the_confirmed_environment_is_the_one_peter_named_and_codex_verified() -> None:
    facts = dict(APPROVED_TARGET_FACTS.as_fields())
    assert facts == {
        "host": "oracle-test",
        "kernel_nodename": "Test",
        "ipv4": "138.2.182.39",
        "operating_system": "Ubuntu 26.04.1 LTS",
        "architecture": "x86_64",
        "active_kernel": "7.0.0-31-generic",
        "filesystem_root": "/var/lib/fb-evidence-p5-0",
        "filesystem_type": "ext4",
        "filesystem_device": "/dev/sda1",
        "postgres_instance": "16/main",
        "postgres_port": "5432",
        "postgres_socket_directory": "/var/run/postgresql",
        "postgres_config_directory": "/etc/postgresql/16/main",
        "evidence_database": "fb_evidence_p5_0",
        "confirmed_by": "Peter Duscha, Operations Owner",
        "confirmed_on": "2026-09-05",
    }


def test_the_disposability_statement_names_the_decision_and_its_owner() -> None:
    statement = APPROVED_TARGET.disposability_evidence
    assert "Peter Duscha" in statement
    assert "2026-09-05" in statement
    assert "disposable" in statement
    # And it is a statement of *why*, not a flag: `DisposableTarget` refuses a
    # confirmed target with a blank one.
    with pytest.raises(TargetRefused):
        DisposableTarget(
            host="oracle-test",
            root_path="/var/lib/fb-evidence-p5-0",
            database_name="fb_evidence_p5_0",
            postgres_socket_directory="/var/run/postgresql",
            confirmed_disposable=True,
            disposability_evidence="   ",
            postgres_config_directory="/etc/postgresql/16/main",
        )


def test_the_approved_target_still_passes_every_structural_guard() -> None:
    """Construction *is* the check, so re-constructing it is the assertion.

    The root is absolute, three levels deep and `fb-evidence-`-prefixed; the
    database is `fb_evidence_`-prefixed and is none of the forbidden names —
    `freedom_test` included; the configuration directory names a PostgreSQL
    instance. Any of those failing raises here.
    """
    rebuilt = DisposableTarget(
        host=APPROVED_TARGET.host,
        root_path=APPROVED_TARGET.root_path,
        database_name=APPROVED_TARGET.database_name,
        postgres_socket_directory=APPROVED_TARGET.postgres_socket_directory,
        confirmed_disposable=True,
        disposability_evidence=APPROVED_TARGET.disposability_evidence,
        postgres_config_directory=APPROVED_TARGET.postgres_config_directory,
    )
    assert rebuilt == APPROVED_TARGET
    assert rebuilt.identity == "oracle-test:/var/lib/fb-evidence-p5-0"


#: One plausible wrong value per compared field. Each is the kind of mistake that
#: passes every structural guard: a sibling evidence root, the other PostgreSQL
#: instance, a host that was rebuilt under a new name.
DEVIATIONS = {
    "host": "oracle-test-2",
    "root_path": "/var/lib/fb-evidence-p5-1",
    "database_name": "fb_evidence_p5_1",
    "postgres_socket_directory": "/var/run/postgresql-16",
    "postgres_config_directory": "/etc/postgresql/18/main",
    "confirmed_disposable": False,
    "disposability_evidence": "Confirmed by someone, at some point.",
}


def test_every_compared_field_has_a_deviation_case() -> None:
    """The parametrisation below is only as complete as this set.

    A field added to `COMPARED_TARGET_FIELDS` without a deviation case would be
    compared by `target_deviations` and never proved to be, which is the
    difference between a guard that runs and a guard that can fail.
    """
    assert set(DEVIATIONS) == set(COMPARED_TARGET_FIELDS)


@pytest.mark.parametrize("field_name", sorted(DEVIATIONS))
def test_a_one_field_deviation_is_refused(field_name: str) -> None:
    values = {name: getattr(APPROVED_TARGET, name) for name in COMPARED_TARGET_FIELDS}
    values[field_name] = DEVIATIONS[field_name]
    if not values["confirmed_disposable"]:
        # An unconfirmed target records no evidence; the two go together, and the
        # deviation being proved here is the confirmation itself.
        values["disposability_evidence"] = ""
    candidate = DisposableTarget(**values)

    deviations = target_deviations(candidate)

    assert deviations, f"a wrong {field_name} was accepted as the approved target"
    assert any(deviation.startswith(f"{field_name}:") for deviation in deviations)
    with pytest.raises(TargetRefused) as refusal:
        require_approved_target(candidate)
    assert field_name in str(refusal.value)


def test_an_unassigned_target_is_refused() -> None:
    with pytest.raises(TargetRefused):
        require_approved_target(DisposableTarget.unassigned())


def test_something_that_is_not_a_target_at_all_is_refused() -> None:
    with pytest.raises(TargetRefused):
        require_approved_target("oracle-test")  # type: ignore[arg-type]


def test_the_approved_target_is_accepted() -> None:
    assert target_deviations(APPROVED_TARGET) == ()
    assert require_approved_target(APPROVED_TARGET) is APPROVED_TARGET


def test_the_confirmation_token_is_tied_to_the_target_identity() -> None:
    """It is derived, not written.

    A constant token would keep working after the target changed, which is the
    one thing a confirmation token must not do.
    """
    assert APPROVED_TARGET.host in CONFIRMATION_TOKEN
    assert APPROVED_TARGET.root_path in CONFIRMATION_TOKEN
    assert APPROVED_TARGET.database_name in CONFIRMATION_TOKEN
    assert CONFIRMATION_TOKEN.endswith(TARGET_IDENTITY_DIGEST[:16])
    assert len(TARGET_IDENTITY_DIGEST) == 64


def test_the_identity_digest_covers_the_environment_facts_too() -> None:
    """A rebuilt host with the same name is not the same target.

    The kernel, the distribution, the filesystem and the PostgreSQL instance are
    in the digest, so a host rebuilt onto a different baseline produces a
    different token and a different manifest digest — and the previously
    approved ones stop working, which is the behaviour Codex's verification of
    those exact facts is worth anything for.
    """
    import hashlib

    parts = [f"{name}={getattr(APPROVED_TARGET, name)!r}" for name in COMPARED_TARGET_FIELDS]
    parts.extend(f"{name}={value}" for name, value in APPROVED_TARGET_FACTS.as_fields())
    assert TARGET_IDENTITY_DIGEST == hashlib.sha256(
        "\n".join(parts).encode("utf-8")
    ).hexdigest()

    changed = list(parts)
    changed[-1] = "confirmed_on=2026-09-06"
    assert TARGET_IDENTITY_DIGEST != hashlib.sha256(
        "\n".join(changed).encode("utf-8")
    ).hexdigest()


def test_the_ssh_alias_and_the_kernel_nodename_are_two_separate_facts() -> None:
    """Peter's Option A decision, LAB-I3-TARGET-1, 2026-09-20.

    The operational name did not move: `host` is still the runbook §2 SSH alias
    `oracle-test`, on both the planning target and the review facts. What is new
    is a *second* name, `Test`, which is what the target's kernel calls itself
    and the only value I3 admission compares its `os.uname()` observation with.

    Asserted as an inequality as well as two values, because the defect this
    decision resolves was precisely the two being treated as one field.
    """
    assert APPROVED_TARGET.host == "oracle-test"
    assert APPROVED_TARGET_FACTS.host == "oracle-test"
    assert APPROVED_TARGET_FACTS.kernel_nodename == "Test"
    assert APPROVED_TARGET_FACTS.kernel_nodename != APPROVED_TARGET_FACTS.host

    # And the alias is not silently a nodename under a different spelling.
    assert APPROVED_TARGET_FACTS.kernel_nodename.lower() != APPROVED_TARGET_FACTS.host.lower()


def test_the_kernel_nodename_is_part_of_the_canonical_identity_material() -> None:
    """It is hashed, ordered and carried into the token — not a loose note.

    The nodename is approved target identity, so supplying a different one must
    move `TARGET_IDENTITY_DIGEST` and `CONFIRMATION_TOKEN` and force the
    re-review that a moved digest triggers. A fact recorded beside the identity
    rather than inside it would let the target's name change under an approved
    digest.
    """
    import hashlib
    from dataclasses import replace

    names = [name for name, _ in APPROVED_TARGET_FACTS.as_fields()]
    assert "kernel_nodename" in names
    # Deterministic ordering: immediately after `host`, the fact it is paired
    # with and must never be confused for.
    assert names.index("kernel_nodename") == names.index("host") + 1
    assert names == sorted(names, key=names.index)  # the order is the tuple's, not a dict's

    def digest_of(facts) -> str:
        parts = [f"{name}={getattr(APPROVED_TARGET, name)!r}" for name in COMPARED_TARGET_FIELDS]
        parts.extend(f"{name}={value}" for name, value in facts.as_fields())
        return hashlib.sha256("\n".join(parts).encode("utf-8")).hexdigest()

    assert digest_of(APPROVED_TARGET_FACTS) == TARGET_IDENTITY_DIGEST
    moved = digest_of(replace(APPROVED_TARGET_FACTS, kernel_nodename="oracle-test"))
    assert moved != TARGET_IDENTITY_DIGEST

    # The token carries the digest's first sixteen characters, so it moves too.
    assert CONFIRMATION_TOKEN.endswith(TARGET_IDENTITY_DIGEST[:16])
    assert not CONFIRMATION_TOKEN.endswith(moved[:16])
    # The token still names the operational alias, which this decision kept.
    assert CONFIRMATION_TOKEN.startswith("oracle-test:")
