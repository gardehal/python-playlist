from abc import ABC, abstractmethod
from typing import Optional

class ExternalStreamProvider(ABC):
    """Interface for external stream sources (e.g., YouTube, Local)."""

    @abstractmethod
    def fetch_metadata(self, uri: str) -> dict:
        """Fetch metadata from a given URI."""
        pass

    @abstractmethod
    def download_stream(self, uri: str) -> bytes:
        """Download stream content from a given URI."""
        pass
