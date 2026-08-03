"""Offline Foundry snapshot ingestion, reconciliation and import (Phase 2).

Nothing in this package opens a network connection, reads a Foundry world
directory, or writes to Foundry. It operates on one artifact a Guild Council
member deliberately exported; see `docs/rules/foundry-export-contract.md`.
"""
