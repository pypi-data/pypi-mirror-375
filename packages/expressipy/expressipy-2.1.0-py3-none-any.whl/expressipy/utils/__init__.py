from __future__ import annotations

from typing import Optional, Union

from .formatter import ReactionFormatter
from ..client import ExpressipyClient
from ..enums import ReactionType
from ..models import GifResponse
from ..types import ReactionInput


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


def format_reaction(
    reaction: Union[str, ReactionType],
    user: str,
    target: Optional[str] = None,
    mention_prefix: str = "@",
) -> str:
    """
    Quick function to format a reaction without creating a ReactionFormatter instance.

    Parameters
    ----------
    reaction : Union[str, ReactionType]
        The reaction type to format
    user : str
        The user performing the reaction
    target : Optional[str]
        The target of the reaction (if applicable)
    mention_prefix : str
        Prefix for mentions (default: "@")

    Returns
    -------
    str
        Formatted sentence describing the reaction

    Examples
    --------
    >>> format_reaction("hug", "Alice", "Bob")
    "@Alice hugs @Bob"

    >>> format_reaction("dance", "Charlie", mention_prefix="")
    "Charlie dances"
    """
    formatter = ReactionFormatter()
    return formatter.format_reaction(reaction, user, target, mention_prefix)
