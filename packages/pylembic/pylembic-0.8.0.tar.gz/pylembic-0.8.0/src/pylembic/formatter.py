from logging import Formatter, LogRecord


class CustomFormatter(Formatter):
    """Custom formatter that handles missing fields gracefully.

    The order of the fields matters. We want them to be:
    "%(dependency)s%(orphans)s%(heads)s%(bases)s%(up_revisions)s%(down_revisions)s"
    """

    DEFAULT_LOGGING_FIELDS = [
        "migration",
        "dependency",
        "orphans",
        "heads",
        "bases",
        "up_revisions",
        "down_revisions",
    ]

    def __init__(
        self, fmt: str = None, datefmt: str = None, fields: list[str] = None
    ) -> None:
        """Initialize the formatter.

        Args:
            fmt (str): The log message format.
            datefmt (str): The date format for log messages.
            params (list, optional): List of additional parameters to include in the
            format.
        """
        fields = fields or self.DEFAULT_LOGGING_FIELDS
        format_string = self._build_format(fields, fmt)
        super().__init__(fmt=format_string, datefmt=datefmt)

    @staticmethod
    def _build_format(fields: list[str], base_fmt: str) -> str:
        """Build the log message format string dynamically.

        Args:
            params (list): List of additional parameters to include in the format.
            base_fmt (str): The base log message format.

        Returns:
            str: The formatted log message
        """
        base_fmt = base_fmt or "%(levelname)s\t %(asctime)s | %(message)s | "
        dynamic_fields = "".join([f"%({field})s" for field in fields])
        return f"{base_fmt}{dynamic_fields}"

    def format(self, record: LogRecord) -> str:
        """Format the log record with default values for missing fields."""
        for field in self.DEFAULT_LOGGING_FIELDS:
            if not hasattr(record, field):
                setattr(record, field, "")

        return super().format(record)
