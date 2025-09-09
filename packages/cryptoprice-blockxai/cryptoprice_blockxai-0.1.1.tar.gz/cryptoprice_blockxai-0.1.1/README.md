# cryptoprice

A tiny Python SDK to get crypto prices in one line – with retries and a TTL cache. Wraps Alpha Vantage’s free API.

```python
from cryptoprice import CryptoPrice

cp = CryptoPrice(api_key="YOUR_ALPHA_VANTAGE_KEY")  # or set env ALPHAVANTAGE_API_KEY
print(cp.get_price("BTC"))     # -> 61234.56 (USD by default)
```

## Install

```
pip install cryptoprice-blockxai
```

## Configure API key

Get a free API key from Alpha Vantage and either:

- Pass directly: `CryptoPrice(api_key="...")`
- Or set environment variable: `export ALPHAVANTAGE_API_KEY=...`

Docs: https://www.alphavantage.co/documentation/

## Why this exists

- Built-in retry-on-failure (including 429/503)
- Fast repeated calls via TTL cache (default 15s)
- Simple, production-ready interface

## API

- `CryptoPrice(vs_currency="usd", ttl_seconds=15.0, api_key=None)`: sync client
  - `get_price("BTC") -> float`
- `CryptoPriceAsync(...).get_price("ETH") -> float`: async variant

## Notes

- Default `vs_currency` is USD. Override with `vs_currency="EUR"`, etc.
- Alpha Vantage endpoint used: `CURRENCY_EXCHANGE_RATE`.
- Respect free API rate limits. Keep a reasonable TTL in production.

## Development

```
python -m venv .venv && . .venv/bin/activate
pip install -e .
pip install pytest respx
pytest
```

## License

MIT
