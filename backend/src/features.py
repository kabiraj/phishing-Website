from __future__ import annotations
import ipaddress
import math
import re
from collections import Counter
from urllib.parse import urlparse

SUSPICIOUS_WORDS = {
    "login", "signin", "verify", "verification", "account", "secure",
    "security", "update", "confirm", "password", "credential", "bank",
    "billing", "payment", "invoice", "wallet", "authorize", "unlock"
}
SHORTENERS = {"bit.ly", "tinyurl.com", "t.co", "goo.gl", "ow.ly", "is.gd", "buff.ly"}

def _entropy(s: str) -> float:
    if not s:
        return 0.0
    counts = Counter(s)
    n = len(s)
    return -sum((c/n) * math.log2(c/n) for c in counts.values())

def _is_ip(host: str) -> int:
    try:
        ipaddress.ip_address(host)
        return 1
    except ValueError:
        return 0

def extract_features(url: str) -> dict:
    """Convert one raw URL into explainable lexical/structural security features."""
    raw = str(url).strip()
      # Clean brackets to prevent IPv6 errors before parsing
    clean_raw = str(raw).replace('[', '').replace(']', '')
    try:
        parsed = urlparse(clean_raw if re.match(r"^[a-zA-Z][a-zA-Z0-9+.-]*://", clean_raw) else "//" + clean_raw)
    except ValueError:
        # Fallback if a URL is still deeply broken
        class BrokenURL:
            scheme = netloc = path = query = fragment = ""
        parsed = BrokenURL()
    host = (parsed.hostname or "").lower()
    path = parsed.path or ""
    query = parsed.query or ""
    fragment = parsed.fragment or ""
    lower = raw.lower()

    host_labels = [x for x in host.split(".") if x]
    special = sum(1 for c in raw if not c.isalnum())
    digits = sum(c.isdigit() for c in raw)
    letters = sum(c.isalpha() for c in raw)
    suspicious_count = sum(1 for w in SUSPICIOUS_WORDS if w in lower)
    encoded_count = len(re.findall(r"%[0-9a-fA-F]{2}", raw))
    repeated_slashes = len(re.findall(r"/{2,}", path))
    tld = host_labels[-1] if len(host_labels) >= 2 else ""

    return {
        "url_length": len(raw),
        "hostname_length": len(host),
        "path_length": len(path),
        "query_length": len(query),
        "fragment_length": len(fragment),
        "num_dots": raw.count("."),
        "num_hyphens": raw.count("-"),
        "num_underscores": raw.count("_"),
        "num_slashes": raw.count("/"),
        "num_question": raw.count("?"),
        "num_equals": raw.count("="),
        "num_ampersands": raw.count("&"),
        "num_at": raw.count("@"),
        "num_colons": raw.count(":"),
        "num_digits": digits,
        "digit_ratio": digits / max(len(raw), 1),
        "letter_ratio": letters / max(len(raw), 1),
        "special_ratio": special / max(len(raw), 1),
        "num_subdomains": max(len(host_labels) - 2, 0),
        "num_path_segments": len([x for x in path.split("/") if x]),
        "num_query_params": len([x for x in query.split("&") if x]),
        "has_ip": _is_ip(host),
        "has_https": int(parsed.scheme.lower() == "https"),
        "has_port": 1 if (parsed.hostname and ":" in (parsed.netloc.split("@")[-1].split("]")[-1]) and parsed.netloc.split(":")[-1].isdigit()) else 0,
        "has_fragment": int(bool(fragment)),
        "has_percent_encoding": int(encoded_count > 0),
        "encoded_char_count": encoded_count,
        "repeated_slash_count": repeated_slashes,
        "suspicious_keyword_count": suspicious_count,
        "has_shortener": int(host in SHORTENERS),
        "hostname_entropy": _entropy(host),
        "path_entropy": _entropy(path),
        "url_entropy": _entropy(raw),
        "tld_length": len(tld),
        "tld_is_long": int(len(tld) >= 6),
        "hostname_has_digit": int(any(c.isdigit() for c in host)),
        "hostname_has_hyphen": int("-" in host),
        "hostname_has_at": int("@" in host),
    }

def extract_dataframe(df):
    import pandas as pd
    features = pd.DataFrame([extract_features(u) for u in df["url"]], index=df.index)
    return features
