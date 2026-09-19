"""
OpenPhish Checker Module

This module checks whether a website URL
appears in the OpenPhish phishing feed.
"""

from urllib.parse import urlparse

import requests
import threading

from logger import (
    log_info,
    log_warning,
    log_error
)


# ==========================================================
# OpenPhish Feed
# ==========================================================

OPENPHISH_FEED_URL = (
    "https://raw.githubusercontent.com/"
    "openphish/public_feed/refs/heads/main/feed.txt"
)


# ==========================================================
# Feed Cache
# ==========================================================

_openphish_cache = {

    "urls": set(),

    "match_keys": set(),

    "loaded": False

}

_openphish_loader_lock = threading.Lock()


# ==========================================================
# Normalize URL
# ==========================================================

def normalize_url(url):
    """
    Normalize a URL for OpenPhish comparison.

    Removes:
    - URL fragments
    - trailing slash
    - hostname casing differences

    Keeps:
    - scheme
    - hostname
    - port
    - path
    - query string
    """

    if not url:
        return ""

    try:
        parsed = urlparse(url.strip())

        if not parsed.scheme or not parsed.netloc:
            return ""

        hostname = parsed.hostname

        if not hostname:
            return ""

        hostname = hostname.lower()

        # Preserve port when present
        if parsed.port:
            hostname = f"{hostname}:{parsed.port}"

        normalized = (
            f"{parsed.scheme.lower()}://"
            f"{hostname}"
            f"{parsed.path.rstrip('/')}"
        )

        if parsed.query:
            normalized += f"?{parsed.query}"

        return normalized

    except Exception as error:
        log_error(
            f"OpenPhish URL normalization error: {error}"
        )
        return ""


def get_openphish_match_key(url):
    """
    Create a stable comparison key for OpenPhish.

    The key ignores:
    - scheme differences
    - URL fragments
    - trailing slash
    - query parameters

    It preserves:
    - hostname
    - path
    """

    normalized = normalize_url(url)

    if not normalized:
        return ""

    try:
        parsed = urlparse(normalized)

        hostname = parsed.hostname.lower()

        path = parsed.path.rstrip("/")

        if not path:
            path = "/"

        return f"{hostname}{path}"

    except Exception as error:
        log_error(
            f"OpenPhish match-key error: {error}"
        )
        return ""



# ==========================================================
# Download OpenPhish Feed
# ==========================================================

def load_openphish_feed():
    """
    Download and cache the OpenPhish phishing feed.

    Returns
    -------
    bool
        True if the feed was successfully loaded.
        False if the feed could not be retrieved.
    """

    log_info(
        "Loading OpenPhish phishing feed..."
    )

    try:

        response = requests.get(
            OPENPHISH_FEED_URL,
            timeout=15
        )

        # ==================================================
        # HTTP Status Validation
        # ==================================================

        if response.status_code != 200:

            log_warning(
                "OpenPhish feed returned "
                f"HTTP {response.status_code}"
            )

            return False

        # ==================================================
        # Validate Feed Content
        # ==================================================

        if not response.text.strip():

            log_warning(
                "OpenPhish feed returned empty content."
            )

            return False

        feed_urls = set()
        feed_match_keys = set()

        for line in response.text.splitlines():

            line = line.strip()

            if not line:
                continue

            normalized = normalize_url(line)

            if not normalized:
                continue        

            match_key = get_openphish_match_key(normalized)

            if not match_key:
                continue

            feed_urls.add(normalized)
            feed_match_keys.add(match_key)

        # ==================================================
        # Validate Parsed Feed
        # ==================================================

        if not feed_match_keys:

            log_warning(
                "OpenPhish feed contained no valid URLs."
            )

            return False

        # ==================================================
        # Update Cache
        # ==================================================

        _openphish_cache["urls"] = feed_urls
        
        _openphish_cache["match_keys"] = feed_match_keys
        _openphish_cache["loaded"] = True

        log_info(
            "OpenPhish feed loaded "
            f"({len(feed_urls)} URLs)"
            f"{len(feed_match_keys)} match keys)"
        )

        return True

    # ======================================================
    # Timeout
    # ======================================================

    except requests.exceptions.Timeout:

        log_error(
            "OpenPhish feed request timed out."
        )

        return False

    # ======================================================
    # Connection Error
    # ======================================================

    except requests.exceptions.ConnectionError:

        log_error(
            "Unable to connect to OpenPhish feed."
        )

        return False

    # ======================================================
    # HTTP Request Error
    # ======================================================

    except requests.exceptions.RequestException as error:

        log_error(
            f"OpenPhish feed request error: {error}"
        )

        return False

    # ======================================================
    # Unexpected Error
    # ======================================================

    except Exception as error:

        log_error(
            f"Unexpected OpenPhish feed error: {error}"
        )

        return False



# ==========================================================
# Background Feed Loader
# ==========================================================



def start_openphish_feed_loader():
    """
    Start loading the OpenPhish feed in a background thread.

    The feed is loaded independently from user scans so that
    the first website scan does not have to wait for the feed
    download.
    """

    with _openphish_loader_lock:
        if _openphish_cache["loaded"]:

            log_info(
                "OpenPhish feed already loaded. "
                "Background loading skipped."
            )

            return

        def _load_feed():

            log_info(
                "Starting background OpenPhish feed loading..."
            )

            success = load_openphish_feed()

            if success:

                log_info(
                    "Background OpenPhish feed loading completed."
                )

            else:

                log_warning(
                    "Background OpenPhish feed loading failed. "
                    "OpenPhish will remain unavailable until "
                    "the feed is loaded successfully."
                )

        thread = threading.Thread(
            target=_load_feed,
            name="OpenPhishFeedLoader",
            daemon=True
        )

        thread.start()

# ==========================================================
# Check OpenPhish
# ==========================================================

def check_openphish(url):
    """
    Check whether a website URL appears
    in the OpenPhish phishing feed.

    Returns
    -------
    dict
        Standardized OpenPhish assessment result.
    """

    log_info(
        f"Checking OpenPhish: {url}"
    )

    # ======================================================
    # Validate URL
    # ======================================================

    normalized_url = normalize_url(url)

    if not normalized_url:

        log_warning(
            "Invalid URL for OpenPhish."
        )

        return {

            "success": False,

            "status": "Unknown",

            "listed": False,

            "risk": "Unknown",

            "score": 0,

            "message":
                "Invalid URL.",

            "error": {

                "code":
                    "OPENPHISH_INVALID_URL",

                "message":
                    "The supplied URL could not be validated.",

                "severity":
                    "warning",

                "recoverable":
                    False

            }

        }

    # ======================================================
    # Check Feed Availability
    # ======================================================

    if not _openphish_cache["loaded"]:

        log_warning(
            "OpenPhish feed is not currently cached. "
            "Skipping OpenPhish lookup for this scan."
        )

        return {

            "success": False,

            "status": "Unavailable",

            "listed": False,

            "risk": "Unknown",

            "score": 0,

            "message":
                "OpenPhish feed is not currently available.",

            "error": {

                "code":
                    "OPENPHISH_FEED_NOT_READY",

                "message":
                    "The OpenPhish feed has not finished loading.",

                "severity":
                    "warning",

                "recoverable":
                    True

            }

        }

    # ======================================================
    # Compare URL
    # ======================================================

    try:

        match_key = get_openphish_match_key(normalized_url)

        if match_key in _openphish_cache["match_keys"]:
            log_warning(
                "OpenPhish match detected."
            )

            return {

                "success": True,

                "status": "Phishing",

                "listed": True,

                "risk": "Critical",

                "score": 0,

                "message":
                    "URL found in the OpenPhish phishing feed.",

                "error": None

            }

        # ==================================================
        # URL Not Listed
        # ==================================================

        log_info(
            "URL not found in OpenPhish feed."
        )

        return {

            "success": True,

            "status": "Not Listed",

            "listed": False,

            "risk": "Low",

            "score": 10,

            "message":
                "URL was not found in the OpenPhish phishing feed.",

            "error": None

        }

    # ======================================================
    # Unexpected Comparison Error
    # ======================================================

    except Exception as error:

        log_error(
            f"OpenPhish comparison error: {error}"
        )

        return {

            "success": False,

            "status": "Unavailable",

            "listed": False,

            "risk": "Unknown",

            "score": 0,

            "message":
                "OpenPhish assessment could not be completed.",

            "error": {

                "code":
                    "OPENPHISH_CHECK_FAILED",

                "message":
                    "An unexpected error occurred "
                    "during the OpenPhish assessment.",

                "severity":
                    "warning",

                "recoverable":
                    True

            }

        }