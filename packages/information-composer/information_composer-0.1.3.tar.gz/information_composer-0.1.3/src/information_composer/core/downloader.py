"""Base downloader implementation."""

from typing import Any, Dict, Optional

import requests


class BaseDownloader:
    def __init__(self, timeout: int = 30):
        self.timeout = timeout
        self.session = requests.Session()

    def download(self, url: str, headers: Optional[Dict[str, str]] = None) -> Any:
        """Download content from specified URL."""
        raise NotImplementedError
