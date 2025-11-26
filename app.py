from flask import Flask, jsonify, request
import json
from flask_sqlalchemy import SQLAlchemy
from flask_marshmallow import Marshmallow

app = Flask(__name__)

# US-08: Global JSON config
# This tells Flask to use proper characters (like é, ñ, 中) in our responses
# Without this, special characters would look weird like \u1234
app.config['JSON_AS_ASCII'] = False

# ============================================
# ERROR HANDLERS (9 total)
# ============================================

# Error 1: Handles 400 error - Bad Request
# When user sends broken data (like invalid JSON or wrong format)
@app.errorhandler(400)
def bad_request(error):
    return jsonify({
        "error": "Bad Request",
        "message": error.description or "Your input is invalid",
        "code": 400
    }), 400

# Error 2: Handles 401 error - Unauthorized
# When user tries to access something without logging in first
@app.errorhandler(401)
def unauthorized(error):
    return jsonify({
        "error": "Unauthorized",
        "message": error.description or "Your Authentication is required",
        "code": 401
    }), 401

# Error 3: Handles 403 error - Forbidden
# When user is logged in BUT doesn't have permission for this action
@app.errorhandler(403)
def forbidden(error):
    return jsonify({
        "error": "Forbidden",
        "message": error.description or "This Access is denied!",
        "code": 403
    }), 403

# Error 4: Handles 404 error - Not Found
# When user tries to visit a page/endpoint that doesn't exist
@app.errorhandler(404)
def not_found(error):
    return jsonify({
        "error": "Not Found",
        "message": error.description or "The endpoint you requested does not exist",
        "code": 404
    }), 404

# Error 5: Handles 405 error - Method Not Allowed
# When user uses wrong HTTP verb (like POST when we only accept GET)
@app.errorhandler(405)
def method_not_allowed(error):
    return jsonify({
        "error": "Method Not Allowed",
        "message": "Use GET for this particular endpoint",
        "code": 405
    }), 405

# Error 6: Handles 422 error - Unprocessable Entity
# When data format is correct but values break our business rules
@app.errorhandler(422)
def unprocessable_entity(error):
    return jsonify({
        "error": "Unprocessable Entity",
        "message": error.description or "This Validation failed",
        "code": 422
    }), 422

# Error 7: Handles 429 error - Too Many Requests
# When user makes too many requests too quickly (spam protection)
@app.errorhandler(429)
def too_many_requests(error):
    return jsonify({
        "error": "Too Many Requests",
        "message": error.description or "You have exceeded the limit, please wait before retrying",
        "code": 429
    }), 429

# Error 8: Handles 500 error - Internal Server Error
# When our code crashes or has a bug
@app.errorhandler(500)
def internal_error(error):
    return jsonify({
        "error": "Internal Server Error",
        "message": "Something went wrong, try again later",
        "code": 500
    }), 500

# Error 9: Handles 503 error - Service Unavailable
# When our server is temporarily down (maintenance, overloaded, etc.)
@app.errorhandler(503)
def service_unavailable(error):
    return jsonify({
        "error": "Service Unavailable",
        "message": error.description or "The Server is temporarily down",
        "code": 503
    }), 503

# ============================================
# MAIN ENDPOINTS
# ============================================

@app.get("/health")
def health():
    return jsonify({"status": "ok"}), 200

@app.get("/")
def root():
    return jsonify({
        "message": "TerraScope API is running",
        "status": "ok"
    }), 200

# ============================================
# TEST ENDPOINTS (For verifying error handlers)
# ============================================

# Test 1: Triggers 400 Bad Request error
@app.post("/test-bad-request")
def test_bad_request():
    from werkzeug.exceptions import BadRequest
    raise BadRequest("Invalid JSON format or missing required fields")

# Test 2: Triggers 401 Unauthorized error
@app.get("/test-unauthorized")
def test_unauthorized():
    from werkzeug.exceptions import Unauthorized
    raise Unauthorized("Invalid or missing authentication token")

# Test 3: Triggers 403 Forbidden error
@app.get("/test-forbidden")
def test_forbidden():
    from werkzeug.exceptions import Forbidden
    raise Forbidden("You do not have permission to access this resource")

# Test 4: 404 Not Found - No test needed (just visit non-existent endpoint like /notfound)

# Test 5: 405 Method Not Allowed - No test needed (just POST to /health which only accepts GET)

# Test 6: Triggers 422 Unprocessable Entity error
@app.post("/test-validate")
def test_validate():
    from werkzeug.exceptions import UnprocessableEntity
    raise UnprocessableEntity("Data validation failed")

# Test 7: Triggers 429 Too Many Requests error
@app.get("/test-rate-limit")
def test_rate_limit():
    from werkzeug.exceptions import TooManyRequests
    raise TooManyRequests("You have made too many requests. Please wait before trying again")

# Test 8: Triggers 500 Internal Server Error
@app.get("/test-server-error")
def test_server_error():
    raise Exception("Simulated server crash")

# Test 9: Triggers 503 Service Unavailable error
@app.get("/test-unavailable")
def test_unavailable():
    from werkzeug.exceptions import ServiceUnavailable
    raise ServiceUnavailable("Service is temporarily unavailable")

if __name__ == "__main__":
    app.run(debug=True)