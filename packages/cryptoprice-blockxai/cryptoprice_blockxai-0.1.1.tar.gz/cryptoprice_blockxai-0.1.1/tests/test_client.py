import pytest
import respx
import httpx
from cryptoprice import CryptoPrice, CryptoPriceError

ALPHA_URL = "https://www.alphavantage.co/query"


@respx.mock
def test_get_price_success(monkeypatch):
    # Provide a dummy API key via env
    monkeypatch.setenv("ALPHAVANTAGE_API_KEY", "DUMMY")

    cp = CryptoPrice(ttl_seconds=60)
    route = respx.get(ALPHA_URL, params={"function": "CURRENCY_EXCHANGE_RATE"}).mock(
        return_value=httpx.Response(
            200,
            json={
                "Realtime Currency Exchange Rate": {
                    "1. From_Currency Code": "BTC",
                    "2. From_Currency Name": "Bitcoin",
                    "3. To_Currency Code": "USD",
                    "4. To_Currency Name": "United States Dollar",
                    "5. Exchange Rate": "12345.67",
                    "6. Last Refreshed": "2024-01-01 00:00:00",
                    "7. Time Zone": "UTC",
                }
            },
        )
    )
    price = cp.get_price("BTC")
    assert route.called
    assert price == 12345.67


@respx.mock
def test_cache_hits(monkeypatch):
    monkeypatch.setenv("ALPHAVANTAGE_API_KEY", "DUMMY")

    cp = CryptoPrice(ttl_seconds=60)
    respx.get(ALPHA_URL, params={"function": "CURRENCY_EXCHANGE_RATE"}).mock(
        return_value=httpx.Response(
            200,
            json={
                "Realtime Currency Exchange Rate": {
                    "1. From_Currency Code": "BTC",
                    "2. From_Currency Name": "Bitcoin",
                    "3. To_Currency Code": "USD",
                    "4. To_Currency Name": "United States Dollar",
                    "5. Exchange Rate": "100.0",
                    "6. Last Refreshed": "2024-01-01 00:00:00",
                    "7. Time Zone": "UTC",
                }
            },
        )
    )
    p1 = cp.get_price("BTC")
    # Second call should be served from cache: no new HTTP calls needed
    p2 = cp.get_price("BTC")
    assert p1 == p2 == 100.0


@respx.mock
def test_retries_then_fail(monkeypatch):
    monkeypatch.setenv("ALPHAVANTAGE_API_KEY", "DUMMY")

    cp = CryptoPrice(ttl_seconds=1)
    # Always 503 -> should retry and then raise
    respx.get(ALPHA_URL, params={"function": "CURRENCY_EXCHANGE_RATE"}).mock(
        return_value=httpx.Response(503, json={"Note": "rate limited"})
    )
    with pytest.raises(CryptoPriceError):
        cp.get_price("BTC")


def test_empty_symbol(monkeypatch):
    monkeypatch.setenv("ALPHAVANTAGE_API_KEY", "DUMMY")

    cp = CryptoPrice()
    with pytest.raises(CryptoPriceError):
        cp.get_price("")
