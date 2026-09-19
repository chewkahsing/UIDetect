import requests

from config import Config

from logger import (
    log_info,
    log_warning,
    log_error
)


SAFE_BROWSING_API_KEY = Config.SAFE_BROWSING_API_KEY


# ==========================================================
# Safe Browsing Error Builder
# ==========================================================

def build_safe_browsing_error(code, message):
    """
    Build a standardized Safe Browsing error response.
    """

    return {
        "status": "Unavailable",
        "error": {
            "code": code,
            "message": message
        }
    }


# ==========================================================
# Google Safe Browsing Check
# ==========================================================

def check_safe_browsing(url):
    """
    Check whether the website is listed in
    Google Safe Browsing.
    """

    log_info(
        f"Checking Google Safe Browsing: {url}"
    )

    # --------------------------------------------------
    # Check API Key
    # --------------------------------------------------

    if not SAFE_BROWSING_API_KEY:

        log_warning(
            "Google Safe Browsing API key is missing."
        )

        return build_safe_browsing_error(
            "SAFE_BROWSING_API_KEY_MISSING",
            "Google Safe Browsing API key is not configured."
        )

    endpoint = (
        "https://safebrowsing.googleapis.com/v4/"
        f"threatMatches:find?key={SAFE_BROWSING_API_KEY}"
    )

    payload = {
        "client": {
            "clientId": "UIDetect",
            "clientVersion": "1.0"
        },

        "threatInfo": {

            "threatTypes": [
                "MALWARE",
                "SOCIAL_ENGINEERING",
                "UNWANTED_SOFTWARE",
                "POTENTIALLY_HARMFUL_APPLICATION"
            ],

            "platformTypes": [
                "ANY_PLATFORM"
            ],

            "threatEntryTypes": [
                "URL"
            ],

            "threatEntries": [
                {
                    "url": url
                }
            ]
        }
    }

    try:

        # --------------------------------------------------
        # Send Request
        # --------------------------------------------------

        response = requests.post(
            endpoint,
            json=payload,
            timeout=5
        )

        # --------------------------------------------------
        # Check HTTP Status
        # --------------------------------------------------

        response.raise_for_status()

        # --------------------------------------------------
        # Parse JSON
        # --------------------------------------------------

        data = response.json()

        # --------------------------------------------------
        # Check Threat Matches
        # --------------------------------------------------

        if "matches" in data:

            log_warning(
                f"Unsafe website detected: {url}"
            )

            return {
                "status": "Unsafe"
            }

        # --------------------------------------------------
        # Safe Result
        # --------------------------------------------------

        log_info(
            "Safe Browsing check completed successfully."
        )

        return {
            "status": "Safe"
        }

    # --------------------------------------------------
    # Connection Timeout
    # --------------------------------------------------

    except requests.exceptions.Timeout:

        log_error(
            "Google Safe Browsing request timed out."
        )

        return build_safe_browsing_error(
            "SAFE_BROWSING_TIMEOUT",
            "Google Safe Browsing request timed out."
        )

    # --------------------------------------------------
    # Connection Error
    # --------------------------------------------------

    except requests.exceptions.ConnectionError:

        log_error(
            "Unable to connect to Google Safe Browsing API."
        )

        return build_safe_browsing_error(
            "SAFE_BROWSING_CONNECTION_ERROR",
            "Unable to connect to Google Safe Browsing API."
        )

    # --------------------------------------------------
    # HTTP Error
    # --------------------------------------------------

    except requests.exceptions.HTTPError as error:

        log_error(
            f"Google Safe Browsing HTTP Error: {error}"
        )

        return build_safe_browsing_error(
            "SAFE_BROWSING_HTTP_ERROR",
            "Google Safe Browsing API returned an HTTP error."
        )

    # --------------------------------------------------
    # Invalid JSON Response
    # --------------------------------------------------

    except ValueError:

        log_error(
            "Invalid JSON received from Google Safe Browsing API."
        )

        return build_safe_browsing_error(
            "SAFE_BROWSING_INVALID_RESPONSE",
            "Google Safe Browsing returned an invalid response."
        )

    # --------------------------------------------------
    # Unexpected Exception
    # --------------------------------------------------

    except Exception as error:

        log_error(
            f"Unexpected Safe Browsing Error: {error}"
        )

        return build_safe_browsing_error(
            "SAFE_BROWSING_INTERNAL_ERROR",
            "An unexpected error occurred during the Safe Browsing check."
        )