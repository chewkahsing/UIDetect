"""
UIDetect Security Posture

Responsibility:
    Determine the final security posture of a website
    from normalized security findings.

This module:
    - Identifies the most important security finding.
    - Determines the final security risk level.
    - Determines the overall security status.
    - Determines the appropriate user action.
    - Provides the primary finding and reason for the action.
    - Generates a human-readable security summary.
    - Returns the final security posture used by the scanner.

This module does not:
    - Perform individual security checks.
    - Calculate the security score.
    - Aggregate raw checker results.
    - Generate AI warnings or recommendations.
"""


from logger import (
    log_info,
    log_error
)


# ==================================================
# Severity Ranking
# ==================================================

SEVERITY_RANK = {

    "Critical": 5,

    "High": 4,

    "Medium": 3,

    "Low": 2,

    "Info": 1

}


# ==================================================
# Sensitive Interactions
# ==================================================

SENSITIVE_INTERACTIONS = {

    "LOGIN",

    "REGISTER",

    "UPLOAD",

    "DOWNLOAD",

    "PAYMENT"

}


# ==================================================
# Helper - Safe Text
# ==================================================

def _safe_text(
    value,
    default=""
):

    if value is None:

        return default

    return str(
        value
    ).strip()


# ==================================================
# Helper - Normalize Findings
# ==================================================

def _normalize_findings(
    normalized_findings
):

    if not isinstance(
        normalized_findings,
        list
    ):

        return []

    valid_findings = []

    for finding in normalized_findings:

        if not isinstance(
            finding,
            dict
        ):

            continue

        finding_class = _safe_text(
            finding.get(
                "findingClass"
            ),
            "SECURITY_WEAKNESS"
        )

        severity = _safe_text(
            finding.get(
                "severity"
            ),
            "Info"
        )

        confirmed = (
            finding.get(
                "confirmed"
            )
            is True
        )

        finding_copy = dict(
            finding
        )

        finding_copy[
            "findingClass"
        ] = finding_class

        finding_copy[
            "severity"
        ] = severity

        finding_copy[
            "confirmed"
        ] = confirmed

        valid_findings.append(
            finding_copy
        )

    return valid_findings


# ==================================================
# Helper - Highest Severity
# ==================================================

def _get_highest_severity(
    findings
):

    highest_rank = 0

    highest_severity = "Info"

    for finding in findings:

        severity = finding.get(
            "severity",
            "Info"
        )

        rank = SEVERITY_RANK.get(
            severity,
            0
        )

        if rank > highest_rank:

            highest_rank = rank

            highest_severity = severity

    return highest_severity


# ==================================================
# Helper - Primary Finding
# ==================================================

def _get_primary_finding(
    findings
):

    priority = {

        "MALICIOUS_THREAT": 5,

        "SECURITY_WEAKNESS": 4,

        "REPUTATION_CONCERN": 3,

        "VERIFICATION_LIMITATION": 2,

        "POSITIVE_SIGNAL": 1

    }


    candidates = [

        finding

        for finding in findings

        if finding.get(
            "confirmed",
            False
        ) is True

        and finding.get(
            "findingClass"
        ) != "POSITIVE_SIGNAL"

    ]


    if not candidates:

        return None


    candidates.sort(

        key=lambda finding: (

            priority.get(
                finding.get(
                    "findingClass"
                ),
                0
            ),

            SEVERITY_RANK.get(
                finding.get(
                    "severity"
                ),
                0
            )

        ),

        reverse=True
    )


    return candidates[0]


# ==================================================
# Helper - Count Severity
# ==================================================

def _calculate_severity_counts(
    findings
):

    severity_counts = {

        "Critical": 0,

        "High": 0,

        "Medium": 0,

        "Low": 0,

        "Info": 0

    }


    for finding in findings:

        severity = finding.get(
            "severity",
            "Info"
        )

        if severity in severity_counts:

            severity_counts[
                severity
            ] += 1


    return severity_counts


# ==================================================
# Helper - Count Finding Classes
# ==================================================

def _calculate_finding_class_counts(
    findings
):

    class_counts = {

        "MALICIOUS_THREAT": 0,

        "SECURITY_WEAKNESS": 0,

        "REPUTATION_CONCERN": 0,

        "VERIFICATION_LIMITATION": 0,

        "POSITIVE_SIGNAL": 0

    }


    for finding in findings:

        finding_class = finding.get(
            "findingClass"
        )

        if finding_class in class_counts:

            class_counts[
                finding_class
            ] += 1


    return class_counts


# ==================================================
# Final Security Posture
# ==================================================

def determine_final_security_posture(
    normalized_findings,
    confidence="Unknown",
    score=0,
    level="Unknown",
    interaction="BROWSE"
):
    """
    Determine UIDetect's final security posture.

    Parameters
    ----------
    normalized_findings : list
        Normalized and classified findings from
        security_aggregator.py.

    confidence : str
        Confidence level from security aggregation.

    score : int
        Existing UIDetect security score.

    level : str
        Existing UIDetect security level.

    interaction : str
        Current user interaction, such as:

        BROWSE
        LOGIN
        REGISTER
        UPLOAD
        DOWNLOAD
        PAYMENT
        RIGHT_CLICK

    Returns
    -------
    dict
        Final security posture.
    """

    try:

        # ==================================================
        # Safety Defaults
        # ==================================================

        findings = _normalize_findings(
            normalized_findings
        )

        confidence = _safe_text(
            confidence,
            "Unknown"
        )

        interaction = _safe_text(
            interaction,
            "BROWSE"
        ).upper()


        # ==================================================
        # Calculate Statistics
        # ==================================================

        severity_counts = (
            _calculate_severity_counts(
                findings
            )
        )

        finding_class_counts = (
            _calculate_finding_class_counts(
                findings
            )
        )


        # ==================================================
        # Identify Important Findings
        # ==================================================

        confirmed_findings = [

            finding

            for finding in findings

            if finding.get(
                "confirmed",
                False
            ) is True

            and finding.get(
                "findingClass"
            ) != "POSITIVE_SIGNAL"

        ]


        malicious_findings = [

            finding

            for finding in confirmed_findings

            if finding.get(
                "findingClass"
            ) == "MALICIOUS_THREAT"

        ]


        weakness_findings = [

            finding

            for finding in confirmed_findings

            if finding.get(
                "findingClass"
            ) == "SECURITY_WEAKNESS"

        ]


        reputation_findings = [

            finding

            for finding in confirmed_findings

            if finding.get(
                "findingClass"
            ) == "REPUTATION_CONCERN"

        ]


        # ==================================================
        # Determine Highest Severity
        # ==================================================

        if malicious_findings:

            highest_severity = "Critical"

        else:

            highest_severity = _get_highest_severity(
                findings
            )


        # ==================================================
        # Determine Primary Finding
        # ==================================================

        primary_finding = _get_primary_finding(
            findings
        )


        # ==================================================
        # Determine Final Risk
        # ==================================================

        final_risk = "Very Low"

        # --------------------------------------------------
        # 1. Confirmed malicious / unsafe threat
        # --------------------------------------------------

        if malicious_findings:

            malicious_severities = [
                finding.get(
                    "severity",
                    "Info"
                )
                for finding in malicious_findings
            ]

            if "Critical" in malicious_severities:

                final_risk = "Critical"

            elif "High" in malicious_severities:

                final_risk = "High"

            elif "Medium" in malicious_severities:

                final_risk = "Medium"

            elif "Low" in malicious_severities:

                final_risk = "Low"

            else:

                final_risk = "Critical"


        # --------------------------------------------------
        # 2. Confirmed security weaknesses
        # --------------------------------------------------

        elif any(
            finding.get(
                "severity"
            ) == "Critical"
            for finding in weakness_findings
        ):

            final_risk = "High"

        elif any(
            finding.get(
                "severity"
            ) == "High"
            for finding in weakness_findings
        ):

            final_risk = "High"

        elif any(
            finding.get(
                "severity"
            ) == "Medium"
            for finding in weakness_findings
        ):

            final_risk = "Medium"

        elif any(
            finding.get(
                "severity"
            ) == "Low"
            for finding in weakness_findings
        ):

            final_risk = "Low"


        # --------------------------------------------------
        # 3. Reputation concerns
        # --------------------------------------------------

        elif any(
            finding.get(
                "severity"
            ) == "High"
            for finding in reputation_findings
        ):

            final_risk = "High"

        elif any(
            finding.get(
                "severity"
            ) == "Medium"
            for finding in reputation_findings
        ):

            final_risk = "Medium"

        elif any(
            finding.get(
                "severity"
            ) == "Low"
            for finding in reputation_findings
        ):

            final_risk = "Low"


        # ==================================================
        # Determine Overall Status
        # ==================================================

        if final_risk == "Critical":

            overall_status = "Unsafe"

        elif final_risk in (
            "High",
            "Medium"
        ):

            overall_status = "Warning"

        else:

            overall_status = "Safe"


        # ==================================================
        # Determine Recommendation Action
        # ==================================================

        recommendation_action = "NORMAL"


        # --------------------------------------------------
        # Malicious threat
        # --------------------------------------------------

        if malicious_findings:

            recommendation_action = "BLOCK"


        # --------------------------------------------------
        # High security weakness
        # --------------------------------------------------

        elif any(

            finding.get(
                "severity"
            ) == "High"

            for finding in weakness_findings

        ):

            if interaction in SENSITIVE_INTERACTIONS:

                recommendation_action = "BLOCK"

            else:

                recommendation_action = "CAUTION"


        # --------------------------------------------------
        # Medium security weakness
        # --------------------------------------------------

        elif any(

            finding.get(
                "severity"
            ) == "Medium"

            for finding in weakness_findings

        ):

            recommendation_action = "CAUTION"


        # --------------------------------------------------
        # High reputation concern
        # --------------------------------------------------

        elif any(

            finding.get(
                "severity"
            ) == "High"

            for finding in reputation_findings

        ):

            if interaction in SENSITIVE_INTERACTIONS:

                recommendation_action = "CAUTION"

            else:

                recommendation_action = "CAUTION"


        # --------------------------------------------------
        # Medium reputation concern
        # --------------------------------------------------

        elif any(

            finding.get(
                "severity"
            ) == "Medium"

            for finding in reputation_findings

        ):

            recommendation_action = "CAUTION"


        # --------------------------------------------------
        # Low weakness / reputation concern
        # --------------------------------------------------

        elif any(

            finding.get(
                "severity"
            ) == "Low"

            for finding in (
                weakness_findings
                + reputation_findings
            )

        ):

            recommendation_action = "NORMAL_CAUTION"


        # ==================================================
        # Recommendation Reason
        # ==================================================

        recommendation_reason = (
            "No confirmed security concern was identified."
        )


        if primary_finding:

            recommendation_reason = _safe_text(

                primary_finding.get(
                    "message"
                ),

                "A confirmed security finding requires attention."

            )


        # ==================================================
        # Generate Posture Summary
        # ==================================================

        if malicious_findings:

            summary = (
                "Confirmed malicious or unsafe security "
                "evidence was detected. Users should avoid "
                "continuing to this website."
            )


        elif final_risk == "High":

            summary = (
                "A high-severity security concern was detected. "
                "The website has a significant security weakness "
                "or reputation concern that requires attention."
            )


        elif final_risk == "Medium":

            summary = (
                "Moderate security concerns were detected. "
                "Users should review the security findings "
                "before performing sensitive actions."
            )


        elif final_risk == "Low":

            summary = (
                "The website appears generally secure, "
                "although minor security weaknesses or "
                "reputation concerns were detected."
            )


        else:

            summary = (
                "No confirmed significant security concerns "
                "were detected based on the available checks."
            )


        # ==================================================
        # Build Final Posture
        # ==================================================

        final_posture = {

            "overallStatus":
                overall_status,

            "risk":
                final_risk,

            "highestSeverity":
                highest_severity,

            "recommendationAction":
                recommendation_action,

            "recommendationReason":
                recommendation_reason,

            "confidence":
                confidence,

            "score":
                score,

            "level":
                level,

            "interaction":
                interaction,

            "primaryFinding":
                primary_finding,

            "severityCounts":
                severity_counts,

            "findingClassCounts":
                finding_class_counts,

            "findings":
                findings,

            "summary":
                summary

        }


        # ==================================================
        # Logging
        # ==================================================

        log_info(
            "Final security posture determined "
            f"(Status={overall_status}, "
            f"Risk={final_risk}, "
            f"Severity={highest_severity}, "
            f"Action={recommendation_action}, "
            f"Confidence={confidence})"
        )


        print(
            "\n========== PHASE 13.4 FINAL SECURITY POSTURE =========="
        )

        print(
            "Overall Status:",
            overall_status
        )

        print(
            "Risk:",
            final_risk
        )

        print(
            "Highest Severity:",
            highest_severity
        )

        print(
            "Recommendation Action:",
            recommendation_action
        )

        print(
            "Primary Finding:",
            primary_finding
        )

        print(
            "Confidence:",
            confidence
        )

        print(
            "========================================================\n"
        )


        return final_posture


    except Exception as error:

        log_error(
            f"Final Security Posture Error: {error}"
        )


        return {

            "overallStatus":
                "Unknown",

            "risk":
                "Unknown",

            "highestSeverity":
                "Unknown",

            "recommendationAction":
                "UNKNOWN",

            "recommendationReason":
                "Final security posture could not be determined.",

            "confidence":
                "Low",

            "score":
                0,

            "level":
                "Unknown",

            "interaction":
                "BROWSE",

            "primaryFinding":
                None,

            "severityCounts": {

                "Critical":
                    0,

                "High":
                    0,

                "Medium":
                    0,

                "Low":
                    0,

                "Info":
                    0

            },

            "findingClassCounts": {

                "MALICIOUS_THREAT":
                    0,

                "SECURITY_WEAKNESS":
                    0,

                "REPUTATION_CONCERN":
                    0,

                "VERIFICATION_LIMITATION":
                    0,

                "POSITIVE_SIGNAL":
                    0

            },

            "findings":
                [],

            "summary":
                "Final security posture could not be determined."

        }