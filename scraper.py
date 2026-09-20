#!/usr/bin/env -S uv run --quiet
# /// script
# requires-python = ">=3.11"
# dependencies = [
#     "beautifulsoup4",
#     "requests",
# ]
# ///

"""Search dba.dk and print the ads that match the query."""

import json
import logging
import sys

import requests
from bs4 import BeautifulSoup

QUERY = "spilerstage"
SEARCH_URL = "https://www.dba.dk/recommerce/forsale/search?q={query}"
HEADERS = {
    "User-Agent": "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 "
    "(KHTML, like Gecko) Chrome/124 Safari/537.36"
}
LOGGER = logging.getLogger(__name__)


def fetch(url: str) -> str:
    """Fetch a URL and return the HTML body."""
    response = requests.get(url, headers=HEADERS, timeout=30)
    response.raise_for_status()
    return response.text


def json_ld(html: str, script_id: str | None = None) -> dict:
    """Extract one JSON-LD object from HTML."""
    soup = BeautifulSoup(html, "html.parser")
    selector = "script[type='application/ld+json']"
    if script_id:
        selector += f"#{script_id}"
    script = soup.select_one(selector)
    if script is None:
        raise ValueError(f"no JSON-LD script found: {script_id}")
    return json.loads(script.get_text())


def search_results(query: str) -> list[dict]:
    """Return title, price and url for every ad on the search page."""
    data = json_ld(fetch(SEARCH_URL.format(query=query)), "seoStructuredData")
    return [
        {
            "title": entry["item"]["name"],
            "price": int(entry["item"]["offers"]["price"]),
            "url": entry["item"]["url"],
        }
        for entry in data["mainEntity"]["itemListElement"]
    ]


def item_details(url: str) -> dict:
    """Return title, price and description for one ad page."""
    data = json_ld(fetch(url))
    return {
        "title": data["name"],
        "price": int(data["offers"]["price"]),
        "description": data.get("description", ""),
        "url": url,
    }


def main() -> None:
    """Search, keep ads whose title contains the query and print their details."""
    query = sys.argv[1] if len(sys.argv) > 1 else QUERY
    logging.basicConfig(level=logging.INFO, format="- DBA Ad %(message)s")
    for result in search_results(query):
        if query.lower() not in result["title"].lower():
            continue
        ad = item_details(result["url"])
        LOGGER.info("%s scraped", ad["title"])
        print(f"{ad['title']} | {ad['price']} kr | {ad['url']} | {ad['description']}")


if __name__ == "__main__":
    main()
