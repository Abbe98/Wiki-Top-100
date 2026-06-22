"""Hatnote API data source — fetches the daily top 100 Wikipedia articles.

Filters out non-article pages (Special:, Wikipedia:, Talk:, etc.).
Results are cached for 24 hours.
"""
import time
import httpx

from ..config import HEADERS, HATNOTE_URL, HATNOTE_CACHE_TTL, WIKI_BASE_URL
from ..cache import _cache_get, _cache_set


SKIP_PREFIXES = {"Special", "Wikipedia", "Wikivoyage", "Talk", "User", "Help", "File",
                 "Template", "Category", "Portal", "Draft", "Module", "MediaWiki"}


def fetch_json(url, max_retries=2):
    """Fetch and parse JSON from a URL with a timeout, user-agent, and retries."""
    for attempt in range(max_retries + 1):
        try:
            with httpx.Client(headers=HEADERS, timeout=30.0) as client:
                resp = client.get(url)
                resp.raise_for_status()
                return resp.json()
        except Exception as e:
            if attempt < max_retries:
                time.sleep(0.5)
            else:
                raise


def fetch_top100(year, month, day, hatnote_url=None, base_url=None):
    """Fetch the top 100 list from the Hatnote API (cached for 24h).

    Filters out Special:, Wikipedia:, Talk:, and other non-article pages.
    Returns a list of dicts with id, title, rank, views, summary, image_url, url.
    Article IDs use underscores (matching Wikipedia URL convention).

    hatnote_url and base_url default to the module-level WIKI_HATNOTE_URL /
    WIKI_BASE_URL but can be overridden per-request to target a different
    Wikimedia project.
    """
    hatnote_url = hatnote_url or HATNOTE_URL
    base_url = base_url or WIKI_BASE_URL
    cache_key = f"{hatnote_url.format(year=year, month=month, day=day)}"
    # Cache key per fully-qualified URL so different wikis don't collide.
    cache_name = cache_key.replace("https://", "").replace("/", "_")
    cached = _cache_get("hatnote", cache_name, HATNOTE_CACHE_TTL)
    if cached is not None:
        return cached

    data = fetch_json(cache_key)
    articles = []
    for a in data["articles"]:
        title = a["article"]
        prefix = title.split(":")[0]
        if prefix in SKIP_PREFIXES or title == "Main_Page":
            continue
        articles.append({
            "id": title.replace(" ", "_"),
            "title": a["title"],
            "rank": a["rank"],
            "views": a["views"],
            "summary": a.get("summary", ""),
            "image_url": a.get("image_url", ""),
            "url": a.get("url", f"{base_url}{title}"),
            "history": a.get("history", []),
        })

    _cache_set("hatnote", cache_name, articles)
    return articles
