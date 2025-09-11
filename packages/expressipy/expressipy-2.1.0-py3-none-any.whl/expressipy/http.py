from typing import Any, Dict, List, Optional

import aiohttp
from aiohttp import ClientTimeout, ClientSession

from . import __version__
from .exceptions import BadRequest, ExpressipyException, HTTPException, NotFound


class HTTPClient:
    """Low-level HTTP client for the OtakuGifs API."""

    BASE_URL = "https://api.otakugifs.xyz/gif"

    def __init__(self, timeout: float = 10.0) -> None:
        self._timeout = ClientTimeout(total=timeout)
        self._session: Optional[ClientSession] = None

    async def _get_session(self) -> ClientSession:
        """Get or create the aiohttp session."""

        if self._session is None or self._session.closed:
            self._session = ClientSession(
                timeout=self._timeout,
                headers={"User-Agent": f"expressipy/{__version__}"},
            )

        return self._session

    async def close(self) -> None:
        """Close the HTTP session."""

        if self._session and not self._session.closed:
            await self._session.close()

    async def _request(
        self, method: str, endpoint: str, **kwargs: Any
    ) -> Dict[str, Any]:
        """Make an HTTP request to the API."""

        session = await self._get_session()
        url = f"{self.BASE_URL}{endpoint}"

        # TODO: Log.debug

        try:
            async with session.request(method, url, **kwargs) as response:
                # TODO: log.debug

                if response.status == 200:
                    return await response.json()
                elif response.status == 404:
                    raise NotFound(response, "Resource not found")
                elif response.status == 400:
                    raise BadRequest(response, "Bad request")
                else:
                    raise HTTPException(response)

        except aiohttp.ClientError as e:
            # TODO: log.error
            raise ExpressipyException(f"Request failed: {e}")

    async def get_all_reactions(self) -> Dict[str, List[str]]:
        return await self._request("GET", "/allreactions")

    async def get_random_gif(self, reaction: str) -> Dict[str, str]:
        """Get a random gif for a specific reaction."""
        params = {"reaction": reaction}
        return await self._request("GET", "/", params=params)
