from typing_extensions import Self

from .exceptions import ExpressipyException
from .http import HTTPClient
from .models import AllReactionsResponse, GifResponse
from .types import ReactionInput, ReactionType


class ExpressipyClient:
    """
    High-level client for the OtakuGIFs API.

    This client provides a simple, fully-typed interface for interacting with the OtakuGIFs API.

    Parameters
    ----------
    timeout : float, optional
        The timeout in seconds for HTTP requests. Defaults to 10.0.

    Example
    -------
    Basic usage:

    ```python
    import asyncio
    from expressipy import ExpressipyClient, ReactionType

    async def main():
        client = ExpressipyClient()

        # Get a random hug GIF
        gif = await client.get_gif(ReactionType.HUG)
        print(f"Got a hug GIF: {gif.url}")

        # Get all available reactions
        reactions = await client.get_all_reactions()
        print(f"Available reactions: {len(reactions)}")

        await client.close()

    asyncio.run(main())
    ```
    """

    def __init__(self, timeout: float = 10.0) -> None:
        self._http = HTTPClient(timeout=timeout)
        self._closed = False

    async def __aenter__(self) -> Self:
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb) -> None:
        await self.close()

    @property
    def is_closed(self) -> bool:
        """Whether the client is closed."""

        return self._closed

    def _validate_reaction(self, reaction: ReactionInput) -> str:
        """Validate and normalize a reaction input."""

        if isinstance(reaction, ReactionType):
            return reaction.value
        elif isinstance(reaction, str):
            reaction_lower = reaction.lower()
            valid_reactions = [r.value for r in ReactionType]

            if reaction_lower in valid_reactions:
                return reaction_lower
            else:
                raise ValueError(
                    f"Invalid reaction: {reaction}. Must be one of: {valid_reactions}"
                )
        else:
            raise TypeError(
                f"Reaction must be a ReactionType, str, or ReactionLiteral, not {type(reaction)}"
            )

    async def get_gif(self, reaction: ReactionInput) -> GifResponse:
        """
        Get a random GIF for a specific reaction

        Parameters
        ----------
        reaction : ReactionInput
            The reaction type to get a GIF for. Can be a ReactionType enum, a string, or a ReactionLiteral.

        Returns
        -------
        GifResponse
            A GifResponse object containing the GIF data.

        Raises
        ------
        ValueError
            If the reaction is not valid.
        HTTPException
            If the API request fails.
        """

        if self._closed:
            raise ExpressipyException("Client is closed")

        reaction_str = self._validate_reaction(reaction)
        data = await self._http.get_random_gif(reaction_str)
        return GifResponse(data)

    async def get_all_reactions(self) -> AllReactionsResponse:
        """
        Get all available reaction types from the API.

        Returns
        -------
        AllReactionsResponse
            An AllReactionsResponse object containing all available reactions.

        Raises
        ------
        HTTPException
            If the API request fails.
        """

        if self._closed:
            raise ExpressipyException("Client is closed.")

        data = await self._http.get_all_reactions()
        return AllReactionsResponse(data)

    async def close(self) -> None:
        """Close the client and clean up resources."""
        if not self._closed:
            await self._http.close()
            self._closed = True
