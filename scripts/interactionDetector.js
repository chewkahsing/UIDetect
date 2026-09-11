/* =====================================================
UIDetect Content Error Fallback
===================================================== */

if (
    typeof CONTENT_ERROR_CODES === "undefined"
)
{
    var CONTENT_ERROR_CODES =
    {
        INVALID_REQUEST:
            "CONTENT_INVALID_REQUEST",

        NO_RESPONSE:
            "CONTENT_NO_RESPONSE",

        EXTENSION_CONTEXT_INVALIDATED:
            "CONTENT_EXTENSION_CONTEXT_INVALIDATED"

        
    };
}


if (
    typeof logContentError !== "function"
)
{
    function logContentError(
        source,
        error
    )
    {
        console.error(
            "UIDetect Content Error:",
            source,
            error
        );
    }
}

/* =====================================================
Interaction Detection State
===================================================== */

let popupOpen = false;
let lastInteraction = 0;
let lastInteractionType = "";
let bypassNextInteraction = false;

/* =====================================================
Register Interaction Detection
===================================================== */

document.addEventListener(
    "click",
    detectInteraction,
    true
);

/* =====================================================
Main Interaction Detection
===================================================== */

async function detectInteraction(event)
{
    try
    {
        /*
        =====================================================
        Bypass Re-triggered Approved Interaction
        =====================================================
        */

        if (bypassNextInteraction)
        {
            bypassNextInteraction = false;

            return;
        }


        /*
        =====================================================
        Ignore Interaction While UIDetect Popup Is Open
        =====================================================
        */

        if (popupOpen)
        {
            return;
        }


        /*
        =====================================================
        Validate Event Target
        =====================================================
        */

        let targetElement =
            event.target;


        if (
            targetElement &&
            targetElement.nodeType !== Node.ELEMENT_NODE
        )
        {
            targetElement =
                targetElement.parentElement;
        }


        if (
            !targetElement ||
            typeof targetElement.closest !== "function"
        )
        {
            return;
        }


        /*
        =====================================================
        Ignore UIDetect Modal
        =====================================================
        */

        const uidetectElement =
            targetElement.closest(
                [
                    "#uidetect-scan-modal",
                    "#uidetect-warning-modal",
                    "#uidetect-modal",
                    ".uidetect-modal",
                    ".uidetect-scan-modal",
                    ".uidetect-warning-modal",
                    "[data-uidetect-modal]"
                ].join(", ")
            );


        if (uidetectElement)
        {
            return;
        }


        /*
        =====================================================
        Find Interactive Element
        =====================================================
        */

        const element =
            targetElement.closest(
                "button, a, input, select, textarea, [role='button'], [onclick]"
            );


        if (!element)
        {

            console.log(
                "UIDetect: Clicked element is not interactive.",
                targetElement
            );

            return;
        }

        console.log(
            "UIDetect CLICK DETECTED:",
            {
                tag: element.tagName,
                text: element.innerText || element.textContent || "",
                href: element.getAttribute("href") || "",
                id: element.id || "",
                className: element.className || ""
            }
        );


        /*
        =====================================================
        Analyze Interaction
        =====================================================
        */

        console.log(
            "UIDetect: Analyzing clicked element..."
        );

        const detection =
            analyzeInteraction(element);

        console.log(
            "UIDetect: Analysis result:",
            detection
        );


        if (!detection)
        {
            console.log(
                "UIDetect: No sensitive interaction detected.",
                element
            );

            return;
        }


        console.log(
            "======================================"
        );

        console.log(
            "UIDetect INTERACTION DETECTED:",
            detection.interaction
        );

        console.log(
            "UIDetect SCORE:",
            detection.score
        );

        console.log(
            "UIDetect CONFIDENCE:",
            detection.confidence
        );

        console.log(
            "UIDetect EVIDENCE:",
            detection.evidence
        );

        console.log(
            "======================================"
        );


        /*
        =====================================================
        Minimum Detection Score
        =====================================================
        */

        if (detection.score < 25)
        {
            console.log(
                "UIDetect: Detection score too low.",
                detection
            );

            return;
        }


        /*
        =====================================================
        Duplicate Interaction Protection
        =====================================================
        */

        const currentTime =
            Date.now();


        if (
            detection.interaction === lastInteractionType &&
            currentTime - lastInteraction < 1000
        )
        {
            console.log(
                "UIDetect: Duplicate interaction ignored."
            );

            return;
        }


        lastInteraction =
            currentTime;

        lastInteractionType =
            detection.interaction;


        /*
        =====================================================
        Stop Original Action
        =====================================================
        */

        event.preventDefault();

        event.stopPropagation();


        /*
        =====================================================
        Generate Interaction Event
        =====================================================
        */

        const eventData =
            generateInteractionEvent(
                detection.interaction
            );


        popupOpen = true;


        try
        {
            /*
            =================================================
            Show Loading Popup
            =================================================
            */

            console.log(
                "UIDetect: Showing interaction scan loading popup."
            );


            chrome.runtime.sendMessage(
                {
                    action:
                        "SHOW_LOADING"
                },
                function(response)
                {
                    if (
                        chrome.runtime.lastError
                    )
                    {
                        console.error(
                            "UIDetect: SHOW_LOADING failed:",
                            chrome.runtime.lastError.message
                        );

                        return;
                    }


                    console.log(
                        "UIDetect: Loading popup response:",
                        response
                    );
                }
            );


            /*
            =================================================
            Wait For User Decision Listener
            =================================================
            */

            const decisionPromise =
                waitForInteractionDecision();


            /*
            =================================================
            Interaction Security Assessment
            =================================================
            */

            const scanPromise =
                chrome.runtime.sendMessage(
                {
                    action:
                        "SCAN_INTERACTION",

                    data:
                        eventData
                });


            /*
            =================================================
            Wait For Either User Decision Or Scan Result
            =================================================
            */

            const firstResult =
                await Promise.race(
                    [
                        decisionPromise.then(
                            function(decision)
                            {
                                return {
                                    type:
                                        "decision",

                                    decision:
                                        decision
                                };
                            }
                        ),

                        scanPromise.then(
                            function(result)
                            {
                                return {
                                    type:
                                        "scan",

                                    result:
                                        result
                                };
                            }
                        )
                    ]
                );


            /*
            =================================================
            User Decision Arrived Before Scan
            =================================================
            */

            if (
                firstResult.type === "decision"
            )
            {
                /*
                -------------------------------------------------
                Skip UIDetect Scan
                -------------------------------------------------
                */

                if (
                    firstResult.decision === "skipped"
                )
                {
                    console.log(
                        "UIDetect: User skipped the security scan."
                    );


                    /*
                    Allow the original interaction
                    to continue.
                    */

                    bypassNextInteraction =
                        true;


                    element.dispatchEvent(
                        new MouseEvent(
                            "click",
                            {
                                bubbles:
                                    true,

                                cancelable:
                                    true,

                                view:
                                    window
                            }
                        )
                    );


                    return;
                }


                /*
                -------------------------------------------------
                Cancel Interaction
                -------------------------------------------------
                */

                if (
                    firstResult.decision === "cancelled"
                )
                {
                    console.log(
                        "UIDetect: User cancelled the interaction."
                    );

                    return;
                }
            }


            /*
            =================================================
            Scan Completed Before User Decision
            =================================================
            */

            const assessmentResult =
                firstResult.result;


            console.log(
                "UIDetect: Interaction Security Assessment Result:",
                assessmentResult
            );


            /*
            =================================================
            Cancellation
            =================================================
            */

            if (
                typeof isInteractionScanCancelled === "function" &&
                isInteractionScanCancelled()
            )
            {
                console.log(
                    "UIDetect: Interaction scan cancelled."
                );

                return;
            }


            /*
            =================================================
            Handle Backend / Scan Error
            =================================================
            */

            if (
                !assessmentResult ||
                typeof assessmentResult !== "object" ||
                assessmentResult.success === false ||
                assessmentResult.error
            )
            {
                console.error(
                    "UIDetect: Security scan failed:",
                    assessmentResult
                );

                console.log(
                    "UIDetect: Backend unavailable or scan failed."
                );


                /*
                -------------------------------------------------
                Show Backend Unavailable Popup
                -------------------------------------------------
                */

                chrome.runtime.sendMessage(
                    {
                        action:
                            "SHOW_BACKEND_UNAVAILABLE"
                    },
                    function(response)
                    {
                        if (
                            chrome.runtime.lastError
                        )
                        {
                            console.error(
                                "UIDetect: SHOW_BACKEND_UNAVAILABLE failed:",
                                chrome.runtime.lastError.message
                            );
                        }
                    }
                );


                /*
                -------------------------------------------------
                Wait For User Decision
                -------------------------------------------------
                */

                const backendDecision =
                    await decisionPromise;


                /*
                -------------------------------------------------
                User Selected Continue
                -------------------------------------------------
                */

                if (
                    backendDecision === "approved"
                )
                {
                    console.log(
                        "UIDetect: User chose Continue without backend assessment."
                    );

                    bypassNextInteraction =
                        true;


                    element.dispatchEvent(
                        new MouseEvent(
                            "click",
                            {
                                bubbles:
                                    true,

                                cancelable:
                                    true,

                                view:
                                    window
                            }
                        )
                    );
                }
                else
                {
                    console.log(
                        "UIDetect: User chose Back after backend failure."
                    );
                }


                return;
            }


            const assessment =
                assessmentResult.assessment ||
                assessmentResult;


            if (
                typeof assessment.aboutWebsite !== "string" ||
                !assessment.aboutWebsite.trim() ||

                typeof assessment.warning !== "string" ||
                !assessment.warning.trim() ||

                typeof assessment.recommendation !== "string" ||
                !assessment.recommendation.trim()
            )
            {
                console.error(
                    "UIDetect: Security assessment is missing required AI fields.",
                    assessment
                );

                chrome.runtime.sendMessage(
                    {
                        action:
                            "SHOW_SECURITY_WARNING",

                        data:
                        {
                            success:
                                false,

                            risk:
                                assessment.risk ||
                                "Unknown",

                            warning:
                                "UIDetect could not generate a complete security assessment.",

                            recommendation:
                                "Please try the interaction again."
                        }
                    }
                );

                return;
            }


            /*
            =================================================
            Show Final Security Assessment
            =================================================
            */

            chrome.runtime.sendMessage(
                {
                    action:
                        "SHOW_SECURITY_WARNING",

                    data:
                        assessment
                },
                function(response)
                {
                    if (
                        chrome.runtime.lastError
                    )
                    {
                        console.error(
                            "UIDetect: SHOW_SECURITY_WARNING failed:",
                            chrome.runtime.lastError.message
                        );

                        return;
                    }

                    console.log(
                        "UIDetect: Final security assessment displayed:",
                        response
                    );
                }
            );


            /*
            =================================================
            Wait For Final User Decision
            =================================================
            */

            const proceed =
                await decisionPromise;


            /*
            =================================================
            User Approved
            =================================================
            */

            if (
                proceed === "approved"
            )
            {
                console.log(
                    "UIDetect: User approved interaction."
                );


                bypassNextInteraction =
                    true;


                element.dispatchEvent(
                    new MouseEvent(
                        "click",
                        {
                            bubbles:
                                true,

                            cancelable:
                                true,

                            view:
                                window
                        }
                    )
                );
            }
            else
            {
                console.log(
                    "UIDetect: User cancelled interaction."
                );
            }
        }
        catch(error)
        {
            console.error(
                "UIDetect: Interaction detection error:",
                error
            );


            try
            {
                if (
                    typeof closePopup === "function"
                )
                {
                    closePopup();
                }
            }
            catch(popupError)
            {
                console.error(
                    "UIDetect: Failed to close popup:",
                    popupError
                );
            }
        }
        finally
        {
            popupOpen =
                false;
        }
    }
    catch(error)
    {
        console.error(
            "UIDetect: detectInteraction() failed:",
            error
        );

        popupOpen =
            false;
    }
}


/* =====================================================
Interaction Detection Helpers
===================================================== */

function addEvidence(
    detection,
    condition,
    score,
    message
)
{
    if (!condition)
    {
        return;
    }

    detection.score += score;

    detection.evidence.push(
        message
    );
}


function containsKeyword(
    text,
    keywords
)
{
    return keywords.some(
        keyword =>
            text.includes(keyword)
    );
}


function containsLoginKeyword(text)
{
    return (
        /\blogin\b/i.test(text) ||
        /\blog in\b/i.test(text) ||
        /\bsignin\b/i.test(text) ||
        /\bsign in\b/i.test(text) ||
        /\bsign-in\b/i.test(text) ||
        /\blogon\b/i.test(text) ||
        /\blog on\b/i.test(text) ||
        /\bmasuk\b/i.test(text) ||
        /\blog masuk\b/i.test(text)
    );
}


function calculateConfidence(score)
{
    if (score >= 90)
    {
        return "Very High";
    }

    if (score >= 70)
    {
        return "High";
    }

    if (score >= 50)
    {
        return "Medium";
    }

    if (score >= 30)
    {
        return "Low";
    }

    return "Very Low";
}

function analyzeInteraction(element)
{
    /*
    =====================================================
    Create Detection Object
    =====================================================
    */

    const detection =
    {
        interaction:
            null,

        score:
            0,

        confidence:
            "Unknown",

        evidence:
            []
    };


    /*
    =====================================================
    Detect Interaction Type
    =====================================================
    */

    detection.interaction =
        getInteractionType(
            element
        );


    if (!detection.interaction)
    {
        return null;
    }


    /*
    =====================================================
    Base Interaction Score
    =====================================================
    */

    detection.score +=
        20;

    detection.evidence.push(
        "Interactive Element"
    );


    /*
    =====================================================
    Locate Form
    =====================================================
    */

    const form =
        element.closest(
            "form"
        );


    /*
    =====================================================
    Locate Relevant Container
    =====================================================
    */

    const container =
        element.closest(
            "[role='dialog'], dialog, section, article, main, aside, nav, div"
        );


    /*
    =====================================================
    Form Context
    =====================================================
    */

    const formContext =
    {
        action:
            "",

        method:
            "",

        id:
            "",

        className:
            ""
    };


    /*
    =====================================================
    Container Context
    =====================================================
    */

    const containerContext =
    {
        id:
            "",

        className:
            "",

        role:
            ""
    };


    /*
    =====================================================
    Read Form Information
    =====================================================
    */

    if (form)
    {
        formContext.action =
            (
                form.action ||
                ""
            ).toLowerCase();


        formContext.method =
            (
                form.method ||
                ""
            ).toLowerCase();


        formContext.id =
            (
                form.id ||
                ""
            ).toLowerCase();


        formContext.className =
            (
                typeof form.className === "string"
                    ? form.className
                    : ""
            ).toLowerCase();
    }


    /*
    =====================================================
    Read Container Information
    =====================================================
    */

    if (container)
    {
        containerContext.id =
            (
                container.id ||
                ""
            ).toLowerCase();


        containerContext.className =
            (
                typeof container.className === "string"
                    ? container.className
                    : ""
            ).toLowerCase();


        containerContext.role =
            (
                container.getAttribute("role") ||
                ""
            ).toLowerCase();
    }


    /*
    =====================================================
    Apply Interaction Context
    =====================================================
    */

    applyInteractionContext(
        detection,
        form,
        formContext,
        containerContext,
        element
    );


    detection.confidence =
        calculateConfidence(
            detection.score
        );
    

    /*
    =====================================================
    Debug Output
    =====================================================
    */

    console.log(
        "UIDetect Detection:",
        detection
    );


    return detection;
}

/*
|--------------------------------------------------------------------------
| Login Context
|--------------------------------------------------------------------------
*/

function applyLoginContext(
    detection,
    form,
    formContext,
    containerContext,
    element
)
{
    /* =====================================================
        Explicit Login Control
        ===================================================== */

        if (element)
        {
            const tagName =
                (
                    element.tagName ||
                    ""
                ).toLowerCase();

            const isInteractiveElement =
                (
                    tagName === "button" ||
                    tagName === "input" ||
                    tagName === "a" ||
                    tagName === "select" ||
                    tagName === "textarea"
                );

            if (isInteractiveElement)
            {
                const elementText =
                    (
                        element.innerText ||
                        element.textContent ||
                        element.value ||
                        ""
                    ).toLowerCase().trim();

                const ariaLabel =
                    (
                        element.getAttribute("aria-label") ||
                        ""
                    ).toLowerCase().trim();

                const title =
                    (
                        element.getAttribute("title") ||
                        ""
                    ).toLowerCase().trim();




                const elementId =
                    (
                        element.id ||
                        ""
                    ).toLowerCase();

                const elementClass =
                    (
                        typeof element.className === "string"
                            ? element.className
                            : ""
                    ).toLowerCase();

                const loginSources =
                    [
                        elementText,
                        ariaLabel,
                        title,
                        elementId,
                        elementClass
                    ].join(" ");

                if (
                    containsLoginKeyword(loginSources)
                )
                {
                    detection.score += 50;

                    detection.evidence.push(
                        "Explicit Login Control"
                    );
                }
            }
        }


    /*
    =====================================================
    POST Method
    =====================================================
    */

    if (
        formContext.method === "post"
    )
    {
        detection.score +=
            10;

        detection.evidence.push(
            "POST Method"
        );
    }


    /*
    =====================================================
    Login Form ID
    =====================================================
    */

    if (
        formContext.id.includes("login") ||
        formContext.id.includes("signin") ||
        formContext.id.includes("sign-in") ||
        formContext.id.includes("auth") ||
        formContext.id.includes("masuk")
    )
    {
        detection.score +=
            15;

        detection.evidence.push(
            "Login Form ID"
        );
    }


    /*
    =====================================================
    Login Form Class
    =====================================================
    */

    if (
        formContext.className.includes("login") ||
        formContext.className.includes("signin") ||
        formContext.className.includes("sign-in") ||
        formContext.className.includes("auth") ||
        formContext.className.includes("masuk")
    )
    {
        detection.score +=
            15;

        detection.evidence.push(
            "Login Form Class"
        );
    }


    /*
    =====================================================
    Login Container ID
    =====================================================
    */

    addEvidence(
        detection,

        containsKeyword(
            containerContext.id,
            [
                "login",
                "signin",
                "sign-in",
                "auth",
                "masuk"
            ]
        ),

        15,

        "Login Container ID"
    );


    /*
    =====================================================
    Login Container Class
    =====================================================
    */

    addEvidence(
        detection,

        containsKeyword(
            containerContext.className,
            [
                "login",
                "signin",
                "sign-in",
                "auth",
                "masuk"
            ]
        ),

        15,

        "Login Container Class"
    );


    /*
    =====================================================
    Login Dialog
    =====================================================
    */

    addEvidence(
        detection,

        containerContext.role === "dialog",

        10,

        "Login Dialog"
    );
}




/*
|--------------------------------------------------------------------------
| Registration Context
|--------------------------------------------------------------------------
*/

function applyRegistrationContext(
    detection,
    form,
    formContext,
    containerContext
)
{

if (detection.interaction === "Registration")
{

    if
    (
        formContext.action.includes("register") ||

        formContext.action.includes("signup") ||

        formContext.action.includes("sign-up") ||

        formContext.action.includes("create-account") ||

        formContext.action.includes("createaccount")
    )
    {

        detection.score += 30;

        detection.evidence.push(
            "Registration Form Action"
        );

    }

}
if
(
    detection.interaction === "Registration" &&

    formContext.method === "post"
)
{

    detection.score += 20;

    detection.evidence.push(
        "POST Method"
    );

}
if
(
    detection.interaction === "Registration"
)
{

    if
    (
        formContext.id.includes("register") ||

        formContext.id.includes("signup") ||

        formContext.id.includes("sign-up") ||

        formContext.id.includes("create")
    )
    {

        detection.score += 15;

        detection.evidence.push(
            "Registration Form ID"
        );

    }

}
if
(
    detection.interaction === "Registration"
)
{

    if
    (
        formContext.className.includes("register") ||

        formContext.className.includes("signup") ||

        formContext.className.includes("sign-up") ||

        formContext.className.includes("create")
    )
    {

        detection.score += 15;

        detection.evidence.push(
            "Registration Form Class"
        );

    }

}
/*
|--------------------------------------------------------------------------
| Registration Password Field
|--------------------------------------------------------------------------
*/

if (form)
{

    const passwordField =
        form.querySelector(
            "input[type='password']"
        );

    addEvidence(

        detection,

        passwordField,

        20,

        "Registration Password"

    );

}
/*
|--------------------------------------------------------------------------
| Confirm Password Detection
|--------------------------------------------------------------------------
*/

if (form)
{

    const passwordFields =
        form.querySelectorAll(
            "input[type='password']"
        );

    addEvidence(

        detection,

        passwordFields.length >= 2,

        25,

        "Confirm Password"

    );

}

/*
|--------------------------------------------------------------------------
| Parent Container Detection
| Module 9
|--------------------------------------------------------------------------
*/

addEvidence(
    detection,
    containsKeyword(
        containerContext.id,
        ["register", "signup", "create"]
    ),
    15,
    "Registration Container ID"
);

addEvidence(
    detection,
    containsKeyword(
        containerContext.className,
        ["register", "signup", "create"]
    ),
    15,
    "Registration Container Class"
);

addEvidence(
    detection,
    containerContext.role === "dialog",
    10,
    "Registration Dialog"
);
}


/*
|--------------------------------------------------------------------------
| Upload Context
|--------------------------------------------------------------------------
*/

function applyUploadContext(
    detection,
    form,
    formContext,
    containerContext,
    element
)
{

if (detection.interaction === "Upload")
{

        detection.score += 20;

        detection.evidence.push(
            "Upload Keyword"
        );

    if
    (
        formContext.action.includes("upload") ||

        formContext.action.includes("import") ||

        formContext.action.includes("attachment") ||

        formContext.action.includes("file")
    )
    {

        detection.score += 30;

        detection.evidence.push(
            "Upload Form Action"
        );

    }

}
if
(
    detection.interaction === "Upload" &&

    formContext.method === "post"
)
{

    detection.score += 20;

    detection.evidence.push(
        "POST Method"
    );

}
if
(
    detection.interaction === "Upload"
)
{

    if
    (
        formContext.id.includes("upload") ||

        formContext.id.includes("import") ||

        formContext.id.includes("attachment") ||

        formContext.id.includes("file")
    )
    {

        detection.score += 15;

        detection.evidence.push(
            "Upload Form ID"
        );

    }

}
if
(
    detection.interaction === "Upload"
)
{

    if
    (
        formContext.className.includes("upload") ||

        formContext.className.includes("import") ||

        formContext.className.includes("attachment") ||

        formContext.className.includes("file")
    )
    {

        detection.score += 15;

        detection.evidence.push(
            "Upload Form Class"
        );

    }

}
if
(
    detection.interaction === "Upload" &&

    form
)
{

    const fileInput =
        form.querySelector(
            "input[type='file']"
        );

    if (fileInput)
    {

        detection.score += 35;

        detection.evidence.push(
            "File Input Detected"
        );

    }

}

/*
|--------------------------------------------------------------------------
| Parent Container Detection
| Module 9
|--------------------------------------------------------------------------
*/

addEvidence(
    detection,
    containsKeyword(
        containerContext.id,
        ["upload", "import", "file"]
    ),
    15,
    "Upload Container ID"
);

addEvidence(
    detection,
    containsKeyword(
        containerContext.className,
        ["upload", "import", "file"]
    ),
    15,
    "Upload Container Class"
);

addEvidence(
    detection,
    containerContext.role === "dialog",
    10,
    "Upload Dialog"
);

}


/*
|--------------------------------------------------------------------------
| Download Context
|--------------------------------------------------------------------------
*/

function applyDownloadContext(
    detection,
    form,
    formContext,
    containerContext,
    element
    
)
{

if (detection.interaction === "Download")
{

    if
    (
        formContext.action.includes("download") ||

        formContext.action.includes("export") ||

        formContext.action.includes("file") ||

        formContext.action.includes("report")
    )
    {

        detection.score += 30;

        detection.evidence.push(
            "Download Form Action"
        );

    }

}
if
(
    detection.interaction === "Download"
)
{

    if
    (
        formContext.id.includes("download") ||

        formContext.id.includes("export") ||

        formContext.id.includes("report")
    )
    {

        detection.score += 15;

        detection.evidence.push(
            "Download Form ID"
        );

    }

}

if
(
    detection.interaction === "Download"
)
{

    if
    (
        formContext.className.includes("download") ||

        formContext.className.includes("export") ||

        formContext.className.includes("report")
    )
    {

        detection.score += 15;

        detection.evidence.push(
            "Download Form Class"
        );

    }

}

if
(
    detection.interaction === "Download"
)
{

    const href =
        (
            element.getAttribute("href") ||
            ""
        ).toLowerCase();

    if
    (
        href.endsWith(".pdf") ||

        href.endsWith(".zip") ||

        href.endsWith(".doc") ||

        href.endsWith(".docx") ||

        href.endsWith(".xls") ||

        href.endsWith(".xlsx") ||

        href.endsWith(".csv") ||

        href.endsWith(".ppt") ||

        href.endsWith(".pptx")
    )
    {

        detection.score += 35;

        detection.evidence.push(
            "Download File Extension"
        );

    }

}

if
(
    detection.interaction === "Download"
)
{

    if
    (
        element.hasAttribute("download")
    )
    {

        detection.score += 25;

        detection.evidence.push(
            "Download Attribute"
        );

    }

}
/*
|--------------------------------------------------------------------------
| Parent Container Detection
| Module 9
|--------------------------------------------------------------------------
*/
addEvidence(
    detection,
    containsKeyword(
        containerContext.id,
        ["download", "export", "report"]
    ),
    15,
    "Download Container ID"
);

addEvidence(
    detection,
    containsKeyword(
        containerContext.className,
        ["download", "export", "report"]
    ),
    15,
    "Download Container Class"
);

addEvidence(
    detection,
    containerContext.role === "dialog",
    10,
    "Download Dialog"
);

}

/*
|--------------------------------------------------------------------------
| Payment Context
|--------------------------------------------------------------------------
*/

function applyPaymentContext(
    detection,
    form,
    formContext,
    containerContext
)
{

if (detection.interaction === "Payment")
{

    if
    (
        formContext.action.includes("payment") ||

        formContext.action.includes("pay") ||

        formContext.action.includes("checkout") ||

        formContext.action.includes("billing") ||

        formContext.action.includes("purchase") ||

        formContext.action.includes("order")
    )
    {

        detection.score += 30;

        detection.evidence.push(
            "Payment Form Action"
        );

    }

}
if
(
    detection.interaction === "Payment" &&

    formContext.method === "post"
)
{

    detection.score += 20;

    detection.evidence.push(
        "POST Method"
    );

}
if
(
    detection.interaction === "Payment"
)
{

    if
    (
        formContext.id.includes("payment") ||

        formContext.id.includes("checkout") ||

        formContext.id.includes("billing") ||

        formContext.id.includes("pay")
    )
    {

        detection.score += 15;

        detection.evidence.push(
            "Payment Form ID"
        );

    }

}if
(
    detection.interaction === "Payment"
)
{

    if
    (
        formContext.className.includes("payment") ||

        formContext.className.includes("checkout") ||

        formContext.className.includes("billing") ||

        formContext.className.includes("pay")
    )
    {

        detection.score += 15;

        detection.evidence.push(
            "Payment Form Class"
        );

    }

}if
(
    detection.interaction === "Payment" &&

    form
)
{

    const cardNumber =
        form.querySelector(
            "input[name*='card'], input[id*='card']"
        );

    if (cardNumber)
    {

        detection.score += 25;

        detection.evidence.push(
            "Card Number Field"
        );

    }

}if
(
    detection.interaction === "Payment" &&

    form
)
{

    const cvv =
        form.querySelector(
            "input[name*='cvv'], input[id*='cvv'], input[name*='cvc'], input[id*='cvc']"
        );

    if (cvv)
    {

        detection.score += 20;

        detection.evidence.push(
            "CVV Field"
        );

    }

}if
(
    detection.interaction === "Payment" &&

    form
)
{

    const expiry =
        form.querySelector(
            "input[name*='expiry'], input[id*='expiry'], input[name*='exp'], input[id*='exp']"
        );

    if (expiry)
    {

        detection.score += 15;

        detection.evidence.push(
            "Expiry Date Field"
        );

    }

}if
(
    detection.interaction === "Payment" &&

    form
)
{

    const billing =
        form.querySelector(
            "input[name*='billing'], input[id*='billing'], input[name*='address'], input[id*='address']"
        );

    if (billing)
    {

        detection.score += 10;

        detection.evidence.push(
            "Billing Address Field"
        );

    }

}

/*
|--------------------------------------------------------------------------
| Parent Container Detection
| Module 9
|--------------------------------------------------------------------------
*/
addEvidence(
    detection,
    containsKeyword(
        containerContext.id,
        ["payment", "checkout", "billing"]
    ),
    15,
    "Payment Container ID"
);

addEvidence(
    detection,
    containsKeyword(
        containerContext.className,
        ["payment", "checkout", "billing"]
    ),
    15,
    "Payment Container Class"
);

addEvidence(
    detection,
    containerContext.role === "dialog",
    10,
    "Payment Dialog"
);

}

/*
|--------------------------------------------------------------------------
| Logout Context
|--------------------------------------------------------------------------
*/

function applyLogoutContext(
    detection,
    form,
    formContext,
    containerContext
)
{

if (detection.interaction === "Logout")
{

    if
    (
        formContext.action.includes("logout") ||

        formContext.action.includes("signout") ||

        formContext.action.includes("sign-out") ||

        formContext.action.includes("logoff") ||

        formContext.action.includes("session")
    )
    {

        detection.score += 30;

        detection.evidence.push(
            "Logout Form Action"
        );

    }

}
if
(
    detection.interaction === "Logout" &&

    formContext.method === "post"
)
{

    detection.score += 15;

    detection.evidence.push(
        "POST Method"
    );

}
if
(
    detection.interaction === "Logout"
)
{

    if
    (
        formContext.id.includes("logout") ||

        formContext.id.includes("signout") ||

        formContext.id.includes("session")
    )
    {

        detection.score += 15;

        detection.evidence.push(
            "Logout Form ID"
        );

    }

}
if
(
    detection.interaction === "Logout"
)
{

    if
    (
        formContext.className.includes("logout") ||

        formContext.className.includes("signout") ||

        formContext.className.includes("session")
    )
    {

        detection.score += 15;

        detection.evidence.push(
            "Logout Form Class"
        );

    }

}
if
(
    detection.interaction === "Logout" &&

    form
)
{

    const logoutInput =
        form.querySelector(
            "input[value*='logout'], input[name*='logout']"
        );

    if (logoutInput)
    {

        detection.score += 20;

        detection.evidence.push(
            "Logout Hidden Field"
        );

    }

}if
(
    detection.interaction === "Logout" &&

    form
)
{

    const token =
        form.querySelector(
            "input[name*='csrf'], input[name*='token'], input[name*='session']"
        );

    if (token)
    {

        detection.score += 20;

        detection.evidence.push(
            "Session Token"
        );

    }

}
/*
|--------------------------------------------------------------------------
| Parent Container Detection
| Module 9
|--------------------------------------------------------------------------
*/
addEvidence(
    detection,
    containsKeyword(
        containerContext.id,
        ["logout", "signout", "session"]
    ),
    15,
    "Logout Container ID"
);

addEvidence(
    detection,
    containsKeyword(
        containerContext.className,
        ["logout", "signout", "session"]
    ),
    15,
    "Logout Container Class"
);

addEvidence(
    detection,
    containerContext.role === "dialog",
    10,
    "Logout Dialog"
);
}

/* =====================================================
Apply Interaction Context
===================================================== */

function applyInteractionContext(
    detection,
    form,
    formContext,
    containerContext,
    element
)
{
    switch(detection.interaction)
    {
        case "Login":

            applyLoginContext(
                detection,
                form,
                formContext,
                containerContext,
                element
            );

            break;


        case "Registration":

            applyRegistrationContext(
                detection,
                form,
                formContext,
                containerContext
            );

            break;


        case "Upload":

            applyUploadContext(
                detection,
                form,
                formContext,
                containerContext,
                element
            );

            break;


        case "Download":

            applyDownloadContext(
                detection,
                form,
                formContext,
                containerContext,
                element
            );

            break;


        case "Payment":

            applyPaymentContext(
                detection,
                form,
                formContext,
                containerContext
            );

            break;


        case "Logout":

            applyLogoutContext(
                detection,
                form,
                formContext,
                containerContext
            );

            break;
    }
}


/*
|--------------------------------------------------------------------------
| Interaction Analysis
|--------------------------------------------------------------------------
*/
function getInteractionType(element)
{
    /*
    =====================================================
    Basic Element Information
    =====================================================
    */

    const text =
        (
            element.innerText ||
            element.textContent ||
            element.value ||
            ""
        ).toLowerCase().trim();


    const id =
        (
            element.id ||
            ""
        ).toLowerCase();


    const className =
        (
            typeof element.className === "string"
                ? element.className
                : ""
        ).toLowerCase();


    const name =
        (
            element.getAttribute("name") ||
            ""
        ).toLowerCase();


    const ariaLabel =
        (
            element.getAttribute("aria-label") ||
            ""
        ).toLowerCase();


    const title =
        (
            element.getAttribute("title") ||
            ""
        ).toLowerCase();


    const type =
        (
            element.getAttribute("type") ||
            ""
        ).toLowerCase();


    const role =
        (
            element.getAttribute("role") ||
            ""
        ).toLowerCase();
    
    const href =
        (
            element.getAttribute("href") ||
            ""
        ).toLowerCase();


    /*
    =====================================================
    Combined Element Source
    =====================================================
    */

    const source =
        [
            text,
            id,
            className,
            name,
            ariaLabel,
            title,
            href,
            type,
            role
        ].join(" ");


    console.log(
        "UIDetect Detection Source:",
        source
    );


    /*
    =====================================================
    Form Information
    =====================================================
    */

    const form =
        element.closest(
            "form"
        );


    let formSource =
        "";


    if (form)
    {
        const formAction =
            (
                form.action ||
                ""
            ).toLowerCase();


        const formId =
            (
                form.id ||
                ""
            ).toLowerCase();


        const formClass =
            (
                typeof form.className === "string"
                    ? form.className
                    : ""
            ).toLowerCase();


        const formName =
            (
                form.getAttribute("name") ||
                ""
            ).toLowerCase();


        formSource =
            [
                formAction,
                formId,
                formClass,
                formName
            ].join(" ");
    }


    /*
    =====================================================
    LOGIN DETECTION
    =====================================================
    */

    /*
    ---------------------------------------------
    Explicit Login Control
    ---------------------------------------------
    */

    const loginKeywordDetected =
        containsLoginKeyword(
            [
                text,
                id,
                className,
                name,
                ariaLabel,
                title,
                type,
                role
            ].join(" ")
        );


    if (loginKeywordDetected)
    {
        /*
        Only classify as Login when the element
        itself appears to be an actual login control.

        Do not classify ordinary article links or
        content links that merely mention "login".
        */

        const isButton =
            (
                type === "submit" ||
                role === "button"
            );


        const isLoginInput =
            (
                type === "password" ||
                type === "email"
            );


        const loginControl =
            (
                isButton ||
                isLoginInput
            );


        if (loginControl)
        {
            return "Login";
        }


        /*
        ---------------------------------------------
        Login Form Context
        ---------------------------------------------
        */

        if (form)
        {
            const passwordField =
                form.querySelector(
                    "input[type='password']"
                );


            const usernameField =
                form.querySelector(
                    "input[type='email'], " +
                    "input[name*='user'], " +
                    "input[name*='username'], " +
                    "input[name*='email'], " +
                    "input[id*='user'], " +
                    "input[id*='username'], " +
                    "input[id*='email']"
                );


            if (
                passwordField &&
                usernameField
            )
            {
                return "Login";
            }
        }
    }


    /*
    =====================================================
    REGISTRATION
    =====================================================
    */

    if (
        source.includes("register") ||
        source.includes("registration") ||
        source.includes("signup") ||
        source.includes("sign up") ||
        source.includes("sign-up") ||
        source.includes("create account") ||
        source.includes("create-account") ||
        source.includes("daftar")
    )
    {
        return "Registration";
    }


    if (
        formSource.includes("register") ||
        formSource.includes("signup") ||
        formSource.includes("sign-up") ||
        formSource.includes("create-account") ||
        formSource.includes("createaccount") ||
        formSource.includes("daftar")
    )
    {
        return "Registration";
    }


    /*
    =====================================================
    UPLOAD
    =====================================================
    */

    if (
        source.includes("upload") ||
        source.includes("import") ||
        source.includes("attachment") 
    )
    {
        return "Upload";
    }


    if (
        formSource.includes("upload") ||
        formSource.includes("import") ||
        formSource.includes("attachment")
    )
    {
        return "Upload";
    }


    /*
    =====================================================
    DOWNLOAD
    =====================================================
    */

    if (
        source.includes("download") ||
        source.includes("export") ||
        source.includes("save file")
    )
    {
        return "Download";
    }


    if (
        element.hasAttribute("download")
    )
    {
        return "Download";
    }


    if (
        href.endsWith(".pdf") ||
        href.endsWith(".zip") ||
        href.endsWith(".doc") ||
        href.endsWith(".docx") ||
        href.endsWith(".xls") ||
        href.endsWith(".xlsx") ||
        href.endsWith(".csv") ||
        href.endsWith(".ppt") ||
        href.endsWith(".pptx")
    )
    {
        return "Download";
    }


    /*
    =====================================================
    PAYMENT
    =====================================================
    */

    /*
    -----------------------------------------------------
    Determine Whether Element Is a Payment Action
    -----------------------------------------------------
    */

    const isPaymentAction =
    (
        type === "submit" ||
        role === "button"
    );


    /*
    -----------------------------------------------------
    Payment Button Keywords
    -----------------------------------------------------
    */

    const paymentActionKeyword =
    (
        source.includes("payment") ||
        source.includes("checkout") ||
        source.includes("pay now") ||
        source.includes("place order") ||
        source.includes("confirm order") ||
        source.includes("buy now") ||
        source.includes("purchase")
    );


    /*
    -----------------------------------------------------
    Payment Form Context
    -----------------------------------------------------
    */

    const paymentFormDetected =
    (
        formSource.includes("payment") ||
        formSource.includes("checkout") ||
        formSource.includes("purchase") ||
        formSource.includes("billing") ||
        formSource.includes("order")
    );


    /*
    -----------------------------------------------------
    Payment Detection
    -----------------------------------------------------

    Only classify Payment when:

    1. The clicked element is an action
    AND
    2. The action or its form indicates payment

    This prevents payment fields such as
    Card Number, CVV and Expiry from triggering
    the security scan.
    -----------------------------------------------------
    */

    if (
        isPaymentAction &&
        (
            paymentActionKeyword ||
            paymentFormDetected
        )
    )
    {
        return "Payment";
    }


    /*
    =====================================================
    LOGOUT
    =====================================================
    */

    if (
        source.includes("logout") ||
        source.includes("log out") ||
        source.includes("signout") ||
        source.includes("sign out") ||
        source.includes("sign-out") ||
        source.includes("logoff") ||
        source.includes("log off") ||
        source.includes("keluar")
    )
    {
        return "Logout";
    }


    if (
        formSource.includes("logout") ||
        formSource.includes("signout") ||
        formSource.includes("sign-out") ||
        formSource.includes("logoff")
    )
    {
        return "Logout";
    }


    /*
    =====================================================
    NO SENSITIVE INTERACTION
    =====================================================
    */

    console.log(
        "UIDetect: No interaction type identified."
    );


    return null;
}


/* =====================================================
Wait For Interaction Decision
===================================================== */

function waitForInteractionDecision()
{
    return new Promise(
        function(resolve)
        {
            function handleApproved()
            {
                cleanup();

                console.log(
                    "UIDetect: Interaction decision = APPROVED"
                );

                resolve(
                    "approved"
                );
            }


            function handleCancelled()
            {
                cleanup();

                console.log(
                    "UIDetect: Interaction decision = CANCELLED"
                );

                resolve(
                    "cancelled"
                );
            }


            function handleSkipped()
            {
                cleanup();

                console.log(
                    "UIDetect: Interaction decision = SKIPPED"
                );

                resolve(
                    "skipped"
                );
            }


            function cleanup()
            {
                window.removeEventListener(
                    "UIDetectInteractionApproved",
                    handleApproved
                );

                window.removeEventListener(
                    "UIDetectInteractionCancelled",
                    handleCancelled
                );

                window.removeEventListener(
                    "UIDetectInteractionSkipped",
                    handleSkipped
                );
            }


            window.addEventListener(
                "UIDetectInteractionApproved",
                handleApproved,
                {
                    once: true
                }
            );


            window.addEventListener(
                "UIDetectInteractionCancelled",
                handleCancelled,
                {
                    once: true
                }
            );


            window.addEventListener(
                "UIDetectInteractionSkipped",
                handleSkipped,
                {
                    once: true
                }
            );
        }
    );
}




/* =====================================================
Generate Interaction Event
===================================================== */

function generateInteractionEvent(
    type
)
{

    try
    {

        const eventData =
        {

            website:
                window.location.href,

            interaction:
                type.toUpperCase(),

            page:
                window.location.pathname,

            timestamp:
                new Date().toISOString()

        };


        console.log(
            "Interaction Event:",
            eventData
        );


        /*
        =============================================
        Create Custom Event
        =============================================
        */

        try
        {

            const interactionEvent =
                new CustomEvent(
                    "UIDetectInteraction",
                    {
                        detail:
                            eventData
                    }
                );


            window.dispatchEvent(
                interactionEvent
            );

        }

        catch(error)
        {

            logContentError(
                "generateInteractionEvent.dispatch",
                error
            );

        }


        return eventData;

    }

    catch(error)
    {

        logContentError(
            "generateInteractionEvent",
            error
        );


        return {

            website:
                window.location.href ||
                "",

            interaction:
                type ||
                "Unknown",

            page:
                window.location.pathname ||
                "",

            timestamp:
                new Date().toISOString()

        };

    }

}


/* =====================================================
Export Function
===================================================== */

try
{

    window.generateInteractionEvent =
        generateInteractionEvent;

}

catch(error)
{

    logContentError(
        "generateInteractionEvent.export",
        error
    );

}