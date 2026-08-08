"""The HTTP boundary for Foundry snapshot submission.

Deliberately small. See
[ADR 0009](../../docs/adr/0009-snapshot-submission-http-boundary.md) for why this
is a stdlib WSGI application rather than the FastAPI stack ADR 0002 records for
the Phase 3 web application.
"""
