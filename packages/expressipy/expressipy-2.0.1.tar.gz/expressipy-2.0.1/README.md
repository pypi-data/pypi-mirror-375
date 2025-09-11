# Expressipy - OtakuGIFs API Wrapper

[![PyPI version](https://badge.fury.io/py/expressipy.svg)](https://badge.fury.io/py/expressipy)
[![Python 3.8+](https://img.shields.io/badge/python-3.8+-blue.svg)](https://www.python.org/downloads/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

A modern, fully-typed, async API wrapper for the [OtakuGIFs API](https://otakugifs.xyz).

## ✨ Features

- **🔒 100% Type Safe** - Full mypy compatibility with strict typing
- **⚡ Async/Await** - Built with aiohttp for optimal performance
- **🎯 Intuitive API** - Clean interface
- **🛡️ Error Handling** - Comprehensive exception hierarchy
- **📝 Well Documented** - Extensive docstrings and examples

## 🚀 Quick Start

### Installation

```bash
pip install expressipy
```

### Basic Usage

```python
import asyncio
from expressipy import ExpressipyClient, ReactionType

async def main():
    async with ExpressipyClient() as client:
        # Get a random hug GIF
        gif = await client.get_gif(ReactionType.HUG)
        print(f"Hug GIF: {gif.url}")

        # Get all available reactions
        reactions = await client.get_all_reactions()
        print(f"Available reactions: {len(reactions)}")

asyncio.run(main())
```

### Quick One-Off Requests

```python
from expressipy import ReactionType
from expressipy.utils import get_gif

# For simple one-off requests
gif = await get_gif(ReactionType.HUG)
print(f"Hug GIF: {gif.url}")
```

## 📖 Documentation

### Supported Reactions

The wrapper supports all 66 reaction types from the OtakuGIFs API:

```python
from expressipy import ReactionType

# All available as enum values:
ReactionType.HUG, ReactionType.DANCE,
ReactionType.CRY, ReactionType.LAUGH,
# ... and 60 more!
```

<details>
<summary>View all supported reactions</summary>

`airkiss`, `angrystare`, `bite`, `bleh`, `blush`, `brofist`, `celebrate`, `cheers`, `clap`, `confused`, `cool`, `cry`, `cuddle`, `dance`, `drool`, `evillaugh`, `facepalm`, `handhold`, `happy`, `headbang`, `hug`, `huh`, `kiss`, `laugh`, `lick`, `love`, `mad`, `nervous`, `no`, `nom`, `nosebleed`, `nuzzle`, `nyah`, `pat`, `peek`, `pinch`, `poke`, `pout`, `punch`, `roll`, `run`, `sad`, `scared`, `shout`, `shrug`, `shy`, `sigh`, `sip`, `slap`, `sleep`, `slowclap`, `smack`, `smile`, `smug`, `sneeze`, `sorry`, `stare`, `stop`, `surprised`, `sweat`, `thumbsup`, `tickle`, `tired`, `wave`, `wink`, `woah`, `yawn`, `yay`, `yes`

</details>

### Type Safety

The wrapper provides excellent type safety with multiple input options:

```python
# Using enum (most type-safe, IDE autocomplete)
gif = await client.get_gif(ReactionType.HAPPY)

# Using string literal (also type-safe)
gif = await client.get_gif("dance")

# Case insensitive
gif = await client.get_gif("SURPRISED")
```

### Error Handling

```python
from expressipy import ExpressipyException, HTTPException, NotFound

try:
    gif = await client.get_gif("invalid_reaction")
except ValueError as e:
    print(f"Invalid reaction: {e}")
except HTTPException as e:
    print(f"API error {e.status}: {e}")
except ExpressipyException as e:
    print(f"Something went wrong: {e}")
```

### Advanced Usage

```python
import asyncio
import logging
from expressipy import ExpressipyClient, setup_logging

# Enable debug logging to see HTTP requests
setup_logging(logging.DEBUG)

async def advanced_example():
    # Custom timeout and manual lifecycle management
    client = ExpressipyClient(timeout=30.0)

    try:
        # Get multiple GIFs efficiently with one client
        reactions = [ReactionType.HUG, ReactionType.KISS, ReactionType.WAVE]

        for reaction in reactions:
            gif = await client.get_gif(reaction)
            print(f"{reaction.value}: {gif.url}")

    finally:
        await client.close()  # Always clean up!

asyncio.run(advanced_example())
```

## 🔧 Development

## 📋 Requirements

- Python 3.8+
- aiohttp >= 3.8.0

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🙏 Acknowledgments

- [OtakuGIFs](https://otakugifs.xyz) for providing the awesome API

## 📞 Support

- 📫 Create an issue on [GitHub](https://github.com/AndehUK/expressipy/issues)
- 📖 Read the [documentation](https://github.com/AndehUK/expressipy#readme)

---

If you enjoy this package, please consider giving it a ⭐ on GitHub!
