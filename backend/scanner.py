from checkers.safe_browsing_checker import check_safe_browsing
from checkers.https_checker import check_https
from checkers.ssl_checker import check_ssl
from modules.score_calculator import calculate_security_score
from checkers.whois_checker import check_whois
from checkers.virustotal_checker import check_virustotal
from checkers.openphish_checker import check_openphish

from modules.warning_ai_consolidated import generate_security_ai
from modules.warning_ai_structured import generate_security_ai_structured


# ==========================================================
# UIDetect Website Security Scanner
# ==========================================================
#
# File Responsibility:
# This module coordinates the complete UIDetect website
# security assessment process.
#
# Main Responsibilities:
# - Execute all website security checkers.
# - Handle checker failures using safe fallback results.
# - Support cancellation of active security scans.
# - Calculate the website security score.
# - Aggregate security assessment data.
# - Determine the final security posture.
# - Generate the unified AI security assessment.
# - Assemble and return the final scan result.
#
# This module acts as the central coordinator between:
# - Security checker modules
# - Security score calculation
# - Security data aggregation
# - Final security posture
# - AI warning and recommendation generation
#
# This module does NOT:
# - Implement individual security checks.
# - Implement AI prompt construction.
# - Implement Ollama response parsing.
# - Implement Flask API routes.
# - Implement frontend/browser UI logic.
#
# ==========================================================


# ==========================================================
# Phase 13 - Security Data Aggregation
# ==========================================================

from modules.security_aggregator import (
    aggregate_security_data
)

from modules.security_posture import (
    determine_final_security_posture
)


from logger import (
    log_info,
    log_warning,
    log_error
)

# ==========================================================
# Phase 10 - Error Handling Helpers
# ==========================================================

def unavailable_safe_browsing():

    return {
        "status": "Unavailable",
        "error": "SAFE_BROWSING_UNAVAILABLE"
    }


def unavailable_virus_total():

    return {
        "status": "Unavailable",
        "malicious": 0,
        "suspicious": 0,
        "harmless": 0,
        "undetected": 0,
        "timeout": 0,
        "reputation": 0,
        "error": "VIRUSTOTAL_UNAVAILABLE"
    }


def unavailable_openphish():

    return {
        "status": "Unavailable",
        "listed": False,
        "risk": "Unknown",
        "error": "OPENPHISH_UNAVAILABLE"
    }


def unavailable_https():

    return {
        "success": False,
        "status": "Unavailable",
        "https": None,
        "error": "HTTPS_CHECK_FAILED"
    }


def unavailable_ssl():

    return {
        "success": False,
        "status": "Unavailable",
        "sslValid": None,
        "protocol": "Unknown",
        "certificate": None,
        "error": "SSL_RETRIEVAL_FAILED"
    }


def unavailable_whois():

    return {
        "status": "Unavailable",
        "registrar": "Unknown",
        "creationDate": None,
        "expirationDate": None,
        "domainAge": 0,
        "risk": "Unknown",
        "error": "WHOIS_UNAVAILABLE"
    }


def unavailable_security_headers():

    return {
        "success": False,
        "status": "Unavailable",
        "error": "SECURITY_HEADERS_UNAVAILABLE",

        "strict-transport-security": False,
        "content-security-policy": False,
        "x-frame-options": False,
        "x-content-type-options": False,
        "referrer-policy": False
    }


# ==========================================================
# Scanner Checker Helper
# ==========================================================

def _run_security_checker(
    checker,
    url,
    fallback,
    checker_name,
    invalid_message
):
    """
    Execute a security checker safely.

    Returns the checker result when valid.
    Returns the supplied fallback when the checker fails.
    """

    try:

        result = checker(
            url
        )

        if not isinstance(
            result,
            dict
        ):

            raise ValueError(
                invalid_message
            )

        return result

    except Exception as error:

        log_error(
            f"{checker_name} failed: {error}"
        )

        return fallback()


# ==========================================================
# Level 2 - Backend Scan Cancellation
# ==========================================================

class ScanCancelled(Exception):
    """Raised when the user cancels an active website scan."""
    pass


def check_scan_cancelled(scan_event):
    """
    Stop the scanner when the backend cancellation event
    has been triggered.
    """

    if scan_event is not None and scan_event.is_set():

        log_info(
            "Website scan cancellation detected."
        )

        raise ScanCancelled(
            "Website scan cancelled by user."
        )


def scan_website(
    url,
    security_headers=None,
    interaction="BROWSE",
    scan_event=None,
    page_title="",
    meta_description=""
):
    """
    Complete UIDetect website security assessment.

    Includes:

    Phase 4:
    - Google Safe Browsing
    - HTTPS
    - SSL/TLS
    - Security Headers
    - Security Score

    Phase 10:
    - WHOIS / RDAP Domain Reputation

    Phase 11:
    - VirusTotal

    Phase 12:
    - OpenPhish

    Phase 13:
    - Security Data Aggregation
    - Final Security Posture

    Security Risk:
    - Use the authoritative final security posture risk
    - Do not calculate a separate context risk in the scanner

    AI Assessment:
    - Generate one unified AI assessment for all interactions.
    """

    log_info(
        f"Starting scan for: {url}"
    )

    # ==================================================
    # Security Headers
    # ==================================================

    headers_result = security_headers or unavailable_security_headers()

    if not isinstance(headers_result, dict):

        log_warning(
            "Security headers data is invalid."
        )

        headers_result = unavailable_security_headers()

    try:

        check_scan_cancelled(scan_event)

        # ==================================================
        # Step 1 - Google Safe Browsing
        # ==================================================

        safe_result = _run_security_checker(

            check_safe_browsing,

            url,

            unavailable_safe_browsing,

            "Safe Browsing module",

            "Safe Browsing returned invalid data."

        )


        log_info(
            f"Safe Browsing Status: "
            f"{safe_result.get('status', 'Unavailable')}"
        )

        check_scan_cancelled(scan_event)

        # ==================================================
        # Step 2 - VirusTotal
        # ==================================================

        virus_total_result = _run_security_checker(

            check_virustotal,

            url,

            unavailable_virus_total,

            "VirusTotal module",

            "VirusTotal returned invalid data."

        )


        log_info(
            f"VirusTotal Status: "
            f"{virus_total_result.get('status', 'Unavailable')}"
        )

        log_info(
            f"VirusTotal Malicious: "
            f"{virus_total_result.get('malicious', 0)}"
        )

        log_info(
            f"VirusTotal Suspicious: "
            f"{virus_total_result.get('suspicious', 0)}"
        )


        check_scan_cancelled(scan_event)

        # ==================================================
        # Step 2.5 - Phase 12 OpenPhish
        # ==================================================

        log_info(
            "Checking OpenPhish phishing database..."
        )

        openphish_result = _run_security_checker(

            check_openphish,

            url,

            unavailable_openphish,

            "OpenPhish module",

            "OpenPhish returned invalid data."

        )


        log_info(
            f"OpenPhish Status: "
            f"{openphish_result.get('status', 'Unavailable')}"
        )

        log_info(
            f"OpenPhish Listed: "
            f"{openphish_result.get('listed', False)}"
        )

        check_scan_cancelled(scan_event)


        # ==================================================
        # Step 3 - HTTPS
        # ==================================================

        https_result = _run_security_checker(

            check_https,

            url,

            unavailable_https,

            "HTTPS checker",

            "HTTPS checker returned invalid data."

        )

        log_info(
            f"HTTPS Enabled: "
            f"{https_result.get('https', False)}"
        )

        check_scan_cancelled(scan_event)


        # ==================================================
        # Step 4 - SSL/TLS
        # ==================================================

        ssl_result = _run_security_checker(

            check_ssl,

            url,

            unavailable_ssl,

            "SSL checker",

            "SSL checker returned invalid data."

        )


        log_info(
            f"SSL Valid: "
            f"{ssl_result.get('sslValid', None)}"
        )

        log_info(
            f"TLS Version: "
            f"{ssl_result.get('protocol', 'Unknown')}"
        )

        check_scan_cancelled(scan_event)



        # ==================================================
        # Step 5 - Security Headers
        # ==================================================

        log_info(
            f"Security Headers: {headers_result}"
        )

        # ==================================================
        # Step 6 - WHOIS Domain Reputation
        # ==================================================

        whois_result = _run_security_checker(

            check_whois,

            url,

            unavailable_whois,

            "WHOIS checker",

            "WHOIS checker returned invalid data."

        )


        log_info(
            f"WHOIS Status: "
            f"{whois_result.get('status', 'Unavailable')}"
        )

        log_info(
            f"Domain Age: "
            f"{whois_result.get('domainAge', 0)} years"
        )

        log_info(
            f"Registrar: "
            f"{whois_result.get('registrar', 'Unknown')}"
        )

        check_scan_cancelled(scan_event)



        # ==================================================
        # Step 7 - Security Score
        # Phase 14 Enhanced Security Score
        # ==================================================

        check_scan_cancelled(scan_event)

        score_result = calculate_security_score(

            safe_result=safe_result,

            https_result=https_result,

            ssl_result=ssl_result,

            headers_result=headers_result,

            whois_result=whois_result,

            openphish_result=openphish_result,

            virus_total_result=virus_total_result

        )

        check_scan_cancelled(scan_event)

        # ==================================================
        # Phase 13 - Security Data Aggregation
        # ==================================================

        check_scan_cancelled(scan_event)

        aggregated_security_data = aggregate_security_data(

            safe_result=safe_result,

            virus_total_result=virus_total_result,

            https_result=https_result,

            ssl_result=ssl_result,

            headers_result=headers_result,

            whois_result=whois_result,

            openphish_result=openphish_result,

            score_result=score_result

        )

        check_scan_cancelled(scan_event)


        # ==================================================
        # Phase 13.4 - Final Security Posture
        # ==================================================

        check_scan_cancelled(scan_event)

        final_security_posture = determine_final_security_posture(

            aggregated_security_data.get(
                "normalizedFindings",
                []
            ),

            confidence=
                aggregated_security_data.get(
                    "confidence",
                    "Unknown"
                ),

            score=
                score_result.get(
                    "score",
                    0
                ),

            level=
                score_result.get(
                    "level",
                    "Unknown"
                ),

            interaction=
                interaction or "BROWSE"

        )



        check_scan_cancelled(scan_event)


        # ==================================================
        # Store Final Security Posture
        # ==================================================

        aggregated_security_data["finalPosture"] = (
            final_security_posture
        )


        log_info(
            "Final security posture determined "
            "using Phase 13.4 security posture module."
        )

        print(
            "\n========== PHASE 13.4 FINAL SECURITY POSTURE =========="
        )

        print(
            f"Overall Status: "
            f"{final_security_posture.get(
                'overallStatus',
                'Unknown'
            )}"
        )

        print(
            f"Risk: "
            f"{final_security_posture.get(
                'risk',
                'Unknown'
            )}"
        )

        print(
            f"Final Severity: "
            f"{final_security_posture.get(
                'highestSeverity',
                'Unknown'
            )}"
        )

        print(
            f"Security Score: "
            f"{score_result.get(
                'score',
                0
            )}"
        )

        print(
            f"Security Level: "
            f"{score_result.get(
                'level',
                'Unknown'
            )}"
        )

        print(
            f"Confidence: "
            f"{final_security_posture.get(
                'confidence',
                'Unknown'
            )}"
        )

        print(
            f"Reason: "
            f"{final_security_posture.get(
                'summary',
                'Unknown'
            )}"
        )

        print(
            "========================================================\n"
        )

        # ==================================================
        # Step 8 - Build Scan Result
        # ==================================================

        result = {

            "url":
                url,

            "interaction":
                interaction or "BROWSE",

            "pageTitle":
                page_title or "Unknown",

            "metaDescription":
                meta_description or "Unknown",

            "safeBrowsing":
                safe_result.get(
                    "status",
                    "Unknown"
                ),

            "virusTotal":
                virus_total_result,

            "openPhish":
                openphish_result,

            "https":
                https_result.get(
                    "https",
                    False
                ),

            "ssl":
                ssl_result,

            "securityHeaders":
                headers_result,

            "whois":
                whois_result,

            "score":
                score_result.get(
                    "score",
                    0
                ),

            "level":
                score_result.get(
                    "level",
                    "Unknown"
                ),

            "securityData":
                aggregated_security_data,

            # ==================================================
            # IMPORTANT:
            # Phase 15 must receive the Phase 13 final posture.
            # ==================================================

            "finalPosture":
                final_security_posture,


            # AI assessment
            "aboutWebsite":
                None,

            "warning":
                None,

            "recommendation":
                None,

            "security_ai_success":
                False

        }

        # ==================================================
        # Verify Phase 15 Input
        # ==================================================

        print(
            "\n========== PHASE 15 INPUT =========="
        )

        print(
            f"Security Score: "
            f"{result.get('score')}"
        )

        print(
            f"Security Level: "
            f"{result.get('level')}"
        )

        print(
            f"Final Security Status: "
            f"{result.get('finalPosture', {}).get('overallStatus', 'Unknown')}"
        )

        print(
            f"Final Security Risk: "
            f"{result.get('finalPosture', {}).get('risk', 'Unknown')}"
        )

        print(
            f"Final Security Severity: "
            f"{result.get('finalPosture', {}).get('highestSeverity', 'Unknown')}"
        )

        print(
            f"Final Security Confidence: "
            f"{result.get('finalPosture', {}).get('confidence', 'Unknown')}"
        )

        print(
            "====================================\n"
        )


        # ==================================================
        # Phase 15 - UIDetect Security AI Assessment
        # ==================================================

        check_scan_cancelled(scan_event)

        log_info(
            "Generating UIDetect Security AI assessment..."
        )

        try:

            # ==================================================
            # Primary path: consolidated natural-language generation.
            #
            # The backend provides the completed UIDetect assessment
            # as factual evidence. Qwen generates the three
            # user-facing fields naturally from those facts while
            # following the finding priority, interaction-context,
            # recommendation, and no-invention rules defined by
            # warning_ai_consolidated.
            #
            # The structured-claims generator remains available as a
            # grounded fallback if the consolidated AI path fails.
            # ==================================================

            ai_result = generate_security_ai({

                "url":
                    url,
           
                "interaction":
                    interaction or "BROWSE",

                "score":
                    score_result.get(
                        "score",
                        0
                    ),

                "securityLevel":
                    score_result.get(
                        "level",
                        "Unknown"
                    ),

                "risk":
                    final_security_posture.get(
                        "risk",
                        "Unknown"
                    ),

                "https":
                    https_result.get(
                        "https",
                        False
                    ),

                "sslValid":
                    ssl_result.get(
                        "sslValid",
                        None
                    ),

                "tlsVersion":
                    ssl_result.get(
                        "protocol",
                        "Unknown"
                    ),

                "safeBrowsing":
                    safe_result.get(
                        "status",
                        "Unknown"
                    ),

                "openPhish":
                    openphish_result,

                "virusTotal":
                    virus_total_result,

                "whoisStatus":
                    whois_result.get(
                        "status",
                        "Unknown"
                    ),

                "domainAge":
                    whois_result.get(
                        "domainAge",
                        0
                    ),

                "securityHeaders":
                    headers_result,

                "securityHeadersStatus":
                    headers_result.get(
                        "status",
                        "Unknown"
                    ),

                "securityHeadersSuccess":
                    headers_result.get(
                        "success",
                        False
                    ),

                "pageTitle":
                    page_title or "Unknown",

                "metaDescription":
                    meta_description or "",

                "finalPosture":
                    final_security_posture

            })

            # ==================================================
            # If the consolidated path itself reports failure (as
            # opposed to raising), fall back to the grounded
            # structured generator so a popup can still render.
            # ==================================================

            if not (
                isinstance(ai_result, dict)
                and ai_result.get("success") is True
            ):

                log_warning(
                    "Consolidated Security AI reported failure; "
                    "falling back to structured generation."
                )

                ai_result = generate_security_ai_structured({

                    "url": url,
                    "interaction": interaction or "BROWSE",
                    "score": score_result.get("score", 0),
                    "securityLevel": score_result.get("level", "Unknown"),
                    "risk": final_security_posture.get("risk", "Unknown"),
                    "https": https_result.get("https", False),
                    "sslValid": ssl_result.get("sslValid", None),
                    "tlsVersion": ssl_result.get("protocol", "Unknown"),
                    "safeBrowsing": safe_result.get("status", "Unknown"),
                    "openPhish": openphish_result,
                    "virusTotal": virus_total_result,
                    "whoisStatus": whois_result.get("status", "Unknown"),
                    "domainAge": whois_result.get("domainAge", 0),
                    "securityHeaders": headers_result,
                    "securityHeadersStatus": headers_result.get("status", "Unknown"),
                    "securityHeadersSuccess": headers_result.get("success", False),
                    "pageTitle": page_title or "Unknown",
                    "metaDescription": meta_description or "",
                    "finalPosture": final_security_posture,

                })

            check_scan_cancelled(scan_event)

        except ScanCancelled:

            raise

        except Exception as error:

            log_error(
                f"Security AI failed: {error}"
            )

            ai_result = {
                "success": False,
                "error": {
                    "code": "SECURITY_AI_EXCEPTION",
                    "message": str(error),
                    "recoverable": True
                }
            }


        # ==================================================
        # Validate Security AI Result
        # ==================================================

        security_ai_success = (
            isinstance(ai_result, dict)
            and ai_result.get("success") is True
        )


        if security_ai_success:

            about_website = ai_result.get(
                "aboutWebsite"
            )

            warning = ai_result.get(
                "warning"
            )

            recommendation = ai_result.get(
                "recommendation"
            )

            # ----------------------------------------------
            # Successful AI response must contain all fields
            # ----------------------------------------------

            if not all(
                isinstance(value, str) and value.strip()
                for value in (
                    about_website,
                    warning,
                    recommendation
                )
            ):

                log_error(
                    "Security AI reported success but one or more "
                    "required AI fields are missing or empty."
                )

                security_ai_success = False

                about_website = None
                warning = None
                recommendation = None

        else:

            about_website = None
            warning = None
            recommendation = None

            log_error(
                "Security AI did not return a successful response."
            )

            if isinstance(ai_result, dict):

                log_error(
                    f"Security AI error: "
                    f"{ai_result.get(
                        'error',
                        'Unknown Security AI error.'
                    )}"
                )

        # ==================================================
        # Store AI Assessment in Centralized Result
        # ==================================================

        result["aboutWebsite"] = about_website
        result["warning"] = warning
        result["recommendation"] = recommendation
        result["security_ai_success"] = security_ai_success


        # ==================================================
        # Security AI Status
        # ==================================================

        if security_ai_success:

            log_info(
                "UIDetect Security AI assessment generated successfully."
            )

        else:

            log_warning(
                "UIDetect Security AI assessment generation failed. "
                "No hardcoded AI text will be used."
            )


        print(
            "\n========== SECURITY AI RESULT =========="
        )

        print(
            f"Security AI Success: "
            f"{security_ai_success}"
        )

        print(
            f"About Website: "
            f"{about_website}"
        )

        print(
            f"Risk: "
            f"{final_security_posture.get(
                'risk',
                'Unknown'
            )}"
        )

        print(
            f"Warning: "
            f"{warning}"
        )

        print(
            f"Recommendation: "
            f"{recommendation}"
        )

        print(
            "========================================\n"
        )

        check_scan_cancelled(scan_event)



        result["success"] = True



        

        print(
            "\n========== FINAL RESULT =========="
        )

        print(
            result
        )

        print(
            "=================================\n"
        )

        log_info(
            "Returning completed scan result."
        )

        return result

    except ScanCancelled:

        log_info(
            f"Scan cancelled by user: {url}"
        )

        return {

            "success":
                False,

            "cancelled":
                True,

            "url":
                url,

            "error":
            {
                "code":
                    "SCAN_CANCELLED",

                "message":
                    "The security scan was cancelled by the user.",

                "recoverable":
                    True
            }
        }

    except Exception as error:

        log_error(
            f"Scanner Error: {error}"
        )

        return {

            "success":
                False,

            "url":
                url,

            "safeBrowsing":
                "Unavailable",

            "virusTotal":
                unavailable_virus_total(),

            "openPhish":
                unavailable_openphish(),

            "https":
                False,

            "ssl":
                unavailable_ssl(),

            "securityHeaders":
                headers_result,

            "whois":
                unavailable_whois(),

            "score":
                0,

            "level":
                "Unknown",

            "interaction":
                interaction,

            "risk":
                "Unknown",

            "aboutWebsite":
                None,

            "warning":
                None,

            "recommendation":
                None,

            "security_ai_success":
                False,



            "error": {
                "code": "INTERNAL_ERROR",
                "message":
                    "An unexpected error occurred during the security assessment.",
                "recoverable": False
            }
        }