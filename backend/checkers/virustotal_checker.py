import os
import base64
import requests

from dotenv import load_dotenv

# ==========================================================
# Load Environment Configuration
# ==========================================================

load_dotenv()


# ==========================================================
# VirusTotal URL ID Encoder
# ==========================================================

def encode_virustotal_url(url):
    """
    Convert a website URL into the URL identifier
    required by the VirusTotal API.

    VirusTotal expects the URL to be encoded using
    URL-safe Base64 with trailing '=' padding removed.
    """

    # ------------------------------------------------------
    # Validate URL type
    # ------------------------------------------------------

    if not isinstance(url, str):
        raise ValueError(
            "URL must be a string."
        )

    # ------------------------------------------------------
    # Remove unnecessary whitespace
    # ------------------------------------------------------

    url = url.strip()

    if not url:
        raise ValueError(
            "URL cannot be empty."
        )

    # ------------------------------------------------------
    # Encode URL using URL-safe Base64
    # ------------------------------------------------------

    encoded_url = base64.urlsafe_b64encode(
        url.encode("utf-8")
    ).decode("utf-8")

    # ------------------------------------------------------
    # VirusTotal URL IDs do not use '=' padding
    # ------------------------------------------------------

    encoded_url = encoded_url.rstrip("=")

    # ------------------------------------------------------
    # Final validation
    # ------------------------------------------------------

    if not encoded_url:
        raise ValueError(
            "URL encoding produced an empty identifier."
        )

    return encoded_url


def check_virustotal(url):
    """
    Check website reputation using VirusTotal.

    Returns a standardized result so that VirusTotal
    failures do not interrupt the complete UIDetect scan.
    """

    # ==========================================================
    # Default Result
    # ==========================================================

    default_result = {

        "success": False,

        "status": "Unavailable",

        "malicious": 0,

        "suspicious": 0,

        "harmless": 0,

        "undetected": 0,

        "timeout": 0,

        "reputation": 0,

        "error": None

    }

    # ==========================================================
    # Step 1 - Validate URL
    # ==========================================================

    if not url or not isinstance(url, str):

        return {

            **default_result,

            "error": {

                "code": "INVALID_URL",

                "message":
                    "The supplied URL is invalid."

            }

        }

    # ==========================================================
    # VirusTotal Configuration
    # ==========================================================

    VT_API_KEY = os.getenv(
        "VT_API_KEY",
        ""
    ).strip()

    # ==========================================================
    # Step 2 - Check VirusTotal API Key
    # ==========================================================

    if not VT_API_KEY:

        return {

            **default_result,

            "error": {

                "code": "VIRUSTOTAL_API_KEY_MISSING",

                "message":
                    "VirusTotal API key is not configured."

            }

        }

    # ==========================================================
    # Step 3 - Convert URL to VirusTotal ID
    # ==========================================================

    try:

        url_id = encode_virustotal_url(url)

    except (TypeError, ValueError):

        return {

            **default_result,

            "error": {

                "code": "VIRUSTOTAL_URL_ENCODING_FAILED",

                "message":
                    "The website URL could not be processed."

            }

        }

    # ==========================================================
    # Step 4 - Build Request
    # ==========================================================

    headers = {

        "x-apikey": VT_API_KEY

    }

    endpoint = (
        "https://www.virustotal.com/api/v3/urls/"
        f"{url_id}"
    )

    # ==========================================================
    # Step 5 - Send VirusTotal Request
    # ==========================================================

    try:

        response = requests.get(

            endpoint,

            headers=headers,

            timeout=15

        )

    # ==========================================================
    # Step 6 - Timeout Error
    # ==========================================================

    except requests.exceptions.Timeout:

        return {

            **default_result,

            "error": {

                "code": "VIRUSTOTAL_TIMEOUT",

                "message":
                    "VirusTotal request timed out."

            }

        }

    # ==========================================================
    # Step 7 - Connection Error
    # ==========================================================

    except requests.exceptions.ConnectionError:

        return {

            **default_result,

            "error": {

                "code": "VIRUSTOTAL_CONNECTION_ERROR",

                "message":
                    "Unable to connect to VirusTotal."

            }

        }

    # ==========================================================
    # Step 8 - Request Error
    # ==========================================================

    except requests.exceptions.RequestException:

        return {

            **default_result,

            "error": {

                "code": "VIRUSTOTAL_REQUEST_ERROR",

                "message":
                    "VirusTotal request could not be completed."

            }

        }

    # ==========================================================
    # Step 9 - HTTP Status Handling
    # ==========================================================

    if response.status_code != 200:

        if response.status_code == 401:

            error_code = "VIRUSTOTAL_UNAUTHORIZED"

            error_message = (
                "VirusTotal API authentication failed."
            )

        elif response.status_code == 403:

            error_code = "VIRUSTOTAL_FORBIDDEN"

            error_message = (
                "VirusTotal rejected the API request."
            )

        elif response.status_code == 404:

            error_code = "VIRUSTOTAL_NOT_FOUND"

            error_message = (
                "VirusTotal does not have an analysis "
                "for this URL."
            )

        elif response.status_code == 429:

            error_code = "VIRUSTOTAL_RATE_LIMIT"

            error_message = (
                "VirusTotal API rate limit was exceeded."
            )

        elif response.status_code >= 500:

            error_code = "VIRUSTOTAL_SERVER_ERROR"

            error_message = (
                "VirusTotal service is temporarily unavailable."
            )

        else:

            error_code = "VIRUSTOTAL_HTTP_ERROR"

            error_message = (
                "VirusTotal returned an unexpected "
                f"HTTP status ({response.status_code})."
            )

        return {

            **default_result,

            "error": {

                "code": error_code,

                "message": error_message

            }

        }

    # ==========================================================
    # Step 10 - Parse JSON Response
    # ==========================================================

    try:

        data = response.json()

    except ValueError:

        return {

            **default_result,

            "error": {

                "code": "VIRUSTOTAL_INVALID_JSON",

                "message":
                    "VirusTotal returned an invalid response."

            }

        }

    # ==========================================================
    # Step 11 - Validate Response Structure
    # ==========================================================

    if not isinstance(data, dict):

        return {

            **default_result,

            "error": {

                "code": "VIRUSTOTAL_INVALID_RESPONSE",

                "message":
                    "VirusTotal returned an invalid response format."

            }

        }

    # ==========================================================
    # Step 12 - Extract Data
    # ==========================================================

    try:

        attributes = (
            data
            .get("data", {})
            .get("attributes", {})
        )

        if not isinstance(attributes, dict):

            raise ValueError(
                "VirusTotal attributes are invalid."
            )

        stats = (
            attributes
            .get("last_analysis_stats", {})
        )

        if not isinstance(stats, dict):

            raise ValueError(
                "VirusTotal analysis statistics are invalid."
            )

    except Exception:

        return {

            **default_result,

            "error": {

                "code": "VIRUSTOTAL_INVALID_DATA",

                "message":
                    "VirusTotal returned incomplete "
                    "analysis data."

            }

        }

    # ==========================================================
    # Step 13 - Extract Statistics
    # ==========================================================

    malicious = stats.get(
        "malicious",
        0
    )

    suspicious = stats.get(
        "suspicious",
        0
    )

    harmless = stats.get(
        "harmless",
        0
    )

    undetected = stats.get(
        "undetected",
        0
    )

    timeout = stats.get(
        "timeout",
        0
    )

    # ==========================================================
    # Step 14 - Validate Statistics
    # ==========================================================

    try:

        malicious = int(malicious)

        suspicious = int(suspicious)

        harmless = int(harmless)

        undetected = int(undetected)

        timeout = int(timeout)

    except (TypeError, ValueError):

        return {

            **default_result,

            "error": {

                "code": "VIRUSTOTAL_INVALID_STATISTICS",

                "message":
                    "VirusTotal returned invalid analysis statistics."

            }

        }

    # ==========================================================
    # Step 15 - Determine Status
    # ==========================================================

    if malicious > 0:

        status = "Unsafe"

    elif suspicious > 0:

        status = "Warning"

    else:

        status = "Safe"

    # ==========================================================
    # Step 16 - Build Successful Result
    # ==========================================================

    result = {

        "success": True,

        "status": status,

        "malicious": malicious,

        "suspicious": suspicious,

        "harmless": harmless,

        "undetected": undetected,

        "timeout": timeout,

        "reputation": harmless,

        "error": None

    }

    # ==========================================================
    # Step 17 - Return Result
    # ==========================================================

    return result