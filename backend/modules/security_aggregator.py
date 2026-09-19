"""
UIDetect Security Data Aggregator

Responsibility:
    Combine the results from all security checkers into one
    standardized security assessment.

This module:
    - Normalizes security findings by severity.
    - Classifies findings by security meaning.
    - Collects critical findings, warnings, and positive signals.
    - Calculates assessment confidence based on unavailable checks.
    - Produces security-check statistics.
    - Builds the unified security data returned to the scanner.

This module does not:
    - Perform the individual security checks.
    - Calculate the security score.
    - Generate AI responses.
    - Determine the final security posture.
"""


from logger import (
    log_info,
    log_error
)


# ==================================================
# Phase 13.3 - Severity Normalization
# ==================================================

def normalize_severity(
    source,
    finding_type,
    status=None
):
    """
    Normalize security findings into UIDetect
    standard severity levels.

    Severity levels:

    Critical
    High
    Medium
    Low
    Info
    """

    source = (
        source or "Unknown"
    ).strip().lower()

    finding_type = (
        finding_type or "Unknown"
    ).strip().lower()

    status = (
        status or ""
    ).strip().lower()


    # ==================================================
    # Critical
    # ==================================================

    if source == "openphish" and (
        finding_type == "listed"
    ):
        return "Critical"


    if source == "google safe browsing" and (
        status == "unsafe"
    ):
        return "Critical"


    if source == "virustotal" and (
        finding_type == "malicious"
    ):
        return "Critical"


    # ==================================================
    # High
    # ==================================================

    if source == "virustotal" and (
        finding_type == "suspicious"
    ):
        return "High"


    if source == "ssl/tls" and (
        finding_type == "invalid"
    ):
        return "High"


    # ==================================================
    # Medium
    # ==================================================

    if source == "whois" and (
        finding_type in (
            "new",
            "moderate"
        )
    ):
        return "Medium"


    # --------------------------------------------------
    # HTTPS disabled is a real weakness, but on its own
    # (no confirmed malicious/reputation signal) it is
    # treated as Medium rather than High so it triggers
    # CAUTION instead of an automatic BLOCK on sensitive
    # interactions. See normalize_severity() docstring.
    # --------------------------------------------------

    if source == "https" and (
        finding_type == "disabled"
    ):
        return "Medium"


    # ==================================================
    # Low
    # ==================================================

    if source == "security headers":
        return "Low"


    # ==================================================
    # Informational
    # ==================================================

    return "Info"


# ==================================================
# Finding Classification
# ==================================================

def classify_finding(
    source,
    finding_type,
    status=None
):
    """
    Classify a finding according to its security meaning.

    Categories:

    MALICIOUS_THREAT
        Evidence indicating a known malicious or unsafe threat.

    SECURITY_WEAKNESS
        A security configuration or protection weakness.

    REPUTATION_CONCERN
        A reputation-related concern that does not prove
        malicious behavior.

    VERIFICATION_LIMITATION
        A security check could not reliably determine
        the result.

    POSITIVE_SIGNAL
        A positive security observation.
    """

    source = (
        source or "Unknown"
    ).strip().lower()

    finding_type = (
        finding_type or "Unknown"
    ).strip().lower()

    status = (
        status or ""
    ).strip().lower()


    # ==================================================
    # Confirmed Malicious / Unsafe Threat
    # ==================================================

    if source == "openphish" and (
        finding_type == "listed"
    ):
        return "MALICIOUS_THREAT"


    if source == "google safe browsing" and (
        status == "unsafe"
    ):
        return "MALICIOUS_THREAT"


    if source == "virustotal" and (
        finding_type == "malicious"
    ):
        return "MALICIOUS_THREAT"


    # ==================================================
    # Reputation Concern
    # ==================================================

    if source == "virustotal" and (
        finding_type == "suspicious"
    ):
        return "REPUTATION_CONCERN"


    if source == "whois" and (
        finding_type in (
            "new",
            "moderate"
        )
    ):
        return "REPUTATION_CONCERN"


    # ==================================================
    # Verification Limitation
    # ==================================================

    if finding_type in (
        "unknown",
        "unavailable",
        "not_available"
    ):
        return "VERIFICATION_LIMITATION"


    # ==================================================
    # Positive Security Signal
    # ==================================================

    if source == "openphish" and (
        finding_type == "not_listed"
    ):
        return "POSITIVE_SIGNAL"


    if source == "google safe browsing" and (
        status == "safe"
    ):
        return "POSITIVE_SIGNAL"


    if source == "virustotal" and (
        finding_type == "safe"
    ):
        return "POSITIVE_SIGNAL"


    if source == "https" and (
        finding_type == "enabled"
    ):
        return "POSITIVE_SIGNAL"


    if source == "ssl/tls" and (
        finding_type == "valid"
    ):
        return "POSITIVE_SIGNAL"


    if source == "security headers" and (
        finding_type == "present"
    ):
        return "POSITIVE_SIGNAL"


    if source == "whois" and (
        finding_type == "established"
    ):
        return "POSITIVE_SIGNAL"


    # ==================================================
    # Security Weakness
    # ==================================================

    if source == "https" and (
        finding_type == "disabled"
    ):
        return "SECURITY_WEAKNESS"


    if source == "ssl/tls" and (
        finding_type == "invalid"
    ):
        return "SECURITY_WEAKNESS"


    if source == "security headers" and (
        finding_type == "missing"
    ):
        return "SECURITY_WEAKNESS"


    # ==================================================
    # Default
    # ==================================================

    return "SECURITY_WEAKNESS"

# ==================================================
# Finding Builder
# ==================================================

def build_finding(
    source,
    category,
    finding_type,
    severity,
    status,
    confirmed,
    message,
    details=None
):
    """
    Build one standardized normalized finding.

    Every finding returned by the aggregator should
    contain the same core fields.
    """

    finding = {

        "source":
            source,

        "category":
            category,

        "findingClass":
            classify_finding(
                source,
                finding_type,
                status
            ),

        "severity":
            severity,

        "status":
            status,

        "confirmed":
            confirmed,

        "message":
            message

    }


    if details is not None:

        finding["details"] = details


    return finding


# ==================================================
# Security Data Aggregation
# ==================================================

def aggregate_security_data(
    safe_result,
    virus_total_result,
    https_result,
    ssl_result,
    headers_result,
    whois_result,
    openphish_result,
    score_result
):
    """
    Aggregate all security assessment results.

    Phase 13.3:
        Normalize and classify security findings.

    Phase 13.4:
        Final security posture is determined separately
        by backend.modules.security_posture.

    Returns
    -------
    dict
        Unified security assessment data containing
        normalized findings, severity statistics,
        confidence, and checker results.
    """

    try:

        # ==================================================
        # Safety Defaults
        # ==================================================

        safe_result = safe_result or {}
        virus_total_result = virus_total_result or {}
        https_result = https_result or {}
        ssl_result = ssl_result or {}
        headers_result = headers_result or {}
        whois_result = whois_result or {}
        openphish_result = openphish_result or {}
        score_result = score_result or {}


        # ==================================================
        # Extract Existing Score Information
        # ==================================================

        score = score_result.get(
            "score",
            0
        )

        level = score_result.get(
            "level",
            "Unknown"
        )


        # ==================================================
        # Extract Security Status
        # ==================================================

        safe_status = safe_result.get(
            "status",
            "Unavailable"
        )

        virus_total_status = virus_total_result.get(
            "status",
            "Unknown"
        )

        https_enabled = https_result.get(
            "https",
            None
        )

        ssl_valid = ssl_result.get(
            "sslValid",
            None
        )

        whois_status = whois_result.get(
            "status",
            "Unavailable"
        )

        openphish_status = openphish_result.get(
            "status",
            "Unknown"
        )



        # ==================================================
        # Security Finding Containers
        # ==================================================

        critical_findings = []

        warnings = []

        positive_signals = []

        normalized_findings = []



        # ==================================================
        # 1. OpenPhish
        # ==================================================

        openphish_success = (
            openphish_result.get(
                "success",
                False
            )
        )

        openphish_listed = (
            openphish_result.get(
                "listed",
                False
            )
        )


        # --------------------------------------------------
        # Confirmed phishing URL
        # --------------------------------------------------

        if (
            openphish_success is True
            and openphish_listed is True
        ):

            message = (
                "URL is listed in the OpenPhish phishing feed."
            )

            critical_findings.append(
                message
            )

            normalized_findings.append(
                build_finding(
                    source="OpenPhish",
                    category="Phishing Detection",
                    finding_type="listed",
                    severity=normalize_severity(
                        "openphish",
                        "listed"
                    ),
                    status="Phishing",
                    confirmed=True,
                    message=message
                )
            )


        # --------------------------------------------------
        # Successfully checked and not listed
        # --------------------------------------------------

        elif (
            openphish_success is True
            and openphish_listed is False
            and openphish_status == "Not Listed"
        ):

            message = (
                "URL was not found in the OpenPhish phishing feed."
            )

            positive_signals.append(
                message
            )

            normalized_findings.append(
                build_finding(
                    source="OpenPhish",
                    category="Phishing Reputation",
                    finding_type="not_listed",
                    severity="Info",
                    status="Not Listed",
                    confirmed=True,
                    message=message
                )
            )


        # --------------------------------------------------
        # OpenPhish unavailable
        # --------------------------------------------------

        elif openphish_status == "Unavailable":

            message = (
                "OpenPhish verification was unavailable."
            )

            warnings.append(
                message
            )

            normalized_findings.append(
                build_finding(
                    source="OpenPhish",
                    category="Phishing Verification",
                    finding_type="unavailable",
                    severity="Info",
                    status="Unavailable",
                    confirmed=False,
                    message=message
                )
            )


        # --------------------------------------------------
        # Unknown / invalid OpenPhish result
        # --------------------------------------------------

        else:

            message = (
                "OpenPhish returned an unknown result."
            )

            warnings.append(
                message
            )

            normalized_findings.append(
                build_finding(
                    source="OpenPhish",
                    category="Phishing Verification",
                    finding_type="unknown",
                    severity="Info",
                    status="Unknown",
                    confirmed=False,
                    message=message
                )
            )




        # ==================================================
        # 2. Google Safe Browsing
        # ==================================================

        if safe_status == "Unsafe":

            message = (
                "Google Safe Browsing identified "
                "the website as unsafe."
            )

            critical_findings.append(
                message
            )

            normalized_findings.append(
                build_finding(
                    source="Google Safe Browsing",
                    category="Threat Detection",
                    finding_type="unsafe",
                    severity=normalize_severity(
                        "google safe browsing",
                        "unsafe",
                        safe_status
                    ),
                    status="Unsafe",
                    confirmed=True,
                    message=message
                )
            )


        elif safe_status == "Safe":

            message = (
                "Google Safe Browsing did not "
                "identify known threats."
            )

            positive_signals.append(
                message
            )

            normalized_findings.append(
                build_finding(
                    source="Google Safe Browsing",
                    category="Threat Detection",
                    finding_type="safe",
                    severity="Info",
                    status="Safe",
                    confirmed=True,
                    message=message
                )
            )


        elif safe_status in (
            "Unknown",
            "Unavailable"
        ):

            message = (
                "Google Safe Browsing verification "
                "was unavailable."
            )

            warnings.append(
                message
            )

            normalized_findings.append(
                build_finding(
                    source="Google Safe Browsing",
                    category="Threat Verification",
                    finding_type="unavailable",
                    severity="Info",
                    status="Unavailable",
                    confirmed=False,
                    message=message
                )
            )


        else:

            message = (
                "Google Safe Browsing returned "
                "an unknown result."
            )

            warnings.append(
                message
            )

            normalized_findings.append(
                build_finding(
                    source="Google Safe Browsing",
                    category="Threat Verification",
                    finding_type="unknown",
                    severity="Info",
                    status="Unknown",
                    confirmed=False,
                    message=message
                )
            )


        # ==================================================
        # 3. VirusTotal
        # ==================================================

        malicious = virus_total_result.get(
            "malicious",
            0
        )

        suspicious = virus_total_result.get(
            "suspicious",
            0
        )


        try:
            malicious = int(malicious or 0)
        except (
            TypeError,
            ValueError
        ):
            malicious = 0


        try:
            suspicious = int(suspicious or 0)
        except (
            TypeError,
            ValueError
        ):
            suspicious = 0


        if malicious > 0:

            message = (
                "VirusTotal reported malicious detections."
            )

            critical_findings.append(
                message
            )

            normalized_findings.append(
                build_finding(
                    source="VirusTotal",
                    category="Malware Detection",
                    finding_type="malicious",
                    severity=normalize_severity(
                        "virustotal",
                        "malicious"
                    ),
                    status="Malicious",
                    confirmed=True,
                    message=message
                )
            )


        elif suspicious > 0:

            message = (
                "VirusTotal reported suspicious detections."
            )

            warnings.append(
                message
            )

            normalized_findings.append(
                build_finding(
                    source="VirusTotal",
                    category="Suspicious Activity",
                    finding_type="suspicious",
                    severity=normalize_severity(
                        "virustotal",
                        "suspicious"
                    ),
                    status="Suspicious",
                    confirmed=True,
                    message=message
                )
            )


        elif virus_total_status == "Safe":

            message = (
                "VirusTotal reported no malicious "
                "or suspicious detections."
            )

            positive_signals.append(
                message
            )

            normalized_findings.append(
                build_finding(
                    source="VirusTotal",
                    category="Malware Detection",
                    finding_type="safe",
                    severity="Info",
                    status="Safe",
                    confirmed=True,
                    message=message
                )
            )


        elif virus_total_status in (
            "Unknown",
            "Unavailable"
        ):

            message = (
                "VirusTotal verification was unavailable."
            )

            warnings.append(
                message
            )

            normalized_findings.append(
                build_finding(
                    source="VirusTotal",
                    category="Malware Verification",
                    finding_type="unavailable",
                    severity="Info",
                    status="Unavailable",
                    confirmed=False,
                    message=message
                )
            )


        else:

            message = (
                "VirusTotal could not provide "
                "a reliable classification."
            )

            warnings.append(
                message
            )

            normalized_findings.append(
                build_finding(
                    source="VirusTotal",
                    category="Malware Verification",
                    finding_type="unknown",
                    severity="Info",
                    status="Unknown",
                    confirmed=False,
                    message=message
                )
            )


        # ==================================================
        # 4. HTTPS
        # ==================================================

        if https_enabled is True:

            message = (
                "HTTPS is enabled."
            )

            positive_signals.append(
                message
            )

            normalized_findings.append(
                build_finding(
                    source="HTTPS",
                    category="Transport Security",
                    finding_type="enabled",
                    severity="Info",
                    status="Enabled",
                    confirmed=True,
                    message=message
                )
            )


        elif https_enabled is False:

            message = (
                "HTTPS is not enabled."
            )

            warnings.append(
                message
            )

            normalized_findings.append(
                build_finding(
                    source="HTTPS",
                    category="Transport Security",
                    finding_type="disabled",
                    severity=normalize_severity(
                        "https",
                        "disabled"
                    ),
                    status="Missing",
                    confirmed=True,
                    message=message
                )
            )


        else:

            message = (
                "HTTPS verification was unavailable."
            )

            warnings.append(
                message
            )

            normalized_findings.append(
                build_finding(
                    source="HTTPS",
                    category="Transport Verification",
                    finding_type="unavailable",
                    severity="Info",
                    status="Unavailable",
                    confirmed=False,
                    message=message
                )
            )


        # ==================================================
        # 5. SSL/TLS Certificate
        # ==================================================

        if ssl_valid is True:

            message = (
                "The SSL/TLS certificate is valid."
            )

            positive_signals.append(
                message
            )

            normalized_findings.append(
                build_finding(
                    source="SSL/TLS",
                    category="Certificate Security",
                    finding_type="valid",
                    severity="Info",
                    status="Valid",
                    confirmed=True,
                    message=message
                )
            )


        elif ssl_valid is False:

            message = (
                "The SSL/TLS certificate is invalid."
            )

            warnings.append(
                message
            )

            normalized_findings.append(
                build_finding(
                    source="SSL/TLS",
                    category="Certificate Security",
                    finding_type="invalid",
                    severity=normalize_severity(
                        "ssl",
                        "invalid"
                    ),
                    status="Invalid",
                    confirmed=True,
                    message=message
                )
            )


        else:

            message = (
                "SSL/TLS certificate verification "
                "was unavailable."
            )

            warnings.append(
                message
            )

            normalized_findings.append(
                build_finding(
                    source="SSL/TLS",
                    category="Certificate Verification",
                    finding_type="unavailable",
                    severity="Info",
                    status="Unavailable",
                    confirmed=False,
                    message=message
                )
            )


        # ==================================================
        # 6. Security Headers
        # ==================================================

        header_names = [

            "strict-transport-security",

            "content-security-policy",

            "x-frame-options",

            "x-content-type-options",

            "referrer-policy"

        ]


        # --------------------------------------------------
        # Determine whether the header check itself succeeded
        # --------------------------------------------------

        header_values_present = all(
            header_name in headers_result
            for header_name in header_names
        )

        explicit_unavailable = (
            headers_result.get("status") == "Unavailable"
            or headers_result.get("error")
            == "SECURITY_HEADERS_UNAVAILABLE"
        )

        headers_check_success = (
            not explicit_unavailable
            and (
                headers_result.get("success") is True
                or header_values_present
            )
        )


        present_headers = 0


        if headers_check_success:

            for header_name in header_names:

                if headers_result.get(
                    header_name
                ) is True:

                    present_headers += 1


            missing_headers = (
                len(header_names)
                - present_headers
            )


            # --------------------------------------------------
            # All headers present
            # --------------------------------------------------

            if present_headers == len(
                header_names
            ):

                message = (
                    "All monitored security headers are present."
                )

                positive_signals.append(
                    message
                )

                normalized_findings.append(
                    build_finding(
                        source="Security Headers",
                        category="Security Configuration",
                        finding_type="present",
                        severity="Info",
                        status="Complete",
                        confirmed=True,
                        message=message
                    )
                )


            # --------------------------------------------------
            # Some headers missing
            # --------------------------------------------------

            elif present_headers > 0:

                message = (
                    f"{missing_headers} monitored security "
                    "header(s) are missing."
                )

                warnings.append(
                    message
                )

                normalized_findings.append(
                    build_finding(
                        source="Security Headers",
                        category="Security Configuration",
                        finding_type="missing",
                        severity=normalize_severity(
                            "securityheaders",
                            "missing"
                        ),
                        status="Missing",
                        confirmed=True,
                        message=message,
                        details={
                            "present":
                                present_headers,

                            "missing":
                                missing_headers,

                            "total":
                                len(header_names)
                        }
                    )
                )


            # --------------------------------------------------
            # No headers detected
            # --------------------------------------------------

            else:

                message = (
                    "None of the monitored security headers "
                    "were detected."
                )

                warnings.append(
                    message
                )

                normalized_findings.append(
                    build_finding(
                        source="Security Headers",
                        category="Security Configuration",
                        finding_type="missing",
                        severity="Low",
                        status="Missing",
                        confirmed=True,
                        message=message,
                        details={
                            "present":
                                0,

                            "missing":
                                len(header_names),

                            "total":
                                len(header_names)
                        }
                    )
                )


        # --------------------------------------------------
        # Header check unavailable
        # --------------------------------------------------

        else:

            message = (
                "Security header verification was unavailable."
            )

            warnings.append(
                message
            )

            normalized_findings.append(
                build_finding(
                    source="Security Headers",
                    category="Security Verification",
                    finding_type="unavailable",
                    severity="Info",
                    status="Unavailable",
                    confirmed=False,
                    message=message,
                    details={
                        "present":
                            None,

                        "missing":
                            None,

                        "total":
                            len(header_names),

                        "checkStatus":
                            "Unavailable"
                    }
                )
            )


        # ==================================================
        # 7. WHOIS Domain Reputation
        # ==================================================

        if whois_status == "Established":

            message = (
                "The domain has an established "
                "registration history."
            )

            positive_signals.append(
                message
            )

            normalized_findings.append(
                build_finding(
                    source="WHOIS",
                    category="Domain Reputation",
                    finding_type="established",
                    severity="Info",
                    status="Established",
                    confirmed=True,
                    message=message
                )
            )


        elif whois_status == "Moderate":

            message = (
                "The domain has a moderate "
                "registration history."
            )

            warnings.append(
                message
            )

            normalized_findings.append(
                build_finding(
                    source="WHOIS",
                    category="Domain Reputation",
                    finding_type="moderate",
                    severity=normalize_severity(
                        "whois",
                        "moderate"
                    ),
                    status="Moderate",
                    confirmed=True,
                    message=message
                )
            )


        elif whois_status == "New":

            message = (
                "The domain has a relatively new "
                "registration history."
            )

            warnings.append(
                message
            )

            normalized_findings.append(
                build_finding(
                    source="WHOIS",
                    category="Domain Reputation",
                    finding_type="new",
                    severity=normalize_severity(
                        "whois",
                        "new"
                    ),
                    status="New",
                    confirmed=True,
                    message=message
                )
            )


        elif whois_status in (
            "Unknown",
            "Unavailable"
        ):

            message = (
                "WHOIS domain reputation information "
                "is unavailable."
            )

            warnings.append(
                message
            )

            normalized_findings.append(
                build_finding(
                    source="WHOIS",
                    category="Domain Verification",
                    finding_type="unavailable",
                    severity="Info",
                    status="Unavailable",
                    confirmed=False,
                    message=message
                )
            )


        else:

            message = (
                "WHOIS domain reputation information "
                "returned an unknown result."
            )

            warnings.append(
                message
            )

            normalized_findings.append(
                build_finding(
                    source="WHOIS",
                    category="Domain Verification",
                    finding_type="unknown",
                    severity="Info",
                    status="Unknown",
                    confirmed=False,
                    message=message
                )
            )


        # ==================================================
        # Determine Confidence
        # ==================================================

        unavailable_checks = 0


        if safe_status in (
            "Unknown",
            "Unavailable"
        ):

            unavailable_checks += 1


        if virus_total_status in (
            "Unknown",
            "Unavailable"
        ):

            unavailable_checks += 1


        if whois_status in (
            "Unknown",
            "Unavailable"
        ):

            unavailable_checks += 1


        if openphish_status in (
            "Unknown",
            "Unavailable"
        ):

            unavailable_checks += 1


        if https_enabled is None:

            unavailable_checks += 1


        if ssl_valid is None:

            unavailable_checks += 1


        if not headers_check_success:

            unavailable_checks += 1


        if unavailable_checks == 0:

            confidence = "High"

        elif unavailable_checks <= 2:

            confidence = "Medium"

        else:

            confidence = "Low"


        # ==================================================
        # Aggregation Statistics
        # ==================================================

        total_checks = 7

        successful_checks = (
            total_checks
            - unavailable_checks
        )


        # ==================================================
        # Phase 13.3 - Severity Statistics
        # ==================================================

        severity_counts = {

            "Critical": 0,

            "High": 0,

            "Medium": 0,

            "Low": 0,

            "Info": 0

        }


        for finding in normalized_findings:

            severity = finding.get(
                "severity",
                "Info"
            )


            if severity in severity_counts:

                severity_counts[
                    severity
                ] += 1


        # ==================================================
        # Finding-Class Statistics
        # ==================================================

        finding_class_counts = {

            "MALICIOUS_THREAT": 0,

            "SECURITY_WEAKNESS": 0,

            "REPUTATION_CONCERN": 0,

            "VERIFICATION_LIMITATION": 0,

            "POSITIVE_SIGNAL": 0

        }


        for finding in normalized_findings:

            finding_class = finding.get(
                "findingClass"
            )


            if finding_class in finding_class_counts:

                finding_class_counts[
                    finding_class
                ] += 1


        # ==================================================
        # Aggregated Result
        # ==================================================

        aggregated_result = {

            "score":
                score,

            "level":
                level,

            "confidence":
                confidence,

            "criticalFindings":
                critical_findings,

            "warnings":
                warnings,

            "positiveSignals":
                positive_signals,

            "normalizedFindings":
                normalized_findings,

            "statistics": {

                "totalChecks":
                    total_checks,

                "successfulChecks":
                    successful_checks,

                "unavailableChecks":
                    unavailable_checks,

                "positiveSignals":
                    len(
                        positive_signals
                    ),

                "warnings":
                    len(
                        warnings
                    ),

                "criticalFindings":
                    len(
                        critical_findings
                    ),

                "severityCounts":
                    severity_counts,

                "findingClassCounts":
                    finding_class_counts

            },

            "checks": {

                "google safe browsing":
                    safe_status,

                "virusTotal":
                    virus_total_status,

                "https":
                    https_enabled,

                "ssl":
                    ssl_valid,

                "securityHeaders":
                    present_headers,

                "securityHeadersTotal":
                    len(
                        header_names
                    ),

                "whois":
                    whois_status,

                "openphish":
                    openphish_status

            }

        }


        # ==================================================
        # Logging
        # ==================================================

        log_info(
            "Security data aggregation completed "
            f"(Score={score}, "
            f"Level={level}, "
            f"Confidence={confidence})"
        )


        print(
            "\n========== PHASE 13 SECURITY AGGREGATION =========="
        )

        print(
            "Security Score:",
            score
        )

        print(
            "Security Level:",
            level
        )

        print(
            "Confidence:",
            confidence
        )

        print(
            "Severity Counts:",
            severity_counts
        )

        print(
            "Finding Class Counts:",
            finding_class_counts
        )

        print(
            "====================================================\n"
        )


        return aggregated_result


    except Exception as error:

        log_error(
            f"Security Data Aggregation Error: {error}"
        )


        return {

            "score":
                0,

            "level":
                "Unknown",

            "confidence":
                "Low",

            "criticalFindings":
                [],

            "warnings": [
                "Security data aggregation failed."
            ],

            "positiveSignals":
                [],

            "normalizedFindings":
                [],

            "statistics": {

                "totalChecks":
                    0,

                "successfulChecks":
                    0,

                "unavailableChecks":
                    0,

                "positiveSignals":
                    0,

                "warnings":
                    1,

                "criticalFindings":
                    0,

                "severityCounts": {

                    "Critical": 0,

                    "High": 0,

                    "Medium": 0,

                    "Low": 0,

                    "Info": 0

                },

                "findingClassCounts": {

                    "MALICIOUS_THREAT": 0,

                    "SECURITY_WEAKNESS": 0,

                    "REPUTATION_CONCERN": 0,

                    "VERIFICATION_LIMITATION": 0,

                    "POSITIVE_SIGNAL": 0

                }

            },

            "checks": {}

        }