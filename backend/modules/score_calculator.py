# ==========================================================
# UIDetect Security Score Calculator
# ==========================================================
#
# File Responsibility:
# This module calculates the overall security score and
# security level for a scanned website.
#
# Main Responsibilities:
# - Combine results from all security checkers.
# - Assign weighted points to each security factor.
# - Calculate the overall security score from 0 to 100.
# - Apply threat-aware score caps for critical or high-risk
#   security findings.
# - Determine the security level and associated risk.
# - Return the final score, level, CSS class, and risk.
#
# Security Factors:
# - Google Safe Browsing
# - VirusTotal
# - OpenPhish
# - HTTPS
# - SSL/TLS
# - Security Headers
# - WHOIS Domain Reputation
#
# This module does NOT:
# - Perform website security checks.
# - Query external security services directly.
# - Generate AI warnings or recommendations.
# - Build AI prompts.
# - Parse Ollama responses.
# - Handle Flask API requests.
# - Control browser-extension UI.
#
# Input:
# Security assessment results produced by the scanner
# and individual security checker modules.
#
# Output:
# A dictionary containing:
# - score
# - level
# - cssClass
# - risk
#
# ==========================================================


import os

print(
    "Using score_calculator:",
    os.path.abspath(__file__)
)

from logger import (
    log_info,
    log_warning,
    log_error
)


def calculate_security_score(
    safe_result,
    https_result,
    ssl_result,
    headers_result,
    whois_result,
    openphish_result,
    virus_total_result=None
):
    """
    Calculate the enhanced overall website security score.

    Phase 14 Weight Distribution:
    - Google Safe Browsing      : 25
    - VirusTotal                : 15
    - HTTPS                     : 15
    - SSL Certificate           : 15
    - Security Headers          : 10
    - WHOIS Domain Reputation   : 10
    - OpenPhish                 : 10

    Total:
    100 points

    Phase 14 also applies threat-aware score caps
    when critical or high-risk findings are detected.
    """

    try:

        # ==================================================
        # Default Security Headers
        # ==================================================

        if not headers_result:

            log_warning(
                "Security headers not received. "
                "Using default values."
            )

            headers_result = {

                "strict-transport-security": False,

                "content-security-policy": False,

                "x-frame-options": False,

                "x-content-type-options": False,

                "referrer-policy": False

            }

        # ==================================================
        # Default VirusTotal Result
        # ==================================================

        if not virus_total_result:

            log_warning(
                "VirusTotal result not received. "
                "Using default values."
            )

            virus_total_result = {

                "status": "Unknown",

                "malicious": 0,

                "suspicious": 0,

                "harmless": 0,

                "undetected": 0,

                "timeout": 0,

                "reputation": 0

            }


        # ==================================================
        # Initialize Score
        # ==================================================

        score = 0

        print(
            "\n========== SCORE INPUT =========="
        )

        print(
            "Safe Result:",
            safe_result
        )

        print(
            "OpenPhish Result:",
            openphish_result
        )

        print(
            "HTTPS Result:",
            https_result
        )

        print(
            "SSL Result:",
            ssl_result
        )

        print(
            "Headers Result:",
            headers_result
        )

        print(
            "WHOIS Result:",
            whois_result
        )

        print(
            "=================================\n"
        )


        # ==================================================
        # 1. Google Safe Browsing
        # Weight: 25
        # ==================================================

        safe_status = safe_result.get(
            "status",
            "Unknown"
        )

        safe_contribution = 0

        if safe_status == "Safe":

            safe_contribution = 25

        elif safe_status == "Unsafe":

            safe_contribution = 0

        else:

            safe_contribution = 0

        score += safe_contribution


        # ==================================================
        # 2. VirusTotal
        # Weight: 15
        # ==================================================

        virus_total_status = virus_total_result.get(
            "status",
            "Unknown"
        )

        virus_total_malicious = int(
            virus_total_result.get(
                "malicious",
                0
            ) or 0
        )

        virus_total_suspicious = int(
            virus_total_result.get(
                "suspicious",
                0
            ) or 0
        )

        virus_total_contribution = 0


        if virus_total_malicious > 0:

            # VirusTotal detected malicious activity.
            virus_total_contribution = 0


        elif virus_total_suspicious > 0:

            # Suspicious detections reduce trust,
            # but do not completely remove the score.
            virus_total_contribution = 5


        elif virus_total_status == "Safe":

            virus_total_contribution = 15


        else:

            # Unknown / unavailable.
            # Do not award points.
            virus_total_contribution = 0


        score += virus_total_contribution

        # ==================================================
        # 2. OpenPhish
        # Weight: 10
        # ==================================================

        openphish_status = openphish_result.get(
            "status",
            "Unknown"
        )

        openphish_listed = openphish_result.get(
            "listed",
            False
        )


        if openphish_listed is True:

            # Known phishing URL.
            # No points awarded.
            score += 0


        elif openphish_status == "Not Listed":

            # URL was not found in OpenPhish.
            score += 10


        else:

            # Feed unavailable / unknown.
            # Do not award points.
            score += 0


        # ==================================================
        # 4. HTTPS
        # Weight: 15
        # ==================================================

        https_contribution = 0

        if https_result.get("https"):

            https_contribution = 15

        score += https_contribution


        # ==================================================
        # 5. SSL Certificate
        # Weight: 15
        # ==================================================

        ssl_contribution = 0

        if ssl_result.get("sslValid"):

            ssl_contribution = 15

        score += ssl_contribution



        # ==================================================
        # 6. Security Headers
        # Weight: 10
        # ==================================================

        required_headers = [

            "strict-transport-security",

            "content-security-policy",

            "x-frame-options",

            "x-content-type-options",

            "referrer-policy"

        ]

        header_score = 0

        for header_name in required_headers:

            if headers_result.get(header_name):

                header_score += 1


        total_headers = len(
            required_headers
        )

        header_contribution = int(
            (header_score / total_headers) * 10
        )

        score += header_contribution


        # ==================================================
        # 7. WHOIS Domain Reputation
        # Weight: 10
        # ==================================================

        whois_status = whois_result.get(
            "status",
            "Unavailable"
        )

        whois_contribution = 0

        if whois_status == "Established":

            whois_contribution = 10

        elif whois_status == "Moderate":

            whois_contribution = 5

        elif whois_status == "New":

            whois_contribution = 0

        else:

            whois_contribution = 0


        score += whois_contribution


        # ==================================================
        # Phase 14 - Threat-Aware Score Protection
        # ==================================================

        original_score = score

        threat_cap = 100

        threat_reason = "No critical threat cap applied."


        # --------------------------------------------------
        # Critical Threats
        # --------------------------------------------------

        if (
            safe_status == "Unsafe"
            or openphish_listed is True
            or virus_total_malicious > 0
        ):

            threat_cap = 20

            threat_reason = (
                "Critical threat detected by one or more "
                "reputation or threat-intelligence sources."
            )


        # --------------------------------------------------
        # High-Risk Threats
        # --------------------------------------------------
        #
        # NOTE:
        # Plain "HTTPS is disabled" is intentionally NOT part
        # of this cap anymore. A site with no HTTPS still loses
        # its direct HTTPS/SSL point weight above (up to 30
        # points), but it is no longer additionally forced into
        # the "Poor" tier when every other check (reputation,
        # threat-intel, WHOIS) is clean.
        #
        # An invalid certificate on a site that DOES claim
        # HTTPS is a different, more concerning signal (possible
        # misconfiguration or interception) and still caps the
        # score, as does a VirusTotal "suspicious" detection.
        # --------------------------------------------------

        elif (
            virus_total_suspicious > 0
            or (
                https_result.get("https") is True
                and not ssl_result.get("sslValid")
            )
        ):

            threat_cap = 49

            threat_reason = (
                "High-risk security weakness detected."
            )


        # --------------------------------------------------
        # Apply Threat Cap
        # --------------------------------------------------

        if score > threat_cap:

            score = threat_cap


        print(
            "Original Score Before Threat Cap:",
            original_score
        )

        print(
            "Threat Cap:",
            threat_cap
        )

        print(
            "Threat Reason:",
            threat_reason
        )

        print(
            "Score After Threat Cap:",
            score
        )


        # ==================================================
        # Safety Clamp
        # ==================================================

        score = max(
            0,
            min(score, 100)
        )


        # ==================================================
        # Security Level
        # ==================================================

        if score >= 90:

            level = "Excellent"

            css_class = "level-excellent"

            risk = "Very Low"


        elif score >= 70:

            level = "Good"

            css_class = "level-good"

            risk = "Low"


        elif score >= 50:

            level = "Moderate"

            css_class = "level-moderate"

            risk = "Medium"


        else:

            level = "Poor"

            css_class = "level-poor"

            risk = "High"


        # ==================================================
        # Logging
        # ==================================================

        log_info(
            "Security score calculated successfully "
            f"(Score={score}, Level={level})"
        )


        print(
            "Safe Browsing Contribution:",
            safe_contribution
        )

        print(
            "VirusTotal Contribution:",
            virus_total_contribution
        )

        print(
            "OpenPhish Contribution:",
            0
            if openphish_listed is True
            else (
                10
                if openphish_status == "Not Listed"
                else 0
            )
        )

        print(
            "HTTPS Contribution:",
            https_contribution
        )

        print(
            "SSL Contribution:",
            ssl_contribution
        )

        print(
            "Header Count:",
            header_score
        )

        print(
            "Header Contribution:",
            header_contribution
        )

        print(
            "WHOIS Status:",
            whois_status
        )

        print(
            "WHOIS Contribution:",
            whois_contribution
        )

        print(
            "VirusTotal Malicious:",
            virus_total_malicious
        )

        print(
            "VirusTotal Suspicious:",
            virus_total_suspicious
        )

        print(
            "Original Score:",
            original_score
        )

        print(
            "Threat Cap:",
            threat_cap
        )

        print(
            "Final Score:",
            score
        )

        print(
            "Security Level:",
            level
        )

        print(
            "Risk:",
            risk
        )

        print(
            "===============================\n"
        )


        # ==================================================
        # Return Result
        # ==================================================

        return {

            "score": score,

            "level": level,

            "cssClass": css_class,

            "risk": risk

        }


    except Exception as error:

        log_error(
            f"Score Calculation Error: {error}"
        )


        return {

            "score": 0,

            "level": "Unknown",

            "cssClass": "level-unknown",

            "risk": "Unknown"

        }