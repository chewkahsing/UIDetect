import json
import time

import re

from urllib.parse import urlparse

from ollama import chat

from logger import (
    log_info,
    log_warning,
    log_error
)



# ==========================================================
# Ollama Configuration
# ==========================================================

MODEL = "qwen2.5:3b"

MAX_ATTEMPTS = 3

RETRY_DELAY = 2


# ==========================================================
# Consolidated Warning AI Helpers
# ==========================================================

# ==========================================================
# Warning Prompt Builder
# ==========================================================
"""
Builds the prompt used by UIDetect's context-aware warning AI.

IMPORTANT:
This module ONLY builds the prompt.

It must NOT:
- import warning_ai
- call Ollama
- validate AI responses

This prevents circular imports.
"""


# ==========================================================
# Build Warning Prompt
# ==========================================================

def build_warning_prompt(data):
    """
    Build the context-aware security warning prompt.

    Backend assessment data is authoritative. Qwen is responsible
    only for turning confirmed facts into short, natural, user-facing
    explanations for the three UIDetect popup sections.
    """

    if not isinstance(data, dict):
        raise ValueError(
            "Warning prompt builder requires a dictionary."
        )

    website = data.get(
        "url",
        data.get("website", "Unknown")
    )

    interaction = str(
        data.get("interaction", "UNKNOWN")
    ).upper()

    score = data.get("score", "Unknown")
    security_level = data.get(
        "level",
        data.get("securityLevel", "Unknown")
    )

    https = data.get("https")
    if https is True:
        https_status = "ENABLED"
    elif https is False:
        https_status = "NOT ENABLED"
    else:
        https_status = "UNKNOWN"

    ssl_data = data.get("ssl", {})
    if not isinstance(ssl_data, dict):
        ssl_data = {}

    ssl_valid = ssl_data.get(
        "sslValid",
        data.get("sslValid", "Unknown")
    )

    tls_version = ssl_data.get(
        "protocol",
        data.get("tlsVersion", "Unknown")
    )

    safe_browsing = data.get(
        "safeBrowsing", "Unknown"
    )

    openphish = data.get("openPhish", {})
    if not isinstance(openphish, dict):
        openphish = {}

    openphish_status = openphish.get(
        "status",
        data.get("openPhishStatus", "Unknown")
    )
    openphish_listed = openphish.get(
        "listed",
        data.get("openPhishListed", False)
    )
    openphish_risk = openphish.get(
        "risk",
        data.get("openPhishRisk", "Unknown")
    )

    virus_total = data.get("virusTotal", {})
    if not isinstance(virus_total, dict):
        virus_total = {}

    virustotal_status = virus_total.get(
        "status",
        data.get("virusTotalStatus", "Unknown")
    )
    virustotal_malicious = virus_total.get(
        "malicious",
        data.get("virusTotalMalicious", 0)
    )
    virustotal_suspicious = virus_total.get(
        "suspicious",
        data.get("virusTotalSuspicious", 0)
    )

    whois_status = data.get("whoisStatus", "Unknown")
    domain_age = data.get("domainAge", "Unknown")

    headers = data.get("securityHeaders", {})
    if not isinstance(headers, dict):
        headers = {}

    header_checks = {
        "Strict-Transport-Security": headers.get("strict-transport-security"),
        "Content-Security-Policy": headers.get("content-security-policy"),
        "X-Frame-Options": headers.get("x-frame-options"),
        "X-Content-Type-Options": headers.get("x-content-type-options"),
        "Referrer-Policy": headers.get("referrer-policy")
    }

    missing_headers = [
        name
        for name, value in header_checks.items()
        if value is False
    ]

    unknown_headers = [
        name
        for name, value in header_checks.items()
        if value is None
    ]

    missing_headers_text = (
        ", ".join(missing_headers)
        if missing_headers
        else "None"
    )

    unknown_headers_text = (
        ", ".join(unknown_headers)
        if unknown_headers
        else "None"
    )

    page_title = data.get("pageTitle", "Unknown")
    meta_description = data.get("metaDescription", "Unknown")

    final_posture = data.get("finalPosture", {})
    if not isinstance(final_posture, dict):
        final_posture = {}

    final_posture_risk = final_posture.get("risk", "Unknown")
    final_posture_severity = final_posture.get(
        "severity",
        final_posture.get("highestSeverity", "Unknown")
    )
    recommendation_reason = final_posture.get(
        "recommendationReason", "Unknown"
    )
    recommendation_action = final_posture.get(
        "recommendationAction", "Unknown"
    )
    overall_status = final_posture.get(
        "overallStatus", "Unknown"
    )
    primary_finding = final_posture.get(
        "primaryFinding", None
    )
    

    # Additional authoritative supporting evidence used to let Qwen
    # build a short primary + supporting summary. These values are
    # evidence only; they do not replace finalPosture's decision.
    supporting_findings = []

    if openphish_listed is True:
        supporting_findings.append("OpenPhish: LISTED")

    try:
        vt_malicious_int = int(virustotal_malicious)
    except (TypeError, ValueError):
        vt_malicious_int = 0

    try:
        vt_suspicious_int = int(virustotal_suspicious)
    except (TypeError, ValueError):
        vt_suspicious_int = 0

    if vt_malicious_int > 0:
        supporting_findings.append(
            f"VirusTotal malicious detections: {vt_malicious_int}"
        )

    if vt_suspicious_int > 0:
        supporting_findings.append(
            f"VirusTotal suspicious detections: {vt_suspicious_int}"
        )

    if str(safe_browsing).strip().upper() in {
        "UNSAFE", "MALICIOUS", "PHISHING", "FLAGGED"
    }:
        supporting_findings.append(
            f"Google Safe Browsing: {safe_browsing}"
        )

    if https is False:
        supporting_findings.append("HTTPS: NOT ENABLED")

    if ssl_valid is False:
        supporting_findings.append("SSL/TLS: INVALID")

    if missing_headers:
        supporting_findings.append(
            f"Missing monitored security headers: {len(missing_headers)}"
        )

    supporting_findings_text = (
        "\n".join(f"- {item}" for item in supporting_findings)
        if supporting_findings
        else "None"
    )

    # ==========================================================
    # Prompt Evidence Values
    # ==========================================================


    ssl_status = (
        f"{ssl_valid} ({tls_version})"
    )

    openphish = {
        "status": openphish_status,
        "listed": openphish_listed,
        "risk": openphish_risk
    }

    virustotal = {
        "status": virustotal_status,
        "malicious": virustotal_malicious,
        "suspicious": virustotal_suspicious
    }

    whois = {
        "status": whois_status,
        "domainAge": domain_age
    }

    security_headers = header_checks

    highest_severity = final_posture_severity

    risk = final_posture_risk

    confidence = final_posture.get(
        "confidence",
        "Unknown"
    )

    finding_class_counts = final_posture.get(
        "findingClassCounts",
        {}
    )

    print("========== WARNING PROMPT DATA ==========")
    print("Website:", website)
    print("Interaction:", interaction)
    print("Score:", score)
    print("Security Level:", security_level)
    print("HTTPS:", https_status)
    print("SSL:", ssl_valid)
    print("Missing Headers:", missing_headers_text)
    print("Overall Status:", overall_status)
    print("Risk:", final_posture_risk)
    print("Severity:", final_posture_severity)
    print("Primary Finding:", primary_finding)
    print("Recommendation Reason:", recommendation_reason)
    print("Recommendation Action:", recommendation_action)
    print("==========================================")

    prompt = f"""

You are UIDetect Security AI.

Your task is to analyze the completed security assessment produced
by the UIDetect backend and convert the backend findings into three
short, natural, user-friendly explanations for the current browser
user.

You are NOT responsible for performing the security assessment.
The backend has already performed the checks.

Your responsibility is to:
1. Understand the security facts provided by the backend.
2. Determine which confirmed finding is most important.
3. Explain that finding accurately and naturally.
4. Use supporting findings when they materially help the explanation.
5. Give practical advice that is appropriate for the current browser
   user.
6. Follow the authoritative recommendation action and reason supplied
   by the backend.
7. Never invent security facts, consequences, actions, or evidence.

============================================================
CORE PRINCIPLE
============================================================

The backend assessment is the source of truth.

Generate the response FROM the supplied backend facts.

Do not replace backend facts with general assumptions.
Do not infer a security problem merely because something is unusual.
Do not treat missing information as evidence of danger.
Do not create additional findings that are not present in the
backend assessment.

Your wording may be natural and conversational, but the meaning must
remain faithful to the backend evidence.

Examples in these instructions describe the intended style and logic.
They are NOT fixed responses that must be copied.

============================================================
RULE 1 — ABOUT WEBSITE
============================================================

The "aboutWebsite" field explains what UIDetect found.

Identify the most important confirmed security finding first.

When there is a primary finding and relevant supporting findings,
summarize the primary finding first and optionally mention the
supporting finding in the same short explanation.

The explanation should answer:

"What did UIDetect actually find?"

Do not turn the explanation into a general security lecture.

Do not mention technical evidence unless it helps the user understand
the finding.

Examples of acceptable reasoning:

- If OpenPhish lists the URL, explain that UIDetect found the website
  listed in the phishing feed.
- If VirusTotal reports malicious detections, explain that UIDetect
  found malicious detections reported by VirusTotal.
- If VirusTotal reports suspicious detections but no malicious
  detections, explain the suspicious result without calling it
  malicious.
- If HTTPS is unavailable or invalid and this is a confirmed finding,
  explain that the connection does not have the expected HTTPS
  protection.
- If only security headers are missing, explain that some monitored
  security protections are missing.
- If there are no major confirmed findings, use the safe/no-major-
  problem interpretation supported by the final posture.

Do not claim that the website is malicious merely because headers are
missing, WHOIS information is unavailable, or a domain is relatively
new.

============================================================
RULE 2 — WARNING
============================================================

The "warning" field explains what the primary finding means to the
current browser user.

The warning must be proportional to the evidence.

Explain the practical security meaning of the finding without
exaggeration.

Do NOT automatically convert a technical weakness into a confirmed
attack scenario.

For example:

Missing security headers may be described as missing security
protections.

Do NOT automatically state that missing headers mean:
- attackers can steal the user's data,
- the user will be hacked,
- the website can compromise the device,
- an attack is currently happening,
unless the backend provides evidence supporting such a conclusion.

Similarly, HTTPS problems should not automatically be described as
proof that someone is intercepting the user's connection.

Use careful wording such as:
- "may reduce the security protection of the connection"
- "means UIDetect could not confirm the expected HTTPS protection"
- "some security protections are missing"

when those statements accurately match the evidence.

============================================================
RULE 3 — RECOMMENDATION
============================================================

The "recommendation" field tells the CURRENT BROWSER USER what to do.

The authoritative backend fields are:

- recommendationReason
- recommendationAction

These fields must guide the recommendation.

The recommendation must remain consistent with the security posture
and the highest-priority confirmed finding.

Do not invent a different action simply because another action sounds
more technically appropriate.

The recommendation should be practical for a normal browser user.

For example:

If the backend indicates that the user should stop:
- clearly tell the user not to continue with the current operation.

If the backend indicates normal continuation:
- explain that the user may continue normally when the assessment
  supports that action.

If caution is appropriate:
- tell the user to continue carefully or verify the website before
  providing sensitive information, when supported by the backend.

============================================================
RULE 4 — FINDING PRIORITY
============================================================

When several confirmed security findings exist, determine the primary
finding using this exact priority order:

1. OpenPhish listed
2. VirusTotal malicious
3. VirusTotal suspicious
4. Google Safe Browsing flagged
5. HTTPS / SSL problems
6. Other confirmed security findings
7. Missing security headers

This priority determines which finding should normally lead the
"user-facing explanation".

A lower-priority finding must not replace a higher-priority confirmed
finding.

For example:

If VirusTotal reports malicious detections AND several missing
security headers, the malicious VirusTotal result is the primary
finding.

Do not make the missing headers the main warning simply because they
are easier to explain.

If OpenPhish lists the website, the OpenPhish result takes priority
over lower-priority findings.

============================================================
RULE 5 — VIRUSTOTAL
============================================================

VirusTotal malicious and suspicious detections are different types
of evidence.

Always preserve this distinction.

"Malicious" must remain malicious.

"Suspicious" must remain suspicious.

Do not convert suspicious detections into malicious detections.

Preserve the actual detection counts.

If malicious = 1:
- say "one malicious detection" or equivalent singular wording.

Do NOT say:
- "multiple malicious detections"
- "many engines detected it as malicious"

unless the backend evidence actually supports that wording.

If malicious > 1:
- multiple malicious detections may be described.

If both malicious and suspicious detections exist:
- malicious is the stronger finding,
- suspicious may be mentioned as supporting evidence,
- keep the two categories separate.

Example backend:

malicious = 1
suspicious = 2

Correct interpretation:

One malicious detection was reported, with two additional suspicious
detections.

Incorrect interpretation:

Multiple security engines confirmed the website is malicious.

The second statement changes the meaning of the backend evidence and
must not be generated.

============================================================
RULE 6 — GOOGLE SAFE BROWSING
============================================================

Only describe Google Safe Browsing as a security finding when the
backend explicitly reports that the website was flagged.

If Safe Browsing is "Safe", do not describe it as a warning.

If Safe Browsing is unavailable, do not treat the unavailable result
as a security finding.

Do not claim that Safe Browsing guarantees that a website is safe.

============================================================
RULE 7 — HTTPS AND SSL/TLS
============================================================

HTTPS and SSL/TLS findings must be interpreted according to the
actual backend values.

If HTTPS is confirmed and SSL/TLS is valid:
- do not invent an HTTPS or SSL problem.

If HTTPS is not enabled:
- explain that the expected HTTPS protection is not present.

If SSL/TLS validation fails:
- explain the confirmed SSL/TLS problem without inventing the cause.

Do not claim that an HTTPS or SSL problem proves that an attacker is
intercepting the connection.

Do not claim that the user's information has already been stolen.

The recommendation must be written for the visitor, not the website
administrator.

============================================================
RULE 8 — SECURITY HEADERS
============================================================

Security headers are website security protections.

If some monitored headers are missing, explain that some security
protections are missing.

Normally do not list raw header names in the three main AI fields.

Technical header names belong in the Security Details section.

Missing headers alone do not prove that:
- the website is malicious,
- an attack is occurring,
- user data has been stolen,
- the user's device is compromised.

Do not tell the current visitor to add, configure, enable, repair, or
install the website's security headers.

============================================================
RULE 9 — WHOIS / DOMAIN AGE
============================================================

WHOIS and domain-age information is supporting context.

A new or recently registered domain is not automatically malicious.

An established domain is not automatically guaranteed to be safe.

Use domain age only when it materially supports the overall
assessment or backend recommendation.

Do not make domain age the primary security finding unless the backend
explicitly identifies it as such.

If WHOIS information is unavailable, do not treat the absence of WHOIS
data as evidence of danger.

============================================================
RULE 10 — NO CONFIRMED MAJOR FINDING
============================================================

When the backend confirms that there are no major security problems,
the response must communicate that UIDetect did not detect any major
security problems.

Use this statement or natural wording with the same meaning:

"UIDetect did not detect any major security problems with this
website."

Do not create a warning merely because some optional information is
unavailable.

Do not create a security problem from missing headers if the overall
assessment does not classify them as a meaningful major finding.

============================================================
RULE 11 — UNAVAILABLE OR UNKNOWN CHECKS
============================================================

Unavailable, unknown, skipped, or failed-to-retrieve checks are NOT
automatically security findings.

Do not mention unavailable checks in:

- aboutWebsite
- warning
- recommendation

unless the backend explicitly identifies the unavailability itself as
a relevant confirmed finding or recommendation reason.

Technical unavailable-check information may remain in Security Details.

============================================================
RULE 12 — SCORE AND SECURITY LEVEL
============================================================

The security score and security level are evidence used to understand
the overall assessment.

Use them internally when deciding whether the wording should indicate
safe, caution, or higher risk.

Never expose the numerical score in:

- aboutWebsite
- warning
- recommendation

Do not make the response sound like a score report.

The user should receive a natural explanation rather than:

"Your score is 81."

Instead, describe the practical security posture supported by the
backend.

A high score does not override a higher-priority confirmed critical
finding.

For example, if a higher-priority malicious VirusTotal finding exists,
do not describe the website as safe merely because another field has
a relatively high score.

============================================================
RULE 13 — FINAL SECURITY POSTURE
============================================================

The finalPosture object summarizes the backend's final interpretation.

Use:

- highestSeverity
- findingClassCounts
- findings
- confidence
- risk
- recommendation
- interaction

when relevant.

The final posture helps determine whether the website should be
presented as safe, cautionary, or requiring the user to stop.

Do not contradict the final posture.

Do not claim "very safe" when the backend identifies a critical
finding.

Do not claim "dangerous" solely because the confidence is medium.

Confidence describes the certainty of the assessment; it is not itself
a security finding.

============================================================
RULE 14 — INTERACTION CONTEXT
============================================================

The detected interaction describes what the user was doing when
UIDetect assessed the website.

Possible interaction examples include:

LOGIN
REGISTRATION
UPLOAD
DOWNLOAD
PAYMENT
LOGOUT
RIGHT_CLICK
BROWSE
FORM

Interaction is contextual information, not automatically a security
finding.

Use the interaction in the explanation only when it materially affects
the meaning or recommended action.

For example:

If the user is uploading a file and the backend identifies a relevant
security concern, the recommendation may appropriately tell the user
to avoid uploading sensitive files.

If the user is logging in and the website has a relevant security
problem, the recommendation may appropriately caution the user before
entering credentials.

If the interaction is BROWSE and there is no special interaction risk,
do not invent one.

Do not force phrases such as "during your login" into every response
simply because LOGIN exists in the backend data.

============================================================
RULE 16 — CURRENT USER VS WEBSITE OWNER
============================================================

The recommendation is written for the current browser user.

The current browser user normally cannot modify the website's server
configuration.

Therefore, do NOT tell the visitor to:

- enable HTTPS on the website,
- install an SSL certificate,
- configure TLS,
- add security headers,
- repair server configuration,
- modify website security settings,
- fix the website's backend.

Those are website-operator actions.

Instead, explain what the visitor should do based on the backend
recommendation.

For example:

Incorrect:
"Enable HTTPS to improve the website's security."

Correct visitor-oriented approach:
"Be cautious when entering sensitive information and verify that you
are using the official website before continuing."

The exact recommendation must still follow recommendationAction and
recommendationReason.

============================================================
RULE 17 — SECURITY CONSEQUENCE CONTROL
============================================================

Only describe consequences supported by the backend evidence.

Do not invent:

- malware infections,
- credential theft,
- data theft,
- account compromise,
- hacking,
- interception,
- attacks,
- malicious intent,
- attacker activity,
- compromised devices.

A technical weakness does not automatically prove that any of these
events are occurring.

Use measured language when the evidence only establishes a weakness
or missing protection.

============================================================
RULE 18 — MULTIPLE FINDINGS
============================================================

When multiple confirmed findings exist:

1. Select the highest-priority finding as the primary finding.
2. Use the strongest finding in aboutWebsite.
3. Explain the primary finding in warning.
4. Mention a supporting finding only when it improves the user's
   understanding.
5. Do not produce a long list of every technical result.
6. Do not allow a supporting finding to contradict the primary finding.

For example:

If:
- VirusTotal malicious = 1
- VirusTotal suspicious = 2
- four security headers missing

The response should focus primarily on the malicious VirusTotal
finding.

The suspicious detections may be mentioned as supporting evidence.

The missing headers should normally remain secondary.

============================================================
RULE 19 — CONSISTENCY WITH AUTHORITATIVE RECOMMENDATION
============================================================

The backend recommendation is authoritative.

The generated recommendation must not contradict:

- recommendationReason
- recommendationAction
- finalPosture
- highestSeverity
- primaryFinding

If the backend says to stop, do not recommend normal continuation.

If the backend says normal continuation and no higher-priority
confirmed finding contradicts it, do not invent a stop recommendation.

If the backend recommends caution, preserve the cautious nature of the
recommendation.

============================================================
RULE 20 — NATURAL USER-FRIENDLY LANGUAGE
============================================================

The response must sound like a security assistant explaining the
result to an ordinary browser user.

Avoid unnecessary jargon.

Do not simply copy backend field names.

Do not mechanically copy examples from this prompt.

Generate natural wording based on the actual combination of facts.

Two websites with similar security assessments may legitimately
receive similar wording.

Do not introduce artificial differences merely to make the responses
look different.

The goal is meaningful variation based on the facts, not random
variation.

============================================================
DECISION PROCESS
============================================================

Before generating the final JSON, internally perform these steps:

STEP 1
Identify the actual website and detected interaction.

STEP 2
Review all confirmed findings.

STEP 3
Ignore unavailable or unknown checks as findings.

STEP 4
Determine the primary finding using the required priority order.

STEP 5
Identify supporting findings that are materially relevant.

STEP 6
Review the final security posture, severity, risk, and confidence.

STEP 7
Check the authoritative recommendation reason and action.

STEP 8
Determine whether the interaction materially changes the advice.

STEP 9
Generate:
- what UIDetect found,
- what the finding means,
- what the current user should do.

STEP 10
Check every sentence against the backend evidence.

STEP 11
Remove any unsupported consequence, technical detail, website-owner
instruction, or unrelated information.

STEP 12
Return only the required JSON object.

============================================================
BACKEND EVIDENCE
============================================================

Website:
{website}

URL:
{website}

Page Title:
{page_title}

Meta Description:
{meta_description}

Detected Interaction:
{interaction}

Security Score:
{score}

Security Level:
{security_level}

Overall Status:
{overall_status}

Final Security Posture:
{final_posture}

Primary Finding:
{primary_finding}

Finding Class Counts:
{finding_class_counts}

Highest Severity:
{highest_severity}

Risk:
{risk}

Confidence:
{confidence}

Recommendation Reason:
{recommendation_reason}

Recommendation Action:
{recommendation_action}

HTTPS:
{https_status}

SSL/TLS:
{ssl_status}

Safe Browsing:
{safe_browsing}

OpenPhish:
{openphish}

VirusTotal:
{virustotal}

WHOIS:
{whois}

Security Headers:
{security_headers}

Missing Security Headers:
{missing_headers}

Unknown Security Headers:
{unknown_headers}

============================================================
OUTPUT SCHEMA
============================================================

Return ONLY one valid JSON object.

The object MUST contain exactly these three fields:

{{
    "aboutWebsite": "...",
    "warning": "...",
    "recommendation": "..."
}}

============================================================
OUTPUT FIELD REQUIREMENTS
============================================================

aboutWebsite:
- Explain what UIDetect found.
- Lead with the primary confirmed finding.
- Include supporting evidence only when useful.
- Remain factual and concise.
- Do not mention the numerical score.

warning:
- Explain what the primary finding means to the user.
- Use proportional, evidence-based language.
- Do not exaggerate consequences.
- Do not mention the numerical score.
- Do not treat unavailable checks as findings.

recommendation:
- Tell the current browser user what to do.
- Follow recommendationReason and recommendationAction.
- Consider interaction only when materially relevant.
- Do not instruct the visitor to modify the website.
- Do not mention the numerical score.

============================================================
FINAL VALIDATION BEFORE RESPONSE
============================================================

Before returning the JSON, verify:

1. Every security claim is supported by backend evidence.
2. No finding was invented.
3. The highest-priority confirmed finding is treated as primary.
4. VirusTotal malicious and suspicious results remain separate.
5. VirusTotal counts are accurate.
6. Unavailable checks are not presented as findings.
7. Missing headers are not exaggerated.
8. Score is not mentioned.
9. Technical details are not unnecessarily exposed.
10. The recommendation is written for the browser user.
11. No website-owner remediation instruction is given.
12. Interaction is used only when materially relevant.
14. The recommendation does not contradict the backend recommendation.
15. The three fields are short, natural, and user-friendly.
16. The output contains exactly:
    aboutWebsite
    warning
    recommendation

Return ONLY valid JSON with exactly these fields:

{{
  "aboutWebsite": "...",
  "warning": "...",
  "recommendation": "..."
}}

No Markdown.
No explanation.
No additional fields.
"""

    return prompt.strip()


def validate_popup_response(response_text):
    """
    Validate the JSON response returned by the AI.

    This function ONLY validates AI output.
    It does NOT generate fallback content.
    It does NOT replace missing AI fields.

    Returns
    -------
    dict
        Validated AI-generated popup.

    Raises
    ------
    ValueError
        If the AI response is invalid.
    """

    # ======================================================
    # Step 1 — Validate Input Type
    # ======================================================

    if not isinstance(response_text, str):

        raise ValueError(
            "AI popup response must be a string."
        )

    # ======================================================
    # Step 2 — Remove Whitespace
    # ======================================================

    response_text = response_text.strip()

    if not response_text:

        raise ValueError(
            "AI popup response is empty."
        )

    # ======================================================
    # Step 3 — Remove Markdown Code Fences
    # ======================================================

    if response_text.startswith("```"):

        response_text = (
            response_text
            .replace("```json", "")
            .replace("```JSON", "")
            .replace("```", "")
            .strip()
        )

    if not response_text:

        raise ValueError(
            "AI popup response is empty after cleanup."
        )

    # ======================================================
    # Step 4 — Parse JSON
    # ======================================================

    try:

        data = json.loads(
            response_text
        )

    except json.JSONDecodeError as error:

        raise ValueError(
            f"AI popup response contains invalid JSON: {error}"
        ) from error

    # ======================================================
    # Step 5 — Validate JSON Object
    # ======================================================

    if not isinstance(data, dict):

        raise ValueError(
            "AI popup response must be a JSON object."
        )

    # ======================================================
    # Step 6 — Validate Exact Fields
    # ======================================================

    required_fields = {
        "aboutWebsite",
        "warning",
        "recommendation"
    }

    if set(data.keys()) != required_fields:

        raise ValueError(
            "AI popup response must contain exactly "
            "aboutWebsite, warning, and recommendation."
        )

    # ======================================================
    # Step 7 — Validate aboutWebsite
    # ======================================================

    about_website = data.get(
        "aboutWebsite"
    )

    if not isinstance(
        about_website,
        str
    ):

        raise ValueError(
            "AI popup aboutWebsite must be a string."
        )

    about_website = about_website.strip()

    if not about_website:

        raise ValueError(
            "AI popup aboutWebsite cannot be empty."
        )

    # ======================================================
    # Step 8 — Validate warning
    # ======================================================

    warning = data.get(
        "warning"
    )

    if not isinstance(
        warning,
        str
    ):

        raise ValueError(
            "AI popup warning must be a string."
        )

    warning = warning.strip()

    if not warning:

        raise ValueError(
            "AI popup warning cannot be empty."
        )

    # ======================================================
    # Step 9 — Validate recommendation
    # ======================================================

    recommendation = data.get(
        "recommendation"
    )

    if not isinstance(
        recommendation,
        str
    ):

        raise ValueError(
            "AI popup 'recommendation' must be a string."
        )

    recommendation = recommendation.strip()

    if not recommendation:

        log_warning(
            "AI popup recommendation field is empty."
        )

        raise ValueError(
            "AI popup recommendation cannot be empty."
        )

    # ======================================================
    # Reject CAUTION as a recommendation
    # ======================================================

    if recommendation.upper() == "CAUTION":

        log_warning(
            "AI popup recommendation cannot be CAUTION."
        )

        raise ValueError(
            "AI popup recommendation cannot be the bare word CAUTION."
        )

    # ======================================================
    # Step 10 — Return AI Output
    # ======================================================

    popup = {
        "aboutWebsite": about_website,
        "warning": warning,
        "recommendation": recommendation
    }

    log_info(
        "AI popup response passed structural validation."
    )

    return popup

def format_warning(text):
    """
    Validate AI-generated text without replacing or
    modifying its content.
    """

    if not isinstance(text, str):
        raise ValueError(
            "AI popup field must be a string."
        )

    text = text.strip()

    if not text:
        raise ValueError(
            "AI popup field cannot be empty."
        )

    return text



def format_popup(data):
    """
    Format popup about website, warning and recommendation.
    """

    return {
        "aboutWebsite": format_warning(
            data.get("aboutWebsite")
        ),

        "warning": format_warning(
            data.get("warning")
        ),

        "recommendation": format_warning(
            data.get("recommendation")
        )
    }


# ==========================================================
# Ollama Response Helper
# ==========================================================

def extract_ollama_content(response):
    """
    Safely extract message content from an Ollama response.

    Supports:
    - Ollama ChatResponse objects
    - Dictionary responses

    Returns
    -------
    str
        Extracted response content.

    Raises
    ------
    ValueError
        If the response does not contain valid message content.
    """

    if response is None:

        raise ValueError(
            "Ollama returned an empty response."
        )

    # ======================================================
    # Case 1 - Ollama ChatResponse Object
    # ======================================================

    message = getattr(
        response,
        "message",
        None
    )

    if message is not None:

        content = getattr(
            message,
            "content",
            None
        )

        if content is not None:

            content = str(
                content
            ).strip()

            if content:

                return content

    # ======================================================
    # Case 2 - Dictionary Response
    # ======================================================

    if isinstance(
        response,
        dict
    ):

        message = response.get(
            "message"
        )

        if isinstance(
            message,
            dict
        ):

            content = message.get(
                "content",
                ""
            )

            if content:

                content = str(
                    content
                ).strip()

                if content:

                    return content

    # ======================================================
    # Invalid Response
    # ======================================================

    raise ValueError(
        "Ollama response does not contain valid message content."
    )

# ==========================================================
# Warning Output Guard
# ==========================================================
"""
Validates and corrects AI-generated popup content
against the actual UIDetect security assessment.

IMPORTANT:
This module does NOT:
- call Ollama
- generate AI content
- perform security lookups
- recalculate the security score

Its purpose is to prevent an AI response from contradicting
the completed UIDetect assessment.
"""


# ==========================================================
# Helpers
# ==========================================================

def _normalise(value):
    """
    Convert a value into a normalized lowercase string.
    """

    if value is None:
        return ""

    return str(value).strip().lower()


def _contains_any(text, keywords):
    """
    Check whether text contains any keyword.
    """

    text = _normalise(text)

    return any(
        keyword in text
        for keyword in keywords
    )


# ==========================================================
# Negation-aware phrase matching
# ==========================================================
#
# A plain substring match on a phrase like "https is enabled"
# will also match "until HTTPS is enabled" or "once HTTPS is
# enabled" - which actually mean the OPPOSITE (HTTPS is NOT
# currently enabled). Those are correct, useful things for the
# AI to say, and must not be treated as a factual contradiction.
#
# This helper only counts a match if it is NOT preceded nearby
# by a conditional/negation cue word.
# ==========================================================

_NEGATION_CUES = [
    "until",
    "once",
    "before",
    "when",
    "unless",
    "as soon as",
    "not yet",
    "hasn't",
    "has not",
    "isn't yet",
    "is not yet"
]


def _contains_unqualified_claim(text, terms, window=40):
    """
    Like _contains_any, but ignores matches that are immediately
    preceded (within `window` characters) by a conditional or
    negation cue such as "until" or "once" - e.g. "until HTTPS
    is enabled" does NOT count as claiming HTTPS is enabled now.
    """

    text = _normalise(text)

    for term in terms:

        start = 0

        while True:

            position = text.find(term, start)

            if position == -1:
                break

            preceding = text[max(0, position - window):position]

            if not any(
                cue in preceding
                for cue in _NEGATION_CUES
            ):
                return True

            start = position + len(term)

    return False



def _contains_unsafe_safety_claim(text):
    """
    Detect claims that incorrectly guarantee website safety.
    """

    unsafe_claims = [
        "completely safe",
        "guaranteed safe",
        "100% safe",
        "definitely safe",
        "fully safe",
        "totally safe",
        "you can trust this website",
        "you can fully trust this website",
        "this website is safe",
        "the website is safe"
    ]

    return _contains_any(
        text,
        unsafe_claims
    )


def _get_interaction(data):
    """
    Get the detected interaction.
    """

    return _normalise(
        data.get(
            "interaction",
            "BROWSE"
        )
    ).upper()


def _get_openphish_listed(data):
    """
    Determine whether OpenPhish explicitly lists the URL.

    Only an explicit boolean True or a recognized true-like
    value is treated as listed.
    """

    openphish = data.get(
        "openPhish",
        {}
    )

    if not isinstance(openphish, dict):
        openphish = {}

    value = openphish.get(
        "listed",
        data.get(
            "openPhishListed",
            False
        )
    )

    if isinstance(value, bool):
        return value

    if isinstance(value, str):
        return value.strip().lower() in {
            "true",
            "yes",
            "listed"
        }

    return False


def _get_virustotal_malicious(data):
    """
    Get VirusTotal malicious detection count.
    """

    virus_total = data.get(
        "virusTotal",
        {}
    )

    if not isinstance(virus_total, dict):
        virus_total = {}

    value = virus_total.get(
        "malicious",
        data.get(
            "virusTotalMalicious",
            0
        )
    )

    try:
        return int(value)

    except (TypeError, ValueError):
        return 0


def _get_safe_browsing(data):
    """
    Get Google Safe Browsing result.
    """

    return _normalise(
        data.get(
            "safeBrowsing",
            "Unknown"
        )
    )


def _get_context_risk(data):
    """
    Get the authoritative risk from the completed assessment.
    """

    final_posture = data.get(
        "finalPosture",
        {}
    )

    if isinstance(
        final_posture,
        dict
    ):
        posture_risk = _normalise(
            final_posture.get(
                "risk",
                ""
            )
        )

        if posture_risk:
            return posture_risk

    return _normalise(
        data.get(
            "contextRisk",
            data.get(
                "risk",
                "Unknown"
            )
        )
    )


def _has_confirmed_primary_finding(primary_finding):
    """
    Return True only when the Primary Finding is explicitly
    confirmed by the backend.
    """

    return (
        isinstance(primary_finding, dict)
        and primary_finding.get("confirmed") is True
    )


def _get_recommendation_action(data):
    """
    Get the authoritative recommendationAction from the
    completed assessment's finalPosture (BLOCK, CAUTION,
    NORMAL, NORMAL_CAUTION, or Unknown).
    """

    final_posture = data.get(
        "finalPosture",
        {}
    )

    if not isinstance(final_posture, dict):
        final_posture = {}

    return _normalise(
        final_posture.get(
            "recommendationAction",
            "Unknown"
        )
    )



# ==========================================================
# Interaction Consistency
# ==========================================================

def _recommendation_matches_interaction(
    recommendation,
    interaction
):
    """
    Validate that the AI recommendation does not introduce
    an interaction that was not detected.

    The guard should reject interaction leakage, but should
    not require exact wording for a valid recommendation.
    """

    recommendation = _normalise(
        recommendation
    )

    interaction = _normalise(
        interaction
    ).upper()

    if not recommendation:
        return False

    # ------------------------------------------------------
    # Interaction-specific forbidden actions
    # ------------------------------------------------------

    # ------------------------------------------------------
    # NOTE:
    # This list intentionally does NOT include generic safety
    # vocabulary like "password" or "credential" - those are
    # normal, reasonable words to use in security advice
    # regardless of the current interaction (e.g. "avoid
    # entering your password on unfamiliar sites" is valid
    # BROWSE advice). Only block words that describe a
    # DIFFERENT flow/action being recommended, which would be
    # confusing or wrong given the detected interaction.
    # ------------------------------------------------------

    forbidden_by_interaction = {

        "BROWSE": [
            "log in now",
            "please log in",
            "sign in now",
            "create an account",
            "sign up now",
            "upload this file",
            "download this file"
        ],

        "RIGHT_CLICK": [
            "log in now",
            "please log in",
            "create an account",
            "sign up now",
            "upload this file",
            "download this file",
            "open the file"
        ],

        "LOGIN": [
            "upload this file",
            "download this file",
            "create an account",
            "sign up now"
        ],

        "REGISTER": [
            "upload this file",
            "download this file"
        ],

        "UPLOAD": [
            "log in now",
            "please log in",
            "create an account",
            "sign up now",
            "download this file"
        ],

        "DOWNLOAD": [
            "log in now",
            "please log in",
            "create an account",
            "sign up now",
            "upload this file"
        ]
    }

    forbidden = forbidden_by_interaction.get(
        interaction,
        []
    )

    if _contains_any(
        recommendation,
        forbidden
    ):
        return False

    return True


# ==========================================================
# Warning Consistency
# ==========================================================

def _warning_matches_interaction(
    warning,
    interaction
):
    """
    Prevent the AI warning from introducing unrelated
    user operations that were not detected.

    The warning must focus on the CURRENT interaction.
    """

    warning = _normalise(
        warning
    )

    interaction = _normalise(
        interaction
    ).upper()

    if not warning:
        return False

    # ------------------------------------------------------
    # NOTE: same rationale as _recommendation_matches_interaction
    # above - only block references to a DIFFERENT flow being
    # underway, not generic safety vocabulary such as
    # "password" or "credential".
    # ------------------------------------------------------

    forbidden_by_interaction = {

        "BROWSE": [
            "you are logging in",
            "you are signing in",
            "you are registering",
            "you are signing up",
            "you are uploading",
            "you are downloading"
        ],

        "RIGHT_CLICK": [
            "you are logging in",
            "you are signing in",
            "you are registering",
            "you are signing up",
            "you are uploading",
            "you are downloading",
            "opening the file"
        ],

        "LOGIN": [
            "you are uploading",
            "you are downloading",
            "you are registering",
            "you are signing up"
        ],

        "REGISTER": [
            "you are uploading",
            "you are downloading"
        ],

        "UPLOAD": [
            "you are logging in",
            "you are signing in",
            "you are registering",
            "you are signing up",
            "you are downloading"
        ],

        "DOWNLOAD": [
            "you are logging in",
            "you are signing in",
            "you are registering",
            "you are signing up",
            "you are uploading"
        ]
    }

    forbidden = forbidden_by_interaction.get(
        interaction,
        []
    )

    if _contains_any(
        warning,
        forbidden
    ):
        return False

    return True

def _get_missing_security_headers(data):
    """
    Return the authoritative list of explicitly missing
    monitored security headers.

    Only False means missing.
    Unknown / None does not mean missing.
    """

    headers = data.get(
        "securityHeaders",
        {}
    )

    if not isinstance(headers, dict):
        headers = {}

    header_map = {
        "Strict-Transport-Security":
            headers.get("strict-transport-security"),

        "Content-Security-Policy":
            headers.get("content-security-policy"),

        "X-Frame-Options":
            headers.get("x-frame-options"),

        "X-Content-Type-Options":
            headers.get("x-content-type-options"),

        "Referrer-Policy":
            headers.get("referrer-policy")
    }

    return [
        name
        for name, value in header_map.items()
        if value is False
    ]


# ==========================================================
# Primary Finding Warning Validation
# ==========================================================

def _warning_matches_primary_finding(
    warning,
    primary_finding
):
    """
    Validate that the AI warning reflects the confirmed
    authoritative primary finding.

    This does NOT require exact wording.
    It only verifies that the warning contains a
    meaningful reference to the primary security condition.
    """

    if not isinstance(primary_finding, dict):
        return True

    if primary_finding.get("confirmed") is not True:
        return True

    warning_text = _normalise(
        warning
    )

    if not warning_text:
        return False

    source = _normalise(
        primary_finding.get(
            "source",
            ""
        )
    )

    category = _normalise(
        primary_finding.get(
            "category",
            ""
        )
    )

    message = _normalise(
        primary_finding.get(
            "message",
            ""
        )
    )

    # ------------------------------------------------------
    # HTTPS
    # ------------------------------------------------------

    if source == "https":
        return _contains_any(
            warning_text,
            [
                "https",
                "secure connection",
                "encrypted connection",
                "http connection"
            ]
        )

    # ------------------------------------------------------
    # SSL / TLS
    # ------------------------------------------------------

    if source in {
        "ssl",
        "ssl/tls",
        "tls"
    }:
        return _contains_any(
            warning_text,
            [
                "ssl",
                "tls",
                "certificate",
                "secure connection"
            ]
        )

    # ------------------------------------------------------
    # Security Headers
    # ------------------------------------------------------

    if source == "security headers":
        return _contains_any(
            warning_text,
            [
                "security header",
                "security headers",
                "security protection",
                "security protections",
                "hsts",
                "content-security-policy",
                "csp",
                "x-frame-options",
                "x-content-type-options",
                "referrer-policy"
            ]
        )

    # ------------------------------------------------------
    # OpenPhish
    # ------------------------------------------------------

    if source == "openphish":
        return _contains_any(
            warning_text,
            [
                "phishing",
                "openphish",
                "listed"
            ]
        )

    # ------------------------------------------------------
    # VirusTotal
    # ------------------------------------------------------

    if source == "virustotal":
        return _contains_any(
            warning_text,
            [
                "virustotal",
                "malicious",
                "suspicious",
                "malware"
            ]
        )

    # ------------------------------------------------------
    # Google Safe Browsing
    # ------------------------------------------------------

    if source == "google safe browsing":
        return _contains_any(
            warning_text,
            [
                "safe browsing",
                "security threat",
                "security concern",
                "unsafe",
                "malicious"
            ]
        )

    # ------------------------------------------------------
    # WHOIS
    # ------------------------------------------------------

    if source == "whois":
        return _contains_any(
            warning_text,
            [
                "domain",
                "registration",
                "domain age",
                "reputation"
            ]
        )

    # ------------------------------------------------------
    # Generic category fallback
    # ------------------------------------------------------

    category_words = [
        word
        for word in category.split()
        if len(word) >= 5
    ]

    if category_words and any(
        word in warning_text
        for word in category_words
    ):
        return True

    # ------------------------------------------------------
    # Generic message fallback
    # ------------------------------------------------------

    message_words = [
        word
        for word in message.split()
        if len(word) >= 6
    ]

    if message_words and any(
        word in warning_text
        for word in message_words
    ):
        return True

    return False



# ============================================================
# WEBSITE-OWNER REMEDIATION VALIDATION
# ============================================================

def _validate_user_facing_recommendation(recommendation):
    """
    Prevent Qwen from giving website-owner remediation advice
    to the current browser user.

    The recommendation is intended for the person currently
    using the browser, not the owner or administrator of the
    website.
    """

    if not isinstance(
        recommendation,
        str
    ):
        raise ValueError(
            "AI recommendation must be a string."
        )

    recommendation_lower = (
        recommendation
        .strip()
        .lower()
    )

    # --------------------------------------------------------
    # Direct website-owner remediation
    # --------------------------------------------------------

    website_owner_terms = [

        # HTTPS / SSL / TLS
        "enable https on your website",
        "enable https on the website",
        "add https to your website",
        "add https to the website",
        "configure https on your website",
        "configure https on the website",
        "enable ssl on your website",
        "enable ssl on the website",
        "configure ssl on your website",
        "configure ssl on the website",
        "install an ssl certificate",
        "install ssl certificate",
        "renew the ssl certificate",
        "renew ssl certificate",
        "replace the ssl certificate",

        # Security headers
        "add the missing security headers",
        "add missing security headers",
        "configure the security headers",
        "configure security headers",
        "configure the missing security headers",
        "add the missing headers",
        "add missing headers",
        "configure the missing headers",
        "configure missing headers",
        "fix the security headers",
        "fix security headers",
        "fix the missing security headers",
        "update the security headers",
        "update security headers",
        "set the security headers",
        "set security headers",

        # Website / server remediation
        "configure the website",
        "configure your website",
        "modify the website",
        "modify your website",
        "change the website configuration",
        "change your website configuration",
        "update the website configuration",
        "update your website configuration",
        "change the server configuration",
        "update the server configuration",
        "configure the server",
        "configure your server",

        # Administrator / owner actions
        "website administrator should",
        "site administrator should",
        "website owner should",
        "site owner should",
        "webmaster should",
        "server administrator should"
    ]

    for term in website_owner_terms:

        if term in recommendation_lower:

            raise ValueError(
                "AI recommendation gives website-owner "
                "remediation instead of browser-user guidance."
            )

    # --------------------------------------------------------
    # Website-owner imperative patterns
    #
    # These catch wording variations that do not exactly match
    # the phrases above.
    # --------------------------------------------------------

    owner_action_patterns = [

        r"\b(?:you|your)\s+(?:should|must|need to)\s+"
        r"(?:add|configure|fix|update|set|enable|install|renew)"
        r".{0,80}"
        r"\b(?:header|headers|https|ssl|tls|certificate)\b",

        r"\b(?:add|configure|fix|update|set|enable|install|renew)"
        r".{0,80}"
        r"\b(?:security headers|missing headers|https|ssl|tls|"
        r"certificate)\b"
        r".{0,80}"
        r"\b(?:website|site|server)\b",

        r"\b(?:website|site|server)\s+"
        r"(?:administrator|owner|admin|operator|webmaster)\b"
        r".{0,100}"
        r"\b(?:should|must|need to)\b"
    ]

    for pattern in owner_action_patterns:

        if re.search(
            pattern,
            recommendation_lower,
            flags=re.IGNORECASE
        ):

            raise ValueError(
                "AI recommendation appears to give "
                "website-owner remediation."
            )

    return True


# ==========================================================
# Public Guard
# ==========================================================

def guard_popup_output(
    data,
    popup
):
    """
    Validate AI-generated popup content against the
    completed UIDetect security assessment.

    IMPORTANT:
    This function NEVER generates replacement content.

    If the AI response conflicts with the assessment,
    this function raises ValueError so the caller can
    treat the AI attempt as unsuccessful and retry.

    A successful AI response is returned unchanged.
    """

    # ======================================================
    # Input Validation
    # ======================================================

    if not isinstance(data, dict):
        raise ValueError(
            "Popup guard requires assessment data as a dictionary."
        )

    if not isinstance(popup, dict):
        raise ValueError(
            "Popup guard requires AI popup as a dictionary."
        )

    # ======================================================
    # Required AI Fields
    # ======================================================

    required_fields = {
        "aboutWebsite",
        "warning",
        "recommendation"
    }

    if set(popup.keys()) != required_fields:
        raise ValueError(
            "AI popup must contain exactly "
            "aboutWebsite, warning, and recommendation."
        )

    # ======================================================
    # Validate Field Values
    # ======================================================

    for field in required_fields:

        value = popup.get(field)

        if not isinstance(value, str):
            raise ValueError(
                f"AI popup field '{field}' must be a string."
            )

        if not value.strip():
            raise ValueError(
                f"AI popup field '{field}' cannot be empty."
            )

    # ======================================================
    # Basic Values
    # ======================================================

    interaction = _get_interaction(
        data
    )

    url = data.get(
        "url",
        data.get(
            "website",
            ""
        )
    )

    try:
        parsed_url = urlparse(
            url
            if "://" in url
            else f"https://{url}"
        )

        domain = parsed_url.netloc or "Unknown"

    except Exception:
        domain = "Unknown"

    about_website = popup[
        "aboutWebsite"
    ]

    warning = popup[
        "warning"
    ]

    recommendation = popup[
        "recommendation"
    ]


    # ======================================================
    # AI SECURITY SCORE CONSISTENCY VALIDATION
    # ======================================================
    #
    # The security score comes from UIDetect's backend
    # assessment. The AI must never invent a different score.
    #
    # ======================================================

    authoritative_score = data.get(
        "score"
    )

    if isinstance(
        authoritative_score,
        (int, float)
    ):

        all_ai_text = " ".join(
            [
                about_website,
                warning,
                recommendation
            ]
        )

        score_matches = re.findall(
            r"\b(\d{1,3})\s*/\s*100\b",
            all_ai_text
        )

        for score_text in score_matches:

            ai_score = int(
                score_text
            )

            if ai_score != int(
                authoritative_score
            ):

                raise ValueError(
                    f"AI generated incorrect security score: "
                    f"{ai_score}/100. "
                    f"Authoritative score is "
                    f"{int(authoritative_score)}/100."
                )

    # ======================================================
    # Placeholder Validation
    # ======================================================
    #
    # AI must never return unresolved placeholders.
    #
    # ======================================================

    placeholder_terms = [
        "[domain]",
        "[website]",
        "[url]",
        "{domain}",
        "{website}",
        "{url}"
    ]

    combined_popup_text = " ".join(
        [
            about_website,
            warning,
            recommendation
        ]
    )

    # ======================================================
    # User-facing score / security-level validation
    # ======================================================
    #
    # The model receives score and security level as evidence, but
    # these belong in Security Details rather than the three main
    # user-facing AI sections. Reject explicit score/level output so
    # the retry loop can regenerate a cleaner explanation.
    # ======================================================

    score_forbidden_patterns = [
        r"\bscore\s*(?:is|of|:)?\s*\d{1,3}\b",
        r"\b\d{1,3}\s*(?:out of|/)\s*100\b"
    ]

    for pattern in score_forbidden_patterns:
        if re.search(pattern, combined_popup_text, flags=re.IGNORECASE):
            raise ValueError(
                "AI popup exposes the security score, which belongs "
                "in Security Details."
            )

    security_level_terms = [
        "security level",
        "risk level",
        "overall score"
    ]

    if _contains_any(combined_popup_text, security_level_terms):
        raise ValueError(
            "AI popup exposes an internal security-level/score detail."
        )

    if _contains_any(
        combined_popup_text,
        placeholder_terms
    ):

        raise ValueError(
            "AI popup contains an unresolved placeholder."
        )


    # ======================================================
    # HTTPS FACTUAL CONSISTENCY VALIDATION
    # ======================================================

    https_result = data.get("https", None)

    combined_https_text = " ".join([warning, recommendation])

    if https_result is True:
        https_negative_terms = [
            "does not use https",
            "doesn't use https",
            "not use https",
            "https is not enabled",
            "https is disabled",
            "without https",
            "no https",
            "not protected by https",
            "not protected by an https",
            "insecure https connection",
            "insecure connection"
        ]

        if _contains_unqualified_claim(combined_https_text, https_negative_terms):
            raise ValueError(
                "AI warning contradicts the confirmed HTTPS status."
            )

    elif https_result is False:
        https_positive_terms = [
            "this website uses https",
            "the website uses https",
            "website uses https",
            "this site uses https",
            "the site uses https",
            "https is enabled",
            "https enabled",
            "https is active",
            "https enabled on this website",
            "secure https connection",
            "https-secured"
        ]

        if _contains_unqualified_claim(combined_https_text, https_positive_terms):
            raise ValueError(
                "AI warning contradicts the confirmed missing HTTPS status."
            )


    # ==========================================================
    # SECURITY HEADER COMPLETENESS CONSISTENCY
    # ==========================================================

    security_headers = data.get(
        "securityHeaders",
        {}
    )

    if not isinstance(security_headers, dict):
        security_headers = {}


    header_values = [
        security_headers.get("strict-transport-security"),
        security_headers.get("content-security-policy"),
        security_headers.get("x-frame-options"),
        security_headers.get("x-content-type-options"),
        security_headers.get("referrer-policy")
    ]


    all_headers_present = (
        len(header_values) == 5
        and all(value is True for value in header_values)
    )


    if all_headers_present:

        header_unknown_terms = [
            "security headers are unknown",
            "security headers is unknown",
            "security header status is unknown",
            "status of the security headers is unknown",
            "security headers are unavailable",
            "security header status is unavailable",
            "security headers could not be determined",
            "security headers cannot be determined",
            "unknown security headers"
        ]

        if _contains_any(warning, header_unknown_terms):
            raise ValueError(
                "AI warning contradicts the confirmed "
                "security header status."
            )

        if _contains_any(recommendation, header_unknown_terms):
            raise ValueError(
                "AI recommendation contradicts the confirmed "
                "security header status."
            )

    # ==========================================================
    # SECURITY HEADER COUNT / NAME VALIDATION
    # ==========================================================

    authoritative_missing_headers = (
        _get_missing_security_headers(data)
    )

    combined_header_text = " ".join(
        [
            about_website,
            warning,
            recommendation
        ]
    )

    # ----------------------------------------------------------
    # Validate numeric missing-header claims
    # ----------------------------------------------------------

    header_count_matches = re.findall(
        r"\b(\d+)\s+(?:monitored\s+)?security\s+headers?\b",
        combined_header_text,
        flags=re.IGNORECASE
    )

    authoritative_missing_count = len(
        authoritative_missing_headers
    )

    for count_text in header_count_matches:

        ai_count = int(count_text)

        if ai_count != authoritative_missing_count:

            raise ValueError(
                "AI generated an incorrect security header "
                f"count: {ai_count}. "
                f"Authoritative missing header count is "
                f"{authoritative_missing_count}."
            )

    # ----------------------------------------------------------
    # Validate explicitly named headers
    # ----------------------------------------------------------

    header_name_aliases = {
        "strict-transport-security":
            "Strict-Transport-Security",

        "content-security-policy":
            "Content-Security-Policy",

        "x-frame-options":
            "X-Frame-Options",

        "x-content-type-options":
            "X-Content-Type-Options",

        "referrer-policy":
            "Referrer-Policy"
    }

    # ----------------------------------------------------------
    # Phrases that indicate an explicitly missing header
    # ----------------------------------------------------------

    missing_header_phrases = [
        "missing",
        "not present",
        "not set",
        "not configured",
        "absent",
        "disabled",
        "lacks",
        "without"
    ]

    # ----------------------------------------------------------
    # Check only explicit missing-header claims
    # ----------------------------------------------------------

    header_text = _normalise(
        combined_header_text
    )

    for alias, canonical_name in header_name_aliases.items():

        if alias not in header_text:
            continue

        explicitly_missing = any(
            re.search(
                rf"{re.escape(phrase)}.{{0,40}}{re.escape(alias)}",
                header_text
            )
            or
            re.search(
                rf"{re.escape(alias)}.{{0,40}}{re.escape(phrase)}",
                header_text
            )
            for phrase in missing_header_phrases
        )

        if (
            explicitly_missing
            and canonical_name not in authoritative_missing_headers
        ):

            raise ValueError(
                "AI identified "
                f"{canonical_name} as missing, but the "
                "authoritative assessment does not mark it "
                "as missing."
            )

    # ----------------------------------------------------------
    # Validate generic "nothing is missing" claims
    # ----------------------------------------------------------
    #
    # The checks above only fire when the AI names a specific
    # header (e.g. "X-Frame-Options is missing") or states a
    # digit (e.g. "2 security headers"). A generic denial like
    # "No monitored security headers are missing." names no
    # header and contains no digit, so it silently passed both
    # checks even while directly contradicting a non-empty
    # authoritative_missing_headers list.
    # ----------------------------------------------------------

    no_headers_missing_phrases = [
        "no monitored security header",
        "no security header",
        "none of the monitored security header",
        "none of the security header",
        "no headers are missing",
        "no header is missing",
        "all monitored security headers are present",
        "all security headers are present",
        "all of the monitored security headers are present"
    ]

    if (
        authoritative_missing_count > 0
        and _contains_any(
            combined_header_text,
            no_headers_missing_phrases
        )
    ):

        raise ValueError(
            "AI claimed no monitored security headers are "
            "missing, but the authoritative assessment marks "
            f"{authoritative_missing_count} header(s) as missing: "
            f"{', '.join(authoritative_missing_headers)}."
        )


    # ======================================================
    # Final Posture / Primary Finding
    # ======================================================

    final_posture = data.get(
        "finalPosture",
        {}
    )

    if not isinstance(
        final_posture,
        dict
    ):
        final_posture = {}

    overall_status = _normalise(
        final_posture.get(
            "overallStatus",
            ""
        )
    )

    primary_finding = final_posture.get(
        "primaryFinding",
        None
    )


    # ======================================================
    # Primary Finding Warning Validation
    # ======================================================

    if isinstance(
        primary_finding,
        dict
    ):

        if not _warning_matches_primary_finding(
            warning,
            primary_finding
        ):

            raise ValueError(
                "AI warning does not reflect the "
                "authoritative primary finding."
            )


    # ======================================================
    # Safe Posture Validation
    # ======================================================

    if (
        overall_status == "safe"
        and not _has_confirmed_primary_finding(primary_finding)
    ):

        significant_negative_terms = [
            "does not use https",
            "doesn't use https",
            "not protected by https",
            "insecure connection",
            "security vulnerability",
            "security vulnerabilities",
            "malware",
            "phishing",
            "malicious",
            "compromised",
            "unsafe",
            "dangerous",
            "high risk",
            "critical risk",
            "significant security weakness"
        ]

        if _contains_any(
            warning,
            significant_negative_terms
        ):

            raise ValueError(
                "AI warning contradicts the safe final security posture."
            )

        if _contains_any(
            recommendation,
            significant_negative_terms
        ):

            raise ValueError(
                "AI recommendation contradicts the safe final security posture."
            )

    # ======================================================
    # Safety Claim Validation
    # ======================================================

    combined_text = " ".join(
        [
            about_website,
            warning,
            recommendation
        ]
    )

    if _contains_unsafe_safety_claim(
        combined_text
    ):

        raise ValueError(
            "AI popup contains an unsafe or "
            "overly certain safety claim."
        )

    # ======================================================
    # Recommendation Interaction Validation
    # ======================================================

    if not _recommendation_matches_interaction(
        recommendation,
        interaction
    ):

        raise ValueError(
            "AI recommendation does not match "
            f"the detected interaction: {interaction}."
        )


    # ======================================================
    # WEBSITE-OWNER REMEDIATION VALIDATION
    # ======================================================
    #
    # The recommendation is written for the current browser
    # user, not the website owner.
    #
    # Reject recommendations that instruct the visitor to
    # modify, configure, repair, or maintain the website.
    # ======================================================

    _validate_user_facing_recommendation(
        recommendation
    )

    # ======================================================
    # Warning Interaction Validation
    # ======================================================

    if not _warning_matches_interaction(
        warning,
        interaction
    ):

        raise ValueError(
            "AI warning introduces an interaction "
            f"that does not match: {interaction}."
        )

    # ======================================================
    # OpenPhish Validation
    # ======================================================

    if _get_openphish_listed(data):

        phishing_terms = [
            "openphish",
            "phishing",
            "listed",
            "do not continue",
            "don't continue",
            "avoid",
            "do not enter",
            "don't enter",
            "do not download",
            "don't download",
            "do not upload",
            "don't upload",
            "do not create",
            "don't create"
        ]

        if not _contains_any(
            warning + " " + recommendation,
            phishing_terms
        ):

            raise ValueError(
                "AI popup does not adequately reflect "
                "the confirmed OpenPhish listing."
            )

    # ======================================================
    # VirusTotal Malicious Validation
    # ======================================================

    if _get_virustotal_malicious(data) > 0:

        malicious_terms = [
            "malicious",
            "avoid",
            "do not continue",
            "don't continue",
            "do not enter",
            "don't enter",
            "do not download",
            "don't download",
            "do not upload",
            "don't upload",
            "do not create",
            "don't create"
        ]

        if not _contains_any(
            warning + " " + recommendation,
            malicious_terms
        ):

            raise ValueError(
                "AI popup does not adequately reflect "
                "the VirusTotal malicious detections."
            )

    # ======================================================
    # Google Safe Browsing Validation
    # ======================================================

    if _get_safe_browsing(data) in {
        "unsafe",
        "malicious",
        "phishing",
        "flagged"
    }:

        safe_browsing_terms = [
            "safe browsing",
            "security concern",
            "unsafe",
            "avoid",
            "do not continue",
            "don't continue"
        ]

        if not _contains_any(
            warning + " " + recommendation,
            safe_browsing_terms
        ):

            raise ValueError(
                "AI popup does not adequately reflect "
                "the Google Safe Browsing result."
            )

    # ======================================================
    # High / Critical Context Risk Validation
    # ======================================================

    context_risk = _get_context_risk(
        data
    )

    if context_risk in {
        "high",
        "critical"
    }:

        final_posture = data.get(
            "finalPosture",
            {}
        )

        if not isinstance(
            final_posture,
            dict
        ):
            final_posture = {}

        primary_finding = final_posture.get(
            "primaryFinding",
            {}
        )

        if not isinstance(
            primary_finding,
            dict
        ):
            primary_finding = {}

        primary_source = _normalise(
            primary_finding.get(
                "source",
                ""
            )
        )

        primary_category = _normalise(
            primary_finding.get(
                "category",
                ""
            )
        )

        primary_message = _normalise(
            primary_finding.get(
                "message",
                ""
            )
        )

        recommendation_text = _normalise(
            recommendation
        )

        # --------------------------------------------------
        # Validate against the confirmed primary finding
        # --------------------------------------------------

        if primary_source == "https":

            technical_terms = [
                "https",
                "secure connection",
                "encrypted connection",
                "http connection"
            ]

            action_terms = [
                "caution",
                "careful",
                "carefully",
                "avoid sensitive information",
                "avoid entering sensitive information",
                "avoid sensitive data",
                "avoid entering sensitive data"
            ]

            recommendation_has_technical_reference = _contains_any(
                recommendation_text,
                technical_terms
            )

            recommendation_has_action_reference = _contains_any(
                recommendation_text,
                action_terms
            )

            if not (
                recommendation_has_technical_reference
                or recommendation_has_action_reference
            ):

                raise ValueError(
                    "AI recommendation does not reflect "
                    "the confirmed HTTPS finding or the required "
                    "cautious action."
                )

        elif primary_source == "ssl/tls":

            if not _contains_any(
                recommendation_text,
                [
                    "ssl",
                    "tls",
                    "certificate",
                    "secure connection"
                ]
            ):

                raise ValueError(
                    "AI recommendation does not reflect "
                    "the confirmed SSL/TLS finding."
                )

        elif primary_category:

            category_words = [
                word
                for word in primary_category.split()
                if len(word) >= 5
            ]

            if category_words and not any(
                word in recommendation_text
                for word in category_words
            ):

                raise ValueError(
                    "AI recommendation does not reflect "
                    "the confirmed primary finding."
                )

        elif primary_message:

            message_words = [
                word
                for word in primary_message.split()
                if len(word) >= 5
            ]

            if message_words and not any(
                word in recommendation_text
                for word in message_words
            ):

                raise ValueError(
                    "AI recommendation does not reflect "
                    "the confirmed primary finding."
                )


    # ======================================================
    # Medium Context Risk Validation
    # ======================================================

    if context_risk == "medium":

        medium_forbidden = [
            "completely safe",
            "guaranteed safe",
            "definitely safe",
            "safe to continue",
            "no security concerns",
            "everything is safe"
        ]

        if _contains_any(
            combined_text,
            medium_forbidden
        ):

            raise ValueError(
                "AI popup incorrectly describes a "
                "medium-risk assessment as completely safe."
            )

    # ======================================================
    # Unknown Context Risk Validation
    # ======================================================

    if context_risk in {
        "unknown",
        "unavailable"
    }:

        unknown_forbidden = [
            "completely safe",
            "guaranteed safe",
            "definitely safe",
            "safe to visit",
            "safe to continue"
        ]

        if _contains_any(
            combined_text,
            unknown_forbidden
        ):

            raise ValueError(
                "AI popup incorrectly claims safety while "
                "context risk is unknown or unavailable."
            )

    # ======================================================
    # RECOMMENDATION ACTION TONE VALIDATION
    # ======================================================
    #
    # This is a safety net for the authoritative. Even if
    # the model ignores that instruction, this check catches an
    # obvious tone mismatch between the recommendation text and
    # the authoritative recommendationAction.
    # ======================================================

    recommendation_action = _get_recommendation_action(data)

    block_language = [
        "stop browsing",
        "stop using this",
        "do not continue",
        "don't continue",
        "do not proceed",
        "don't proceed",
        "leave this site",
        "leave this website",
        "close this page",
        "close this tab"
    ]

    permissive_language = [
        "continue normally",
        "browsing normally",
        "browse normally",
        "no action is required",
        "no additional action is required",
        "no further action is needed"
    ]

    if recommendation_action == "block":

        if _contains_unqualified_claim(
            recommendation,
            permissive_language
        ):

            raise ValueError(
                "AI recommendation uses permissive language "
                "('continue normally' / 'no action required') "
                "while the authoritative recommendationAction "
                "is BLOCK."
            )

    elif recommendation_action in {
        "caution",
        "normal",
        "normal_caution"
    }:

        if _contains_unqualified_claim(
            recommendation,
            block_language
        ):

            raise ValueError(
                "AI recommendation uses BLOCK-level language "
                f"while the authoritative recommendationAction "
                f"is {recommendation_action.upper()}."
            )

    # ======================================================
    # IMPORTANT
    #
    # Do NOT modify:
    # - aboutWebsite
    # - warning
    # - recommendation
    #
    # The AI response has passed the guard.
    # Return it unchanged.
    # ======================================================

    log_info(
        "AI popup passed security consistency guard."
    )

    return popup



# ==========================================================
# Generate UIDetect Security AI Assessment (NEW IMPLEMENTED)
# ==========================================================

def generate_security_ai(assessment_data):
    """
    Generate the canonical UIDetect AI security assessment.

    This function is the single AI generation path for:
        - BROWSE
        - LOGIN
        - REGISTER
        - UPLOAD
        - DOWNLOAD
        - RIGHT_CLICK

    Parameters
    ----------
    assessment_data : dict
        Complete security assessment data produced by scanner.py.

    Returns
    -------
    dict
        Successful response:

        {
            "success": True,
            "aboutWebsite": "...",
            "warning": "...",
            "recommendation": "..."
        }

        Failed response:

        {
            "success": False,
            "error": "All Security AI attempts failed."
        }
    """

    # ======================================================
    # 1. Validate input
    # ======================================================

    if not isinstance(assessment_data, dict):
        log_error(
            "Security AI generation failed: "
            "assessment_data must be a dictionary."
        )

        return {
            "success": False,
            "error": "Invalid assessment data."
        }

    # ======================================================
    # 2. Build the unified AI prompt
    # ======================================================

    try:
        prompt = build_warning_prompt(assessment_data)

    except Exception as error:
        log_error(
            "Security AI prompt generation failed: "
            f"{error}"
        )

        return {
            "success": False,
            "error": "Failed to build Security AI prompt."
        }

    # ======================================================
    # 3. Retry AI generation
    # ======================================================

    last_error = None
    last_failed_popup = None

    for attempt in range(1, MAX_ATTEMPTS + 1):

        try:

            log_info(
                f"Security AI generation attempt "
                f"{attempt}/{MAX_ATTEMPTS}"
            )

            # ==================================================
            # 3.1 Build correction feedback from the previous
            #     rejected attempt (if any).
            #
            # Retries previously repeated the exact same prompt
            # (only the sampling seed changed), so the model had
            # no way to know WHY it was rejected and could easily
            # repeat the same mistake. Feeding back the specific
            # guard failure turns this into a real self-correction
            # loop instead of a blind re-roll.
            # ==================================================

            if last_error and last_failed_popup:

                correction_notice = f"""
==================================================
CORRECTION REQUIRED
==================================================

The previous AI output was rejected by the UIDetect
security consistency guard.

Previous output:

{json.dumps(last_failed_popup)}

Rejection reason:

{last_error}

IMPORTANT:

The backend assessment remains authoritative.

Do not change any backend value.

Fix ONLY the specific problem identified by the rejection.

Re-read the CURRENT ASSESSMENT and the relevant field rule
before generating the corrected output.

Recommendation Action values such as:

NORMAL
NORMAL_CAUTION
CAUTION
BLOCK

are INTERNAL backend decision values.

They are NEVER valid final recommendation text.

The recommendation must convert the authoritative action
into natural-language user guidance.

Return ONLY the corrected JSON object with:

aboutWebsite
warning
recommendation
"""

            else:

                correction_notice = ""

            popup = None

            # ==================================================
            # 4. Send request to Ollama
            # ==================================================

            response = chat(
                model=MODEL,

                format={
                    "type": "object",
                    "properties": {
                        "aboutWebsite": {
                            "type": "string"
                        },
                        "warning": {
                            "type": "string"
                        },
                        "recommendation": {
                            "type": "string"
                        }
                    },
                    "required": [
                        "aboutWebsite",
                        "warning",
                        "recommendation"
                    ],
                    "additionalProperties": False
                },

                # ==================================================
                # Sampling options
                # ==================================================
                #
                # IMPORTANT:
                # Without explicit sampling options, small models
                # (e.g. qwen2.5:3b) tend to collapse onto the same
                # boilerplate completion whenever two assessments
                # look broadly similar (e.g. "safe, some headers
                # missing"). A random seed per attempt plus a
                # moderate temperature keeps wording varied and
                # tied to the specific assessment, while retries
                # naturally get a fresh seed instead of repeating
                # the same generation.
                # ==================================================

                options={
                    "temperature": 0.3,
                    "top_p": 0.9,
                    "seed": int(time.time() * 1000) % 2_147_483_647
                },

                messages=[
                    {
                        "role": "system",
                        "content": """
You are UIDetect Security AI.

Convert the CURRENT UIDetect backend assessment into exactly
three user-facing fields:

aboutWebsite
warning
recommendation

The CURRENT backend assessment is authoritative.

Do not invent, change, or reinterpret backend security facts.

Do not perform an independent security assessment.

If Primary Finding is None, do not invent a security finding.

If Primary Finding is confirmed, the warning must describe
that actual finding.

Recommendation must follow Recommendation Action and
Recommendation Reason.

Translate technical backend information into clear,
concise, user-friendly language.

Do not expose internal backend implementation details.

Return only the requested JSON object.

"""


            },
                    {
                        "role": "user",
                        "content": (
                            prompt + correction_notice
                            if correction_notice
                            else prompt
                        )
                    }
                ]
            )

            # ==================================================
            # 5. Extract Ollama response
            # ==================================================

            popup_text = extract_ollama_content(response)


            # ==================================================
            # 6. Validate AI JSON response
            # ==================================================

            popup = validate_popup_response(
                popup_text
            )


            # ======================================================
            # 6.1 aboutWebsite processing
            # ======================================================
            #
            # aboutWebsite now answers "What Did UIDetect Find?".
            # Do not prepend or rewrite website identity here; the
            # backend facts have already been supplied to Qwen and
            # the consistency guard validates the generated content.
            #
            # This intentionally preserves the AI wording so that
            # aboutWebsite remains a finding summary rather than a
            # forced "You're visiting ..." sentence.
            # ======================================================

            log_info(
                f"AI generated aboutWebsite: "
                f"{popup.get('aboutWebsite')}"
            )

            log_info(
                f"AI generated warning: "
                f"{popup.get('warning')}"
            )

            log_info(
                f"AI generated recommendation: "
                f"{popup.get('recommendation')}"
            )

            # ==================================================
            # 7. Guard AI output against unsafe/inconsistent
            #    claims
            # ==================================================

            popup = guard_popup_output(
                assessment_data,
                popup
            )

            # ==================================================
            # 8. Format final AI output
            # ==================================================

            popup = format_popup(
                popup
            )

            # ==================================================
            # 9. Verify required fields after processing
            # ==================================================

            if not isinstance(popup, dict):
                raise ValueError(
                    "Formatted AI response is not a dictionary."
                )

            about_website = popup.get(
                "aboutWebsite"
            )

            warning = popup.get(
                "warning"
            )

            recommendation = popup.get(
                "recommendation"
            )

            if not isinstance(
                about_website,
                str
            ) or not about_website.strip():

                raise ValueError(
                    "AI aboutWebsite is empty or invalid."
                )

            if not isinstance(
                warning,
                str
            ) or not warning.strip():

                raise ValueError(
                    "AI warning is empty or invalid."
                )

            if not isinstance(
                recommendation,
                str
            ) or not recommendation.strip():

                raise ValueError(
                    "AI recommendation is empty or invalid."
                )

            # ==================================================
            # 10. Return canonical AI result
            # ==================================================

            log_info(
                "Security AI generation successful."
            )

            return {
                "success": True,
                "aboutWebsite": about_website,
                "warning": warning,
                "recommendation": recommendation
            }

        except Exception as error:

            last_error = str(error)

            last_failed_popup = (
                popup if isinstance(popup, dict) else None
            )

            log_warning(
                f"Security AI attempt "
                f"{attempt}/{MAX_ATTEMPTS} failed: "
                f"{error}"
            )

            log_error(
                f"Security AI attempt "
                f"{attempt}/{MAX_ATTEMPTS} exception type: "
                f"{type(error).__name__}"
            )

            # ==================================================
            # Retry if attempts remain
            # ==================================================

            if attempt < MAX_ATTEMPTS:

                time.sleep(
                    RETRY_DELAY
                )

    # ======================================================
    # 11. All attempts failed
    # ======================================================

    log_error(
        "All Security AI attempts failed."
    )

    # ======================================================
    # 12. Deterministic fallback
    # ======================================================
    #
    # Free-text generation (and the guard above) has now failed
    # MAX_ATTEMPTS times. Rather than surfacing a bare failure
    # (which previously left aboutWebsite/warning/recommendation
    # as None all the way to the popup), fall back to the
    # structured-claims pipeline in warning_ai_structured.py.
    #
    # That pipeline builds its three fields from pre-authored
    # phrasing keyed directly off the same authoritative
    # finalPosture/recommendationAction this function received --
    # it cannot hallucinate a claim and cannot overshoot the
    # CAUTION/BLOCK tone, because there is no free text for the
    # tone guard above to reject in the first place. It also
    # degrades gracefully on its own (falls back to variant 0)
    # if even its own small AI call fails, so this is safe even
    # when the local model is completely unavailable.
    #
    # Imported here (not at module load time) to avoid a circular
    # import, since warning_ai_structured imports
    # extract_ollama_content from this module.
    # ======================================================

    try:

        from modules.warning_ai_structured import (
            generate_security_ai_structured,
        )

        fallback_popup = generate_security_ai_structured(
            assessment_data
        )

        if fallback_popup.get("success") is True:

            # ==================================================
            # Validate structured fallback using the SAME
            # security consistency guard.
            #
            # The fallback must not bypass the final validation
            # rules applied to Qwen output.
            # ==================================================

            fallback_content = {
                "aboutWebsite": fallback_popup.get(
                    "aboutWebsite"
                ),
                "warning": fallback_popup.get(
                    "warning"
                ),
                "recommendation": fallback_popup.get(
                    "recommendation"
                )
            }

            try:

                validated_fallback = guard_popup_output(
                    assessment_data,
                    fallback_content
                )

            except Exception as fallback_guard_error:

                log_error(
                    "Structured-claims fallback failed "
                    "security consistency validation: "
                    f"{fallback_guard_error}"
                )

                return {
                    "success": False,
                    "error": {
                        "code": "SECURITY_AI_FAILED",
                        "message": (
                            "All Security AI attempts and "
                            "fallback validation failed."
                        ),
                        "lastError": str(
                            fallback_guard_error
                        )
                    }
                }

            log_warning(
                "Security AI: all free-text attempts failed; "
                "structured-claims fallback passed the same "
                "security consistency guard."
            )

            return {
                "success": True,
                "aboutWebsite": validated_fallback[
                    "aboutWebsite"
                ],
                "warning": validated_fallback[
                    "warning"
                ],
                "recommendation": validated_fallback[
                    "recommendation"
                ],
                "fallback_used": True
            }

        log_error(
            "Structured-claims fallback also reported failure: "
            f"{fallback_popup.get('error')}"
        )

    except Exception as fallback_error:

        log_error(
            f"Structured-claims fallback raised an exception: "
            f"{fallback_error}"
        )

    return {
        "success": False,
        "error": {
            "code": "SECURITY_AI_FAILED",
            "message": "All Security AI attempts failed.",
            "lastError": last_error
        }
    }