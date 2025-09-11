"""Base site information collector implementation."""

from typing import Any


class BaseSiteCollector:
    """Base class for site-specific information collectors."""

    def __init__(self):
        self.name = self.__class__.__name__

    def collect(self) -> Any:
        """Implement the information collection logic."""
        raise NotImplementedError

    def compose(self, data: Any) -> Any:
        """Implement the information composition logic."""
        raise NotImplementedError
