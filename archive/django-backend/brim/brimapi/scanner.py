"""Lightweight website veracity scanner agent.

Uses only the Python standard library so it runs without extra dependencies.
It fetches a page, inspects real signals (TLS, domain authority, citations,
author/contact transparency, external references) and computes a 0-100 score.
"""

import re
import socket
from html.parser import HTMLParser
from urllib.parse import urlparse
from urllib.request import Request, urlopen

USER_AGENT = "BrimVeracityAgent/1.0 (+https://brim.local)"
TIMEOUT_SECONDS = 6
MAX_BYTES = 600_000

AUTHORITY_TLDS = {
    "gov": 1.0,
    "edu": 0.95,
    "mil": 0.95,
    "int": 0.9,
    "org": 0.78,
}

TRANSPARENCY_KEYWORDS = [
    "about",
    "contact",
    "author",
    "editorial",
    "privacy",
    "references",
    "citation",
    "sources",
    "methodology",
]


class _PageParser(HTMLParser):
    def __init__(self):
        super().__init__()
        self.title = ""
        self._in_title = False
        self.links = 0
        self.external_links = 0
        self.headings = 0
        self.has_author_meta = False
        self.text_chunks = []

    def handle_starttag(self, tag, attrs):
        attrs = dict(attrs)
        if tag == "title":
            self._in_title = True
        elif tag == "a" and attrs.get("href"):
            self.links += 1
            if attrs["href"].startswith("http"):
                self.external_links += 1
        elif tag in {"h1", "h2", "h3"}:
            self.headings += 1
        elif tag == "meta":
            name = (attrs.get("name") or attrs.get("property") or "").lower()
            if name in {"author", "article:author"}:
                self.has_author_meta = True

    def handle_endtag(self, tag):
        if tag == "title":
            self._in_title = False

    def handle_data(self, data):
        if self._in_title:
            self.title += data
        stripped = data.strip()
        if stripped:
            self.text_chunks.append(stripped)


def _domain_authority(domain):
    tld = domain.rsplit(".", 1)[-1].lower() if "." in domain else ""
    return AUTHORITY_TLDS.get(tld, 0.55)


def scan_site(url):
    parsed = urlparse(url)
    if parsed.scheme not in {"http", "https"}:
        return {
            "url": url,
            "domain": parsed.netloc or url,
            "reachable": False,
            "score": 0.0,
            "signals": {"error": "Only http and https URLs can be scanned."},
        }

    domain = parsed.netloc
    signals = {
        "https": parsed.scheme == "https",
        "domain_authority": _domain_authority(domain),
    }

    reachable = False
    body = ""
    try:
        request = Request(url, headers={"User-Agent": USER_AGENT})
        with urlopen(request, timeout=TIMEOUT_SECONDS) as response:
            reachable = True
            signals["status_code"] = getattr(response, "status", 200)
            raw = response.read(MAX_BYTES)
            charset = response.headers.get_content_charset() or "utf-8"
            body = raw.decode(charset, errors="replace")
    except (socket.timeout, OSError, ValueError) as error:
        signals["error"] = f"Could not reach site: {error}"

    if reachable and body:
        parser = _PageParser()
        try:
            parser.feed(body)
        except Exception:
            pass

        text = " ".join(parser.text_chunks).lower()
        transparency_hits = sorted(
            {keyword for keyword in TRANSPARENCY_KEYWORDS if keyword in text}
        )
        citation_mentions = len(re.findall(r"\bcit(?:e|ation|ed)\b", text))
        reference_mentions = len(re.findall(r"\breference[s]?\b", text))

        signals.update(
            {
                "title": parser.title.strip()[:160],
                "total_links": parser.links,
                "external_links": parser.external_links,
                "headings": parser.headings,
                "author_metadata": parser.has_author_meta,
                "transparency_signals": transparency_hits,
                "citation_mentions": citation_mentions,
                "reference_mentions": reference_mentions,
            }
        )

    score = _compute_score(signals, reachable)
    return {
        "url": url,
        "domain": domain or url,
        "reachable": reachable,
        "score": score,
        "signals": signals,
    }


def _compute_score(signals, reachable):
    if not reachable:
        # Domain-only fallback when the page cannot be fetched.
        return round(signals.get("domain_authority", 0.5) * 40, 2)

    weights = {
        "https": 12 if signals.get("https") else 0,
        "authority": signals.get("domain_authority", 0.55) * 30,
        "author": 10 if signals.get("author_metadata") else 0,
        "transparency": min(len(signals.get("transparency_signals", [])), 5) * 4,
        "references": min(
            signals.get("citation_mentions", 0) + signals.get("reference_mentions", 0),
            10,
        )
        * 1.5,
        "external_links": min(signals.get("external_links", 0), 20) * 0.4,
        "structure": min(signals.get("headings", 0), 12) * 0.5,
    }
    score = sum(weights.values())
    signals["score_breakdown"] = {key: round(value, 2) for key, value in weights.items()}
    return round(min(score, 100.0), 2)
