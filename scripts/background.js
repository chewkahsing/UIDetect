/* =====================================================
   UIDetect - Background Service Worker

   Responsibilities:
   - Coordinate website security scans
   - Send scan requests to the backend
   - Preserve backend security assessment results
   - Forward AI-generated aboutWebsite, warning,
     and recommendation to the UI
   - Handle scan cancellation
   - Handle security header detection
   - Handle right-click scans

===================================================== */


console.log("UIDetect BACKGROUND LOADED");

// =====================================================
// PHASE 10 - ERROR HANDLING
// Centralized Error Configuration
// =====================================================

const ERROR_CODES = {
    BACKEND_UNAVAILABLE: "BACKEND_UNAVAILABLE",
    BACKEND_TIMEOUT: "BACKEND_TIMEOUT",
    BACKEND_HTTP_ERROR: "BACKEND_HTTP_ERROR",
    INVALID_RESPONSE: "INVALID_RESPONSE",
    MESSAGE_ERROR: "MESSAGE_ERROR",
    NO_ACTIVE_TAB: "NO_ACTIVE_TAB",
    NO_WEBSITE: "NO_WEBSITE",
    UNKNOWN_ACTION: "UNKNOWN_ACTION",
    INJECTION_ERROR: "INJECTION_ERROR",
    UNKNOWN_ERROR: "UNKNOWN_ERROR"
};


// Backend configuration
const BACKEND_BASE_URL =
    "http://127.0.0.1:5000";


// Request timeout values
const BACKEND_TIMEOUT = 60000;
const SCAN_TIMEOUT = 60000;

// =====================================================
// Active Scan Cancellation
// =====================================================

let activeScanController = null;

let activeScanId = null;

let activeScanPromise = null;


// =====================================================
// Create Standard Error Object
// =====================================================

function createError(
    code,
    message,
    recoverable = true )
{
    return {
        success: false,

        error: {
            code: code,
            message: message,
            recoverable: recoverable
        }
    };
}


// =====================================================
// URL Validation
// =====================================================
function validateURL(url)
{
    if (!url)
    {
        return {
            valid: false,
            reason: "URL is empty"
        };
    }

    // =============================================
    // Browser / Extension / Local Pages
    // =============================================

    if (url.startsWith("chrome://"))
    {
        return {
            valid: false,
            reason: "Chrome internal pages cannot be scanned"
        };
    }

    if (url.startsWith("edge://"))
    {
        return {
            valid: false,
            reason: "Browser internal pages cannot be scanned"
        };
    }

    if (url.startsWith("chrome-extension://"))
    {
        return {
            valid: false,
            reason: "Extension pages cannot be scanned"
        };
    }

    if (url.startsWith("file://"))
    {
        return {
            valid: false,
            reason: "Local files cannot be scanned"
        };
    }

    // =============================================
    // Parse URL
    // =============================================

    let parsedURL;

    try
    {
        parsedURL =
            new URL(url);
    }
    catch
    {
        return {
            valid: false,
            reason: "Invalid URL format"
        };
    }

    // =============================================
    // HTTP / HTTPS Only
    // =============================================

    if (
        parsedURL.protocol !== "http:" &&
        parsedURL.protocol !== "https:"
    )
    {
        return {
            valid: false,
            reason: "Only HTTP/HTTPS websites can be scanned"
        };
    }

    return {
        valid: true,
        reason: "Valid URL"
    };
}


// =====================================================
// Fetch With Timeout
// =====================================================

async function fetchWithTimeout(
    url,
    options = {},
    timeout = BACKEND_TIMEOUT,
    externalController = null
)
{
    const controller =
        externalController ||
        new AbortController();

    let timedOut = false;

    const timeoutId =
        setTimeout(
            () =>
            {
                timedOut = true;

                controller.abort();
            },
            timeout
        );

    try
    {
        const response =
            await fetch(
                url,
                {
                    ...options,
                    signal:
                        controller.signal
                }
            );

        return response;
    }
    catch(error)
    {

        console.error(
            "UIDetect fetch error:",
            {
                name: error.name,
                message: error.message,
                url: url,
                timedOut: timedOut
            }
        );

        if(error.name === "AbortError")
        {
            if(timedOut)
            {
                throw new Error(
                    "REQUEST_TIMEOUT"
                );
            }

            throw new Error(
                "REQUEST_ABORTED"
            );
        }

        throw error;
    }
    finally
    {
        clearTimeout(timeoutId);
    }
}

// =====================================================
// Validate Backend Response
// =====================================================

async function parseBackendResponse(
    response
)
{
    if(!response.ok)
    {
        throw new Error(
            "HTTP_" + response.status
        );
    }

    let data;

    try
    {
        data = await response.json();
    }
    catch(error)
    {
        throw new Error(
            "INVALID_JSON_RESPONSE"
        );
    }

    if(!data || typeof data !== "object")
    {
        throw new Error(
            "INVALID_RESPONSE"
        );
    }

    return data;
}

// =====================================================
// Centralized Background Error Logger
// =====================================================

function logBackgroundError(
    context,
    error
)
{
    console.error(
        "======================================"
    );

    console.error(
        "UIDetect Background Error"
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
   Website Assessment Result
===================================================== */

let websiteResult =
{

    url:"",

    safeBrowsing:"Unknown",

    virusTotal:{

        status: "Unknown",

        malicious: 0,

        suspicious: 0,

        harmless: 0,

        undetected: 0,

        timeout: 0,

        reputation: 0

    },

    https:false,


    ssl:
    {
        sslValid:false,
        protocol:"Unknown"
    },


    securityHeaders:
    {
        "strict-transport-security":false,

        "content-security-policy":false,

        "x-frame-options":false,

        "x-content-type-options":false,

        "referrer-policy":false
    },


    score:0,

    level:"Unknown",


    interaction:"BROWSE",

    finalPosture:
    {
        overallStatus:"Unknown",
        risk:"Unknown",
        highestSeverity:"Unknown",
        confidence:"Unknown"
    },

    aboutWebsite:null,

    warning:null,

    recommendation:null,

    security_ai_success:false

};



let latestAssessment = {};

let securityHeadersByURL = {};



/* =====================================================
   Initialize Background
===================================================== */

function initializeBackground()
{

    console.log(
        "======================================"
    );

    console.log(
        "UIDetect Background Service Started."
    );

    console.log(
        "======================================"

    );

}






/* =====================================================
   Extension Events
===================================================== */

function registerExtensionEvents()
{


chrome.runtime.onInstalled.addListener(()=>{


    console.log(
        "UIDetect Installed Successfully."
    );


    chrome.contextMenus.removeAll(()=>{


        chrome.contextMenus.create({

            id:"uidetectScan",

            title:"Scan with UIDetect",

            contexts:["link"]

        });


        console.log(
            "Context menu created"
        );


    });


});



chrome.runtime.onStartup.addListener(()=>{


    console.log(
        "UIDetect Browser Started."
    );


});


}



/* =====================================================
   Message Listener
===================================================== */

function registerMessageListener()
{
    chrome.runtime.onMessage.addListener((request, sender, sendResponse) =>
    {
        (async () =>
        {
            try
            {
                console.log("======================================");
                console.log("Incoming Message:", request.action);
                console.log(request);
                console.log("======================================");


                // =====================================================
                // Interaction Security Scan
                // Reuse the existing /api/scan backend
                // =====================================================

                if (request.action === "SCAN_INTERACTION")
                {
                    console.log(
                        "UIDetect: SCAN_INTERACTION received."
                    );

                    const interactionData =
                        request.data || {};

                    const interaction =
                        interactionData.interaction ||
                        "BROWSE";

                    let scanController = null;

                    try
                    {
                        const tab =
                            sender.tab ||
                            await getCurrentTab();

                        if (!tab || !tab.url)
                        {
                            sendResponse(
                                createError(
                                    ERROR_CODES.NO_WEBSITE,
                                    "No website was found in the active tab.",
                                    false
                                )
                            );

                            return;
                        }

                        const interactionScanURL =
                            getInteractionScanURL(
                                tab.url
                            );

                        console.log(
                            "UIDetect: Interaction scan original URL:",
                            tab.url
                        );

                        console.log(
                            "UIDetect: Interaction scan assessment URL:",
                            interactionScanURL
                        );

                        const urlValidation =
                            validateURL(tab.url);

                        if (!urlValidation.valid)
                        {
                            sendResponse(
                                createError(
                                    "INVALID_URL",
                                    urlValidation.reason,
                                    false
                                )
                            );

                            return;
                        }

                        const websiteInformation =
                            await getWebsiteInformation(tab);

                        scanController =
                            new AbortController();

                        const scanId =
                            crypto.randomUUID();

                        activeScanController =
                            scanController;

                        activeScanId =
                            scanId;

                        const response =
                            await fetchWithTimeout(
                                BACKEND_BASE_URL +
                                "/api/scan",

                                {
                                    method: "POST",

                                    headers:
                                    {
                                        "Content-Type":
                                            "application/json"
                                    },

                                    body:
                                        JSON.stringify(
                                        {
                                            scanId:
                                                scanId,

                                            url:
                                                interactionScanURL,

                                            pageTitle:
                                                websiteInformation.pageTitle,

                                            metaDescription:
                                                websiteInformation.metaDescription,

                                            securityHeaders:
                                                securityHeadersByURL[
                                                    normalizeURL(
                                                        interactionScanURL
                                                    )
                                                ] ||
                                                websiteResult.securityHeaders ||
                                                {},

                                            interaction:
                                                interaction
                                        })
                                },

                                BACKEND_TIMEOUT,
                                scanController
                            );

                        console.log(
                            "UIDetect: Interaction scan HTTP status:",
                            response.status
                        );

                        console.log(
                            "UIDetect: Interaction scan URL:",
                            interactionScanURL
                        );

                        const result =
                            await parseBackendResponse(
                                response
                            );

                        console.log(
                            "UIDetect: Interaction scan result:",
                            result
                        );

                        sendResponse(
                            result
                        );
                    }
                    catch(error)
                    {
                        // =============================================
                        // User Cancelled Interaction Scan
                        // =============================================

                        if(
                            error.message ===
                            "REQUEST_ABORTED"
                        )
                        {
                            console.log(
                                "UIDetect: Interaction scan cancelled by user."
                            );

                            sendResponse(
                                {
                                    success: false,

                                    cancelled: true,

                                    error:
                                    {
                                        code:
                                            "SCAN_CANCELLED",

                                        message:
                                            "The interaction security scan was cancelled by the user.",

                                        recoverable:
                                            true
                                    }
                                }
                            );

                            return;
                        }


                        logBackgroundError(
                            "SCAN_INTERACTION",
                            error
                        );


                        // =============================================
                        // Backend Timeout
                        // =============================================

                        if(
                            error.message ===
                            "REQUEST_TIMEOUT"
                        )
                        {
                            sendResponse(
                                createError(
                                    ERROR_CODES.BACKEND_TIMEOUT,
                                    "The security scan took too long to respond.",
                                    true
                                )
                            );

                            return;
                        }


                        // =============================================
                        // Invalid JSON Response
                        // =============================================

                        if(
                            error.message ===
                            "INVALID_JSON_RESPONSE"
                        )
                        {
                            sendResponse(
                                createError(
                                    ERROR_CODES.INVALID_RESPONSE,
                                    "UIDetect received an invalid response from the backend.",
                                    true
                                )
                            );

                            return;
                        }


                        // =============================================
                        // HTTP Error
                        // =============================================

                        if(
                            error.message.startsWith("HTTP_")
                        )
                        {
                            sendResponse(
                                createError(
                                    ERROR_CODES.BACKEND_HTTP_ERROR,
                                    "The UIDetect backend returned an error.",
                                    true
                                )
                            );

                            return;
                        }


                        // =============================================
                        // Backend Unavailable
                        // Usually means Flask / UIDetect software
                        // is not running or cannot be reached.
                        // =============================================

                        sendResponse(
                            createError(
                                ERROR_CODES.BACKEND_UNAVAILABLE,
                                "UIDetect is not running. Please start the UIDetect software and try the scan again.",
                                true
                            )
                        );
                    }

                    finally
                    {
                        if (
                            activeScanController ===
                            scanController
                        )
                        {
                            activeScanController =
                                null;

                            activeScanId =
                                null;
                        }
                    }

                    return;
                }

                // =====================================================
                // Dashboard Scan
                // =====================================================

                if (request.action === "SCAN_WEBSITE")
                {
                    console.log(
                        "Starting dashboard scan..."
                    );

                    const scanResult =
                        await sendScanRequest();

                    console.log(
                        "Dashboard scan completed."
                    );

                    console.log(
                        scanResult
                    );

                    // =============================================
                    // Send Result
                    // =============================================

                    sendResponse(
                        scanResult
                    );

                    return;
                }

                

                
                // =====================================================
                // SHOW LOADING
                // Forward UI action to content script
                // =====================================================

                if (request.action === "SHOW_LOADING")
                {
                    console.log(
                        "UIDetect: SHOW_LOADING received."
                    );

                    if (!sender.tab || !sender.tab.id)
                    {
                        console.warn(
                            "UIDetect: Cannot forward SHOW_LOADING - tab unavailable."
                        );

                        sendResponse(
                            createError(
                                ERROR_CODES.NO_ACTIVE_TAB,
                                "The active tab is unavailable.",
                                true
                            )
                        );

                        return;
                    }

                    chrome.tabs.sendMessage(
                        sender.tab.id,
                        {
                            action:
                                "SHOW_LOADING"
                        },
                        function(response)
                        {
                            if (chrome.runtime.lastError)
                            {
                                console.error(
                                    "UIDetect: Failed to forward SHOW_LOADING:",
                                    chrome.runtime.lastError.message
                                );

                                return;
                            }

                            console.log(
                                "UIDetect: SHOW_LOADING forwarded.",
                                response
                            );
                        }
                    );

                    return false;
                }


                // =====================================================
                // SHOW BACKEND UNAVAILABLE
                // Forward UI action to content script
                // =====================================================

                if (request.action === "SHOW_BACKEND_UNAVAILABLE")
                {
                    console.log(
                        "UIDetect: SHOW_BACKEND_UNAVAILABLE received."
                    );

                    if (!sender.tab || !sender.tab.id)
                    {
                        console.warn(
                            "UIDetect: Cannot forward SHOW_BACKEND_UNAVAILABLE - tab unavailable."
                        );

                        sendResponse(
                            createError(
                                ERROR_CODES.NO_ACTIVE_TAB,
                                "The active tab is unavailable.",
                                true
                            )
                        );

                        return;
                    }

                    chrome.tabs.sendMessage(
                        sender.tab.id,
                        {
                            action:
                                "SHOW_BACKEND_UNAVAILABLE"
                        },
                        function(response)
                        {
                            if (chrome.runtime.lastError)
                            {
                                console.error(
                                    "UIDetect: Failed to forward SHOW_BACKEND_UNAVAILABLE:",
                                    chrome.runtime.lastError.message
                                );

                                return;
                            }

                            console.log(
                                "UIDetect: SHOW_BACKEND_UNAVAILABLE forwarded.",
                                response
                            );
                        }
                    );

                    return false;
                }


                // =====================================================
                // SHOW SECURITY WARNING
                // Forward UI action to content script
                // =====================================================

                if (request.action === "SHOW_SECURITY_WARNING")
                {
                    console.log(
                        "UIDetect: SHOW_SECURITY_WARNING received."
                    );

                    if (!sender.tab || !sender.tab.id)
                    {
                        console.warn(
                            "UIDetect: Cannot forward SHOW_SECURITY_WARNING - tab unavailable."
                        );

                        sendResponse(
                            createError(
                                ERROR_CODES.NO_ACTIVE_TAB,
                                "The active tab is unavailable.",
                                true
                            )
                        );

                        return;
                    }

                    chrome.tabs.sendMessage(
                        sender.tab.id,
                        {
                            action:
                                "SHOW_SECURITY_WARNING",

                            data:
                                request.data ||
                                request.scanResult ||
                                request.result ||
                                request.assessment
                        },
                        function(response)
                        {
                            if (chrome.runtime.lastError)
                            {
                                console.error(
                                    "UIDetect: Failed to forward SHOW_SECURITY_WARNING:",
                                    chrome.runtime.lastError.message
                                );

                                return;
                            }

                            console.log(
                                "UIDetect: SHOW_SECURITY_WARNING forwarded.",
                                response
                            );
                        }
                    );

                    return false;
                }



                // =====================================================
                // Cancel Active Website Scan
                // =====================================================

                if (request.action === "CANCEL_SCAN")
                {
                    console.log(
                        "UIDetect: Cancel scan requested."
                    );

                    // =============================================
                    // Abort Browser Fetch Immediately
                    // =============================================

                    if (activeScanController)
                    {
                        activeScanController.abort();

                        console.log(
                            "UIDetect: Active browser request aborted."
                        );
                    }
                    else
                    {
                        console.log(
                            "UIDetect: No active browser scan request."
                        );
                    }

                    // =============================================
                    // Tell Backend To Cancel Scanner
                    // =============================================

                    if (activeScanId)
                    {
                        console.log(
                            "UIDetect: Sending backend cancellation:",
                            activeScanId
                        );

                        fetch(
                            BACKEND_BASE_URL +
                            "/api/scan/cancel",
                            {
                                method: "POST",

                                headers:
                                {
                                    "Content-Type":
                                        "application/json"
                                },

                                body:
                                    JSON.stringify({

                                        scanId:
                                            activeScanId

                                    })
                            }
                        )
                        .then(
                            response =>
                            {
                                console.log(
                                    "UIDetect: Backend cancellation status:",
                                    response.status
                                );
                            }
                        )
                        .catch(
                            error =>
                            {
                                console.warn(
                                    "UIDetect: Backend cancellation failed:",
                                    error
                                );
                            }
                        );
                    }
                    else
                    {
                        console.log(
                            "UIDetect: No active backend scan ID."
                        );
                    }

                    // =============================================
                    // Clear Active Scan State
                    // =============================================

                    activeScanController =
                        null;

                    activeScanId =
                        null;

                    activeScanPromise =
                        null;


                    sendResponse(
                        {
                            success: true,

                            cancelled: true,

                            message:
                                "Scan cancellation requested successfully."
                        }
                    );

                    return;
                }
                

                console.warn(
                    "Unknown action:",
                    request.action
                );

                sendResponse(
                    createError(
                        ERROR_CODES.UNKNOWN_ACTION,
                        "The requested UIDetect action is not supported.",
                        false
                    )
                );

                return;

            }
            catch(error)
            {
                logBackgroundError(
                    "registerMessageListener",
                    error
                );

                sendResponse({

                    success: false,

                    website:
                        request.data?.website,

                    interaction:
                        request.data?.interaction,

                    risk:
                        "Unknown",

                    warning:
                        "UIDetect could not complete the requested operation.",

                    recommendation:
                        "Please try again.",

                    error:
                    {
                        code:
                            ERROR_CODES.UNKNOWN_ERROR,

                        message:
                            "An unexpected error occurred.",

                        recoverable:
                            true
                    }
                });
            }

        })();

        return true;
    });
}


/* =====================================================
   Get Current Tab
===================================================== */

async function getCurrentTab()
{
    try
    {
        const tabs =
            await chrome.tabs.query({
                active: true,
                currentWindow: true
            });

        if(!tabs || tabs.length === 0)
        {
            throw new Error(
                ERROR_CODES.NO_ACTIVE_TAB
            );
        }

        const tab = tabs[0];

        if(!tab)
        {
            throw new Error(
                ERROR_CODES.NO_ACTIVE_TAB
            );
        }

        return tab;
    }
    catch(error)
    {
        logBackgroundError(
            "getCurrentTab",
            error
        );

        throw error;
    }
}


/* =====================================================
   Check Cached Assessment
   Prevent stale assessment from another website
===================================================== */

function isAssessmentForCurrentURL(
    assessment,
    currentURL
)
{
    if (
        !assessment ||
        typeof assessment !== "object"
    )
    {
        return false;
    }

    if (
        !assessment.url ||
        !currentURL
    )
    {
        return false;
    }

    try
    {
        const assessmentURL =
            new URL(assessment.url);

        const currentTabURL =
            new URL(currentURL);

        return (
            assessmentURL.origin ===
            currentTabURL.origin &&
            assessmentURL.pathname ===
            currentTabURL.pathname &&
            assessmentURL.search ===
            currentTabURL.search
        );
    }
    catch(error)
    {
        console.warn(
            "UIDetect: Unable to compare assessment URL:",
            error
        );

        return false;
    }
}



/* =====================================================
   Get Current Website Information
===================================================== */

async function getWebsiteInformation(
    tab
)
{
    try
    {
        if(!tab || !tab.id)
        {
            return {
                pageTitle:
                    tab?.title || "",

                metaDescription:
                    ""
            };
        }

        const results =
            await chrome.scripting.executeScript({

                target:
                {
                    tabId:
                        tab.id
                },

                func:
                    () =>
                    {
                        const meta =
                            document.querySelector(
                                'meta[name="description"]'
                            );

                        return {

                            pageTitle:
                                document.title || "",

                            metaDescription:
                                meta
                                    ?
                                    meta.content || ""
                                    :
                                    ""
                        };
                    }

            });

        const pageInfo =
            results?.[0]?.result || {};

        return {

            pageTitle:
                pageInfo.pageTitle ||
                tab.title ||
                "",

            metaDescription:
                pageInfo.metaDescription ||
                ""
        };
    }
    catch(error)
    {
        logBackgroundError(
            "getWebsiteInformation",
            error
        );

        return {

            pageTitle:
                tab?.title || "",

            metaDescription:
                ""
        };
    }
}


/* =====================================================
   Manual Scan Request
===================================================== */

async function sendScanRequest()
{
    // =============================================
    // PREVENT DUPLICATE SCANS
    // Reuse the currently running scan
    // =============================================

    if (activeScanPromise)
    {
        console.log(
            "UIDetect: Scan already in progress. Reusing existing scan."
        );

        return await activeScanPromise;
    }

    // =============================================
    // Create Scan Controller
    // =============================================

    const scanController =
        new AbortController();

    // =============================================
    // Create Unique Scan ID
    // =============================================

    const scanId =
        crypto.randomUUID();

    // =============================================
    // Save Active Scan State
    // =============================================

    activeScanController =
        scanController;

    activeScanId =
        scanId;

    // =============================================
    // Start Scan
    // =============================================

    const scanPromise =
        performScanRequest(
            scanController,
            scanId
        );

    activeScanPromise =
        scanPromise;

    try
    {
        return await scanPromise;
    }
    finally
    {
        // =============================================
        // Only clear if this is still the same scan
        // =============================================

        if (
            activeScanPromise ===
            scanPromise
        )
        {
            activeScanPromise =
                null;
        }
    }
}


async function performScanRequest(
    scanController,
    scanId
)
{
    try
        {
            const tab =
                await getCurrentTab();

            // =============================================
            // Validate Current Tab
            // =============================================

            if(!tab || !tab.url)
            {
                return createError(
                    ERROR_CODES.NO_WEBSITE,
                    "No website was found in the active tab.",
                    false
                );
            }


            const urlValidation =
                validateURL(tab.url);

            if(!urlValidation.valid)
            {
                return createError(
                    "INVALID_URL",
                    urlValidation.reason,
                    false
                );
            }


            const websiteInformation =
                await getWebsiteInformation(
                    tab
                );


            console.log(
                "UIDetect Backend URL:",
                BACKEND_BASE_URL + "/api/scan"
            );


            // =============================================
            // Send Scan Request
            // =============================================

            const response =
                await fetchWithTimeout(

                    BACKEND_BASE_URL +
                    "/api/scan",

                    {
                        method: "POST",

                        headers:
                        {
                            "Content-Type":
                                "application/json"
                        },

                        body:
                            JSON.stringify({

                                scanId:
                                    scanId,

                                url:
                                    tab.url,

                                pageTitle:
                                    websiteInformation.pageTitle,

                                metaDescription:
                                    websiteInformation.metaDescription,

                                securityHeaders:
                                    securityHeadersByURL[normalizeURL(tab.url)] ||
                                    websiteResult.securityHeaders ||
                                    {},

                                interaction:
                                    websiteResult.interaction ||
                                    "BROWSE"
                            })
                    },

                    BACKEND_TIMEOUT,
                    scanController
                );

            console.log(
                "Scan HTTP Status:",
                response.status
            );

            // =============================================
            // Validate Response
            // =============================================

            const result =
                await parseBackendResponse(
                    response
                );

            console.log(
                "Raw Scan Result:",
                result
            );

            console.log(
                "========== BACKEND FIELD CHECK =========="
            );


            console.log(
                "result.assessment.aboutWebsite:",
                result.assessment?.aboutWebsite
            );


            console.log(
                "result.assessment.recommendation:",
                result.assessment?.recommendation
            );

            console.log(
                "result.assessment.warning:",
                result.assessment?.warning
            );

            console.log(
                "=========================================="
            );

            // =============================================
            // Backend Returned Error
            // =============================================

            if(result.success === false)
            {
                return result;
            }

            // =============================================
            // Validate Assessment
            // =============================================

            const assessment =
                result.assessment || result;

            if(
                !assessment ||
                typeof assessment !== "object"
            )
            {
                throw new Error(
                    "INVALID_ASSESSMENT"
                );
            }

            // =============================================
            // Preserve Final Posture
            // Backend may return finalPosture either:
            // 1. inside assessment
            // 2. at the top level
            // =============================================

            if(
                result.finalPosture &&
                !assessment.finalPosture
            )
            {
                assessment.finalPosture =
                    result.finalPosture;
            }

            if (
                !assessment.finalPosture ||
                typeof assessment.finalPosture !== "object"
            )
            {
                console.warn(
                    "UIDetect: Final security posture is missing."
                );

                assessment.finalPosture =
                {
                    overallStatus:
                        "Unknown",

                    risk:
                        assessment.risk ||
                        "Unknown",

                    highestSeverity:
                        "Unknown",

                    confidence:
                        "Unknown"
                };
            }

            // =============================================
            // Normalize Final Posture Risk
            // =============================================

            const finalPostureRisk =
                assessment.finalPosture.risk ||
                assessment.risk ||
                "Unknown";

            assessment.finalPosture.risk =
                finalPostureRisk;

            // =============================================
            // Save Assessment
            // Preserve website metadata collected from page
            // =============================================

            latestAssessment =
            {
                ...assessment,

                pageTitle:
                    assessment.pageTitle ||
                    websiteInformation.pageTitle ||
                    "",

                metaDescription:
                    assessment.metaDescription ||
                    websiteInformation.metaDescription ||
                    ""
            };


            // =============================================
            // Validate AI-Generated Output
            // aboutWebsite, warning, and recommendation
            // must come from the backend AI response
            // =============================================

            if (
                typeof latestAssessment.aboutWebsite !== "string" ||
                !latestAssessment.aboutWebsite.trim()
            )
            {
                console.warn(
                    "UIDetect: AI aboutWebsite is missing."
                );
            }

            if (
                typeof latestAssessment.warning !== "string" ||
                !latestAssessment.warning.trim()
            )
            {
                console.warn(
                    "UIDetect: AI warning is missing."
                );
            }

            if (
                typeof latestAssessment.recommendation !== "string" ||
                !latestAssessment.recommendation.trim()
            )
            {
                console.warn(
                    "UIDetect: AI recommendation is missing."
                );
            }

            // =============================================
            // Final Posture Logging
            // =============================================

            console.log(
                "========== FINAL POSTURE TOP-LEVEL CHECK =========="
            );

            console.log(
                "Top-level finalPosture:",
                latestAssessment.finalPosture
            );

            console.log(
                "Top-level posture status:",
                latestAssessment.finalPosture?.overallStatus
            );

            console.log(
                "Top-level posture risk:",
                latestAssessment.finalPosture?.risk
            );

            console.log(
                "Top-level posture severity:",
                latestAssessment.finalPosture?.highestSeverity
            );

            console.log(
                "Top-level posture confidence:",
                latestAssessment.finalPosture?.confidence
            );

            console.log(
                "==================================================="
            );

            // =============================================
            // Update Global Website Result
            // =============================================

            websiteResult =
            {
                ...websiteResult,
                ...latestAssessment
            };

            console.log(
                "========== VIRUSTOTAL =========="
            );

            console.log(
                websiteResult.virusTotal
            );

            console.log(
                "================================"
            );

            console.log(
                "========== SAVED ASSESSMENT =========="
            );

            console.log(
                latestAssessment
            );

            console.log(
                "Saved URL:",
                latestAssessment.url
            );

            console.log(
                "======================================"
            );

            return {
                success: true,
                assessment: latestAssessment
            };
        }
        catch(error)
        {
            // =============================================
            // User Cancelled Scan
            // =============================================

            if(
                error.message ===
                "REQUEST_ABORTED"
            )
            {
                console.log(
                    "UIDetect: Scan cancelled by user."
                );

                return {
                    success: false,

                    cancelled: true,

                    error:
                    {
                        code:
                            "SCAN_CANCELLED",

                        message:
                            "The security scan was cancelled by the user.",

                        recoverable:
                            true
                    }
                };
            }

            // =============================================
            // Log Unexpected Errors
            // =============================================

            logBackgroundError(
                "sendScanRequest",
                error
            );

            // =============================================
            // Timeout
            // =============================================

            if(
                error.message ===
                "REQUEST_TIMEOUT"
            )
            {
                return createError(
                    ERROR_CODES.BACKEND_TIMEOUT,
                    "The security assessment took too long to respond.",
                    true
                );
            }

            // =============================================
            // Invalid JSON
            // =============================================

            if(
                error.message ===
                "INVALID_JSON_RESPONSE"
            )
            {
                return createError(
                    ERROR_CODES.INVALID_RESPONSE,
                    "The backend returned an invalid response.",
                    true
                );
            }

            // =============================================
            // HTTP Error
            // =============================================

            if(
                error.message.startsWith("HTTP_")
            )
            {
                return createError(
                    ERROR_CODES.BACKEND_HTTP_ERROR,
                    "The UIDetect backend returned an error.",
                    true
                );
            }

            // =============================================
            // Backend / Network Error
            // =============================================

            return createError(
                ERROR_CODES.BACKEND_UNAVAILABLE,
                "UIDetect is not running. Please start the UIDetect software and try the scan again.",
                true
            );
        }
        finally
        {
            if (
                activeScanController ===
                scanController
            )
            {
                activeScanController =
                    null;

                activeScanId =
                    null;
            }
        }

    }


function normalizeURL(url) {
    try {
        const parsed = new URL(url);

        // Fragments are not sent to the server and should not affect
        // security-header matching.
        parsed.hash = "";

        // Remove trailing slash except for the domain root.
        if (
            parsed.pathname.length > 1 &&
            parsed.pathname.endsWith("/")
        ) {
            parsed.pathname = parsed.pathname.slice(0, -1);
        }

        return parsed.toString();
    } catch (error) {
        return url;
    }
}    

function getInteractionScanURL(url)
{
    if(!url)
    {
        return url;
    }

    try
    {
        const parsedURL =
            new URL(url);

        const isGoogleForms =
            (
                parsedURL.hostname ===
                    "docs.google.com" &&

                parsedURL.pathname
                    .toLowerCase()
                    .startsWith("/forms/")
            );

        if(
            isGoogleForms &&
            parsedURL.pathname
                .toLowerCase()
                .endsWith("/formresponse")
        )
        {
            parsedURL.pathname =
                parsedURL.pathname.replace(
                    /\/formresponse$/i,
                    "/viewform"
                );

            return parsedURL.toString();
        }

        return url;
    }
    catch(error)
    {
        console.warn(
            "UIDetect: Unable to normalize interaction scan URL:",
            error
        );

        return url;
    }
}


/* =====================================================
   Security Header Detection
===================================================== */

function registerWebRequestEvents()
{
    chrome.webRequest.onHeadersReceived.addListener(

        (details) =>
        {
            if(details.type !== "main_frame")
            {
                return;
            }

            const headers =
                details.responseHeaders || [];

            const hasHeader =
                (name) =>
                {
                    return headers.some(
                        header =>
                            header.name &&
                            header.name.toLowerCase() ===
                            name.toLowerCase()
                    );
                };


            const securityHeaders =
            {
                "strict-transport-security":
                    hasHeader(
                        "strict-transport-security"
                    ),

                "content-security-policy":
                    hasHeader(
                        "content-security-policy"
                    ),

                "x-frame-options":
                    hasHeader(
                        "x-frame-options"
                    ),

                "x-content-type-options":
                    hasHeader(
                        "x-content-type-options"
                    ),

                "referrer-policy":
                    hasHeader(
                        "referrer-policy"
                    )
            };


            const normalizedURL =
                normalizeURL(details.url);

            securityHeadersByURL[normalizedURL] =
                securityHeaders;


            websiteResult.securityHeaders =
                securityHeaders;


            console.log(
                "Security Headers:",
                securityHeaders
            );

            console.log(
                "Security Headers URL:",
                details.url
            );
        },

        {
            urls:
            [
                "<all_urls>"
            ]
        },

        [
            "responseHeaders"
        ]
    );

}







/* =====================================================
   Start Background Service
===================================================== */

function startBackgroundService()
{


initializeBackground();


registerExtensionEvents();


registerMessageListener();


registerWebRequestEvents();


}



startBackgroundService();


// =====================================
// PHASE 9 - RIGHT CLICK SCAN
// =====================================








// =====================================
// INJECT CONTENT SCRIPT IF NEEDED
// =====================================

// =====================================
// CHECK UIDETECT CONTENT SCRIPT
// =====================================

async function injectUIDetect(
    tabId
)
{
    try
    {
        if(!tabId)
        {
            throw new Error(
                ERROR_CODES.INJECTION_ERROR
            );
        }

        console.log(
            "UIDetect content scripts are loaded through manifest.json."
        );

        return {
            success: true
        };
    }
    catch(error)
    {
        logBackgroundError(
            "injectUIDetect",
            error
        );

        return createError(
            ERROR_CODES.INJECTION_ERROR,
            "Unable to prepare the UIDetect scan interface.",
            true
        );
    }
}


// =====================================
// SEND MESSAGE TO PAGE
// =====================================

async function sendToPage(
    tabId,
    message,
    maxAttempts = 10,
    delay = 150
)
{
    try
    {
        if(!tabId)
        {
            console.warn(
                "Unable to send message: tab ID missing."
            );

            return false;
        }

        for(let attempt = 1; attempt <= maxAttempts; attempt++)
        {
            try
            {
                await chrome.tabs.sendMessage(
                    tabId,
                    message
                );

                console.log(
                    "Message sent successfully:",
                    message.action,
                    "Attempt:",
                    attempt
                );

                return true;
            }
            catch(error)
            {
                const errorMessage =
                    error?.message ||
                    String(error);

                console.warn(
                    "Message delivery attempt " +
                    attempt +
                    "/" +
                    maxAttempts +
                    " failed:",
                    errorMessage
                );

                // =====================================
                // Wait before retrying
                // =====================================

                if(attempt < maxAttempts)
                {
                    await new Promise(
                        resolve =>
                            setTimeout(
                                resolve,
                                delay
                            )
                    );
                }
            }
        }

        console.error(
            "Unable to deliver message to content script:",
            message.action
        );

        return false;
    }
    catch(error)
    {
        logBackgroundError(
            "sendToPage",
            error
        );

        return false;
    }
}


/**
 * Resolve a URL to its final destination before scanning.
 *
 * Example:
 * Google redirect URL
 *      ↓
 * https://myflixerz.day/
 *
 * This prevents UIDetect from scanning the redirect wrapper
 * instead of the website the user actually selected.
 */
async function resolveRedirectURL(originalURL) {
    if (!originalURL) {
        throw new Error("Empty URL");
    }

    console.log(
        "UIDetect: Resolving target URL:",
        originalURL
    );

    try {
        const controller =
            new AbortController();

        const timeout =
            setTimeout(
                () => controller.abort(),
                8000
            );

        const response =
            await fetch(
                originalURL,
                {
                    method: "GET",
                    redirect: "follow",
                    signal: controller.signal
                }
            );

        clearTimeout(timeout);

        const finalURL =
            response.url || originalURL;

        console.log(
            "UIDetect: Final target URL:",
            finalURL
        );

        return finalURL;

    } catch (error) {

        console.warn(
            "UIDetect: Unable to resolve redirect:",
            error
        );

        /*
         * Do NOT silently treat the redirect URL as the
         * final website.
         *
         * Returning null allows the caller to stop the scan
         * safely instead of scanning the wrong website.
         */
        return null;
    }
}


// =====================================
// RIGHT CLICK EVENT
// =====================================


chrome.contextMenus.onClicked.addListener(
    async(info, tab) =>
    {
        if(info.menuItemId !== "uidetectScan")
        {
            return;
        }

        /*
         * The URL supplied by Chrome may be a redirect/tracking
         * URL, especially for search engine results.
         */
        const originalURL =
            info.linkUrl;

        console.log(
            "UIDetect Right-Click original URL:",
            originalURL
        );

        if(!originalURL)
        {
            console.error(
                "UIDetect: No link URL available."
            );

            return;
        }

        /*
         * Resolve the actual destination before scanning.
         */
        const url =
            await resolveRedirectURL(
                originalURL
            );

        if(!url)
        {
            console.error(
                "UIDetect: Could not determine final destination URL."
            );

            return;
        }

        console.log(
            "UIDetect scanning final destination:",
            url
        );

        // =============================================
        // Validate URL
        // =============================================

        const urlValidation =
            validateURL(url);

        if(!urlValidation.valid)
        {
            console.log(
                "UIDetect: Invalid URL:",
                urlValidation.reason
            );

            return;
        }

        // =============================================
        // Validate Tab
        // =============================================

        if(!tab || !tab.id)
        {
            console.error(
                "Tab not found."
            );

            return;
        }

        // =============================================
        // Prepare UIDetect Content Script
        // =============================================

        await injectUIDetect(
            tab.id
        );

        // =============================================
        // Show Loading Popup
        // =============================================

        await sendToPage(
            tab.id,
            {
                action:
                    "SHOW_LOADING"
            }
        );



        const websiteInformation =
        {
            pageTitle: "",
            metaDescription: ""
        };

        // =============================================
        // Send URL to Backend
        // =============================================

        const autoScanController =
            new AbortController();

        const autoScanId =
            crypto.randomUUID();

        activeScanController =
            autoScanController;

        activeScanId =
            autoScanId;

        try
        {
            const response =
                await fetchWithTimeout(
                    BACKEND_BASE_URL +
                    "/api/scan",
                    {
                        method: "POST",

                        headers: {
                            "Content-Type":
                                "application/json"
                        },

                        body: JSON.stringify({

                            scanId:
                                autoScanId,

                            url:
                                url,

                            pageTitle:
                                websiteInformation.pageTitle,

                            metaDescription:
                                websiteInformation.metaDescription,

                            interaction:
                                "RIGHT_CLICK",

                            securityHeaders:
                                securityHeadersByURL[normalizeURL(url)] ||
                                websiteResult.securityHeaders ||
                                {}                                

                        })
                    },

                    SCAN_TIMEOUT,

                    autoScanController
                );

            console.log(
                "Backend status:",
                response.status
            );

            // =============================================
            // Validate Backend Response
            // =============================================

            const result =
                await parseBackendResponse(
                    response
                );

            console.log(
                "SCAN RESULT:",
                result
            );

            // =============================================
            // Backend Returned Error
            // =============================================

            if(
                result.success === false
            )
            {
                const backendError =
                    result.error || {};

                const backendErrorCode =
                    backendError.code ||
                    ERROR_CODES.UNKNOWN_ERROR;

                const backendErrorMessage =
                    backendError.message ||
                    "The UIDetect backend could not complete the scan.";

                const backendErrorObject =
                    new Error(
                        backendErrorMessage
                    );

                backendErrorObject.uidetectErrorCode =
                    backendErrorCode;

                throw backendErrorObject;
            }

            // =============================================
            // Save Assessment
            // =============================================

            latestAssessment =
                result.assessment ||
                result;

            // =============================================
            // Normalize Final Security Posture
            // =============================================

            if (
                !latestAssessment.finalPosture &&
                result.finalPosture
            )
            {
                latestAssessment.finalPosture =
                    result.finalPosture;
            }

            if (
                !latestAssessment.finalPosture ||
                typeof latestAssessment.finalPosture !== "object"
            )
            {
                latestAssessment.finalPosture =
                {
                    overallStatus:
                        "Unknown",

                    risk:
                        latestAssessment.risk ||
                        "Unknown",

                    highestSeverity:
                        "Unknown",

                    confidence:
                        "Unknown"
                };
            }

            latestAssessment.finalPosture.risk =
                latestAssessment.finalPosture.risk ||
                latestAssessment.risk ||
                "Unknown";

            websiteResult =
            {
                ...websiteResult,
                ...latestAssessment
            };


            // =============================================
            // Persist Result For The Extension Popup
            //
            // The on-page modal (SHOW_SCAN_MODAL) only
            // reaches the tab that was right-clicked.
            // Save the same assessment to storage so that
            // popup.js can display it if the user opens the
            // toolbar popup afterwards.
            // =============================================

            try
            {
                await chrome.storage.local.set(
                    {
                        rightClickResult:
                            latestAssessment
                    }
                );

                console.log(
                    "UIDetect: Right-click scan result saved to storage."
                );
            }
            catch(storageError)
            {
                logBackgroundError(
                    "Right Click Scan - chrome.storage.local.set",
                    storageError
                );
            }


            // =============================================
            // Show Scan Result
            // Wait for content script to receive result
            // =============================================

            const popupDisplayed =
                await sendToPage(
                    tab.id,
                    {
                        action:
                            "SHOW_SCAN_MODAL",

                        data:
                            {
                                assessment:
                                    latestAssessment
                            }
                    }
                );

            if(!popupDisplayed)
            {
                console.error(
                    "UIDetect: Scan completed, but result popup could not be delivered to the page."
                );
            }
            else
            {
                console.log(
                    "UIDetect: Right-click scan result popup displayed successfully."
                );
            }
        }
        catch(error)
        {
            // =============================================
            // User Cancelled Right-Click Scan
            // =============================================

            if(
                error.message ===
                "REQUEST_ABORTED"
            )
            {
                console.log(
                    "UIDetect: Right-Click Scan cancelled by user."
                );

                return;
            }


            logBackgroundError(
                "Right Click Scan",
                error
            );

            let warning =
                "UIDetect is not running. Please start the UIDetect software and try the scan again.";

            let recommendation =
                "Start the UIDetect software and try the scan again.";

            let errorCode =
                error.uidetectErrorCode ||
                ERROR_CODES.BACKEND_UNAVAILABLE;

            // =============================================
            // Timeout
            // =============================================

            if(
                error.message ===
                "REQUEST_TIMEOUT"
            )
            {
                errorCode =
                    ERROR_CODES.BACKEND_TIMEOUT;

                warning =
                    "The security scan took too long to respond.";

                recommendation =
                    "Please try the scan again.";
            }

            // =============================================
            // Invalid Response
            // =============================================

            else if(
                error.message ===
                "INVALID_JSON_RESPONSE"
            )
            {
                errorCode =
                    ERROR_CODES.INVALID_RESPONSE;

                warning =
                    "UIDetect received an invalid response.";

                recommendation =
                    "Please try the scan again.";
            }

            // =============================================
            // HTTP Error
            // =============================================

            else if(
                error.message.startsWith("HTTP_")
            )
            {
                errorCode =
                    ERROR_CODES.BACKEND_HTTP_ERROR;

                warning =
                    "The UIDetect backend returned an error.";

                recommendation =
                    "Please try the scan again.";
            }

            // =============================================
            // Show Backend Unavailable Popup
            // =============================================

            if (
                errorCode ===
                ERROR_CODES.BACKEND_UNAVAILABLE
            )
            {
                await sendToPage(
                    tab.id,
                    {
                        action:
                            "SHOW_BACKEND_UNAVAILABLE"
                    }
                );

                return;
            }

            // =============================================
            // Show Error Modal
            // =============================================

            sendToPage(
                tab.id,
                {
                    action:
                        "SHOW_SCAN_MODAL",

                    data:
                    {
                        assessment:
                        {
                            url: url,

                            score: "--",

                            level:
                                "Unknown",

                            risk:
                                "Unknown",

                            warning:
                                warning,

                            recommendation:
                                recommendation,

                            error:
                            {
                                code:
                                    errorCode,

                                message:
                                    warning,

                                recoverable:
                                    true
                            }
                        }
                    }
                }
            );
        }
        finally {

            // =====================================
            // Clear Right-Click Scan State
            // =====================================

            if(
                activeScanController ===
                autoScanController
            )
            {
                activeScanController =
                    null;

                activeScanId =
                    null;
            }

        }
    }
);