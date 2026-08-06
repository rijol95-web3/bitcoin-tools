from __future__ import annotations

import html
import json
import statistics
import sys
import time
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path
from typing import Callable

import requests


OUTPUT_FILE = Path("assets/bitcoin-stats.svg")
CACHE_FILE = Path("assets/bitcoin-market-cache.json")

TOTAL_ADDRESSES = 56_701_876
CHUNK_COUNT = 94
MAX_CHUNK_SIZE_MIB = 24

REQUEST_TIMEOUT = 15
MAX_RETRIES = 3

SESSION = requests.Session()
SESSION.headers.update(
    {
        "User-Agent": "bitcoin-address-dataset-banner/1.0",
        "Accept": "application/json",
    }
)


@dataclass(frozen=True)
class PriceQuote:
    provider: str
    price_usd: float
    change_24h_percent: float | None = None


def request_json(url: str) -> dict:
    last_error: Exception | None = None

    for attempt in range(1, MAX_RETRIES + 1):
        try:
            response = SESSION.get(url, timeout=REQUEST_TIMEOUT)
            response.raise_for_status()
            data = response.json()

            if not isinstance(data, dict):
                raise ValueError("API response is not a JSON object")

            return data

        except (requests.RequestException, ValueError) as error:
            last_error = error

            if attempt < MAX_RETRIES:
                time.sleep(2 ** (attempt - 1))

    raise RuntimeError(f"Request failed: {url}: {last_error}")


def fetch_coingecko() -> PriceQuote:
    data = request_json(
        "https://api.coingecko.com/api/v3/simple/price"
        "?ids=bitcoin&vs_currencies=usd&include_24hr_change=true"
    )

    bitcoin = data.get("bitcoin")
    if not isinstance(bitcoin, dict):
        raise ValueError("CoinGecko response is missing bitcoin")

    price = float(bitcoin["usd"])
    change_value = bitcoin.get("usd_24h_change")
    change = float(change_value) if change_value is not None else None

    if price <= 0:
        raise ValueError("CoinGecko returned an invalid price")

    return PriceQuote("CoinGecko", price, change)


def fetch_coinbase() -> PriceQuote:
    data = request_json(
        "https://api.coinbase.com/v2/prices/BTC-USD/spot"
    )

    item = data.get("data")
    if not isinstance(item, dict):
        raise ValueError("Coinbase response is missing data")

    price = float(item["amount"])

    if price <= 0:
        raise ValueError("Coinbase returned an invalid price")

    return PriceQuote("Coinbase", price)


def fetch_kraken() -> PriceQuote:
    data = request_json(
        "https://api.kraken.com/0/public/Ticker?pair=XBTUSD"
    )

    errors = data.get("error")
    if isinstance(errors, list) and errors:
        raise RuntimeError(f"Kraken returned errors: {errors}")

    result = data.get("result")
    if not isinstance(result, dict) or not result:
        raise ValueError("Kraken response is missing ticker data")

    ticker = next(iter(result.values()))
    if not isinstance(ticker, dict):
        raise ValueError("Kraken ticker is invalid")

    close_values = ticker.get("c")
    if not isinstance(close_values, list) or not close_values:
        raise ValueError("Kraken response is missing close price")

    price = float(close_values[0])
    change: float | None = None

    open_value = ticker.get("o")
    if open_value is not None:
        open_price = float(open_value)
        if open_price > 0:
            change = (price - open_price) / open_price * 100

    if price <= 0:
        raise ValueError("Kraken returned an invalid price")

    return PriceQuote("Kraken", price, change)


def read_cache() -> tuple[float, float | None, list[str]] | None:
    if not CACHE_FILE.exists():
        return None

    try:
        data = json.loads(CACHE_FILE.read_text(encoding="utf-8"))
        return (
            float(data["price_usd"]),
            (
                float(data["change_24h_percent"])
                if data.get("change_24h_percent") is not None
                else None
            ),
            [str(item) for item in data.get("providers", ["Cached value"])],
        )
    except (OSError, ValueError, KeyError, TypeError, json.JSONDecodeError):
        return None


def save_cache(
    price_usd: float,
    change_24h: float | None,
    providers: list[str],
) -> None:
    CACHE_FILE.parent.mkdir(parents=True, exist_ok=True)
    CACHE_FILE.write_text(
        json.dumps(
            {
                "price_usd": price_usd,
                "change_24h_percent": change_24h,
                "providers": providers,
                "updated_at": datetime.now(timezone.utc).isoformat(),
            },
            indent=2,
        )
        + "\n",
        encoding="utf-8",
    )


def fetch_market_data() -> tuple[float, float | None, list[str]]:
    sources: list[tuple[str, Callable[[], PriceQuote]]] = [
        ("CoinGecko", fetch_coingecko),
        ("Coinbase", fetch_coinbase),
        ("Kraken", fetch_kraken),
    ]

    quotes: list[PriceQuote] = []

    for name, fetcher in sources:
        try:
            quote = fetcher()
            quotes.append(quote)
            print(f"[OK] {quote.provider}: ${quote.price_usd:,.2f}")
        except Exception as error:
            print(
                f"[WARNING] {name} failed: {type(error).__name__}: {error}",
                file=sys.stderr,
            )

    if not quotes:
        cached = read_cache()
        if cached is None:
            raise RuntimeError("All BTC price providers failed and no cache exists")

        print("[WARNING] Using cached market data", file=sys.stderr)
        return cached

    price = float(statistics.median(q.price_usd for q in quotes))
    changes = [
        q.change_24h_percent
        for q in quotes
        if q.change_24h_percent is not None
    ]
    change = float(statistics.median(changes)) if changes else None
    providers = [q.provider for q in quotes]

    save_cache(price, change, providers)
    return price, change, providers


def fmt_price(value: float) -> str:
    return f"${value:,.2f}"


def fmt_change(value: float | None) -> str:
    if value is None:
        return "N/A"

    return f"{'+' if value >= 0 else ''}{value:.2f}%"


def change_color(value: float | None) -> str:
    if value is None:
        return "#94a3b8"
    if value > 0:
        return "#22c55e"
    if value < 0:
        return "#ef4444"
    return "#94a3b8"


def generate_svg(
    price_usd: float,
    change_24h: float | None,
    providers: list[str],
) -> str:
    updated_at = datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M UTC")
    price_text = html.escape(fmt_price(price_usd))
    change_text = html.escape(fmt_change(change_24h))
    providers_text = html.escape(", ".join(providers))
    change_fill = change_color(change_24h)

    return f'''<svg xmlns="http://www.w3.org/2000/svg"
  width="1200" height="420" viewBox="0 0 1200 420"
  role="img" aria-labelledby="title description">

  <title id="title">Bitcoin Address Dataset</title>
  <desc id="description">Live Bitcoin price and dataset statistics</desc>

  <defs>
    <linearGradient id="bg" x1="0" y1="0" x2="1" y2="1">
      <stop offset="0%" stop-color="#050816"/>
      <stop offset="55%" stop-color="#0f172a"/>
      <stop offset="100%" stop-color="#172033"/>
    </linearGradient>

    <radialGradient id="glow">
      <stop offset="0%" stop-color="#f7931a" stop-opacity=".48"/>
      <stop offset="100%" stop-color="#f7931a" stop-opacity="0"/>
    </radialGradient>

    <linearGradient id="orange" x1="0" y1="0" x2="1" y2="1">
      <stop offset="0%" stop-color="#ffb347"/>
      <stop offset="100%" stop-color="#f7931a"/>
    </linearGradient>

    <filter id="shadow" x="-40%" y="-40%" width="180%" height="180%">
      <feDropShadow dx="0" dy="12" stdDeviation="18"
        flood-color="#000000" flood-opacity=".50"/>
    </filter>
  </defs>

  <rect width="1200" height="420" rx="30" fill="url(#bg)"/>

  <circle cx="145" cy="210" r="135" fill="url(#glow)"/>
  <circle cx="145" cy="210" r="88" fill="url(#orange)" filter="url(#shadow)"/>
  <text x="145" y="244" text-anchor="middle"
    font-family="Arial, Helvetica, sans-serif"
    font-size="108" font-weight="700" fill="#ffffff">₿</text>

  <text x="285" y="72"
    font-family="Arial, Helvetica, sans-serif"
    font-size="38" font-weight="700" fill="#ffffff">
    Bitcoin Address Dataset
  </text>

  <text x="285" y="108"
    font-family="Arial, Helvetica, sans-serif"
    font-size="17" fill="#94a3b8">
    Live market data · chunked public dataset · Windows balance checker
  </text>

  <rect x="285" y="145" width="420" height="120" rx="20"
    fill="#09111f" stroke="#334155"/>
  <text x="312" y="181"
    font-family="Arial, Helvetica, sans-serif"
    font-size="16" fill="#94a3b8">BTC / USD</text>
  <text x="312" y="235"
    font-family="Arial, Helvetica, sans-serif"
    font-size="44" font-weight="700" fill="#f7931a">{price_text}</text>
  <text x="674" y="183" text-anchor="end"
    font-family="Arial, Helvetica, sans-serif"
    font-size="15" fill="#94a3b8">24h change</text>
  <text x="674" y="222" text-anchor="end"
    font-family="Arial, Helvetica, sans-serif"
    font-size="27" font-weight="700" fill="{change_fill}">{change_text}</text>

  <rect x="730" y="145" width="205" height="120" rx="20"
    fill="#09111f" stroke="#334155"/>
  <text x="756" y="181"
    font-family="Arial, Helvetica, sans-serif"
    font-size="16" fill="#94a3b8">Total addresses</text>
  <text x="756" y="229"
    font-family="Arial, Helvetica, sans-serif"
    font-size="29" font-weight="700" fill="#ffffff">{TOTAL_ADDRESSES:,}</text>

  <rect x="960" y="145" width="190" height="120" rx="20"
    fill="#09111f" stroke="#334155"/>
  <text x="986" y="181"
    font-family="Arial, Helvetica, sans-serif"
    font-size="16" fill="#94a3b8">Dataset chunks</text>
  <text x="986" y="229"
    font-family="Arial, Helvetica, sans-serif"
    font-size="31" font-weight="700" fill="#ffffff">{CHUNK_COUNT}</text>

  <line x1="285" y1="305" x2="1150" y2="305"
    stroke="#334155" stroke-width="1"/>

  <text x="285" y="343"
    font-family="Arial, Helvetica, sans-serif"
    font-size="15" fill="#94a3b8">
    Maximum chunk size: {MAX_CHUNK_SIZE_MIB} MiB
  </text>

  <text x="285" y="373"
    font-family="Arial, Helvetica, sans-serif"
    font-size="14" fill="#64748b">
    Price sources: {providers_text}
  </text>

  <text x="1150" y="343" text-anchor="end"
    font-family="Arial, Helvetica, sans-serif"
    font-size="15" fill="#94a3b8">
    Updated: {updated_at}
  </text>
</svg>
'''


def main() -> None:
    OUTPUT_FILE.parent.mkdir(parents=True, exist_ok=True)

    price_usd, change_24h, providers = fetch_market_data()
    svg = generate_svg(price_usd, change_24h, providers)

    OUTPUT_FILE.write_text(svg, encoding="utf-8", newline="\n")

    print(f"Generated: {OUTPUT_FILE}")
    print(f"BTC price: {fmt_price(price_usd)}")
    print(f"24h change: {fmt_change(change_24h)}")


if __name__ == "__main__":
    main()
