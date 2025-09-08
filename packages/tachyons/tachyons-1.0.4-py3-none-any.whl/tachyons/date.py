

from typing import Any


class ISO8601:
    """A class for handling ISO 8601 date strings."""

    def __init__(self, date_str: str) -> None:
        self.date_str = date_str

    def to_dict(self) -> dict[str, Any]:
        """Convert the ISO 8601 date string to a dictionary representation."""
        return {"iso8601": self.date_str}

    def __str__(self) -> str:
        return self.date_str

