"""
WHOIS Checker Module

This module retrieves domain registration
information to help evaluate website legitimacy.
"""

from urllib.parse import urlparse
from datetime import datetime

import whois

from logger import (
    log_info,
    log_warning,
    log_error
)


def check_whois(url):
    """
    Retrieve WHOIS information for a website.

    Parameters
    ----------
    url : str

    Returns
    -------
    dict
        Standardized WHOIS result.
    """

    log_info(f"Checking WHOIS: {url}")

    # ==========================================================
    # Default Result
    # ==========================================================

    default_result = {

        "success": False,

        "status": "Unavailable",

        "registrar": "Unknown",

        "creationDate": None,

        "expirationDate": None,

        "domainAge": 0,

        "risk": "Unknown",

        "error": None

    }

    try:

        # ======================================================
        # Step 1 - Validate URL
        # ======================================================

        if not url or not isinstance(url, str):

            log_warning(
                "Invalid URL supplied to WHOIS checker."
            )

            return {

                **default_result,

                "error": {

                    "code": "INVALID_URL",

                    "message":
                        "The supplied URL is invalid."
                }

            }

        # ======================================================
        # Step 2 - Extract Domain
        # ======================================================

        domain = urlparse(url).hostname

        if not domain:

            log_warning(
                "Unable to extract domain from URL."
            )

            return {

                **default_result,

                "error": {

                    "code": "INVALID_DOMAIN",

                    "message":
                        "A valid domain could not be extracted "
                        "from the URL."
                }

            }

        # ======================================================
        # Normalize Domain
        # ======================================================

        domain = domain.lower().strip()

        log_info(
            f"WHOIS domain: {domain}"
        )

        # ======================================================
        # Step 3 - WHOIS Lookup
        # ======================================================

        try:

            info = whois.whois(domain)

        except Exception as error:

            log_error(
                f"WHOIS lookup failed for {domain}: {error}"
            )

            return {

                **default_result,

                "error": {

                    "code": "WHOIS_LOOKUP_FAILED",

                    "message":
                        "The WHOIS service could not retrieve "
                        "domain information."
                }

            }

        # ======================================================
        # Step 4 - Validate WHOIS Response
        # ======================================================

        if not info:

            log_warning(
                f"WHOIS returned no information for {domain}."
            )

            return {

                **default_result,

                "error": {

                    "code": "WHOIS_EMPTY_RESPONSE",

                    "message":
                        "The WHOIS service returned no domain information."
                }

            }

        # ======================================================
        # Step 5 - Extract Registrar
        # ======================================================

        try:

            registrar = (
                getattr(info, "registrar", None)
                or "Unknown"
            )

        except Exception as error:

            log_warning(
                f"Unable to extract WHOIS registrar: {error}"
            )

            registrar = "Unknown"

        # ======================================================
        # Step 6 - Extract Creation Date
        # ======================================================

        try:

            creation = getattr(
                info,
                "creation_date",
                None
            )

        except Exception as error:

            log_warning(
                f"Unable to extract creation date: {error}"
            )

            creation = None

        # ======================================================
        # Step 7 - Extract Expiration Date
        # ======================================================

        try:

            expiration = getattr(
                info,
                "expiration_date",
                None
            )

        except Exception as error:

            log_warning(
                f"Unable to extract expiration date: {error}"
            )

            expiration = None

        # ======================================================
        # Step 8 - Handle WHOIS Date Lists
        # ======================================================

        if isinstance(creation, list):

            creation = (
                creation[0]
                if creation
                else None
            )

        if isinstance(expiration, list):

            expiration = (
                expiration[0]
                if expiration
                else None
            )

        # ======================================================
        # Step 9 - Calculate Domain Age
        # ======================================================

        domain_age = 0

        if creation:

            try:

                # ----------------------------------------------
                # Remove timezone information
                # ----------------------------------------------

                if (
                    hasattr(creation, "tzinfo")
                    and creation.tzinfo is not None
                ):

                    creation = creation.replace(
                        tzinfo=None
                    )

                # ----------------------------------------------
                # Validate datetime
                # ----------------------------------------------

                if isinstance(
                    creation,
                    datetime
                ):

                    age_days = (
                        datetime.now() - creation
                    ).days

                    if age_days >= 0:

                        domain_age = age_days // 365

                    else:

                        log_warning(
                            "WHOIS creation date is in the future."
                        )

                        domain_age = 0

                else:

                    log_warning(
                        "WHOIS creation date is not a valid datetime."
                    )

                    creation = None

            except Exception as error:

                log_warning(
                    f"Domain age calculation failed: {error}"
                )

                domain_age = 0

                creation = None

        # ======================================================
        # Step 10 - Reputation Status
        # ======================================================

        if domain_age >= 5:

            status = "Established"

        elif domain_age >= 1:

            status = "Moderate"

        else:

            status = "New"

        # ======================================================
        # Step 11 - WHOIS Risk Level
        # ======================================================

        if domain_age >= 5:

            risk = "Low"

        elif domain_age >= 1:

            risk = "Medium"

        else:

            risk = "High"

        # ======================================================
        # Step 12 - Format Dates
        # ======================================================

        try:

            creation_date = (

                creation.strftime("%Y-%m-%d")

                if creation
                and isinstance(creation, datetime)

                else None

            )

        except Exception as error:

            log_warning(
                f"Creation date formatting failed: {error}"
            )

            creation_date = None

        try:

            expiration_date = (

                expiration.strftime("%Y-%m-%d")

                if expiration
                and isinstance(expiration, datetime)

                else None

            )

        except Exception as error:

            log_warning(
                f"Expiration date formatting failed: {error}"
            )

            expiration_date = None

        # ======================================================
        # Step 13 - Successful Result
        # ======================================================

        result = {

            "success": True,

            "status": status,

            "registrar": registrar,

            "creationDate": creation_date,

            "expirationDate": expiration_date,

            "domainAge": domain_age,

            "risk": risk,

            "error": None

        }

        # ======================================================
        # Logging
        # ======================================================

        log_info(
            "WHOIS lookup completed successfully."
        )

        log_info(
            f"WHOIS Status: {status}"
        )

        log_info(
            f"WHOIS Domain Age: {domain_age} years"
        )

        log_info(
            f"WHOIS Risk: {risk}"
        )

        return result

    # ==========================================================
    # Unexpected WHOIS Error
    # ==========================================================

    except Exception as error:

        log_error(
            f"Unexpected WHOIS Error: {error}"
        )

        return {

            **default_result,

            "error": {

                "code": "WHOIS_INTERNAL_ERROR",

                "message":
                    "An unexpected error occurred "
                    "during the WHOIS check."
            }

        }