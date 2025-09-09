from __future__ import annotations
import os
import time
from typing import Dict, Optional

import httpx

from .errors import CryptoPriceError

ALPHAVANTAGE_BASE = "https://www.alphavantage.co"
ALPHAVANTAGE_PATH = "/query"


class _TTLCache:
    def __init__(self, ttl_seconds: float = 15.0):
        self.ttl = ttl_seconds
        self._store: Dict[str, tuple[float, float]] = {}

    def get(self, key: str) -> Optional[float]:
        item = self._store.get(key)
        if not item:
            return None
        expires_at, value = item
        if time.time() > expires_at:
            self._store.pop(key, None)
            return None
        return value

    def set(self, key: str, value: float) -> None:
        self._store[key] = (time.time() + self.ttl, value)


def _retry_request(client: httpx.Client, url: str, params: Dict[str, str]) -> httpx.Response:
    backoff = 0.3
    last_exc: Optional[Exception] = None
    for _ in range(4):
        try:
            r = client.get(url, params=params)
            if r.status_code in (429, 503):
                time.sleep(backoff)
                backoff *= 2
                continue
            r.raise_for_status()
            return r
        except httpx.HTTPError as e:
            last_exc = e
            time.sleep(backoff)
            backoff *= 2
    raise CryptoPriceError(f"Request failed after retries: {last_exc}")


class CryptoPrice:
    """
    Simple, synchronous Alpha Vantage wrapper with TTL cache and retries.

    Fetches crypto price using the CURRENCY_EXCHANGE_RATE function.
    """

    def __init__(
        self,
        api_key: Optional[str] = None,
        base_url: str = ALPHAVANTAGE_BASE,
        timeout: float = 5.0,
        ttl_seconds: float = 15.0,
        vs_currency: str = "usd",
    ):
        self._client = httpx.Client(base_url=base_url, timeout=timeout, headers={"Accept": "application/json"})
        self._cache = _TTLCache(ttl_seconds)
        self._vs = vs_currency.upper()
        self._api_key = api_key or os.getenv("ALPHAVANTAGE_API_KEY")
        if not self._api_key:
            raise CryptoPriceError(
                "Alpha Vantage API key required. Pass api_key=... or set ALPHAVANTAGE_API_KEY in env."
            )

    def get_price(self, symbol: str) -> float:
        """
        Returns the current price for the given symbol in the configured vs_currency (default USD).
        Example: get_price("BTC") -> 61000.23
        """
        if not symbol:
            raise CryptoPriceError("Symbol must be non-empty")

        key = f"{symbol.upper()}:{self._vs}"
        cached = self._cache.get(key)
        if cached is not None:
            return cached

        url = ALPHAVANTAGE_PATH
        params = {
            "function": "CURRENCY_EXCHANGE_RATE",
            "from_currency": symbol.upper(),
            "to_currency": self._vs,
            "apikey": self._api_key,
        }

        r = _retry_request(self._client, url, params)
        data = r.json()
        try:
            payload = data["Realtime Currency Exchange Rate"]
            price_str = payload["5. Exchange Rate"]
            price = float(price_str)
        except (KeyError, ValueError, TypeError) as e:
            raise CryptoPriceError(f"Bad response format for {symbol}:{self._vs}: {data}") from e

        self._cache.set(key, price)
        return price

    def close(self) -> None:
        self._client.close()


class CryptoPriceAsync:
    """
    Async variant using httpx.AsyncClient with the same API.
    """

    def __init__(
        self,
        api_key: Optional[str] = None,
        base_url: str = ALPHAVANTAGE_BASE,
        timeout: float = 5.0,
        ttl_seconds: float = 15.0,
        vs_currency: str = "usd",
    ):
        self._client = httpx.AsyncClient(base_url=base_url, timeout=timeout, headers={"Accept": "application/json"})
        self._cache = _TTLCache(ttl_seconds)
        self._vs = vs_currency.upper()
        self._api_key = api_key or os.getenv("ALPHAVANTAGE_API_KEY")
        if not self._api_key:
            raise CryptoPriceError(
                "Alpha Vantage API key required. Pass api_key=... or set ALPHAVANTAGE_API_KEY in env."
            )

    async def get_price(self, symbol: str) -> float:
        if not symbol:
            raise CryptoPriceError("Symbol must be non-empty")

        key = f"{symbol.upper()}:{self._vs}"
        cached = self._cache.get(key)
        if cached is not None:
            return cached

        url = ALPHAVANTAGE_PATH
        params = {
            "function": "CURRENCY_EXCHANGE_RATE",
            "from_currency": symbol.upper(),
            "to_currency": self._vs,
            "apikey": self._api_key,
        }

        backoff = 0.3
        last_exc: Optional[Exception] = None
        for _ in range(4):
            try:
                r = await self._client.get(url, params=params)
                if r.status_code in (429, 503):
                    await _asleep(backoff)
                    backoff *= 2
                    continue
                r.raise_for_status()
                data = r.json()
                payload = data["Realtime Currency Exchange Rate"]
                price_str = payload["5. Exchange Rate"]
                price = float(price_str)
                self._cache.set(key, price)
                return price
            except (httpx.HTTPError, KeyError, ValueError, TypeError) as e:
                last_exc = e
                await _asleep(backoff)
                backoff *= 2
        raise CryptoPriceError(f"Async request failed after retries: {last_exc}")

    async def aclose(self) -> None:
        await self._client.aclose()


async def _asleep(seconds: float) -> None:
    import asyncio
    await asyncio.sleep(seconds)
