class ConcurrencyConflictError(RuntimeError):
    """The aggregate changed after the caller read it."""
