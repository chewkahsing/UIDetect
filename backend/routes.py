from flask import Blueprint, request, jsonify
import threading

from scanner import scan_website

from logger import (
    log_info,
    log_warning,
    log_error
)


# ==========================================================
# UIDetect API Routes
#
# Responsibility:
# - Define Flask API endpoints used by the extension.
# - Receive and validate incoming JSON requests.
# - Route requests to the appropriate backend modules.
# - Return standardized JSON responses.
# - Manage active scan cancellation events.
#
# This file does NOT:
# - Perform website security checks.
# - Calculate security scores.
# - Generate AI content.
# - Perform context-risk calculations directly.
# ==========================================================


# ==========================================================
# Request Validation Helper
# ==========================================================

def get_json_request():
    """
    Safely retrieve JSON request data.

    Returns:
        tuple:
            (data, None) when valid
            (None, error_response) when invalid
    """

    data = request.get_json(silent=True)

    if data is None:
        log_warning("Request contains invalid or missing JSON data.")

        return None, (
            jsonify({
                "success": False,
                "status": "error",
                "message": "Invalid or missing JSON request data.",
                "assessment": None
            }),
            400
        )

    if not isinstance(data, dict):
        log_warning("Request JSON must be an object.")

        return None, (
            jsonify({
                "success": False,
                "status": "error",
                "message": "Request data must be a JSON object.",
                "assessment": None
            }),
            400
        )

    return data, None

# ==========================================================
# Create Blueprint
# ==========================================================

scan_bp = Blueprint("scan", __name__)


# ==========================================================
# Level 2 - Backend Scan Cancellation
# ==========================================================

active_scan_events = {}

active_scan_events_lock = threading.Lock()



# ==========================================================
# Health Check
# ==========================================================

@scan_bp.route("/", methods=["GET"])
def home():

    log_info("Health check requested.")

    return jsonify({

        "status": "running",

        "message": "UIDetect Backend is running."

    })




# ==========================================================
# Backend Status
# ==========================================================

@scan_bp.route("/api/status", methods=["GET"])
def status():

    log_info("Backend status requested.")

    return jsonify({

        "backend": "online",

        "service": "UIDetect Backend",

        "version": "1.0"

    })




# ==========================================================
# Test Connection
# ==========================================================

@scan_bp.route("/api/test", methods=["POST"])
def test():

    log_info("Backend connection test.")

    return jsonify({

        "success": True,

        "message": "Backend connected successfully."

    })



# ==========================================================
# Level 2 - Cancel Website Security Scan
# ==========================================================

@scan_bp.route("/api/scan/cancel", methods=["POST"])
def cancel_scan():

    try:

        log_info(
            "Received POST request: /api/scan/cancel"
        )

        data, error_response = get_json_request()

        if error_response is not None:
            return error_response

        scan_id = data.get("scanId")

        if not scan_id:

            log_warning(
                "Scan cancellation request missing scanId."
            )

            return jsonify({
                "success": False,
                "status": "error",
                "message": "Scan ID is required.",
                "assessment": None
            }), 400

        # ==============================================
        # Mark Scan As Cancelled
        # ==============================================

        with active_scan_events_lock:

            scan_event = active_scan_events.get(
                scan_id
            )

            if scan_event is None:

                log_warning(
                    f"No active scan found for cancellation: "
                    f"{scan_id}"
                )

                return jsonify({

                    "success": True,

                    "cancelled": False,

                    "scanId": scan_id,

                    "message":
                        "No active scan was found."

                }), 200

            scan_event.set()

        log_info(
            f"Scan cancellation marked: {scan_id}"
        )

        return jsonify({
            "success": True,
            "cancelled": True,
            "scanId": scan_id,
            "message":
                "Scan cancellation requested."
        }), 200

    except Exception as error:

        log_error(
            f"Unexpected scan cancellation error: {error}"
        )

        return jsonify({
            "success": False,
            "status": "error",
            "message": "Unable to cancel the security scan.",
            "assessment": None
        }), 500




# ==========================================================
# Website Security Scan
# ==========================================================

@scan_bp.route("/api/scan", methods=["POST"])
def scan():

    scan_id = None

    try:


        log_info(
            "Received POST request: /api/scan"
        )



        # ==============================================
        # Read Request
        # ==============================================

        data, error_response = get_json_request()

        if error_response is not None:

            return error_response


        # ==============================================
        # Get URL
        # ==============================================

        url = data.get("url")

        page_title = data.get(
            "pageTitle",
            ""
        )

        meta_description = data.get(
            "metaDescription",
            ""
        )


        # ==============================================
        # Level 2 - Scan Cancellation
        # ==============================================

        scan_id = data.get("scanId")

        if not scan_id:

            log_warning(
                "Scan request missing scanId."
            )

            return jsonify({
                "success": False,
                "status": "error",
                "message": "Scan ID is required.",
                "assessment": None
            }), 400


        scan_event = threading.Event()

        with active_scan_events_lock:

            active_scan_events[scan_id] = scan_event


        log_info(
            f"Registered active scan: {scan_id}"
        )




        # ==============================================
        # Phase 8
        # Get User Interaction
        # ==============================================

        interaction = data.get(

            "interaction",

            "BROWSE"

        )



        log_info(

            f"Scanning URL: {url}"

        )


        log_info(

            f"User Interaction: {interaction}"

        )





        # ==============================================
        # Get Security Headers
        # ==============================================

        security_headers = data.get(

            "securityHeaders",

            {}

        )



        log_info(

            f"Received Security Headers: "
            f"{security_headers}"

        )





        # ==============================================
        # Start Scan
        # ==============================================

        log_info(

            "Starting website security scan..."

        )



        result = scan_website(

            url,

            security_headers,

            interaction,

            scan_event,
            
            page_title,

            meta_description


        )





        # ==============================================
        # Scanner Result Validation
        # ==============================================

        if result is None:

            log_error(
                "Scanner returned None."
            )

            return jsonify({
                "success": False,
                "status": "error",
                "message": "Website scanner returned no result.",
                "assessment": None
            }), 500


        if not isinstance(result, dict):

            log_error(
                "Scanner returned an invalid result type."
            )

            return jsonify({
                "success": False,
                "status": "error",
                "message": "Website scanner returned an invalid result.",
                "assessment": None
            }), 500


        # ==============================================
        # Scanner Cancelled
        # ==============================================

        if result.get("cancelled") is True:

            log_info(
                f"Website scan cancelled: {scan_id}"
            )

            return jsonify({

                "success": False,

                "cancelled": True,

                "scanId":
                    scan_id,

                "url":
                    result.get(
                        "url",
                        url
                    ),

                "error":
                    result.get(
                        "error",
                        {
                            "code":
                                "SCAN_CANCELLED",

                            "message":
                                "The security scan was cancelled by the user.",

                            "recoverable":
                                True
                        }
                    )

            }), 200


        # ==============================================
        # Scanner Failed
        # ==============================================

        if not result.get("success"):

            error_message = result.get(
                "error",
                "Unknown scanning error."
            )

            log_error(
                f"Website scanner failed: {error_message}"
            )

            return jsonify({
                "success": False,
                "status": "error",
                "message": error_message,
                "assessment": None
            }), 500



        # ==============================================
        # Scanner Success
        # ==============================================

        log_info(

            f"Scan completed successfully "
            f"(Score={result['score']}, "
            f"Level={result['level']}, "
            f"Risk={result.get('finalPosture', {}).get('risk')})"

        )



        return jsonify({
            "success": True,
            "status": "success",
            "assessment": result
        }), 200





    except Exception as error:

        log_error(

            f"Unexpected error during scan: {error}"

        )


        return jsonify({
            "success": False,
            "status": "error",
            "message": "Internal Server Error.",
            "assessment": None
        }), 500


    finally:

        if scan_id is not None:

            with active_scan_events_lock:

                active_scan_events.pop(
                    scan_id,
                    None
                )

            log_info(
                f"Removed active scan: {scan_id}"
            )


# ==========================================================
# Receive User Interaction Event (Phase 7)
# ==========================================================

@scan_bp.route("/interaction", methods=["POST"])
def receive_interaction():


    try:


        log_info(

            "Received POST request: /interaction"

        )



        data = request.get_json(
            silent=True
        )
        if data is None:

            log_warning(
                "Invalid or missing interaction JSON."
            )

            return jsonify({

                "status": "error",

                "message":
                    "Invalid or missing JSON request data."

            }), 400


        if not isinstance(data, dict):

            log_warning(
                "Interaction request must be a JSON object."
            )

            return jsonify({

                "status": "error",

                "message":
                    "Interaction request must be a JSON object."

            }), 400



        print("==============================")

        print("Interaction Received:")

        print(data)

        print("==============================")



        return jsonify({


            "status": "success",


            "message": "Interaction received",


            "data": {


                "website":
                    data.get("website"),


                "interaction":
                    data.get("interaction"),


                "page":
                    data.get("page"),


                "timestamp":
                    data.get("timestamp")


            }


        }), 200





    except Exception as error:



        log_error(

            f"Interaction Error: {error}"

        )



        return jsonify({


            "status": "error",


            "message":
                "Failed to receive interaction"


        }), 500