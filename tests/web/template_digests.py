
# `base.html` re-frozen 2026-08-27 for finding N-23. HTMX 2.0.10 injects an inline
# `<style>` for `.htmx-indicator` at load, which N-26's `style-src 'self'` blocks —
# a CSP violation logged by a real browser engine on every page that loads HTMX.
# Nothing used the feature, so nothing broke; the noise mattered because a console
# with a permanent error in it hides the next one. A `<meta name="htmx-config">`
# turns the injection off, placed before the script because HTMX reads it at load.
# A meta tag rather than an inline `<script>`, which would have needed a
# `script-src` exception — a worse trade than the problem.
# Re-frozen deliberately, with the previous value recorded here rather than
# silently overwritten:
#   was a7ff85b659b77b9fc496d5d3afdf0499b70cb7cdd43afde403c2d4686e892770
#
# **The Step 1–10 accepted baseline below is untouched.** That entry is the P3.4
# acceptance record, and this change moves only the implementation digest.
#
# `includes/header.html` re-frozen 2026-08-23 by the C35-05 shell contract.
# The P3.4 digest recorded a *static* header: the same three links for every
# caller, no sign-out control anywhere, and no route to any privileged surface
# (F-17). The frame is now rendered from the server-owned shell, so the digest
# necessarily changed. Re-frozen deliberately, with the previous value recorded
# here rather than silently overwritten:
#   was bf2d9a81ce9614c43461a7cedb0db9d2c7e0ba5050e14a7cda8e46f02d426857
"""Canonical registry of P3.4 template digests.

This test-support module is the single authoritative source for template SHA-256
digests across Phase 3.4 test suites.

Strictly distinguishes:
- Accepted Step 1 through Step 10 templates (23 accepted baseline templates); and
- Step 11 proposed implementation template digests (with accessibility corrections in
  `character_links.html` and `council_characters.html`).

All exported mappings are immutable MappingProxyType instances.
"""
from __future__ import annotations

import types

#: Accepted baseline digests for all 23 templates established through Step 10.
_ACCEPTED_STEP_1_THROUGH_10_DIGESTS: dict[str, str] = {
    "account_identities.html": "5f458b6fe335d34b7ba400d4f7c4c0dcbcceadabd613bfbd5c25890af37f1287",
    "audit_results.html": "42883ac57fd38b342cb4471c46f001b549818e07faa7c772d8f2a2df09ba0e38",
    "audit_search.html": "6453c99cd068918be029d7f592b8a934654b11f05e324400ef080d83e878ec23",
    "character_detail.html": "7524e43e0e2ee814b5c8b65365f4e0d72bcb9c1e42e4087ea927e3934c0c9890",
    "character_links.html": "a1f280c1700ee4aa53655fb94a7290ff43edc108159b1df85c8572ee37ac395d",
    "conflict.html": "1dda40f2e43212631fba5001e4982748fc5a090b0a32a6be57965daae4805648",
    "council_characters.html": "a18419ab163e00e54987ae7a4071f7b8698b916bf517a714b51cb0ea6dff7a02",
    "council_snapshots.html": "627b42f740bceac8ae5665a5be235aa76add3ffd7f08617861f39f2befcb5d8e",
    "degraded.html": "98f3ac888788d24e173fb4a497e0b138c23987b459d29d37b4131c9bbd211915",
    "denied.html": "197913db5909d6d9801f599b0a0b2eed47b6384f4e5bd3e38de6e9ae6c686c20",
    "emergency.html": "0eec75c17bb6ea602fabc7aace0aaf1453e70fd102e61da5298759e094980a99",
    "error.html": "6fdf24733c0b06139434c7b7198cab979438758fb6b8c18175e473b4ad404945",
    "field_profile.html": "06277334db018cd82e313af0556a35e658c86841e06602a7bd65d0edde15f703",
    "identity_migration.html": "66f3669661c40f2a73d250122c35e0f8af397d6f8bd94a4571402e7a8a63134b",
    "identity_search.html": "36978ca19d5366188ae42892111cb5425ece1b6e2355710a32b71e2c6ef1e394",
    "import_result.html": "15735d60fdb5a5b3c8435a7ee389af7e6ec027c2f386cdee55f3d109bd42c86e",
    "job_status.html": "9a7a62892f9983ccd1a359f213f4feab0f85b1a084dccdabdbb0cb68a380deb3",
    "job_status_fragment.html": "81fcd1bb2a80657c979e8c4581657bb0ba0b3940fb689ca7d56483c9d66ee234",
    "login.html": "eafd7635be0b6b8dfb7d60df7a827a49863b5b12bb1cdc0e49ddbd4c0f7d5e3b",
    "my_characters.html": "3705fbcd3e0803b2190746102cf6a67e20aa607432de128e3127a5a8987ce042",
    "non_member.html": "de43a127d11f77bfccfb515fa93e3a2ef9373b123c880c1290dcedc1f1721f02",
    "role_capabilities.html": "e297c26dc326a2a28c9439948fcd781c29b12d3cda74911d9f747727d760613a",
    "validation.html": "ff00f7acf78f8d055c3a37af92d0f32230b98fb95aa385b4f327e3851c3e4e7d",
}

ACCEPTED_STEP_1_THROUGH_10_TEMPLATE_DIGESTS: types.MappingProxyType[str, str] = (
    types.MappingProxyType(_ACCEPTED_STEP_1_THROUGH_10_DIGESTS)
)

#: Historical alias for Steps 1 through 9.
_ACCEPTED_STEP_1_THROUGH_9_DIGESTS: dict[str, str] = {
    k: v for k, v in _ACCEPTED_STEP_1_THROUGH_10_DIGESTS.items()
    if k not in {"audit_results.html", "audit_search.html", "import_result.html"}
}

ACCEPTED_STEP_1_THROUGH_9_TEMPLATE_DIGESTS: types.MappingProxyType[str, str] = (
    types.MappingProxyType(_ACCEPTED_STEP_1_THROUGH_9_DIGESTS)
)

#: Step 10 digests alias.
PROPOSED_STEP_10_TEMPLATE_DIGESTS: types.MappingProxyType[str, str] = (
    types.MappingProxyType({
        "audit_results.html": _ACCEPTED_STEP_1_THROUGH_10_DIGESTS["audit_results.html"],
        "audit_search.html": _ACCEPTED_STEP_1_THROUGH_10_DIGESTS["audit_search.html"],
        "import_result.html": _ACCEPTED_STEP_1_THROUGH_10_DIGESTS["import_result.html"],
    })
)

#: Proposed Step 11/P3.5 implementation digests reflecting accessibility corrections and F-15 emergency WebAuthn.
_P3_4_IMPLEMENTATION_DIGESTS: dict[str, str] = {
    **_ACCEPTED_STEP_1_THROUGH_10_DIGESTS,
    "character_links.html": "78fdaac512f3bddc2073e20b03fc610f8afb0243db5907e8c1cadf904c5bed49",
    "council_characters.html": "671e8308f5f746941bcd875cb66ccc368e8c4a18dc5738e8f5411e6f62be5c87",
    "council_snapshots.html": "4aca2c0e057f94a061e10af1640dcae5ec43ecb66765db8ff629a3f616a00229",
    "emergency.html": "3ed40f3c5fa6e8a0a161cf4c9182a6f10a2d98058d65a341aad6e41fa2b386d9",
    "error.html": "269e72e427a7166ebf22ca12f46827c2ee30671a2f48fdde9a504ca87f1c4f33",
    "job_status_fragment.html": "a2e5c106ac44c4f38c203286918219fec61858d9909e2a851a5a2eb6fb0096e3",
    "validation.html": "3f71db358dbd5a83bd85b520fe3541b93d5a04f6cd1db2c4047a9a3bc9b18c39",
}

P3_4_IMPLEMENTATION_TEMPLATE_DIGESTS: types.MappingProxyType[str, str] = (
    types.MappingProxyType(_P3_4_IMPLEMENTATION_DIGESTS)
)

#: Alias for review-candidate verification across test suites.
P3_4_REVIEW_CANDIDATE_TEMPLATE_DIGESTS: types.MappingProxyType[str, str] = (
    P3_4_IMPLEMENTATION_TEMPLATE_DIGESTS
)

#: 15 Non-Step-4 templates for auth_and_system suite.
_NON_STEP_4_DIGESTS: dict[str, str] = {
    k: v
    for k, v in _P3_4_IMPLEMENTATION_DIGESTS.items()
    if k
    not in {
        "conflict.html",
        "degraded.html",
        "denied.html",
        "emergency.html",
        "error.html",
        "login.html",
        "non_member.html",
        "validation.html",
    }
}

NON_STEP_4_TEMPLATE_DIGESTS: types.MappingProxyType[str, str] = (
    types.MappingProxyType(_NON_STEP_4_DIGESTS)
)

NON_STEP_4_IMPLEMENTATION_TEMPLATE_DIGESTS: types.MappingProxyType[str, str] = (
    NON_STEP_4_TEMPLATE_DIGESTS
)

#: Accepted baseline digests for shared includes and base shell established through Step 10.
_ACCEPTED_STEP_1_THROUGH_10_INCLUDE_DIGESTS: dict[str, str] = {
    "includes/footer.html": "2f1068b436a38a7ef79580aec4b55ed23dcaa5a3b827596509caa000ed72f7c3",
    "includes/header.html": "ede238e9d6f83c70eb228b54d58d40fa5b01d6df4c82ce8479c641dc28a46796",
    "base.html": "6dcd0631901cb2cf3c0275bbfcdab51996af9e71927fd84dedcf74901a0188fb",
}

ACCEPTED_STEP_1_THROUGH_10_INCLUDE_DIGESTS: types.MappingProxyType[str, str] = (
    types.MappingProxyType(_ACCEPTED_STEP_1_THROUGH_10_INCLUDE_DIGESTS)
)

#: Proposed Step 11/P3.5 implementation digests for shared includes and base shell.
_P3_4_IMPLEMENTATION_INCLUDE_DIGESTS: dict[str, str] = {
    "includes/footer.html": "2f1068b436a38a7ef79580aec4b55ed23dcaa5a3b827596509caa000ed72f7c3",
    "includes/header.html": "fc1fc051f19454be4df9e430e6b76d3209f4c6a528cc86f8c23992324359ccbb",
    "base.html": "f9ce0e17255dc30043fc8167681af1274cc6f50ce0b5a1ae1ca29819d0284838",
}

P3_4_IMPLEMENTATION_INCLUDE_DIGESTS: types.MappingProxyType[str, str] = (
    types.MappingProxyType(_P3_4_IMPLEMENTATION_INCLUDE_DIGESTS)
)

__all__ = [
    "ACCEPTED_STEP_1_THROUGH_10_INCLUDE_DIGESTS",
    "ACCEPTED_STEP_1_THROUGH_10_TEMPLATE_DIGESTS",
    "ACCEPTED_STEP_1_THROUGH_9_TEMPLATE_DIGESTS",
    "NON_STEP_4_IMPLEMENTATION_TEMPLATE_DIGESTS",
    "NON_STEP_4_TEMPLATE_DIGESTS",
    "P3_4_IMPLEMENTATION_INCLUDE_DIGESTS",
    "P3_4_IMPLEMENTATION_TEMPLATE_DIGESTS",
    "P3_4_REVIEW_CANDIDATE_TEMPLATE_DIGESTS",
    "PROPOSED_STEP_10_TEMPLATE_DIGESTS",
]
