import sys

try:
    sys.stdout.reconfigure(
        encoding="utf-8",
        errors="replace"
    )

    sys.stderr.reconfigure(
        encoding="utf-8",
        errors="replace"
    )
except Exception:
    pass

import logging
import os


# ==========================================================
# UIDetect Backend Logging Module
# ==========================================================
#
# Definition:
# This file provides centralized logging for the UIDetect
# backend.
#
# Responsibilities:
# - Create the backend logs directory.
# - Configure the logging format and output destinations.
# - Store logs in the UIDetect log file.
# - Display logs in the backend console.
# - Provide simple helper functions for INFO, WARNING,
#   and ERROR messages.
#
# This file does NOT:
# - Perform website security checks.
# - Scan websites.
# - Calculate security scores.
# - Generate AI responses.
# - Build AI prompts.
# - Handle API requests.
#
# Other backend modules should use the logging functions
# provided by this file instead of configuring their own
# logger.
# ==========================================================


# ==========================================================
# Create logs folder
# ==========================================================

# UIDetect may be installed under Program Files, which is
# normally protected from standard user write access.
#
# Runtime-generated logs are therefore stored in the user's
# Local AppData directory.

RUNTIME_FOLDER = os.path.join(
    os.environ.get(
        "LOCALAPPDATA",
        os.path.expanduser("~")
    ),
    "UIDetect"
)

LOG_FOLDER = os.path.join(
    RUNTIME_FOLDER,
    "logs"
)

os.makedirs(
    LOG_FOLDER,
    exist_ok=True
)


# ==========================================================
# Force UTF-8 for Console / Redirected Output
# ==========================================================

for stream in (
    sys.stdout,
    sys.stderr
):
    try:
        stream.reconfigure(
            encoding="utf-8",
            errors="replace"
        )
    except Exception:
        pass


# ==========================================================
# Configure Logger
# ==========================================================

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s | %(levelname)s | %(message)s",
    handlers=[
        logging.FileHandler(
            os.path.join(
                LOG_FOLDER,
                "uidetect.log"
            ),
            encoding="utf-8"
        ),
        logging.StreamHandler()
    ]
)

logger = logging.getLogger("UIDetect")

# ==========================================================
# Logging Functions
# ==========================================================

def log_info(message):
    logger.info(message)


def log_warning(message):
    logger.warning(message)


def log_error(message):
    logger.error(message)