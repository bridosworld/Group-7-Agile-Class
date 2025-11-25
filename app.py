from flask import Flask, jsonify, request
import json
from flask_sqlalchemy import SQLAlchemy
from flask_marshmallow import Marshmallow

app = Flask(__name__)

# US-08: Global JSON config
# This tells Flask to use proper characters (like é, ñ, 中) in our responses
# Without this, special characters would look weird like \u1234
app.config['JSON_AS_ASCII'] = False

# US-08: Error handlers
# Instead of ugly errors, users get helpful JSON responses

# Error 1: Handles 400 error - Bad Request
# When user sends broken data (like invalid JSON or wrong format)
# Example: Sending "age: old" instead of "age: 25"
@app.errorhandler(400)
def bad_request(error):
    return jsonify({
        "error": "Bad Request",
        "message": error.description or "Your input is invalid",
        "code": 400
    }), 400

# Error 2: Handles 404 error - Not Found
# When user tries to visit a page/endpoint that doesn't exist
# Example: Going to /unicorn when we only have /health
@app.errorhandler(404)
def not_found(error):
    return jsonify({
        "error": "Not Found",
        "message": error.description or "The endpoint you requested does not exist",
        "code": 404
    }), 404

# Error 3: Handles 405 error - Method Not Allowed
# When user uses wrong HTTP verb (like POST when we only accept GET)
# Example: POSTing to /health when it only accepts GET
@app.errorhandler(405)
def method_not_allowed(error):
    return jsonify({
        "error": "Method Not Allowed",
        "message": "Use GET for this particular endpoint",
        "code": 405
    }), 405

# Error 4: Handles 500 error - Internal Server Error
# When our code crashes or has a bug
# We hide the scary technical details and show a friendly message
@app.errorhandler(500)
def internal_error(error):
    return jsonify({
        "error": "Internal Server Error",
        "message": "Something went wrong, try again later",
        "code": 500
    }), 500

# Error 5: Handles 401 error - Unauthorized
# When user tries to access something without logging in first
# Example: Visiting /admin without a valid login token
@app.errorhandler(401)
def unauthorized(error):
    return jsonify({
        "error": "Unauthorized",
        "message": error.description or "Your Authentication is required",
        "code": 401
    }), 401

# Error 6: Handles 403 error - Forbidden
# When user is logged in BUT doesn't have permission for this action
# Example: A regular user trying to delete admin data
@app.errorhandler(403)
def forbidden(error):
    return jsonify({
        "error": "Forbidden",
        "message": error.description or "This Access is denied",
        "code": 403
    }), 403

# Error 7: Handles 422 error - Unprocessable Entity
# When data format is correct but values break our business rules
# Example: Sending age = -5 (format is right, but negative age makes no sense)
@app.errorhandler(422)
def unprocessable_entity(error):
    return jsonify({
        "error": "Unprocessable Entity",
        "message": error.description or "This Validation failed",
        "code": 422
    }), 422

# Error 8: Handles 429 error - Too Many Requests
# When user makes too many requests too quickly (spam protection)
# Example: Clicking refresh 100 times in 1 second
@app.errorhandler(429)
def too_many_requests(error):
    return jsonify({
        "error": "Too Many Requests",
        "message": error.description or "You have exceeded the limit, please wait before retrying",
        "code": 429
    }), 429

# Error 9: Handles 503 error - Service Unavailable
# When our server is temporarily down (maintenance, overloaded, etc.)
# Example: Database is restarting or server ran out of memory
@app.errorhandler(503)
def service_unavailable(error):
    return jsonify({
        "error": "Service Unavailable",
        "message": error.description or "The Server is temporarily down",
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