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
            label: "High Risk",
            icon: "⚠",
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
            label: "High Risk",
            icon: "⚠",
            className: "risk-high"
        };
    }


    if(
        risk.includes("medium") ||
        risk.includes("moderate")
    )
    {
        return {
            label: "Caution",
            icon: "⚠",
            className: "risk-medium"
        };
    }


    if(
        risk.includes("low") ||
        risk.includes("safe")
    )
    {
        return {
            label: "Low Risk",
            icon: "✓",
            className: "risk-low"
        };
    }


    return {
        label: "Unknown Risk",
        icon: "",
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
            data.scanType,
            ""
        ).toLowerCase();

    const interactionType =
        safeText(
            data.interaction,
            ""
        ).toLowerCase();

    const detectionType =
        safeText(
            data.detectionType,
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
       PRIORITY 2 - Form Detection
       ============================================= */

    if(
        result.formDetected === true ||
        result.googleFormDetected === true ||
        detectionType.includes("form") ||
        scanType.includes("form") ||
        interactionType.includes("form")
    )
    {
        return "form";
    }


    /* =============================================
       PRIORITY 3 - Right Click Scan
       ============================================= */

    if(
        scanType.includes("rightclick") ||
        scanType.includes("right_click") ||
        scanType.includes("right-click")
    )
    {
        return "right-click";
    }


    /* =============================================
       PRIORITY 4 - Interaction Scan
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
            return "Right-Click Scan";

        case "interaction":
            return "Interaction Scan";

        case "form":
            return "Form Detection";

        case "login":
            return "Login Detection";

        default:
            return "Website Scan";
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
                            UIDetect could not connect
                            to the security assessment
                            backend.
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

                    <div class="uidetect-row">

                        <b>
                            Scan Type
                        </b>

                        <span>
                            ${friendlyDetectionType}
                        </span>

                    </div>


                    <!-- =============================
                         Security Verdict
                    ============================== -->

                    <div class="
                        uidetect-verdict
                        ${phishingClass}">


                        <div class="uidetect-verdict-status">

                            ${securityStatus.icon}
                            ${displayRisk} Risk

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
                            🔎 What UIDetect Detected
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
                            ⚠ Why It Matters
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
                            💡 What You Should Do
                        </h3>

                        <p id="uidetect-recommendation">
                            ${recommendation}
                        </p>

                    </div>

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