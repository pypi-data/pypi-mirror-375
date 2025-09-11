from typing import Dict, Iterator, List


class GifResponse:
    """Represents a GIF response from the API."""

    def __init__(self, data: Dict[str, str]) -> None:
        self._data = data

    @property
    def url(self) -> str:
        """The URL of the GIF."""
        return self._data.get("url", "")

    @property
    def reaction(self) -> str:
        """The reaction type of this GIF."""
        return ""

    def __repr__(self) -> str:
        return f"<GifResponse reaction='{self.reaction}' url='{self.url}'>"


class AllReactionsResponse:
    """Represents the response from the /allreactions endpoint."""

    def __init__(self, data: Dict[str, List[str]]) -> None:
        self._data = data

    @property
    def reactions(self) -> List[str]:
        """List of all available reaction types."""
        return self._data.get("reactions", [])

    def __repr__(self) -> str:
        return f"<AllReactionsResponse reactions={len(self.reactions)} items>"

    def __iter__(self) -> Iterator[str]:
        return iter(self.reactions)

    def __len__(self) -> int:
        return len(self.reactions)
