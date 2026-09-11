from flask import Flask, jsonify, request
from flask_cors import CORS
from routes import scan_bp
from config import Config
from logger import (
    log_info,
    log_warning,
    log_error
)

from checkers.openphish_checker import (
    start_openphish_feed_loader
)

# ==========================================================
# Flask Application Entry Point
# ==========================================================
#
# Definition:
# This file is the main entry point of the UIDetect Flask
# backend.
#
# Responsibilities:
# - Create the Flask application.
# - Load backend configuration.
# - Enable CORS for the browser extension.
# - Register UIDetect API routes.
# - Handle global HTTP errors.
# - Start the Flask development server.
#
# This file does NOT:
# - Perform website security scans.
# - Generate AI responses.
# - Build AI prompts.
# - Calculate security scores.
# - Perform security checks.
#
# Those responsibilities belong to the appropriate modules.
# ==========================================================

# ==========================================================
# Create Flask Application
# ==========================================================

app = Flask(__name__)
app.config.from_object(Config)

# Allow Chrome Extension to access Flask API
CORS(app)

# ==========================================================
# Register API Routes
# ==========================================================

app.register_blueprint(scan_bp)

print("=== REGISTERED ROUTES ===")

for rule in app.url_map.iter_rules():
    print(rule)

# ==========================================================
# Global Error Handling
# ==========================================================

@app.errorhandler(400)
def handle_bad_request(error):

    log_warning(
        f"Global 400 Bad Request: {error}"
    )

    return jsonify({
        "success": False,
        "status": "error",
        "message": "Invalid request.",
        "assessment": None
    }), 400

@app.errorhandler(404)
def handle_not_found(error):

    log_warning(
        f"Global 404 Not Found: {request.path}"
    )

    return jsonify({
        "success": False,
        "status": "error",
        "message": "Requested endpoint was not found.",
        "assessment": None
    }), 404

@app.errorhandler(405)
def handle_method_not_allowed(error):

    log_warning(
        f"Global 405 Method Not Allowed: "
        f"{request.method} {request.path}"
    )

    return jsonify({
        "success": False,
        "status": "error",
        "message": "HTTP method is not allowed for this endpoint.",
        "assessment": None
    }), 405

@app.errorhandler(Exception)
def handle_unexpected_error(error):

    log_error(
        f"Unhandled Flask exception: {error}"
    )

    return jsonify({
        "success": False,
        "status": "error",
        "message": "Internal Server Error.",
        "assessment": None
    }), 500
    
        
# ==========================================================
# Start Flask Server
# ==========================================================

if __name__ == "__main__":

    log_info("====================================")
    log_info("UIDetect Backend Started")
    log_info(f"Host : {Config.HOST}")
    log_info(f"Port : {Config.PORT}")
    log_info("====================================")

    start_openphish_feed_loader()

    app.run(
        host=Config.HOST,
        port=Config.PORT,
        debug=True,
        use_reloader=False
    )