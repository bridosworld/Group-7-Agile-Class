# Group-7-Agile-Class
Deliver a fully functional and documented API that enables reliable data exchange, ensuring it is thoroughly tested and ready for integration by consumers.

API

# TerraScope API – Sprint 1

This project contains the basic Flask API for Sprint 1. To run it:


In the project folder, create and activate a virtual environment:

(Git Bash):
python -m venv .venv

(Git Bash):
source .venv/Scripts/activate

Install the required packages:
pip install flask flask-sqlalchemy flask-marshmallow marshmallow-sqlalchemy

Start API:
python app.py

The server will run at:
http://127.0.0.1:5000

Health check endpoint for US-05:
http://127.0.0.1:5000/health

Expected output:
{ "status": "ok" }

This confirms the API works and is ready for other Sprint 1 user stories.

# US-08: Global JSON Config and Error Handling

This user story configures the API to handle non-ASCII characters in JSON responses globally (via app.config['JSON_AS_ASCII'] = False) and implements standardized error handlers for common HTTP status codes. These ensure consistent, user-friendly error responses in JSON format, improving API reliability and developer experience.
Error handlers cover:

400 Bad Request: Invalid input (e.g., malformed JSON).
401 Unauthorized: Authentication failures (e.g., invalid tokens).
403 Forbidden: Access denied despite authentication.
404 Not Found: Missing endpoints.
405 Method Not Allowed: Incorrect HTTP method.
422 Unprocessable Entity: Valid format but invalid business logic (e.g., data validation).
429 Too Many Requests: Rate limiting exceeded.
500 Internal Server Error: Unexpected server issues.
503 Service Unavailable: Temporary server downtime.

To test these (and the root/health endpoints), save the following as requests.http and run with VS Code's REST Client extension. 

### Test health endpoint
GET http://127.0.0.1:5000/health

### Test root endpoint
GET http://127.0.0.1:5000/

### Test 404 error - Endpoint not found
GET http://127.0.0.1:5000/notfound

### Test 405 error - Wrong HTTP method
POST http://127.0.0.1:5000/health

### Test 400 error - Bad request
POST http://127.0.0.1:5000/health
Content-Type: application/json

{invalid json}

### Test 401 error - Unauthorized
GET http://127.0.0.1:5000/health
Authorization: Bearer invalid_token

### Test 403 error - Forbidden
GET http://127.0.0.1:5000/forbidden

### Test 422 error - Unprocessable entity
POST http://127.0.0.1:5000/validate
Content-Type: application/json

{"age": "not_a_number"}

### Test 429 error - Too many requests
GET http://127.0.0.1:5000/health
GET http://127.0.0.1:5000/health
GET http://127.0.0.1:5000/health

### Test 503 error - Service unavailable
GET http://127.0.0.1:5000/unavailable

It demonstrates expected responses for success and errors, helping the team verify US-08 functionality.