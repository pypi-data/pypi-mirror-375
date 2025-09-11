REST_BASE = "https://api.crypto.com/exchange/v1"
WS_MARKET = "wss://stream.crypto.com/exchange/v1/market"

# Channel names
CHANNEL_TRADE = "trade"
CHANNEL_BOOK = "book"
CHANNEL_TICKER = "ticker"

def to_instrument(symbol: str) -> str:
    """Map canonical symbol like 'BTCUSDT' or 'BTC-USDT' to Crypto.com 'BTC_USDT'."""
    s = symbol.replace("-", "").upper()
    if len(s) >= 6 and s[-4:] in {"USDT", "USDC", "BUSD"}:
        base = s[:-4]
        quote = s[-4:]
    elif len(s) >= 3 and s[-3:] in {"USD", "BTC", "ETH"}:
        base = s[:-3]
        quote = s[-3:]
    else:
        # Fallback: try split by non-alnum
        import re
        parts = re.split(r"[^A-Z0-9]+", s)
        if len(parts) == 2:
            base, quote = parts
        else:
            # last resort, guess base/quote halves
            mid = len(s) // 2
            base, quote = s[:mid], s[mid:]
    return f"{base}_{quote}"

