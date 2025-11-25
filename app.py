from flask import Flask, jsonify, request
import json
from flask_sqlalchemy import SQLAlchemy
from flask_marshmallow import Marshmallow

app = Flask(__name__)

# US-08: Global JSON config
app.config['JSON_AS_ASCII'] = False

# US-08: Error handlers
# Step 1: Handles 400 error - Catches bad user input like wrong data format. Returns friendly message.
@app.errorhandler(400)
def bad_request(error):
    return jsonify({
        "error": "Bad Request",
        "message": error.description or "Invalid input",
        "code": 400
    }), 400

# Step 2: Handles 404 error - Triggers when requested page/endpoint doesn't exist. Guides user to check URL.
@app.errorhandler(404)
def not_found(error):
    return jsonify({
        "error": "Not Found",
        "message": error.description or "Endpoint not found",
        "code": 404
    }), 404

# Step 3: Handles 405 error - Happens if wrong HTTP method (e.g., POST instead of GET) is used. Suggests correct method.
@app.errorhandler(405)
def method_not_allowed(error):
    return jsonify({
        "error": "Method Not Allowed",
        "message": "Use GET for this endpoint",
        "code": 405
    }), 405

# Step 4: Handles 500 error - Covers server crashes or bugs. Hides details, shows safe "try again" message.
@app.errorhandler(500)
def internal_error(error):
    return jsonify({
        "error": "Internal Server Error",
        "message": "Something went wrong",
        "code": 500
    }), 500

# Step 5: Handles 401 error - Occurs when authentication fails, like invalid token. Prompts user to log in.
@app.errorhandler(401)
def unauthorized(error):
    return jsonify({
        "error": "Unauthorized",
        "message": error.description or "Authentication required",
        "code": 401
    }), 401

# Step 6: Handles 403 error - User is authenticated but lacks permission for action. Explains access denied.
@app.errorhandler(403)
def forbidden(error):
    return jsonify({
        "error": "Forbidden",
        "message": error.description or "Access denied",
        "code": 403
    }), 403

# Step 7: Handles 422 error - Input data is valid format but fails business rules. Details validation issues.
@app.errorhandler(422)
def unprocessable_entity(error):
    return jsonify({
        "error": "Unprocessable Entity",
        "message": error.description or "Validation failed",
        "code": 422
    }), 422

# Step 8: Handles 429 error - Too many requests from user too quickly. Suggests waiting before retry.
@app.errorhandler(429)
def too_many_requests(error):
    return jsonify({
        "error": "Too Many Requests",
        "message": error.description or "Rate limit exceeded",
        "code": 429
    }), 429

# Step 9: Handles 503 error - Server temporarily unavailable, like during maintenance. Advises to check back later.
@app.errorhandler(503)
def service_unavailable(error):
    return jsonify({
        "error": "Service Unavailable",
        "message": error.description or "Server temporarily down",
        "code": 503
    }), 503

@app.get("/health")
def health():
    return jsonify({"status": "ok"}), 200

@app.get("/")
def root():
    return jsonify({
        "message": "TerraScope API is running",
        "status": "ok"
    }), 200

if __name__ == "__main__":
    app.run(debug=True)