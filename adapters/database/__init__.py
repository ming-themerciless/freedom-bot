"""PostgreSQL adapter. ORM records never cross this package boundary."""

from .metadata import metadata

__all__ = ["metadata"]
