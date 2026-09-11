/* =====================================================
UIDetect - Popup Script

Phase 16:
UI Enhancement

Phase 10:
Error Handling

===================================================== */


/* =====================================================
PHASE 10 - ERROR HANDLING
===================================================== */

const POPUP_ERROR_CODES =
{
    NO_ACTIVE_TAB:
        "NO_ACTIVE_TAB",

    NO_WEBSITE:
        "NO_WEBSITE",

    UNSUPPORTED_PAGE:
        "UNSUPPORTED_PAGE",

    MESSAGE_ERROR:
        "MESSAGE_ERROR",

    INVALID_RESPONSE:
        "INVALID_RESPONSE",

    STORAGE_ERROR:
        "STORAGE_ERROR",

    INVALID_ASSESSMENT:
        "INVALID_ASSESSMENT",

    UNKNOWN_ERROR:
        "UNKNOWN_ERROR"
};


/* =====================================================
Create User-Friendly Error Message
===================================================== */

function getUserErrorMessage(
    error,
    fallback =
        "Unable to complete the security scan."
)
{
    if(!error)
    {
        return fallback;
    }


    /*
    Backend standardized error object
    */

    if(
        typeof error === "object" &&
        error.message
    )
    {
        return error.message;
    }


    /*
    Error object
    */

    if(
        error instanceof Error &&
        error.message
    )
    {
        return error.message;
    }


    /*
    String error
    */

    if(
        typeof error === "string"
    )
    {
        return error;
    }


    return fallback;
}


/* =====================================================
Centralized Popup Error Logger
===================================================== */

function logPopupError(
    context,
    error
)
{
    console.error(
        "======================================"
    );

    console.error(
        "UIDetect Popup Error"
    );

    console.error(
        "Context:",
        context
    );

    console.error(
        "Error:",
        error
    );

    console.error(
        "======================================"
    );
}


/* =====================================================
Create Standard Popup Error
===================================================== */

function createPopupError(
    code,
    message,
    recoverable = true
)
{
    return {

        success:
            false,

        error:
        {
            code:
                code,

            message:
                message,

            recoverable:
                recoverable
        }

    };
}


/* =====================================================
Initialize UI
===================================================== */

function initializeUI()
{
    try
    {
        updateWebsite(
            "Loading..."
        );


        updateWebsiteURL(
            "Waiting..."
        );


        updateWebsiteStatus(
            "Waiting for Scan"
        );


        updateSecurityScore(
            "--"
        );


        updateSecurityLevel(
            "Waiting for Scan"
        );


        updateSecurityDetails(
            "--",
            "--",
            "--",
            "--"
        );


        updateSecurityHeaders({

            "strict-transport-security": false,

            "content-security-policy": false,

            "x-frame-options": false,

            "x-content-type-options": false,

            "referrer-policy": false

        });


        updateWhois({

            status:
                "Waiting...",

            registrar:
                "Waiting...",

            domainAge:
                "Waiting..."

        });


        /* =============================================
           Phase 11 - Initialize VirusTotal
        ============================================= */

        updateVirusTotal({

            status:
                "Waiting...",

            malicious: 0,

            suspicious: 0,

            harmless: 0,

            undetected: 0,

            timeout: 0,

            reputation: 0

        });


        /* =============================================
           Phase 15 - Initialize AI Reputation
        ============================================= */

        updateAIReputation({});


        updateRecommendation(
            "Waiting for AI recommendation..."
        );


        /* =============================================
           Phase 8 - Initialize Context
        ============================================= */

        updateContextAssessment({

            interaction:
                "None",

            risk:
                "Unknown",

            warning:
                "No warning",

            contextRecommendation:
                "No recommendation"

        });


        registerEventListeners();

        hideLoading();

        hideScanError();


        console.log(
            "Popup initialized."
        );

    }
    catch(error)
    {
        logPopupError(
            "initializeUI",
            error
        );

        showScanError(
            "UIDetect could not initialize the popup interface."
        );
    }
}


/* =====================================================
Register Events
===================================================== */

function registerEventListeners()
{
    try
    {
        const scanButton =
            document.getElementById(
                "scanButton"
            );


        if(scanButton)
        {
            scanButton.addEventListener(
                "click",
                scanButtonClicked
            );
        }
        else
        {
            console.warn(
                "Scan button was not found."
            );
        }

        const cancelScanButton =
            document.getElementById(
                "cancelScanButton"
            );


        if(cancelScanButton)
        {
            cancelScanButton.addEventListener(
                "click",
                () =>
                {
                    console.log(
                        "UIDetect: User cancelled scan."
                    );

                    cancelScanButton.disabled =
                        true;

                    chrome.runtime.sendMessage(
                        {
                            action:
                                "CANCEL_SCAN"
                        },
                        (response) =>
                        {
                            if(
                                chrome.runtime.lastError
                            )
                            {
                                console.warn(
                                    "Unable to cancel scan:",
                                    chrome.runtime.lastError.message
                                );

                                cancelScanButton.disabled =
                                    false;

                                return;
                            }

                            console.log(
                                "Cancel scan response:",
                                response
                            );
                        }
                    );
                }
            );
        }


    }
    catch(error)
    {
        logPopupError(
            "registerEventListeners",
            error
        );
    }

}


/* =====================================================
Update Website
===================================================== */

function updateWebsite(name)
{
    try
    {
        const element =
            document.getElementById(
                "website-name"
            );


        if(element)
        {
            element.textContent =
                name || "Unknown";
        }

    }
    catch(error)
    {
        logPopupError(
            "updateWebsite",
            error
        );
    }
}


/* =====================================================
Update Website URL
===================================================== */

function updateWebsiteURL(url)
{
    try
    {
        const element =
            document.getElementById(
                "website-url"
            );


        if(element)
        {
            element.textContent =
                url || "Unknown";
        }

    }
    catch(error)
    {
        logPopupError(
            "updateWebsiteURL",
            error
        );
    }
}


/* =====================================================
Update Website Status
===================================================== */

function updateWebsiteStatus(status)
{
    try
    {
        const element =
            document.getElementById(
                "website-status-badge"
            );


        if(!element)
        {
            return;
        }


        element.textContent =
            status || "Unknown";


        element.classList.remove(

            "status-neutral",

            "status-safe",

            "status-warning",

            "status-danger"

        );


        const normalized =
            String(status || "")
            .toLowerCase();


        if(
            normalized.includes("completed")
        )
        {
            element.classList.add(
                "status-safe"
            );
        }

        else if(
            normalized.includes("scan")
        )
        {
            element.classList.add(
                "status-warning"
            );
        }

        else if(
            normalized.includes("failed") ||
            normalized.includes("unsupported")
        )
        {
            element.classList.add(
                "status-danger"
            );
        }

        else
        {
            element.classList.add(
                "status-neutral"
            );
        }

    }
    catch(error)
    {
        logPopupError(
            "updateWebsiteStatus",
            error
        );
    }
}


/* =====================================================
Security Score
===================================================== */

function updateSecurityScore(score)
{
    try
    {
        const scoreElement =
            document.getElementById(
                "security-score"
            );


        const progressBar =
            document.getElementById(
                "security-score-bar"
            );


        if(scoreElement)
        {
            scoreElement.textContent =
                score !== undefined &&
                score !== null
                    ? score
                    : "--";
        }


        if(!progressBar)
        {
            return;
        }


        let numericScore =
            Number(score);


        if(
            isNaN(numericScore)
        )
        {
            numericScore = 0;
        }


        numericScore =
            Math.max(
                0,
                Math.min(
                    100,
                    numericScore
                )
            );


        progressBar.style.width =
            numericScore + "%";


        progressBar.classList.remove(

            "score-excellent",

            "score-good",

            "score-moderate",

            "score-poor",

            "score-unknown"

        );


        if(score === "--")
        {
            progressBar.classList.add(
                "score-unknown"
            );
        }

        else if(numericScore >= 90)
        {
            progressBar.classList.add(
                "score-excellent"
            );
        }

        else if(numericScore >= 80)
        {
            progressBar.classList.add(
                "score-good"
            );
        }

        else if(numericScore >= 60)
        {
            progressBar.classList.add(
                "score-moderate"
            );
        }

        else
        {
            progressBar.classList.add(
                "score-poor"
            );
        }

    }
    catch(error)
    {
        logPopupError(
            "updateSecurityScore",
            error
        );
    }
}


/* =====================================================
Security Level
===================================================== */

function updateSecurityLevel(level)
{
    try
    {
        const element =
            document.getElementById(
                "security-level-badge"
            );


        if(!element)
        {
            return;
        }


        element.textContent =
            level || "Waiting for Scan";


        element.classList.remove(

            "status-neutral",

            "status-safe",

            "status-good",

            "status-warning",

            "status-danger"

        );


        const normalized =
            String(level || "")
            .toLowerCase()
            .trim();

        
        /*
        Waiting for Scan
        */

        if(
            normalized === "waiting for scan"
        )
        {
            element.classList.add(
                "status-neutral"
            );
        }

        else if(
            normalized === "scanning..."
        )
        {
            element.classList.add(
                "status-warning"
            );
        }

        else if(
            normalized === "excellent"
        )
        {
            element.classList.add(
                "status-safe"
            );
        }

        else if(
            normalized === "good"
        )
        {
            element.classList.add(
                "status-good"
            );
        }

        else if(
            normalized === "moderate"
        )
        {
            element.classList.add(
                "status-warning"
            );
        }

        else if(
            normalized === "poor"
        )
        {
            element.classList.add(
                "status-danger"
            );
        }

        else
        {
            element.classList.add(
                "status-neutral"
            );
        }

    }
    catch(error)
    {
        logPopupError(
            "updateSecurityLevel",
            error
        );
    }
}


/* =====================================================
Security Details
===================================================== */

function updateSecurityDetails(
    https,
    safeBrowsing,
    ssl,
    tls
)
{
    try
    {
        updateStatusElement(
            "https-status",
            https
        );


        updateStatusElement(
            "safe-browsing-status",
            safeBrowsing
        );


        updateStatusElement(
            "ssl-status",
            ssl
        );


        updateStatusElement(
            "tlsVersion",
            tls
        );

    }
    catch(error)
    {
        logPopupError(
            "updateSecurityDetails",
            error
        );
    }
}


/* =====================================================
Generic Security Status
===================================================== */

function updateStatusElement(
    elementId,
    value
)
{
    try
    {
        const element =
            document.getElementById(
                elementId
            );


        if(!element)
        {
            return;
        }


        const text =
            value === undefined ||
            value === null
                ? "Unknown"
                : String(value);


        element.textContent =
            text;


        element.classList.remove(

            "present",

            "enabled",

            "valid",

            "safe",

            "missing",

            "disabled",

            "invalid",

            "unsafe",

            "malicious"

        );


        const normalized =
            text.toLowerCase();


        if(
            normalized === "enabled" ||
            normalized === "valid" ||
            normalized === "safe" ||
            normalized === "present" ||
            normalized === "established"
        )
        {
            element.classList.add(
                "safe"
            );
        }

        else if(
            normalized === "disabled" ||
            normalized === "invalid" ||
            normalized === "missing"
        )
        {
            element.classList.add(
                "missing"
            );
        }

        else if(
            normalized === "unsafe" ||
            normalized === "malicious"
        )
        {
            element.classList.add(
                "unsafe"
            );
        }

    }
    catch(error)
    {
        logPopupError(
            "updateStatusElement",
            error
        );
    }
}


/* =====================================================
Security Headers
===================================================== */

function updateSecurityHeaders(
    headers = {}
)
{
    try
    {
        if(
            !headers ||
            typeof headers !== "object"
        )
        {
            headers = {};
        }


        updateStatusElement(

            "hsts-status",

            headers[
                "strict-transport-security"
            ]
                ? "Present"
                : "Missing"

        );


        updateStatusElement(

            "csp-status",

            headers[
                "content-security-policy"
            ]
                ? "Present"
                : "Missing"

        );


        updateStatusElement(

            "xframe-status",

            headers[
                "x-frame-options"
            ]
                ? "Present"
                : "Missing"

        );


        updateStatusElement(

            "xcontent-status",

            headers[
                "x-content-type-options"
            ]
                ? "Present"
                : "Missing"

        );


        updateStatusElement(

            "referrer-status",

            headers[
                "referrer-policy"
            ]
                ? "Present"
                : "Missing"

        );

    }
    catch(error)
    {
        logPopupError(
            "updateSecurityHeaders",
            error
        );
    }
}


/* =====================================================
WHOIS Information
===================================================== */

function updateWhois(
    data = {}
)
{
    try
    {
        if(
            !data ||
            typeof data !== "object"
        )
        {
            data = {};
        }


        const statusElement =
            document.getElementById(
                "whois-status"
            );


        const registrarElement =
            document.getElementById(
                "registrar"
            );


        const ageElement =
            document.getElementById(
                "domain-age"
            );


        if(statusElement)
        {
            statusElement.textContent =
                data.status ||
                "Unknown";
        }


        if(registrarElement)
        {
            registrarElement.textContent =
                data.registrar ||
                "Unknown";
        }


        const age =
            data.domainAge;


        if(ageElement)
        {
            ageElement.textContent =

                (
                    age !== undefined &&
                    age !== null
                )

                    ?

                age + " years"

                    :

                "Unknown";
        }


        updateStatusElement(

            "whois-status",

            data.status ||
            "Unknown"

        );

    }
    catch(error)
    {
        logPopupError(
            "updateWhois",
            error
        );
    }
}


/* =====================================================
Phase 11 - VirusTotal
===================================================== */

function updateVirusTotal(
    data = {}
)
{
    try
    {
        console.log(
            "Updating VirusTotal UI:",
            data
        );


        if(
            !data ||
            typeof data !== "object"
        )
        {
            data = {};
        }


        const status =
            data.status ||
            "Unknown";


        const malicious =
            data.malicious ??
            0;


        const suspicious =
            data.suspicious ??
            0;


        const harmless =
            data.harmless ??
            0;


        const undetected =
            data.undetected ??
            0;


        const timeout =
            data.timeout ??
            0;


        const statusElement =
            document.getElementById(
                "virustotal-status"
            );


        if(statusElement)
        {
            statusElement.textContent =
                status;


            statusElement.classList.remove(

                "status-neutral",

                "status-safe",

                "status-warning",

                "status-danger",

                "virustotal-safe",

                "virustotal-suspicious",

                "virustotal-malicious",

                "virustotal-unknown"

            );


            const normalizedStatus =
                String(status)
                .toLowerCase();


            if(
                normalizedStatus === "safe"
            )
            {
                statusElement.classList.add(
                    "virustotal-safe"
                );
            }

            else if(
                normalizedStatus === "warning"
            )
            {
                statusElement.classList.add(
                    "virustotal-suspicious"
                );
            }

            else if(
                normalizedStatus === "unsafe"
            )
            {
                statusElement.classList.add(
                    "virustotal-malicious"
                );
            }

            else
            {
                statusElement.classList.add(
                    "virustotal-unknown"
                );
            }
        }


        updateElementText(
            "virustotal-malicious",
            malicious
        );


        updateElementText(
            "virustotal-suspicious",
            suspicious
        );


        updateElementText(
            "virustotal-harmless",
            harmless
        );


        updateElementText(
            "virustotal-undetected",
            undetected
        );


        updateElementText(
            "virustotal-timeout",
            timeout
        );


        let explanation =
            "VirusTotal assessment unavailable.";


        const normalizedStatus =
            String(status)
            .toLowerCase();


        if(
            normalizedStatus === "safe"
        )
        {
            if(
                malicious === 0 &&
                suspicious === 0
            )
            {
                explanation =
                    "VirusTotal did not report any " +
                    "malicious or suspicious detections. " +
                    harmless +
                    " security engines considered " +
                    "the website harmless. This does " +
                    "not guarantee complete safety.";
            }
            else
            {
                explanation =
                    "VirusTotal currently classifies " +
                    "the website as safe, although " +
                    "some engine results should still " +
                    "be reviewed.";
            }
        }

        else if(
            normalizedStatus === "warning"
        )
        {
            explanation =
                "Some VirusTotal security engines " +
                "considered the website suspicious. " +
                "Review the website carefully before " +
                "sharing sensitive information.";
        }

        else if(
            normalizedStatus === "unsafe"
        )
        {
            explanation =
                "VirusTotal detected malicious activity " +
                "associated with this website. " +
                "Avoid continuing and do not enter " +
                "sensitive information.";
        }


        const explanationElement =
            document.getElementById(
                "virustotal-explanation"
            );


        if(explanationElement)
        {
            explanationElement.textContent =
                explanation;
        }


        console.log(
            "VirusTotal UI updated successfully."
        );

    }
    catch(error)
    {
        logPopupError(
            "updateVirusTotal",
            error
        );
    }
}


/* =====================================================
Generic Text Update
===================================================== */

function updateElementText(
    elementId,
    value
)
{
    try
    {
        const element =
            document.getElementById(
                elementId
            );


        if(element)
        {
            element.textContent =
                value !== undefined &&
                value !== null
                    ? value
                    : "";
        }

    }
    catch(error)
    {
        logPopupError(
            "updateElementText",
            error
        );
    }
}


/* =====================================================
Phase 15
AI Reputation Analysis
===================================================== */

function updateAIReputation(
    data = {}
)
{
    try
    {
        console.log(
            "Updating AI Reputation UI:",
            data
        );


        if(
            !data ||
            typeof data !== "object"
        )
        {
            data = {};
        }


        const reputation =
            data.reputation ||
            "Waiting...";


        const risk =
            data.risk ||
            "Unknown";


        const reason =
            data.reason ||
            "Waiting for AI reputation analysis...";


        const recommendation =
            data.recommendation ||
            "Waiting for recommendation...";


        updateElementText(
            "ai-reputation",
            reputation
        );


        updateElementText(
            "ai-reputation-risk-text",
            risk
        );


        updateElementText(
            "ai-reputation-reason",
            reason
        );


        updateElementText(
            "ai-reputation-recommendation",
            recommendation
        );


        const riskBadge =
            document.getElementById(
                "ai-reputation-risk"
            );


        if(!riskBadge)
        {
            return;
        }


        riskBadge.textContent =
            risk;


        riskBadge.classList.remove(

            "status-neutral",

            "status-safe",

            "status-good",

            "status-warning",

            "status-danger"

        );


        const normalizedRisk =
            String(risk)
            .toLowerCase();


        if(
            normalizedRisk === "very low" ||
            normalizedRisk === "low"
        )
        {
            riskBadge.classList.add(
                "status-safe"
            );
        }

        else if(
            normalizedRisk === "medium"
        )
        {
            riskBadge.classList.add(
                "status-warning"
            );
        }

        else if(
            normalizedRisk === "high" ||
            normalizedRisk === "critical"
        )
        {
            riskBadge.classList.add(
                "status-danger"
            );
        }

        else
        {
            riskBadge.classList.add(
                "status-neutral"
            );
        }

    }
    catch(error)
    {
        logPopupError(
            "updateAIReputation",
            error
        );
    }
}


/* =====================================================
AI Recommendation
===================================================== */

function updateRecommendation(
    text
)
{
    try
    {
        const element =
            document.getElementById(
                "ai-recommendation"
            );


        if(element)
        {
            element.textContent =
                text ||
                "No recommendation available.";
        }

    }
    catch(error)
    {
        logPopupError(
            "updateRecommendation",
            error
        );
    }
}


/* =====================================================
Phase 8
Context Assessment
===================================================== */

function updateContextAssessment(
    result
)
{
    try
    {
        if(
            !result ||
            typeof result !== "object"
        )
        {
            return;
        }


        updateElementText(

            "interaction",

            result.interaction ||
            "None"

        );


        const riskElement =
            document.getElementById(
                "risk"
            );


        const riskTextElement =
            document.getElementById(
                "context-risk-text"
            );


        const risk =
            result.risk ||
            "Unknown";


        const normalizedRisk =
            String(risk)
            .toLowerCase()
            .replace(
                /\s+/g,
                "-"
            );


        if(riskElement)
        {
            riskElement.textContent =
                risk;


            riskElement.classList.remove(

                "risk-very-low",

                "risk-low",

                "risk-medium",

                "risk-high",

                "risk-critical",

                "risk-unknown",

                "status-neutral",

                "status-safe",

                "status-warning",

                "status-danger"

            );


            riskElement.classList.add(

                "risk-" +
                normalizedRisk

            );
        }


        if(riskTextElement)
        {
            riskTextElement.textContent =
                risk;
        }


        updateElementText(

            "warning",

            result.warning ||
            "No warning"

        );


        updateElementText(

            "contextRecommendation",

            result.recommendation   ||
            "No recommendation"

        );

    }
    catch(error)
    {
        logPopupError(
            "updateContextAssessment",
            error
        );
    }
}


/* =====================================================
Loading
===================================================== */

function showLoading()
{
    try
    {
        const loading =
            document.getElementById(
                "loading-spinner"
            );


        if(loading)
        {
            loading.style.display =
                "flex";
        }


        const button =
            document.getElementById(
                "scanButton"
            );


        if(button)
        {
            button.disabled =
                true;
        }

        const cancelScanButton =
            document.getElementById(
                "cancelScanButton"
            );


        if(cancelScanButton)
        {
            cancelScanButton.style.display =
                "block";

            cancelScanButton.disabled =
                false;
        }




        updateElementText(
            "scan-button-text",
            "Scanning..."
        );


        updateElementText(

            "scan-progress-text",

            "Running security checks"

        );

    }
    catch(error)
    {
        logPopupError(
            "showLoading",
            error
        );
    }
}


/* =====================================================
Hide Loading
===================================================== */

function hideLoading()
{
    try
    {
        const loading =
            document.getElementById(
                "loading-spinner"
            );


        if(loading)
        {
            loading.style.display =
                "none";
        }

        const cancelScanButton =
            document.getElementById(
                "cancelScanButton"
            );


        if(cancelScanButton)
        {
            cancelScanButton.style.display =
                "none";

            cancelScanButton.disabled =
                false;
        }

    }
    catch(error)
    {
        logPopupError(
            "hideLoading",
            error
        );
    }
}


/* =====================================================
Scan Error
===================================================== */

function showScanError(
    message
)
{
    try
    {
        const errorBox =
            document.getElementById(
                "scan-error"
            );


        const errorMessage =
            document.getElementById(
                "scan-error-message"
            );


        if(errorMessage)
        {
            errorMessage.textContent =
                message ||
                "An unexpected error occurred.";
        }


        if(errorBox)
        {
            errorBox.style.display =
                "block";
        }


    }
    catch(error)
    {
        logPopupError(
            "showScanError",
            error
        );
    }
}


/* =====================================================
Hide Scan Error
===================================================== */

function hideScanError()
{
    try
    {
        const errorBox =
            document.getElementById(
                "scan-error"
            );


        if(errorBox)
        {
            errorBox.style.display =
                "none";
        }

    }
    catch(error)
    {
        logPopupError(
            "hideScanError",
            error
        );
    }
}


/* =====================================================
Scan Button
===================================================== */

async function scanButtonClicked()
{
    console.log(
        "Scan started."
    );


    hideScanError();

    showLoading();


    updateWebsiteStatus(
        "Scanning..."
    );

    updateSecurityLevel(
        "Scanning..."
    );


    try
    {
        /* =============================================
           Get Active Tab
        ============================================= */

        let tabs;

        try
        {
            tabs =
                await chrome.tabs.query({

                    active:
                        true,

                    currentWindow:
                        true

                });
        }
        catch(error)
        {
            logPopupError(
                "chrome.tabs.query",
                error
            );

            throw createPopupError(

                POPUP_ERROR_CODES.NO_ACTIVE_TAB,

                "Unable to access the active browser tab.",

                true

            );
        }


        const tab =
            tabs?.[0];


        /* =============================================
           Validate Active Tab
        ============================================= */

        if(
            !tab ||
            !tab.url
        )
        {
            throw createPopupError(

                POPUP_ERROR_CODES.NO_WEBSITE,

                "No website was found in the active tab.",

                false

            );
        }


        /* =============================================
           Validate Supported URL
        ============================================= */

        if(

            tab.url.startsWith(
                "chrome://"
            ) ||

            tab.url.startsWith(
                "edge://"
            ) ||

            tab.url.startsWith(
                "file://"
            ) ||

            tab.url.startsWith(
                "about:"
            ) ||

            tab.url.startsWith(
                "chrome-extension://"
            )

        )
        {
            throw createPopupError(

                POPUP_ERROR_CODES.UNSUPPORTED_PAGE,

                "This page cannot be scanned by UIDetect.",

                false

            );
        }


        /* =============================================
           Validate URL Format
        ============================================= */

        let url;

        try
        {
            url =
                new URL(
                    tab.url
                );
        }
        catch(error)
        {
            logPopupError(
                "URL validation",
                error
            );

            throw createPopupError(

                POPUP_ERROR_CODES.NO_WEBSITE,

                "The current page does not contain a valid website URL.",

                false

            );
        }


        updateWebsite(
            url.hostname
        );


        updateWebsiteURL(
            tab.url
        );


        /* =============================================
           Send Message To Background
        ============================================= */

        let response;

        try
        {
            response =
                await chrome.runtime.sendMessage({

                    action:
                        "SCAN_WEBSITE"

                });


            /*
            Chrome may expose messaging errors
            through runtime.lastError.
            */

            if(
                chrome.runtime.lastError
            )
            {
                throw new Error(
                    chrome.runtime.lastError.message
                );
            }

        }
        catch(error)
        {
            logPopupError(
                "chrome.runtime.sendMessage",
                error
            );

            throw createPopupError(

                POPUP_ERROR_CODES.MESSAGE_ERROR,

                "Unable to communicate with the UIDetect background service.",

                true

            );
        }


        console.log(
            "Scan response:",
            response
        );


        

        /* =============================================
           Validate Response
        ============================================= */

        if(
            !response ||
            typeof response !== "object"
        )
        {
            throw createPopupError(

                POPUP_ERROR_CODES.INVALID_RESPONSE,

                "UIDetect received an invalid response from the background service.",

                true

            );
        }

        if(
            response.cancelled === true
        )
        {
            console.log(
                "UIDetect scan cancelled by user."
            );

            updateWebsiteStatus(
                "Scan Cancelled"
            );

            updateRecommendation(
                "The security scan was cancelled."
            );

            return;
        }


        /* =============================================
           Backend / Background Error
        ============================================= */

        if(
            response.success === false
        )
        {
            const backendError =
                response.error;


            throw {

                success:
                    false,

                error:
                    backendError ||

                    {

                        code:
                            POPUP_ERROR_CODES.UNKNOWN_ERROR,

                        message:
                            "The security assessment could not be completed.",

                        recoverable:
                            true

                    }

            };
        }


        /* =============================================
           Validate Assessment
        ============================================= */

        const assessment =
            response.assessment;


        if(
            !assessment ||
            typeof assessment !== "object"
        )
        {
            throw createPopupError(

                POPUP_ERROR_CODES.INVALID_ASSESSMENT,

                "UIDetect received an incomplete security assessment.",

                true

            );
        }


        /* =============================================
           Update Popup
        ============================================= */

        updatePopup(
            assessment
        );


        console.log(
            "Scan completed successfully."
        );

    }
    catch(error)
    {
        logPopupError(
            "scanButtonClicked",
            error
        );


        updateWebsiteStatus(
            "Scan Failed"
        );


        const message =
            getUserErrorMessage(

                error,

                "Unable to scan this website. Please try again."

            );


        updateRecommendation(
            message
        );


        showScanError(
            message
        );

    }
    finally
    {
        hideLoading();


        const button =
            document.getElementById(
                "scanButton"
            );


        if(button)
        {
            button.disabled =
                false;
        }


        updateElementText(
            "scan-button-text",
            "Scan Website"
        );
    }
}


/* =====================================================
Update Popup Data
===================================================== */

function updatePopup(
    result
)
{
    try
    {
        console.log(
            "Popup Result:",
            result
        );


        /* =============================================
           Validate Result
        ============================================= */

        if(
            !result ||
            typeof result !== "object"
        )
        {
            throw new Error(
                "INVALID_ASSESSMENT"
            );
        }


        /* =============================================
           Validate URL
        ============================================= */

        let hostname =
            "Unknown";


        if(result.url)
        {
            try
            {
                hostname =
                    new URL(
                        result.url
                    ).hostname;
            }
            catch(error)
            {
                logPopupError(
                    "updatePopup URL",
                    error
                );

                hostname =
                    "Unknown";
            }
        }


        updateWebsite(
            hostname
        );


        updateWebsiteURL(
            result.url ||
            "Unknown"
        );


        updateWebsiteStatus(
            "Scan Completed"
        );


        updateSecurityScore(
            result.score
        );


        updateSecurityLevel(
            result.level
        );


        updateSecurityDetails(

            result.https
                ? "Enabled"
                : "Disabled",

            result.safeBrowsing ||
            "Unknown",

            (
                result.ssl &&
                result.ssl.sslValid
            )
                ? "Valid"
                : "Invalid",

            (
                result.ssl &&
                result.ssl.protocol
            ) ||
            "Unknown"

        );


        updateSecurityHeaders(
            result.securityHeaders ||
            {}
        );


        updateWhois(
            result.whois ||
            {}
        );


        /* =============================================
           Phase 11 - VirusTotal
        ============================================= */

        console.log(
            "========== POPUP VIRUSTOTAL =========="
        );


        console.log(
            result.virusTotal
        );


        console.log(
            "======================================="
        );


        updateVirusTotal(
            result.virusTotal ||
            {}
        );


        /* =============================================
           Phase 15 - AI Reputation
        ============================================= */

        updateAIReputation(

            result.reputationAnalysis ||

            result.aiReputation ||

            result.reputation ||

            result.phase15 ||

            {}

        );


        /* =============================================
           AI Recommendation
        ============================================= */

        updateRecommendation(

            result.recommendation   ||

            "No recommendation available."

        );


        /* =============================================
           Phase 8 - Context Assessment
        ============================================= */

        updateContextAssessment(
            result
        );


        console.log(
            "Popup UI updated successfully."
        );

    }
    catch(error)
    {
        logPopupError(
            "updatePopup",
            error
        );


        updateWebsiteStatus(
            "Scan Failed"
        );


        showScanError(
            "UIDetect received an invalid security assessment."
        );
    }
}


/* =====================================================
Load Right Click Scan Result
===================================================== */

document.addEventListener(

    "DOMContentLoaded",

    () =>
    {
        try
        {
            initializeUI();


            /* =========================================
               Read Storage
            ========================================= */

            chrome.storage.local.get(

                "rightClickResult",

                (data) =>
                {
                    try
                    {
                        /*
                        Check Chrome storage error.
                        */

                        if(
                            chrome.runtime.lastError
                        )
                        {
                            logPopupError(

                                "chrome.storage.local.get",

                                chrome.runtime.lastError.message

                            );


                            showScanError(
                                "Unable to load the previous scan result."
                            );


                            return;
                        }


                        console.log(
                            "Popup Data:",
                            data
                        );


                        if(
                            !data ||
                            !data.rightClickResult
                        )
                        {
                            console.log(
                                "No right-click result found."
                            );

                            return;
                        }


                        const result =
                            data.rightClickResult;


                        if(
                            typeof result !== "object"
                        )
                        {
                            logPopupError(
                                "Invalid right-click result",
                                result
                            );


                            showScanError(
                                "The saved scan result is invalid."
                            );


                            return;
                        }


                        updatePopup(
                            result
                        );


                        /* =================================
                           Remove Used Result
                        ================================= */

                        chrome.storage.local.remove(

                            "rightClickResult",

                            () =>
                            {
                                if(
                                    chrome.runtime.lastError
                                )
                                {
                                    logPopupError(

                                        "chrome.storage.local.remove",

                                        chrome.runtime.lastError.message

                                    );
                                }
                            }

                        );

                    }
                    catch(error)
                    {
                        logPopupError(
                            "Right-click storage callback",
                            error
                        );


                        showScanError(
                            "Unable to load the saved scan result."
                        );
                    }
                }

            );

        }
        catch(error)
        {
            logPopupError(
                "DOMContentLoaded",
                error
            );


            hideLoading();


            showScanError(
                "UIDetect could not initialize correctly."
            );
        }
    }

);