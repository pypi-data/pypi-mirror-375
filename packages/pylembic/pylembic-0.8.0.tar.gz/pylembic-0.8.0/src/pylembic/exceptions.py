class CircularDependencyError(Exception):
    """Raised when a circular dependency is detected in the migration graph.

    Original exception is CommandError from Alembic util module. This exception
    is created for readability.
    """

    pass
