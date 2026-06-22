"""Configuration management via environment variables and .env file.

Loads settings at module import time. All constants are available for
direct import by other modules.
"""
import os
import re
from pathlib import Path


def _load_dotenv():
    """Load .env file if present, populating os.environ (does not override)."""
    env_path = Path(".env")
    if env_path.exists():
        for line in env_path.read_text().splitlines():
            line = line.strip()
            if not line or line.startswith("#") or "=" not in line:
                continue
            key, _, val = line.partition("=")
            key, val = key.strip(), val.strip().strip("\"'")
            os.environ.setdefault(key, val)


def _is_valid_ua(ua):
    """Check if a User-Agent string appears Wikimedia-compliant (has contact info).

    Wikimedia requires User-Agent strings to include a way to contact the
    developer — either an email address or a project URL. Returns True if
    the string contains an email or http(s) URL.
    """
    return bool(re.search(r'[^@\s]+@[^@\s]+\.[^@\s]+|https?://\S+', ua))


# Load .env at import time (matches original build_graph.py behaviour)
_load_dotenv()


SUPPORTED_PROJECTS = ("wikivoyage", "wikipedia")

WIKI_LANG = os.environ.get("WIKI_LANG", "en")
WIKI_PROJECT = os.environ.get("WIKI_PROJECT", "wikivoyage")


def wiki_endpoints(lang=None, project=None):
    """Return (hatnote_url, mw_api, base_url) for a given lang/project.

    Falls back to the WIKI_LANG / WIKI_PROJECT defaults when args are None.
    Honors the WIKI_HATNOTE_URL / WIKI_MW_API overrides only when both
    lang and project match the configured defaults; per-request picks
    always derive URLs from lang/project.
    """
    lang = lang or WIKI_LANG
    project = project or WIKI_PROJECT
    using_defaults = (lang == WIKI_LANG and project == WIKI_PROJECT)
    hatnote = f"https://top.hatnote.com/{lang}/{project}/{{year}}/{{month}}/{{day}}.json"
    mw = f"https://{lang}.{project}.org/w/api.php"
    base = f"https://{lang}.{project}.org/wiki/"
    if using_defaults:
        hatnote = os.environ.get("WIKI_HATNOTE_URL", hatnote)
        mw = os.environ.get("WIKI_MW_API", mw)
    return hatnote, mw, base


HATNOTE_URL, MW_API, WIKI_BASE_URL = wiki_endpoints()

_DEFAULT_UA = "WikiTop100Viz/1.0 (contact: andrew.lih@gmail.com)"
HEADERS = {"User-Agent": os.environ.get("WIKI_USER_AGENT", _DEFAULT_UA)}
MAX_CONCURRENT = int(os.environ.get("WIKI_MAX_CONCURRENT", "3"))
CACHE_DIR = os.environ.get("WIKI_CACHE_DIR", ".cache")
HATNOTE_CACHE_TTL = int(os.environ.get("WIKI_HATNOTE_CACHE_TTL", "86400"))  # 24h
MW_CACHE_TTL = int(os.environ.get("WIKI_MW_CACHE_TTL", "604800"))  # 7d
