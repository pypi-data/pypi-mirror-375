"""
Dynamic Reaction Formatter for ExpressiPy
Converts reaction types into natural language sentences
"""

from __future__ import annotations

from typing import Dict, Optional, Union, TypedDict, Literal
from enum import Enum
from ..enums import ReactionType


class SentenceType(Enum):
    """Types of sentence structures for reactions."""

    TRANSITIVE = "transitive"  # user verbs target
    INTRANSITIVE = "intransitive"  # user verbs
    STATE = "state"  # user is adjective
    COMPLEX = "complex"  # custom template


class TransitiveReaction(TypedDict):
    """Type for transitive reaction data."""

    verb: str
    type: Literal[SentenceType.TRANSITIVE]


class IntransitiveReaction(TypedDict):
    """Type for intransitive reaction data."""

    verb: str
    type: Literal[SentenceType.INTRANSITIVE]


class StateReaction(TypedDict):
    """Type for state reaction data."""

    adjective: str
    type: Literal[SentenceType.STATE]


class ComplexReaction(TypedDict):
    """Type for complex reaction data."""

    template: str
    type: Literal[SentenceType.COMPLEX]


# Union type for all reaction data types
ReactionData = Union[
    TransitiveReaction, IntransitiveReaction, StateReaction, ComplexReaction
]


class ReactionFormatter:
    """
    Formats reactions into natural language sentences.

    Examples:
    --------
    formatter = ReactionFormatter()

    # Basic usage
    sentence = formatter.format_reaction("hug", "Alice", "Bob")
    # Result: "Alice hugs Bob"

    # Without target (for intransitive verbs)
    sentence = formatter.format_reaction("dance", "Alice")
    # Result: "Alice dances"

    # State reactions
    sentence = formatter.format_reaction("happy", "Alice")
    # Result: "Alice is happy"
    """

    # Comprehensive reaction mapping with proper grammar
    REACTION_DATA: Dict[str, ReactionData] = {
        # Physical actions (transitive)
        "hug": {"verb": "hugs", "type": SentenceType.TRANSITIVE},
        "kiss": {"verb": "kisses", "type": SentenceType.TRANSITIVE},
        "slap": {"verb": "slaps", "type": SentenceType.TRANSITIVE},
        "bite": {"verb": "bites", "type": SentenceType.TRANSITIVE},
        "pat": {"verb": "pats", "type": SentenceType.TRANSITIVE},
        "poke": {"verb": "pokes", "type": SentenceType.TRANSITIVE},
        "punch": {"verb": "punches", "type": SentenceType.TRANSITIVE},
        "tickle": {"verb": "tickles", "type": SentenceType.TRANSITIVE},
        "lick": {"verb": "licks", "type": SentenceType.TRANSITIVE},
        "pinch": {"verb": "pinches", "type": SentenceType.TRANSITIVE},
        "smack": {"verb": "smacks", "type": SentenceType.TRANSITIVE},
        "nuzzle": {"verb": "nuzzles", "type": SentenceType.TRANSITIVE},
        # Interactive actions
        "cuddle": {"verb": "cuddles with", "type": SentenceType.TRANSITIVE},
        "handhold": {"verb": "holds hands with", "type": SentenceType.TRANSITIVE},
        "love": {"verb": "loves", "type": SentenceType.TRANSITIVE},
        "brofist": {"verb": "fist bumps", "type": SentenceType.TRANSITIVE},
        "cheers": {"verb": "cheers with", "type": SentenceType.TRANSITIVE},
        # Visual actions (transitive)
        "stare": {"verb": "stares at", "type": SentenceType.TRANSITIVE},
        "angrystare": {"verb": "angrily stares at", "type": SentenceType.TRANSITIVE},
        "peek": {"verb": "peeks at", "type": SentenceType.TRANSITIVE},
        "wink": {"verb": "winks at", "type": SentenceType.TRANSITIVE},
        "smile": {"verb": "smiles at", "type": SentenceType.TRANSITIVE},
        "wave": {"verb": "waves at", "type": SentenceType.TRANSITIVE},
        # Communicative actions
        "shout": {"verb": "shouts at", "type": SentenceType.TRANSITIVE},
        "laugh": {"verb": "laughs at", "type": SentenceType.TRANSITIVE},
        "sorry": {"verb": "apologizes to", "type": SentenceType.TRANSITIVE},
        "thumbsup": {"verb": "gives a thumbs up to", "type": SentenceType.TRANSITIVE},
        "yes": {"verb": "says yes to", "type": SentenceType.TRANSITIVE},
        "no": {"verb": "says no to", "type": SentenceType.TRANSITIVE},
        # Complex actions with special templates
        "airkiss": {
            "template": "{user} blows a kiss to {target}",
            "type": SentenceType.COMPLEX,
        },
        "roll": {
            "template": "{user} rolls their eyes at {target}",
            "type": SentenceType.COMPLEX,
        },
        "stop": {
            "template": "{user} tells {target} to stop",
            "type": SentenceType.COMPLEX,
        },
        "slowclap": {
            "template": "{user} slow claps for {target}",
            "type": SentenceType.COMPLEX,
        },
        "clap": {"template": "{user} claps for {target}", "type": SentenceType.COMPLEX},
        "celebrate": {
            "template": "{user} celebrates with {target}",
            "type": SentenceType.COMPLEX,
        },
        "nyah": {
            "template": "{user} sticks their tongue out at {target}",
            "type": SentenceType.COMPLEX,
        },
        "bleh": {
            "template": "{user} sticks their tongue out at {target}",
            "type": SentenceType.COMPLEX,
        },
        # Intransitive actions (no target needed)
        "dance": {"verb": "dances", "type": SentenceType.INTRANSITIVE},
        "cry": {"verb": "cries", "type": SentenceType.INTRANSITIVE},
        "run": {"verb": "runs", "type": SentenceType.INTRANSITIVE},
        "sleep": {"verb": "sleeps", "type": SentenceType.INTRANSITIVE},
        "facepalm": {"verb": "facepalms", "type": SentenceType.INTRANSITIVE},
        "headbang": {"verb": "headbangs", "type": SentenceType.INTRANSITIVE},
        "sigh": {"verb": "sighs", "type": SentenceType.INTRANSITIVE},
        "yawn": {"verb": "yawns", "type": SentenceType.INTRANSITIVE},
        "sneeze": {"verb": "sneezes", "type": SentenceType.INTRANSITIVE},
        "sweat": {"verb": "sweats", "type": SentenceType.INTRANSITIVE},
        "shrug": {"verb": "shrugs", "type": SentenceType.INTRANSITIVE},
        "pout": {"verb": "pouts", "type": SentenceType.INTRANSITIVE},
        "drool": {"verb": "drools", "type": SentenceType.INTRANSITIVE},
        "nom": {"verb": "noms", "type": SentenceType.INTRANSITIVE},
        "sip": {"verb": "sips", "type": SentenceType.INTRANSITIVE},
        # Complex intransitive actions
        "evillaugh": {"template": "{user} laughs evilly", "type": SentenceType.COMPLEX},
        "nosebleed": {
            "template": "{user} has a nosebleed",
            "type": SentenceType.COMPLEX,
        },
        "yay": {"template": "{user} cheers excitedly", "type": SentenceType.COMPLEX},
        "woah": {"template": "{user} says woah", "type": SentenceType.COMPLEX},
        "huh": {"template": "{user} looks confused", "type": SentenceType.COMPLEX},
        # Emotional states (adjectives)
        "happy": {"adjective": "happy", "type": SentenceType.STATE},
        "sad": {"adjective": "sad", "type": SentenceType.STATE},
        "mad": {"adjective": "mad", "type": SentenceType.STATE},
        "confused": {"adjective": "confused", "type": SentenceType.STATE},
        "cool": {"adjective": "cool", "type": SentenceType.STATE},
        "nervous": {"adjective": "nervous", "type": SentenceType.STATE},
        "shy": {"adjective": "shy", "type": SentenceType.STATE},
        "scared": {"adjective": "scared", "type": SentenceType.STATE},
        "surprised": {"adjective": "surprised", "type": SentenceType.STATE},
        "tired": {"adjective": "tired", "type": SentenceType.STATE},
        "smug": {"adjective": "smug", "type": SentenceType.STATE},
        "blush": {"adjective": "blushing", "type": SentenceType.STATE},
    }

    def __init__(self):
        """Initialize the reaction formatter."""
        pass

    def format_reaction(
        self,
        reaction: Union[str, ReactionType],
        user: str,
        target: Optional[str] = None,
        mention_prefix: str = "@",
    ) -> str:
        """
        Format a reaction into a natural language sentence.

        Parameters
        ----------
        reaction : Union[str, ReactionType]
            The reaction type to format
        user : str
            The user performing the reaction
        target : Optional[str]
            The target of the reaction (if applicable)
        mention_prefix : str
            Prefix for mentions (e.g., "@" for Discord, "" for plain text)

        Returns
        -------
        str
            Formatted sentence describing the reaction

        Raises
        ------
        ValueError
            If the reaction is not supported

        Examples
        --------
        >>> formatter = ReactionFormatter()
        >>> formatter.format_reaction("hug", "Alice", "Bob")
        "@Alice hugs @Bob"

        >>> formatter.format_reaction("dance", "Alice")
        "@Alice dances"

        >>> formatter.format_reaction("happy", "Alice")
        "@Alice is happy"
        """
        # Convert enum to string if needed
        if isinstance(reaction, ReactionType):
            reaction = reaction.value

        # Normalize reaction name
        reaction = reaction.lower().strip()

        # Check if reaction is supported
        if reaction not in self.REACTION_DATA:
            raise ValueError(f"Unsupported reaction: {reaction}")

        # Get reaction data
        data = self.REACTION_DATA[reaction]
        sentence_type = data["type"]

        # Format user and target with mention prefix
        formatted_user = f"{mention_prefix}{user}" if mention_prefix else user
        formatted_target = (
            f"{mention_prefix}{target}" if mention_prefix and target else target
        )

        # Generate sentence based on type
        if sentence_type == SentenceType.TRANSITIVE:
            if not target:
                raise ValueError(f"Reaction '{reaction}' requires a target")
            # Type checker now knows this is TransitiveReaction
            verb = data["verb"]  # type: ignore
            return f"{formatted_user} {verb} {formatted_target}"

        elif sentence_type == SentenceType.INTRANSITIVE:
            # Type checker now knows this is IntransitiveReaction
            verb = data["verb"]  # type: ignore
            return f"{formatted_user} {verb}"

        elif sentence_type == SentenceType.STATE:
            # Type checker now knows this is StateReaction
            adjective = data["adjective"]  # type: ignore
            return f"{formatted_user} is {adjective}"

        elif sentence_type == SentenceType.COMPLEX:
            # Type checker now knows this is ComplexReaction
            template = data["template"]  # type: ignore
            if target and "{target}" in template:
                return template.format(user=formatted_user, target=formatted_target)
            else:
                return template.format(user=formatted_user)

        # This should never be reached, but satisfies type checker
        raise ValueError(f"Unknown sentence type: {sentence_type}")

    def supports_target(self, reaction: Union[str, ReactionType]) -> bool:
        """
        Check if a reaction supports/requires a target.

        Parameters
        ----------
        reaction : Union[str, ReactionType]
            The reaction to check

        Returns
        -------
        bool
            True if the reaction can have a target, False otherwise
        """
        if isinstance(reaction, ReactionType):
            reaction = reaction.value

        reaction = reaction.lower().strip()

        if reaction not in self.REACTION_DATA:
            return False

        data = self.REACTION_DATA[reaction]
        sentence_type = data["type"]

        if sentence_type == SentenceType.TRANSITIVE:
            return True
        elif sentence_type == SentenceType.COMPLEX:
            # Type checker knows this is ComplexReaction
            template = data["template"]  # type: ignore
            return "{target}" in template
        else:
            return False

    def requires_target(self, reaction: Union[str, ReactionType]) -> bool:
        """
        Check if a reaction requires a target.

        Parameters
        ----------
        reaction : Union[str, ReactionType]
            The reaction to check

        Returns
        -------
        bool
            True if the reaction requires a target, False otherwise
        """
        if isinstance(reaction, ReactionType):
            reaction = reaction.value

        reaction = reaction.lower().strip()

        if reaction not in self.REACTION_DATA:
            return False

        data = self.REACTION_DATA[reaction]
        return data["type"] == SentenceType.TRANSITIVE

    def get_supported_reactions(self) -> list[str]:
        """
        Get a list of all supported reaction names.

        Returns
        -------
        list[str]
            List of supported reaction names
        """
        return list(self.REACTION_DATA.keys())

    def get_reaction_info(self, reaction: Union[str, ReactionType]) -> dict:
        """
        Get detailed information about a reaction.

        Parameters
        ----------
        reaction : Union[str, ReactionType]
            The reaction to get info for

        Returns
        -------
        dict
            Dictionary containing reaction information

        Examples
        --------
        >>> formatter = ReactionFormatter()
        >>> info = formatter.get_reaction_info("hug")
        >>> print(info)
        {
            'reaction': 'hug',
            'type': 'transitive',
            'supports_target': True,
            'requires_target': True,
            'verb': 'hugs'
        }
        """
        if isinstance(reaction, ReactionType):
            reaction = reaction.value

        reaction = reaction.lower().strip()

        if reaction not in self.REACTION_DATA:
            raise ValueError(f"Unsupported reaction: {reaction}")

        data = self.REACTION_DATA[reaction]

        result = {
            "reaction": reaction,
            "type": data["type"].value,
            "supports_target": self.supports_target(reaction),
            "requires_target": self.requires_target(reaction),
        }

        # Add type-specific fields
        if (
            data["type"] == SentenceType.TRANSITIVE
            or data["type"] == SentenceType.INTRANSITIVE
        ):
            result["verb"] = data["verb"]
        elif data["type"] == SentenceType.STATE:
            result["adjective"] = data["adjective"]
        elif data["type"] == SentenceType.COMPLEX:
            result["template"] = data["template"]

        return result
