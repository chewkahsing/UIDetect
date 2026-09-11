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

LOG_FOLDER = "logs"

os.makedirs(LOG_FOLDER, exist_ok=True)

# ==========================================================
# Configure Logger
# ==========================================================

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s | %(levelname)s | %(message)s",
    handlers=[
        logging.FileHandler(f"{LOG_FOLDER}/uidetect.log"),
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