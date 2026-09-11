/* =====================================================
UIDetect - Content Script

Purpose:
- Initialize UIDetect content script
- Detect current webpage
- Provide basic page security helpers

Interaction detection:
Handled by interactionDetector.js

Security scan modal:
Handled by scanModal.js
===================================================== */



/* =====================================================
Centralized Content Script Error Logger
===================================================== */

function logContentError(
    context,
    error
)
{
    console.error(
        "======================================"
    );

    console.error(
        "UIDetect Content Script Error"
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
Initialize Content Script
===================================================== */

function initializeContentScript()
{
    try
    {
        console.log(
            "======================================"
        );

        console.log(
            "UIDetect Content Script Loaded."
        );

        console.log(
            "======================================"
        );
    }
    catch(error)
    {
        logContentError(
            "initializeContentScript",
            error
        );
    }
}


/* =====================================================
Detect Current Website
===================================================== */

function detectCurrentWebsite()
{
    try
    {
        const currentURL =
            window.location.href;

        console.log(
            "Current Website:",
            currentURL
        );

        return currentURL;
    }
    catch(error)
    {
        logContentError(
            "detectCurrentWebsite",
            error
        );

        return null;
    }
}




/* =====================================================
Start Content Script
===================================================== */

function startContentScript()
{
    try
    {
        initializeContentScript();

        detectCurrentWebsite();
    }
    catch(error)
    {
        logContentError(
            "startContentScript",
            error
        );
    }
}


/* =====================================================
Start
===================================================== */

if(
    document.readyState === "loading"
)
{
    window.addEventListener(
        "load",
        startContentScript,
        {
            once: true
        }
    );
}
else
{
    startContentScript();
}


/* =====================================================
Startup Logging
===================================================== */

console.log(
    "UIDetect content.js ready."
);