from .client import ExpressipyClient
from .models import GifResponse
from .types import ReactionInput


async def get_gif(reaction: ReactionInput, timeout: float = 10.0) -> GifResponse:
    """
    Convenience function to get a random GIF for a reaction.

    This function creates a client, fetches the GIF, and closes the client automatically.
    For multiple requests, it's more efficient to create and reuse a client instance.

    Parameters
    ----------
    reaction : ReactionInput
        The reaction type to get a GIF for.
    timeout : float, optional
        The timeout in seconds for the HTTP request.

    Returns
    -------
    GifResponse
        A GifResponse object containing the GIF data
    """

    async with ExpressipyClient(timeout=timeout) as client:
        return await client.get_gif(reaction)
