/* =====================================================
UIDetect - Scan Modal

Phase 9:
Right Click Scan

Phase 10:
Error Handling & Recovery
===================================================== */

console.log(
    "UIDetect scanModal.js loaded"
);


/* =====================================================
Error Codes
===================================================== */

const SCAN_MODAL_ERROR_CODES =
{
    INVALID_DATA:
        "SCAN_MODAL_INVALID_DATA",

    DOM_ERROR:
        "SCAN_MODAL_DOM_ERROR",

    RENDER_ERROR:
        "SCAN_MODAL_RENDER_ERROR"
};


/* =====================================================
Modal Constants
===================================================== */

const MODAL_ID =
    "uidetect-security-modal";



/* =====================================================
Interaction Scan Cancellation State
===================================================== */

let interactionScanCancelled = false;



/* =====================================================
Mark Interaction Scan as Cancelled
===================================================== */

function markInteractionScanCancelled()
{
    interactionScanCancelled = true;

    console.log(
        "UIDetect: Interaction Scan marked as cancelled."
    );
}


/* =====================================================
Check Interaction Scan Cancellation
===================================================== */

function isInteractionScanCancelled()
{
    return interactionScanCancelled;
}


/* =====================================================
Centralized Error Logger
===================================================== */

function logScanModalError(
    context,
    error
)
{
    console.error(
        "======================================"
    );

    console.error(
        "UIDetect Scan Modal Error"
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
Message Validation
===================================================== */

function validateMessage(request)
{
    if(
        !request ||
        typeof request !== "object"
    )
    {
        return {
            valid: false,

            error:
                createScanModalError(
                    SCAN_MODAL_ERROR_CODES.INVALID_DATA,
                    "Invalid UIDetect message received.",
                    true
                )
        };
    }

    if(
        !request.action ||
        typeof request.action !== "string"
    )
    {
        return {
            valid: false,

            error:
                createScanModalError(
                    SCAN_MODAL_ERROR_CODES.INVALID_DATA,
                    "UIDetect message action is missing.",
                    true
                )
        };
    }

    return {
        valid: true
    };
}


/* =====================================================
Safe Message Response
===================================================== */

function sendSafeResponse(
    sendResponse,
    response
)
{
    try
    {
        if(typeof sendResponse === "function")
        {
            sendResponse(
                response
            );
        }
    }
    catch(error)
    {
        logScanModalError(
            "sendSafeResponse",
            error
        );
    }
}



/* =====================================================
Create Standard Error
===================================================== */

function createScanModalError(
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
Safe Text
===================================================== */

function safeText(
    value,
    fallback = "Unknown"
)
{
    if(
        value === undefined ||
        value === null ||
        value === ""
    )
    {
        return fallback;
    }

    return String(value);
}


/* =====================================================
Escape HTML
===================================================== */

function escapeHtml(
    value
)
{
    return String(value)
        .replace(/&/g, "&amp;")
        .replace(/</g, "&lt;")
        .replace(/>/g, "&gt;")
        .replace(/"/g, "&quot;")
        .replace(/'/g, "&#039;");
}


/* =====================================================
Website URL
===================================================== */

function getWebsiteUrl(
    data,
    result
)
{
    const url =
        result.url ||
        result.website ||
        data.url ||
        data.website ||
        data.assessment?.url ||
        data.assessment?.website;


    if(
        url &&
        typeof url === "string" &&
        url.trim() !== ""
    )
    {
        return url.trim();
    }


    return "Unknown";
}


/* =====================================================
Safe Number
===================================================== */

function safeScore(
    value
)
{
    if(
        value === undefined ||
        value === null ||
        value === ""
    )
    {
        return "--";
    }

    const numericValue =
        Number(value);

    if(
        Number.isNaN(
            numericValue
        )
    )
    {
        return "--";
    }

    return Math.max(
        0,
        Math.min(
            100,
            numericValue
        )
    );
}


/* =====================================================
Overall Security Status
===================================================== */

function getSecurityStatus(
    result,
    openphishDetected
)
{
    if(openphishDetected)
    {
        return {
            label: "UIDetect Alert!!!",
            icon: "🔴",
            className: "risk-critical"
        };
    }


    const risk =
        getDisplayRisk(
            result
        ).toLowerCase();


    if(
        risk.includes("critical") ||
        risk.includes("high")
    )
    {
        return {
            label: "UIDetect Alert!!!",
            icon: "🔴",
            className: "risk-high"
        };
    }


    if(
        risk.includes("medium") ||
        risk.includes("moderate")
    )
    {
        return {
            label: "Be Cautious",
            icon: "🟡",
            className: "risk-medium"
        };
    }


    if(
        risk.includes("very low") ||
        risk.includes("very safe")
    )
    {
        return {
            label: "Very Safe",
            icon: "🟢",
            className: "risk-low"
        };
    }


    if(
        risk.includes("low") ||
        risk.includes("safe")
    )
    {
        return {
            label: "Safe",
            icon: "🟢",
            className: "risk-low"
        };
    }


    return {
        label: "Security Status Unavailable",
        icon: "⚪",
        className: "risk-unknown"
    };
}



/* =====================================================
Display Risk
===================================================== */

function getDisplayRisk(
    result
)
{
    if(
        result.finalPosture &&
        typeof result.finalPosture === "object"
    )
    {
        const postureRisk =
            safeText(
                result.finalPosture.risk,
                ""
            ).trim();

        if(postureRisk)
        {
            return postureRisk;
        }
    }

    const risk =
        safeText(
            result.risk,
            ""
        ).trim();

    if(risk)
    {
        return risk;
    }

    const contextRisk =
        safeText(
            result.contextRisk,
            ""
        ).trim();

    if(contextRisk)
    {
        return contextRisk;
    }

    if(
        result.finalPosture &&
        typeof result.finalPosture === "object"
    )
    {
        const severity =
            safeText(
                result.finalPosture.highestSeverity,
                ""
            ).trim();

        if(severity)
        {
            return severity;
        }
    }

    return "Unknown";
}



/* =====================================================
   Detection Type
===================================================== */

function getDetectionType(data, result) 
{
    const scanType = 
        safeText(
            data.scanType || result.scanType,
            ""
        ).toLowerCase();


    const interactionType = 
        safeText(
            data.interaction || result.interaction,
            ""
        ).toLowerCase();


    const detectionType = 
        safeText(
            data.detectionType || result.detectionType,
            ""
        ).toLowerCase();


    const websiteUrl = 
        safeText(
            data.url || result.url,
            ""
        ).toLowerCase();


    /* =============================================
       PRIORITY 1 - Login Detection
       ============================================= */

    if(
        result.loginDetected === true ||
        detectionType.includes("login") ||
        scanType.includes("login") ||
        interactionType.includes("login")
    )
    {
        return "login";
    }


    /* =============================================
       PRIORITY 2 - Explicit Form Detection
       ============================================= */

    if(
        result.formDetected === true ||
        detectionType.includes("form") ||
        scanType.includes("form") ||
        interactionType.includes("form")
    )
    {
        return "form";
    }



    /* =============================================
       PRIORITY 4 - Right Click Scan
       ============================================= */

    if(
        scanType.includes("rightclick") ||
        scanType.includes("right_click") ||
        scanType.includes("right-click") ||
        interactionType.includes("rightclick") ||
        interactionType.includes("right_click") ||
        interactionType.includes("right-click")
    )
    {
        return "right-click";
    }


    /* =============================================
       PRIORITY 5 - Specific Interaction Action
       ============================================= */

    if(
        interactionType.includes("registration")
    )
    {
        return "registration";
    }


    if(
        interactionType.includes("upload")
    )
    {
        return "upload";
    }


    if(
        interactionType.includes("download")
    )
    {
        return "download";
    }


    if(
        interactionType.includes("payment")
    )
    {
        return "payment";
    }


    if(
        interactionType.includes("logout")
    )
    {
        return "logout";
    }


    /* =============================================
       PRIORITY 6 - Interaction Scan
       ============================================= */

    if(
        scanType.includes("interaction") ||
        detectionType.includes("interaction")
    )
    {
        return "interaction";
    }


    /* =============================================
       Default
       ============================================= */

    return "website";
}




/* =====================================================
Remove Existing Modal
===================================================== */

function removeExistingModal()
{
    try
    {
        const oldModal =
            document.getElementById(
                MODAL_ID
            );

        if(oldModal)
        {
            oldModal.remove();
        }
    }
    catch(error)
    {
        logScanModalError(
            "removeExistingModal",
            error
        );
    }
}


function getFriendlyDetectionType(
    detectionType
)
{
    switch(detectionType)
    {
        case "right-click":
            return "Right-Click Scan Detected";

        case "login":
            return "Login Action Detected";

        case "registration":
            return "Registration Action Detected";

        case "upload":
            return "Upload Action Detected";

        case "download":
            return "Download Action Detected";

        case "payment":
            return "Payment Action Detected";

        case "logout":
            return "Logout Action Detected";

        case "interaction":
            return "Security-Sensitive Action Detected";

        default:
            return "Website Scan Detected";
    }
}


/* =====================================================
Loading Popup
===================================================== */

function showLoadingPopup()
{
    try
    {
        removeExistingModal();

        interactionScanCancelled = false;


        if(!document.body)
        {
            throw new Error(
                "Document body is unavailable."
            );
        }


        const overlay =
            document.createElement(
                "div"
            );


        overlay.id =
            MODAL_ID;


        overlay.innerHTML = `

            <div class="uidetect-modal-box uidetect-loading-modal">

                <div class="uidetect-spinner"></div>


                <h2>
                    🛡 UIDetect
                </h2>


                <p>
                    Analyzing Website Security...
                </p>

                <div class="uidetect-buttons">

                    <button
                        id="uidetect-cancel-scan"
                        type="button">

                        Cancel Scan

                    </button>

                    <button
                        id="uidetect-skip-scan"
                        type="button">

                        Skip

                    </button>

                </div>

            </div>

        `;


        document.body.appendChild(
            overlay
        );


        console.log(
            "Loading popup displayed"
        );


        const skipButton =
            document.getElementById(
                "uidetect-skip-scan"
            );

        if(!skipButton)
        {
            throw new Error(
                "Scan modal Skip button could not be created."
            );
        }


        skipButton.addEventListener(
            "click",
            function()
            {
                try
                {
                    console.log(
                        "UIDetect: Skip Scan clicked."
                    );


                    // =============================================
                    // Tell interactionDetector.js to allow the
                    // original user interaction to continue.
                    // =============================================

                    window.dispatchEvent(
                        new CustomEvent(
                            "UIDetectInteractionSkipped"
                        )
                    );


                    // =============================================
                    // Cancel the UIDetect security scan.
                    // The original interaction is NOT cancelled.
                    // =============================================

                    chrome.runtime.sendMessage(
                        {
                            action:
                                "CANCEL_SCAN"
                        },
                        function(response)
                        {
                            if(
                                chrome.runtime.lastError
                            )
                            {
                                logScanModalError(
                                    "Skip Scan cancellation message",
                                    chrome.runtime.lastError.message
                                );
                            }
                            else
                            {
                                console.log(
                                    "UIDetect: Skip Scan cancellation response:",
                                    response
                                );
                            }
                        }
                    );


                    removeExistingModal();
                }
                catch(error)
                {
                    logScanModalError(
                        "Skip Scan button",
                        error
                    );


                    // =============================================
                    // Even if cancellation messaging fails,
                    // preserve Skip semantics.
                    // =============================================

                    window.dispatchEvent(
                        new CustomEvent(
                            "UIDetectInteractionSkipped"
                        )
                    );


                    removeExistingModal();
                }
            }
        );


        // =============================================
        // CANCEL SCAN BUTTON
        // =============================================

        const cancelButton =
            document.getElementById(
                "uidetect-cancel-scan"
            );


        if(!cancelButton)
        {
            throw new Error(
                "Scan modal Cancel button could not be created."
            );
        }


        cancelButton.addEventListener(
            "click",
            function()
            {
                try
                {
                    console.log(
                        "UIDetect: Cancel Scan clicked."
                    );


                    markInteractionScanCancelled();

                    window.dispatchEvent(
                        new CustomEvent(
                            "UIDetectInteractionCancelled"
                        )
                    );


                    cancelButton.disabled =
                        true;


                    cancelButton.textContent =
                        "Cancelling...";


                    chrome.runtime.sendMessage(
                        {
                            action:
                                "CANCEL_SCAN"
                        },
                        function(response)
                        {
                            if(
                                chrome.runtime.lastError
                            )
                            {
                                logScanModalError(
                                    "Cancel Scan message",
                                    chrome.runtime.lastError.message
                                );

                                removeExistingModal();

                                return;
                            }


                            console.log(
                                "UIDetect: Cancel response:",
                                response
                            );


                            removeExistingModal();
                        }
                    );

                }
                catch(error)
                {
                    logScanModalError(
                        "Cancel Scan button",
                        error
                    );


                    markInteractionScanCancelled();

                    window.dispatchEvent(
                        new CustomEvent(
                            "UIDetectInteractionCancelled"
                        )
                    );


                    removeExistingModal();
                }
            }
        );


        return {
            success: true
        };
    }
    catch(error)
    {
        logScanModalError(
            "showLoadingPopup",
            error
        );

        removeExistingModal();

        return createScanModalError(
            SCAN_MODAL_ERROR_CODES.DOM_ERROR,
            "Unable to display the UIDetect scan window.",
            true
        );
    }
}


/* =====================================================
Backend Unavailable Popup
===================================================== */

function showBackendUnavailablePopup()
{
    try
    {
        console.log(
            "UIDetect: Showing Backend Unavailable popup."
        );


        /*
        -------------------------------------------------
        Replace the existing loading popup.
        -------------------------------------------------
        */

        removeExistingModal();


        if(!document.body)
        {
            throw new Error(
                "Document body is unavailable."
            );
        }


        const overlay =
            document.createElement(
                "div"
            );


        overlay.id =
            MODAL_ID;


        overlay.innerHTML = `

            <div class="uidetect-modal-box">

                <!-- =================================
                     Header
                ================================== -->

                <div class="uidetect-header">

                    🛡 UIDetect Security Scan

                </div>


                <!-- =================================
                     Content
                ================================== -->

                <div class="uidetect-content">

                    <div class="uidetect-section">

                        <h3>
                            ⚠ Backend Unavailable
                        </h3>


                        <p>
                            UIDetect cannot connect
                            to the backend. Please make sure
                            the UIDetect software is running
                            and try again.
                        </p>


                        <p>
                            You can return to the page
                            or continue without the
                            UIDetect security assessment.
                        </p>

                    </div>

                </div>


                <!-- =================================
                     Buttons
                ================================== -->

                <div class="uidetect-buttons">

                    <button
                        id="uidetect-backend-back"
                        type="button">

                        ← Back

                    </button>


                    <button
                        id="uidetect-backend-continue"
                        type="button">

                        Continue →

                    </button>

                </div>

            </div>

        `;


        document.body.appendChild(
            overlay
        );


        console.log(
            "UIDetect: Backend Unavailable popup displayed."
        );


        /* =============================================
           BACK BUTTON
           ============================================= */

        const backButton =
            document.getElementById(
                "uidetect-backend-back"
            );


        if(!backButton)
        {
            throw new Error(
                "Backend Unavailable Back button could not be created."
            );
        }


        backButton.addEventListener(
            "click",
            function()
            {
                try
                {
                    console.log(
                        "UIDetect: Backend Unavailable - Back clicked."
                    );


                    /*
                    -----------------------------------------
                    Cancel the original interaction.

                    IMPORTANT:
                    Do NOT call markInteractionScanCancelled()
                    here.

                    interactionDetector.js is waiting for
                    UIDetectInteractionCancelled and will
                    handle the cancellation.
                    -----------------------------------------
                    */

                    window.dispatchEvent(
                        new CustomEvent(
                            "UIDetectInteractionCancelled"
                        )
                    );


                    removeExistingModal();

                }
                catch(error)
                {
                    logScanModalError(
                        "Backend Unavailable Back button",
                        error
                    );


                    window.dispatchEvent(
                        new CustomEvent(
                            "UIDetectInteractionCancelled"
                        )
                    );


                    removeExistingModal();
                }
            }
        );


        /* =============================================
           CONTINUE BUTTON
           ============================================= */

        const continueButton =
            document.getElementById(
                "uidetect-backend-continue"
            );


        if(!continueButton)
        {
            throw new Error(
                "Backend Unavailable Continue button could not be created."
            );
        }


        continueButton.addEventListener(
            "click",
            function()
            {
                try
                {
                    console.log(
                        "UIDetect: Backend Unavailable - Continue clicked."
                    );


                    /*
                    -----------------------------------------
                    Allow the original interaction to continue
                    without a UIDetect backend assessment.
                    -----------------------------------------
                    */

                    window.dispatchEvent(
                        new CustomEvent(
                            "UIDetectInteractionApproved"
                        )
                    );


                    removeExistingModal();

                }
                catch(error)
                {
                    logScanModalError(
                        "Backend Unavailable Continue button",
                        error
                    );


                    removeExistingModal();
                }
            }
        );


        return {
            success: true
        };

    }
    catch(error)
    {
        logScanModalError(
            "showBackendUnavailablePopup",
            error
        );


        removeExistingModal();


        return createScanModalError(
            SCAN_MODAL_ERROR_CODES.DOM_ERROR,
            "Unable to display the backend unavailable message.",
            true
        );
    }
}



/* =====================================================
Security Warning Popup
===================================================== */

function showScanModal(
    data
)
{
    try
    {
        console.log(
            "========== UIDetect RESULT =========="
        );

        console.log(
            data
        );

        console.log(
            "====================================="
        );


        /* =============================================
           Validate Backend Response
        ============================================= */

        if(
            !data ||
            typeof data !== "object"
        )
        {
            const error =
                createScanModalError(
                    SCAN_MODAL_ERROR_CODES.INVALID_DATA,
                    "Invalid security scan data was received.",
                    false
                );

            logScanModalError(
                "showScanModal",
                error
            );

            showErrorModal(
                error.error.message
            );

            return error;
        }


        /*
        Backend Response:

        {
            success:true,

            scanType:"rightClick",

            assessment:{

                url:"",
                risk:"",
                warning:"",
                recommendation:"",
                score:"",

                openPhish:{
                    listed:false
                }

            }

        }
        */


        const result =
            data.assessment ||
            data;


        if(
            !result ||
            typeof result !== "object"
        )
        {
            const error =
                createScanModalError(
                    SCAN_MODAL_ERROR_CODES.INVALID_DATA,
                    "The security assessment is unavailable.",
                    true
                );

            logScanModalError(
                "showScanModal",
                error
            );

            showErrorModal(
                error.error.message
            );

            return error;
        }


        // =============================================
        // PHASE 12 - OPENPHISH DETECTION
        // =============================================

        const openphish =
            result.openPhish &&
            typeof result.openPhish === "object"

                ?

                result.openPhish

                :

                {};


        /*
        OpenPhish uses "listed"
        as the authoritative result.
        */

        const openphishDetected =
            openphish.listed === true;


        console.log(
            "OpenPhish Result:",
            openphish
        );


        console.log(
            "OpenPhish Detected:",
            openphishDetected
        );


        console.log(
            "Final Result:",
            result
        );


        removeExistingModal();


        if(!document.body)
        {
            throw new Error(
                "Document body is unavailable."
            );
        }


        const overlay =
            document.createElement(
                "div"
            );


        overlay.id =
            MODAL_ID;


        // =============================================
        // Determine Display Values
        // =============================================

        const displayRisk =
            openphishDetected
                ?

                "Critical"

                :

                getDisplayRisk(
                    result
                );


        const displayScore =
            safeScore(
                result.score
            );


        const securityStatus =
            getSecurityStatus(
                result,
                openphishDetected
            );

        const phishingStatus =
            securityStatus.icon +
            " " +
            securityStatus.label;

        const phishingClass =
            securityStatus.className;


        const detectionType =
            getDetectionType(
                data,
                result
            );

        const friendlyDetectionType =
            getFriendlyDetectionType(
                detectionType
            );



        const aboutWebsite =
            escapeHtml(
                safeText(
                    result.aboutWebsite,
                    "UIDetect completed the security assessment."
                )
            );

        const warning =
            escapeHtml(
                safeText(
                    result.warning,
                    "No specific warning was provided."
                )
            );

        const recommendation =
            escapeHtml(
                safeText(
                    result.recommendation,
                    "Review the security results carefully before continuing."
                )
            );


        console.log(
            "Detection Type:",
            detectionType
        );

        console.log(
            "About Website:",
            aboutWebsite
        );

        console.log(
            "Warning:",
            warning
        );

        console.log(
            "Recommendation:",
            recommendation
        );
        const websiteUrl =
            escapeHtml(
                getWebsiteUrl(
                    data,
                    result
                )
            );

        // =============================================
        // Create Modal
        // =============================================

        overlay.innerHTML = `

            <div class="uidetect-modal-box">

                <!-- =================================
                     Header
                ================================== -->

                <div class="uidetect-header">

                    🛡 UIDetect Security Scan

                </div>


                <!-- =================================
                     Content
                ================================== -->

                <div class="uidetect-content">


                    <!-- =============================
                         Website
                    ============================== -->

                    <div class="uidetect-row">

                        <b>
                            Website
                        </b>

                        <span class="uidetect-url">

                            ${websiteUrl}

                        </span>

                    </div>

                    <div style="
                        text-align:center;
                        font-size:14px;
                        font-weight:bold;
                        color:#374151;
                        margin:12px 0;
                    ">
                        ${friendlyDetectionType}
                    </div>


                    <!-- =============================
                         Security Verdict
                    ============================== -->

                    <div class="
                        uidetect-verdict
                        ${phishingClass}">


                        <div class="uidetect-verdict-status">

                            ${securityStatus.icon}
                            ${securityStatus.label}

                        </div>


                    </div>


                    <!-- =============================
                         Security Score
                    ============================== -->

                    <div class="uidetect-row">

                        <b>
                            Security Score
                        </b>


                        <span class="uidetect-score">

                            ${displayScore}/100

                        </span>

                    </div>

                    <!-- =================================
                        What UIDetect Detected
                    ================================== -->

                    <div class="uidetect-section">

                        <h3>
                            What Did UIDetect Find?
                        </h3>

                        <p id="uidetect-about-website">
                            ${aboutWebsite}
                        </p>

                    </div>


                    <!-- =================================
                        Why It Matters
                    ================================== -->

                    <div class="uidetect-section">

                        <h3>
                            What Does This Mean?
                        </h3>

                        <p id="uidetect-warning">
                            ${warning}
                        </p>

                    </div>


                    <!-- =================================
                        What You Should Do
                    ================================== -->

                    <div class="uidetect-section">

                        <h3>
                            What Should You Do?
                        </h3>

                        <p id="uidetect-recommendation">
                            ${recommendation}
                        </p>

                    </div>


                    <!-- =================================
                         Learn More - Dashboard Style
                    ================================== -->

                    ${buildLearnMoreHtml(result)}

                </div> 

                <!-- =================================
                     Buttons
                ================================== -->

                

                <div class="uidetect-buttons">

                    <button
                        id="uidetect-back"
                        type="button">

                        ← Back

                    </button>

                    <button
                        id="uidetect-proceed"
                        type="button">

                        Continue →

                    </button>


                </div>


            </div>

        `;


        document.body.appendChild(
            overlay
        );


        /* =============================================
        VERIFY AI FIELDS WERE RENDERED INTO DOM
        ============================================= */

        const aboutElement =
            document.getElementById(
                "uidetect-about-website"
            );

        const warningElement =
            document.getElementById(
                "uidetect-warning"
            );

        const recommendationElement =
            document.getElementById(
                "uidetect-recommendation"
            );


        console.log(
            "========== UIDetect MODAL DOM CHECK =========="
        );

        console.log(
            "UIDetect About Website DOM:",
            aboutElement?.textContent
        );

        console.log(
            "UIDetect Warning DOM:",
            warningElement?.textContent
        );

        console.log(
            "UIDetect Recommendation DOM:",
            recommendationElement?.textContent
        );

        console.log(
            "About element exists:",
            !!aboutElement
        );

        console.log(
            "Warning element exists:",
            !!warningElement
        );

        console.log(
            "Recommendation element exists:",
            !!recommendationElement
        );

        console.log(
            "==============================================="
        );


        console.log(
            "Warning popup displayed"
        );


        /*
        BACK BUTTON
        */

        const backButton =
            document.getElementById(
                "uidetect-back"
            );


        if(!backButton)
        {
            throw new Error(
                "Scan modal Back button could not be created."
            );
        }


        backButton.addEventListener(
            "click",
            function()
            {
                try
                {
                    console.log(
                        "UIDetect: Back clicked."
                    );

                    window.dispatchEvent(
                        new CustomEvent(
                            "UIDetectInteractionCancelled"
                        )
                    );

                    removeExistingModal();

                    window.history.back();
                }
                catch(error)
                {
                    logScanModalError(
                        "Back button",
                        error
                    );

                    removeExistingModal();
                }
            }
        );


        /*
        CONTINUE BUTTON
        */

        const proceedButton =
            document.getElementById(
                "uidetect-proceed"
            );


        if(!proceedButton)
        {
            throw new Error(
                "Scan modal Continue button could not be created."
            );
        }


        proceedButton.addEventListener(
            "click",
            function()
            {
                try
                {
                    console.log(
                        "UIDetect: Continue clicked."
                    );


                    window.dispatchEvent(
                        new CustomEvent(
                            "UIDetectInteractionApproved"
                        )
                    );


                    removeExistingModal();

                }
                catch(error)
                {
                    logScanModalError(
                        "Continue button",
                        error
                    );

                    removeExistingModal();
                }
            }
        );

        /*
        =============================================
        Modal displayed successfully
        =============================================
        */

        return {
            success: true
        };
    }
    catch(error)
    {
        logScanModalError(
            "showScanModal",
            error
        );

        removeExistingModal();


        showErrorModal(
            "UIDetect could not display the security scan result."
        );


        return createScanModalError(
            SCAN_MODAL_ERROR_CODES.RENDER_ERROR,
            "Unable to display the security scan result.",
            true
        );
    }
}



/* =====================================================
Learn More - Popup Style
===================================================== */

function getLearnMoreStatusClass(value)
{
    const normalized =
        String(value ?? "Unknown")
        .toLowerCase()
        .trim();

    if(
        normalized === "enabled" ||
        normalized === "valid" ||
        normalized === "safe" ||
        normalized === "present" ||
        normalized === "established"
    )
    {
        return "status-safe";
    }

    if(
        normalized === "disabled" ||
        normalized === "invalid" ||
        normalized === "missing"
    )
    {
        return "status-warning";
    }

    if(
        normalized === "unsafe" ||
        normalized === "malicious"
    )
    {
        return "status-danger";
    }

    return "status-neutral";
}


function getLearnMoreStatus(value)
{
    if(
        value === undefined ||
        value === null ||
        String(value).trim() === ""
    )
    {
        return "Unknown";
    }

    return String(value);
}


function getScanModalSecurityValues(result)
{
    const ssl =
        result.ssl &&
        typeof result.ssl === "object"
            ? result.ssl
            : {};

    const headers =
        result.securityHeaders &&
        typeof result.securityHeaders === "object"
            ? result.securityHeaders
            : {};

    const whois =
        result.whois &&
        typeof result.whois === "object"
            ? result.whois
            : {};

    const virusTotal =
        result.virusTotal &&
        typeof result.virusTotal === "object"
            ? result.virusTotal
            : {};

    return {
        https:
            result.https === true
                ? "Enabled"
                : result.https === false
                    ? "Disabled"
                    : "Unknown",

        safeBrowsing:
            getLearnMoreStatus(
                result.safeBrowsing
            ),

        ssl:
            ssl.sslValid === true
                ? "Valid"
                : ssl.sslValid === false
                    ? "Invalid"
                    : "Unknown",

        tls:
            ssl.protocol || "Unknown",

        hsts:
            headers["strict-transport-security"]
                ? "Present"
                : "Missing",

        csp:
            headers["content-security-policy"]
                ? "Present"
                : "Missing",

        xframe:
            headers["x-frame-options"]
                ? "Present"
                : "Missing",

        xcontent:
            headers["x-content-type-options"]
                ? "Present"
                : "Missing",

        referrer:
            headers["referrer-policy"]
                ? "Present"
                : "Missing",

        whois:
            whois.status || "Unknown",

        domainAge:
            whois.domainAge !== undefined &&
            whois.domainAge !== null &&
            whois.domainAge !== ""
                ? String(whois.domainAge) + " years"
                : "Unknown",

        registrar:
            whois.registrar || "Unknown",

        virusTotal: virusTotal
    };
}


function getVirusTotalLearnMoreExplanation(data)
{
    const status =
        data.status || "Unknown";

    const malicious =
        data.malicious ?? 0;

    const suspicious =
        data.suspicious ?? 0;

    const harmless =
        data.harmless ?? 0;

    const normalizedStatus =
        String(status).toLowerCase();

    if(normalizedStatus === "safe")
    {
        if(
            malicious === 0 &&
            suspicious === 0
        )
        {
            return "VirusTotal did not report any malicious or suspicious detections. " +
                   harmless +
                   " security engines considered the website harmless. " +
                   "This does not guarantee complete safety.";
        }

        return "VirusTotal currently classifies the website as safe, although some engine results should still be reviewed.";
    }

    if(normalizedStatus === "warning")
    {
        return "Some VirusTotal security engines considered the website suspicious. Review the website carefully before sharing sensitive information.";
    }

    if(normalizedStatus === "unsafe")
    {
        return "VirusTotal detected malicious activity associated with this website. Avoid continuing and do not enter sensitive information.";
    }

    return "VirusTotal could not provide a result for this website." + 
            "This does not mean the website is unsafe. It means VirusTotal's assessment was unavailable, so UIDetect could not use VirusTotal data in this scan.";
}


function buildPopupStyleSecurityItem(
    title,
    status,
    explanationHtml
)
{
    const safeStatus =
        getLearnMoreStatus(status);

    const statusClass =
        getLearnMoreStatusClass(status);

    return `
        <div class="uidetect-popup-security-item">

            <div class="uidetect-popup-security-header">

                <span class="uidetect-popup-security-title">
                    ${title}
                </span>

                <span class="uidetect-popup-status ${statusClass}">
                    ${escapeHtml(safeStatus)}
                </span>

            </div>

            <details>

                <summary>
                    Learn More
                </summary>

                <div class="uidetect-popup-info-box">
                    ${explanationHtml}
                </div>

            </details>

        </div>
    `;
}


function buildLearnMoreHtml(result)
{
    const values =
        getScanModalSecurityValues(result);

    const vt = values.virusTotal;

    const malicious = vt.malicious ?? 0;
    const suspicious = vt.suspicious ?? 0;
    const harmless = vt.harmless ?? 0;
    const undetected = vt.undetected ?? 0;
    const timeout = vt.timeout ?? 0;
    const vtStatus = vt.status || "Unknown";

    return `
        <details class="uidetect-learn-more">

            <summary>
                Learn More
            </summary>

            <div class="uidetect-learn-more-content">

                <!-- =====================================
                     SECURITY CHECKS
                ====================================== -->

                <div class="uidetect-popup-card">

                    <div class="uidetect-popup-section-heading">

                        <span class="uidetect-popup-section-label">
                            SECURITY CHECKS
                        </span>

                        <h2>
                            Core Protection
                        </h2>

                    </div>

                    ${buildPopupStyleSecurityItem(
                        "HTTPS",
                        values.https,
                        `
                            <strong>What is HTTPS?</strong>
                            <br><br>
                            HTTPS creates a secure connection between your browser and the website.
                            <br><br>
                            <strong>Why does it matter?</strong>
                            <br><br>
                            When HTTPS is enabled, information sent between you and the website is protected while it is being transferred.
                            <br><br>
                            <strong>Important:</strong>
                            <br><br>
                            HTTPS protects the connection, but it does not guarantee that the website itself is trustworthy or free from scams.
                        `
                    )}

                    ${buildPopupStyleSecurityItem(
                        "Google Safe Browsing",
                        values.safeBrowsing,
                        `
                            <strong>What is Google Safe Browsing?</strong>
                            <br><br>
                            Google Safe Browsing checks websites for known dangers such as phishing, malware, and other harmful activities.
                            <br><br>
                            <strong>What does "Safe" mean?</strong>
                            <br><br>
                            A Safe result means Google Safe Browsing did not find a known threat associated with the website at the time of the check.
                            <br><br>
                            <strong>Important:</strong>
                            <br><br>
                            A Safe result does not guarantee that the website is completely safe. UIDetect uses other security checks to provide a broader assessment.
                        `
                    )}

                    ${buildPopupStyleSecurityItem(
                        "SSL Certificate",
                        values.ssl,
                        `
                            <strong>What is an SSL Certificate?</strong>
                            <br><br>
                            An SSL certificate helps a browser verify that a website has a valid certificate and can use a secure connection.
                            <br><br>
                            <strong>Why does it matter?</strong>
                            <br><br>
                            A valid certificate helps protect your connection and shows that the website's certificate is currently valid.
                            <br><br>
                            <strong>Important:</strong>
                            <br><br>
                            A valid certificate does not guarantee that the website is safe or legitimate. Scammers can also use valid certificates.
                        `
                    )}

                    ${buildPopupStyleSecurityItem(
                        "TLS Version",
                        values.tls,
                        `
                            <strong>What is TLS?</strong>
                            <br><br>
                            TLS is the technology that protects information while it travels between your browser and a website.
                            <br><br>
                            <strong>Why does it matter?</strong>
                            <br><br>
                            Newer TLS versions provide stronger and more modern protection for your connection.
                            <br><br>
                            <strong>For example:</strong>
                            <br><br>
                            TLS 1.3 is a modern and secure version of TLS. If UIDetect shows TLS 1.3, the website is using a strong connection protection method.
                        `
                    )}

                </div>


                <!-- =====================================
                     WEBSITE SECURITY SETTINGS
                ====================================== -->

                <div class="uidetect-popup-card">

                    <div class="uidetect-popup-section-heading">

                        <span class="uidetect-popup-section-label">
                            WEBSITE SECURITY SETTINGS
                        </span>

                        <h2>
                            Security Headers
                        </h2>

                    </div>

                    ${buildPopupStyleSecurityItem(
                        "HSTS",
                        values.hsts,
                        `
                            HSTS tells your browser to always use a secure HTTPS connection when visiting this website. This helps prevent attackers from trying to force your connection to use an unsafe connection.
                        `
                    )}

                    ${buildPopupStyleSecurityItem(
                        "Content Security Policy",
                        values.csp,
                        `
                            Content Security Policy helps control which scripts and other content are allowed to run on a website. This can reduce the risk of harmful scripts being used to attack visitors.
                        `
                    )}

                    ${buildPopupStyleSecurityItem(
                        "X-Frame-Options",
                        values.xframe,
                        `
                            X-Frame-Options helps prevent a website from being secretly displayed inside another website. This can help protect you from tricks that make you click something without realizing it.
                        `
                    )}

                    ${buildPopupStyleSecurityItem(
                        "X-Content-Type-Options",
                        values.xcontent,
                        `
                            This setting tells your browser to use the file type provided by the website instead of trying to guess it. This helps prevent some types of unsafe content from being treated incorrectly.
                        `
                    )}

                    ${buildPopupStyleSecurityItem(
                        "Referrer Policy",
                        values.referrer,
                        `
                            Referrer Policy controls how much information about the page you came from is shared when you visit another website. This can help reduce unnecessary sharing of your browsing information.
                        `
                    )}

                </div>


                <!-- =====================================
                     DOMAIN REPUTATION
                ====================================== -->

                <div class="uidetect-popup-card">

                    <div class="uidetect-popup-section-heading">

                        <span class="uidetect-popup-section-label">
                            DOMAIN REPUTATION
                        </span>

                        <h2>
                            Domain Information
                        </h2>

                    </div>

                    ${buildPopupStyleSecurityItem(
                        "WHOIS Status",
                        values.whois,
                        `
                            WHOIS information shows the registration history of a website's domain. UIDetect uses this information to estimate whether the domain is new or has been established for many years. An established domain may have a longer history, but this does not guarantee that the website is safe.
                        `
                    )}

                    ${buildPopupStyleSecurityItem(
                        "Domain Age",
                        values.domainAge,
                        `
                            Domain Age shows how long the website's domain has existed. A very new domain may deserve more caution because it has a short history. An older domain has a longer registration history, but age alone does not mean that a website is trustworthy.
                        `
                    )}

                    ${buildPopupStyleSecurityItem(
                        "Registrar",
                        values.registrar,
                        `
                            The registrar is the company that manages the registration of the website's domain name. It helps maintain the domain registration, but the registrar itself does not determine whether the website is safe.
                        `
                    )}

                </div>


                <!-- =====================================
                     MULTI-ENGINE REPUTATION
                ====================================== -->

                <div class="uidetect-popup-card">

                    <div class="uidetect-popup-section-heading">

                        <span class="uidetect-popup-section-label">
                            MULTI-ENGINE REPUTATION
                        </span>

                        <h2>
                            VirusTotal Analysis
                        </h2>

                    </div>

                    <div class="uidetect-popup-virustotal-status ${getLearnMoreStatusClass(vtStatus)}">
                        ${escapeHtml(getLearnMoreStatus(vtStatus))}
                    </div>

                    <div class="uidetect-popup-reputation-grid">

                        <div class="uidetect-popup-reputation-stat">
                            <span class="uidetect-popup-reputation-value">
                                ${escapeHtml(String(malicious))}
                            </span>
                            <span class="uidetect-popup-reputation-label">
                                Malicious
                            </span>
                        </div>

                        <div class="uidetect-popup-reputation-stat">
                            <span class="uidetect-popup-reputation-value">
                                ${escapeHtml(String(suspicious))}
                            </span>
                            <span class="uidetect-popup-reputation-label">
                                Suspicious
                            </span>
                        </div>

                        <div class="uidetect-popup-reputation-stat">
                            <span class="uidetect-popup-reputation-value">
                                ${escapeHtml(String(harmless))}
                            </span>
                            <span class="uidetect-popup-reputation-label">
                                Harmless
                            </span>
                        </div>

                        <div class="uidetect-popup-reputation-stat">
                            <span class="uidetect-popup-reputation-value">
                                ${escapeHtml(String(undetected))}
                            </span>
                            <span class="uidetect-popup-reputation-label">
                                Undetected
                            </span>
                        </div>

                        <div class="uidetect-popup-reputation-stat">
                            <span class="uidetect-popup-reputation-value">
                                ${escapeHtml(String(timeout))}
                            </span>
                            <span class="uidetect-popup-reputation-label">
                                Timeout
                            </span>
                        </div>

                    </div>

                    <div class="uidetect-popup-info-box uidetect-popup-reputation-explanation">
                        ${escapeHtml(
                            getVirusTotalLearnMoreExplanation(vt)
                        )}
                    </div>

                </div>

            </div>

        </details>
    `;
}


/* =====================================================
Error Modal
===================================================== */

function showErrorModal(
    message
)
{
    try
    {
        removeExistingModal();


        if(!document.body)
        {
            throw new Error(
                "Document body is unavailable."
            );
        }


        const overlay =
            document.createElement(
                "div"
            );


        overlay.id =
            MODAL_ID;


        overlay.innerHTML = `

            <div class="uidetect-modal-box">

                <div class="uidetect-header">

                    🛡 UIDetect Security Scan

                </div>


                <div class="uidetect-content">

                    <div class="uidetect-section">

                        <h3>
                            ⚠ Scan Error
                        </h3>


                        <p>
                            ${safeText(
                                message,
                                "Unable to complete the security scan."
                            )}
                        </p>


                        <p>
                            Please try the scan again.
                        </p>

                    </div>

                </div>


                <div class="uidetect-buttons">

                    <button
                        id="uidetect-error-ok">

                        OK

                    </button>

                </div>

            </div>

        `;


        document.body.appendChild(
            overlay
        );


        const button =
            document.getElementById(
                "uidetect-error-ok"
            );


        if(button)
        {
            button.addEventListener(
                "click",
                function()
                {
                    removeExistingModal();
                }
            );
        }


        return {
            success: true
        };
    }
    catch(error)
    {
        logScanModalError(
            "showErrorModal",
            error
        );

        removeExistingModal();

        return createScanModalError(
            SCAN_MODAL_ERROR_CODES.DOM_ERROR,
            "Unable to display the scan error.",
            false
        );
    }
}


/* =====================================================
Receive Message From Background
===================================================== */

/* =====================================================
Receive Background Messages
===================================================== */

chrome.runtime.onMessage.addListener(

    (request, sender, sendResponse) =>
    {
        console.log(
            "======================================"
        );

        console.log(
            "Content Script Received:"
        );

        console.log(
            request
        );

        console.log(
            "======================================"
        );


        /* =============================================
           Validate Message
           ============================================= */

        const validation =
            validateMessage(
                request
            );


        if(
            !validation.valid
        )
        {
            sendSafeResponse(
                sendResponse,
                validation.error
            );

            return false;
        }


        try
        {
            switch(
                request.action
            )
            {

                /* =====================================
                   SHOW SCAN MODAL
                   ===================================== */

                case "SHOW_SCAN_MODAL":
                {
                    console.log(
                        "UIDetect: SHOW_SCAN_MODAL received."
                    );

                    console.log(
                        "UIDetect: Scan modal data:",
                        request
                    );


                    const modalData =
                        request.data ||
                        request.scanResult ||
                        request.result ||
                        request.assessment;


                    if(
                        !modalData ||
                        typeof modalData !== "object"
                    )
                    {
                        console.error(
                            "UIDetect: SHOW_SCAN_MODAL contains no valid scan data."
                        );


                        const error =
                            createScanModalError(
                                SCAN_MODAL_ERROR_CODES.INVALID_DATA,
                                "No valid security scan result was received.",
                                true
                            );


                        showErrorModal(
                            error.error.message
                        );


                        sendSafeResponse(
                            sendResponse,
                            error
                        );

                        return false;
                    }


                    const result =
                        showScanModal(
                            modalData
                        );


                    sendSafeResponse(
                        sendResponse,
                        result
                    );


                    return false;
                }


                /* =====================================
                   SECURITY WARNING

                   Compatibility replacement for:

                   SHOW_SECURITY_WARNING
                   ===================================== */

                case "SHOW_SECURITY_WARNING":
                {
                    console.log(
                        "UIDetect: SHOW_SECURITY_WARNING received."
                    );

                    console.log(
                        "UIDetect: Redirecting to scanModal.showScanModal()."
                    );


                    const modalData =
                        request.data ||
                        request.scanResult ||
                        request.result ||
                        request.assessment;


                    if(
                        !modalData ||
                        typeof modalData !== "object"
                    )
                    {
                        console.error(
                            "UIDetect: SHOW_SECURITY_WARNING contains no valid scan data."
                        );


                        const error =
                            createScanModalError(
                                SCAN_MODAL_ERROR_CODES.INVALID_DATA,
                                "No valid security warning data was received.",
                                true
                            );


                        showErrorModal(
                            error.error.message
                        );


                        sendSafeResponse(
                            sendResponse,
                            error
                        );


                        return false;
                    }


                    /*
                    Use the same scan modal.

                    No separate warning popup is required.
                    */

                    const result =
                        showScanModal(
                            modalData
                        );


                    sendSafeResponse(
                        sendResponse,
                        result
                    );


                    return false;
                }


                /* =====================================
                   SHOW WARNING LOADING

                   Compatibility replacement for:

                   SHOW_WARNING_LOADING
                   ===================================== */

                case "SHOW_WARNING_LOADING":
                {
                    console.log(
                        "UIDetect: SHOW_WARNING_LOADING received."
                    );

                    console.log(
                        "UIDetect: Redirecting to scanModal.showLoadingPopup()."
                    );


                    const result =
                        showLoadingPopup();


                    sendSafeResponse(
                        sendResponse,
                        result
                    );


                    return false;
                }


                /* =====================================
                   SHOW LOADING

                   General loading action
                   ===================================== */

                case "SHOW_LOADING":
                {
                    console.log(
                        "UIDetect: SHOW_LOADING received."
                    );


                    const result =
                        showLoadingPopup();


                    sendSafeResponse(
                        sendResponse,
                        result
                    );


                    return false;
                }


                /* =====================================
                SHOW BACKEND UNAVAILABLE

                Displayed when the interaction scan
                cannot connect to the backend.
                ===================================== */

                case "SHOW_BACKEND_UNAVAILABLE":
                {
                    console.log(
                        "UIDetect: SHOW_BACKEND_UNAVAILABLE received."
                    );


                    /*
                    -----------------------------------------
                    Replace the loading popup with the
                    Backend Unavailable popup.
                    -----------------------------------------
                    */

                    const result =
                        showBackendUnavailablePopup();


                    sendSafeResponse(
                        sendResponse,
                        result
                    );


                    return false;
                }


                /* =====================================
                   HIDE WARNING LOADING

                   Compatibility replacement for:

                   HIDE_WARNING_LOADING
                   ===================================== */

                case "HIDE_WARNING_LOADING":
                {
                    console.log(
                        "UIDetect: HIDE_WARNING_LOADING received."
                    );

                    console.log(
                        "UIDetect: Redirecting to scanModal.removeExistingModal()."
                    );


                    removeExistingModal();


                    sendSafeResponse(
                        sendResponse,
                        {
                            success: true
                        }
                    );


                    return false;
                }


                /* =====================================
                   CANCEL SCAN
                   ===================================== */

                case "CANCEL_SCAN":
                {
                    console.log(
                        "UIDetect: CANCEL_SCAN received."
                    );


                    sendSafeResponse(
                        sendResponse,
                        {
                            success: true
                        }
                    );


                    return false;
                }


                /* =====================================
                   UNKNOWN ACTION
                   ===================================== */

                default:
                {
                    console.warn(
                        "Unknown action:",
                        request.action
                    );


                    sendSafeResponse(
                        sendResponse,
                        createScanModalError(
                            SCAN_MODAL_ERROR_CODES.INVALID_DATA,
                            "The requested UIDetect action is not supported.",
                            false
                        )
                    );


                    return false;
                }

            }

        }
        catch(error)
        {
            logScanModalError(
                "Background message handler",
                error
            );


            const response =
                createScanModalError(
                    SCAN_MODAL_ERROR_CODES.DOM_ERROR,
                    "UIDetect could not process the requested operation.",
                    true
                );


            sendSafeResponse(
                sendResponse,
                response
            );


            return false;
        }

    }

);