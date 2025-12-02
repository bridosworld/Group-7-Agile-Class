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

pip install flasgger
pip install PyYAML

Start API:
python app.py

The server will run at:
http://127.0.0.1:5000

Health check endpoint for US-05:
http://127.0.0.1:5000/health

Expected output:
{ "status": "ok" }
 # Testing:

Step 1 — Run the API

Open VS Code terminal and run:

python app.py


Step 2 — Get your JWT token (NEEDED for many US tests)

In Postman:

POST
http://127.0.0.1:5000/auth/login

Body → raw → JSON:

{
  "username": "testuser",
  "password": "testpass"
}

Copy the access_token.

# US-05 — ERROR HANDLING
Goal: Make sure your 400/401/403/422/429/500/503 handlers work.
Test 1 — 400 BAD REQUEST

Postman →
POST
http://127.0.0.1:5000/test-bad-request

Expected:

{
  "error": "Bad Request",
  "message": "Invalid JSON format or missing required fields",
  "code": 400
}

Test 2 — 401 UNAUTHORIZED

GET
http://127.0.0.1:5000/test-unauthorized

Expected:

{
  "error": "Unauthorized",
  "message": "Invalid or missing authentication token",
  "code": 401
}

Test 3 — 403 FORBIDDEN

GET
http://127.0.0.1:5000/test-forbidden

Expected:

{
  "error": "Forbidden",
  "message": "You do not have permission to access this resource",
  "code": 403
}

Test 4 — 422 VALIDATION

POST
http://127.0.0.1:5000/test-validate

Expected:

{
  "error": "Unprocessable Entity",
  "message": "Data validation failed",
  "code": 422
}

Test 5 — 429 RATE LIMIT

GET
http://127.0.0.1:5000/test-rate-limit

Test 6 — 500 INTERNAL ERROR

GET
http://127.0.0.1:5000/test-server-error

Test 7 — 503 SERVICE UNAVAILABLE

GET
http://127.0.0.1:5000/test-unavailable

# US-06 — SWAGGER / OPENAPI
How to test

Open your browser and go to:

http://127.0.0.1:5000/apidocs/


Expected:
You should see the Swagger UI showing all your endpoints.

# US-07 — CRUD METHODS ON /items

No authentication needed.

Test GET

Postman → GET
http://127.0.0.1:5000/items

Expected:

{"message": "GET OK", "items": []}

Test POST

POST → /items
(no body needed)

Expected:

{"message": "POST OK", "details": "Item created (dummy)"}

Test PUT

PUT → /items/1

Expected:

{"message": "PUT OK", "id": 1, "details": "Full update completed (dummy)"}

Test PATCH

PATCH → /items/1

Expected:

{"message": "PATCH OK", "id": 1, "details": "Partial update completed (dummy)"}

Test DELETE

DELETE → /items/1

Expected:

{"message": "DELETE OK", "id": 1, "details": "Item deleted (dummy)"}

# US-08 — HEALTH CHECK

GET →
http://127.0.0.1:5000/health

Expected:

{"status": "ok"}

# US-09

Get the Access Token
Method: POST

URL: http://127.0.0.1:5000/auth/login

Body → raw → JSON:

{
  "username": "testuser",
  "password": "testpass"
}


Click Send → copy the "access_token" value from the response (long JWT string).
Now test US-09: GET /observations

Method: GET

URL:

http://127.0.0.1:5000/observations


Go to the Headers tab:

Key = Authorization

Value = Bearer YOUR ACCESS TOKEN

Click Send → you should get [] or a list of observations with 200 OK

# US-10 – Store Geospatial Observation Data (POST /observations)
1. Get the Access Token

You already know this, but for completeness:

Method: POST
URL: http://127.0.0.1:5000/auth/login
Body → raw → JSON:

{
  "username": "testuser",
  "password": "testpass"
}


Copy "access_token".

2. Create a valid observation (Happy path)

Method: POST
URL: http://127.0.0.1:5000/observations

Headers:

Content-Type = application/json

Authorization = Bearer YOUR_ACCESS_TOKEN_HERE

Body → raw → JSON (example within current quarter):

{
  "timestamp": "2025-11-27T12:00:00",
  "timezone": "UTC",
  "coordinates": "lat=53.5,long=-2.4",
  "satellite_id": "TS-001",
  "spectral_indices": "{\"ndvi\": 0.72}",
  "notes": "Sample observation created for US-10 test"
}


Click Send
Expected: 201 Created with JSON of the observation (including an id).

3. Invalid timestamp format (error path)

Same request but break the timestamp:

{
  "timestamp": "27-11-2025 12:00",
  "timezone": "UTC",
  "coordinates": "lat=53.5,long=-2.4",
  "satellite_id": "TS-001",
  "spectral_indices": "{\"ndvi\": 0.72}",
  "notes": "Bad timestamp"
}


Expected: 400 Bad Request with message like
"Invalid timestamp format. Use ISO 8601..."

4. Missing required timestamp (error path)

Remove timestamp:

{
  "timezone": "UTC",
  "coordinates": "lat=53.5,long=-2.4",
  "satellite_id": "TS-001",
  "spectral_indices": "{\"ndvi\": 0.72}",
  "notes": "No timestamp"
}


Expected: 400 Bad Request with error about missing timestamp.

# US-11 – Protected historical updates (PUT / PATCH /observations/<id>)

First you need at least one observation in the DB (created via US-10 step 2).

Let’s assume the created observation had id = 1.
(If not sure, call GET /observations first and check the IDs.)

1. Happy path: Update a current observation (PUT)

Method: PUT
URL: http://127.0.0.1:5000/observations/1

Headers:

Content-Type = application/json

Authorization = Bearer YOUR_ACCESS_TOKEN_HERE

Body → raw → JSON:

{
  "timestamp": "2025-11-28T10:00:00",
  "timezone": "UTC",
  "coordinates": "lat=53.6,long=-2.3",
  "satellite_id": "TS-002",
  "spectral_indices": "{\"ndvi\": 0.80}",
  "notes": "Updated full observation via PUT"
}

Expected:
200 OK, JSON of the updated observation with changed fields.

2. Happy path: Partial update (PATCH)

Method: PATCH
URL: http://127.0.0.1:5000/observations/1

Headers:

Content-Type = application/json

Authorization = Bearer YOUR_ACCESS_TOKEN_HERE

Body → raw → JSON (only some fields):

{
  "notes": "Patched notes only (US-11 test)",
  "spectral_indices": "{\"ndvi\": 0.83}"
}

Expected:
200 OK, JSON of the observation with only those fields changed.

3. Invalid timestamp on update

Same as PUT or PATCH, but with a broken timestamp format:

{
  "timestamp": "28-11-2025 10:00"
}

Expected:
400 Bad Request with "Invalid timestamp format...".

# US-12 – Bulk create observations (POST /observations/bulk)
1. Happy path bulk insert

Method: POST
URL: http://127.0.0.1:5000/observations/bulk

(This one is not protected with @jwt_required() in your code, so no token needed.)

Headers:

Content-Type = application/json

Body → raw → JSON:

[
  {
    "timestamp": "2025-11-28T09:00:00",
    "timezone": "UTC",
    "coordinates": "lat=53.5,long=-2.4",
    "satellite_id": "TS-101",
    "spectral_indices": { "ndvi": 0.60 },
    "notes": "Bulk obs 1"
  },
  {
    "timestamp": "2025-11-28T09:10:00",
    "timezone": "UTC",
    "coordinates": "lat=53.6,long=-2.3",
    "satellite_id": "TS-102",
    "spectral_indices": { "ndvi": 0.65 },
    "notes": "Bulk obs 2"
  }
]


Expected:
201 Created
Body with:

"message": "Bulk insert successful"

"created_count": 2

"records": [...] list of created observations.

2. Bulk validation error (rollback all)

Send a list where one item is missing a required field, e.g. no timestamp:

[
  {
    "timestamp": "2025-11-28T09:00:00",
    "timezone": "UTC",
    "coordinates": "lat=53.5,long=-2.4",
    "satellite_id": "TS-101",
    "spectral_indices": { "ndvi": 0.60 },
    "notes": "Good one"
  },
  {
    "timezone": "UTC",
    "coordinates": "lat=53.6,long=-2.3",
    "satellite_id": "TS-102",
    "spectral_indices": { "ndvi": 0.65 },
    "notes": "Missing timestamp"
  }
]


Expected:
400 Bad Request

"message": "Bulk insert failed"

"errors" array mentioning the missing fields.

# US-13 – JWT Auth + Protected Route

You basically already did this, but here’s the checklist.

1. Valid login

POST http://127.0.0.1:5000/auth/login
Body:

{
  "username": "testuser",
  "password": "testpass"
}


200 + access_token.

2. Protected route without token

GET http://127.0.0.1:5000/protected
(no Authorization header)

Expected: 401 Unauthorized with "Missing Authorization Header" (or similar).

3. Protected route with valid token

GET http://127.0.0.1:5000/protected
Headers:

Authorization: Bearer YOUR_ACCESS_TOKEN_HERE

Expected:
200 OK

{
  "message": "Access granted",
  "user_id": 1
}

# US-19 + US-22 – ORM & Datasets (/datasets/demo, /datasets)

These two show that SQLAlchemy models map to the DB and can be queried.

1. Create demo dataset (ORM insert)

Method: POST
URL: http://127.0.0.1:5000/datasets/demo

(no body, no auth)

Expected:
201 Created with JSON something like:

{
  "id": 1,
  "name": "Demo dataset",
  "description": "Created via SQLAlchemy ORM"
}

2. List datasets (ORM read)

Method: GET
URL: http://127.0.0.1:5000/datasets

Expected:
200 OK with an array of dataset objects, including the demo one.

This directly matches US-22 DoD / acceptance criteria:

“Given database connection, when queried, then ORM maps objects.” → /datasets shows DB rows as Python objects → JSON.

“Given model changes, when migrated, then schema updates.” → You can mention that changing Dataset and recreating DB updates schema (even if you don’t fully demo migrations in Sprint-1).
