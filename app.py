from flask import Flask, jsonify, request
import datetime
import jwt
from functools import wraps
from flask_sqlalchemy import SQLAlchemy
from flask_marshmallow import Marshmallow
from datetime import datetime  # For date parsing in filtering

app = Flask(__name__)

# -----------------------------
# CONFIG
# -----------------------------
app.config['JSON_AS_ASCII'] = False
app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///terrascope_dev.db"
app.config["SQLALCHEMY_ECHO"] = True  
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
app.config["SECRET_KEY"] = "CHANGE_ME_SECRET_KEY"  # JWT secret

db = SQLAlchemy(app)
ma = Marshmallow(app)

# -----------------------------
# DATABASE MODELS + SCHEMAS
# US-19: Dataset Model + US-10: Observation Model
# -----------------------------
class Dataset(db.Model):
    __tablename__ = "datasets"

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(120), nullable=False)
    description = db.Column(db.String(255), nullable=True)

    def __repr__(self):
        return f"<Dataset {self.id} - {self.name}>"

class DatasetSchema(ma.SQLAlchemyAutoSchema):
    class Meta:
        model = Dataset
        load_instance = True

dataset_schema = DatasetSchema()
datasets_schema = DatasetSchema(many=True)

# US-10: Observation Model (for satellite data with filtering support)
class Observation(db.Model):
    __tablename__ = "observations"

    id = db.Column(db.Integer, primary_key=True)
    timestamp = db.Column(db.DateTime, nullable=False)  # ISO 8601 via datetime
    timezone = db.Column(db.String(50), nullable=True)
    coordinates = db.Column(db.String(100), nullable=True)  # e.g., "lat=40.7,long=-74.0"
    satellite_id = db.Column(db.String(50), nullable=True)
    spectral_indices = db.Column(db.Text, nullable=True)  # Can store as JSON string
    notes = db.Column(db.Text, nullable=True)

    def __repr__(self):
        return f"<Observation {self.id} - {self.timestamp}>"

class ObservationSchema(ma.SQLAlchemyAutoSchema):
    class Meta:
        model = Observation
        load_instance = True

observation_schema = ObservationSchema()
observations_schema = ObservationSchema(many=True)

# US-19: Create database tables once
tables_created = False
@app.before_request
def create_tables_once():
    global tables_created
    if not tables_created:
        db.create_all()  # Creates both datasets and observations tables
        tables_created = True

# ============================================
# JWT IMPLEMENTATION
# ============================================
DEMO_USER = {"username": "admin", "password": "password123"}

def create_token(username):
    payload = {
        "username": username,
        "exp": datetime.datetime.utcnow() + datetime.timedelta(hours=1)
    }
    return jwt.encode(payload, app.config["SECRET_KEY"], algorithm="HS256")

def jwt_required(fn):
    @wraps(fn)
    def wrapper(*args, **kwargs):
        auth_header = request.headers.get("Authorization")
        if not auth_header:
            return jsonify({
                "error": "Missing Authorization Header",
                "message": "Provide token in format: Bearer <token>"
            }), 401
        try:
            token = auth_header.split(" ")[1]
            decoded = jwt.decode(token, app.config["SECRET_KEY"], algorithms=["HS256"])
            request.user = decoded["username"]
        except Exception:
            return jsonify({
                "error": "Invalid or expired token",
                "message": "Login again to get a new token"
            }), 401
        return fn(*args, **kwargs)
    return wrapper

# ============================================
# ERROR HANDLERS (9 total)
# ============================================
@app.errorhandler(400)
def bad_request(error):
    return jsonify({"error": "Bad Request", "message": error.description or "Your input is invalid", "code": 400}), 400

@app.errorhandler(401)
def unauthorized(error):
    return jsonify({"error": "Unauthorized", "message": error.description or "Authentication required", "code": 401}), 401

@app.errorhandler(403)
def forbidden(error):
    return jsonify({"error": "Forbidden", "message": error.description or "Access denied", "code": 403}), 403

@app.errorhandler(404)
def not_found(error):
    return jsonify({"error": "Not Found", "message": error.description or "Endpoint not found", "code": 404}), 404

@app.errorhandler(405)
def method_not_allowed(error):
    return jsonify({"error": "Method Not Allowed", "message": "Use valid HTTP method", "code": 405}), 405

@app.errorhandler(422)
def unprocessable_entity(error):
    return jsonify({"error": "Unprocessable Entity", "message": error.description or "Validation failed", "code": 422}), 422

@app.errorhandler(429)
def too_many_requests(error):
    return jsonify({"error": "Too Many Requests", "message": error.description or "Rate limit exceeded", "code": 429}), 429

@app.errorhandler(500)
def internal_error(error):
    return jsonify({"error": "Internal Server Error", "message": "Something went wrong", "code": 500}), 500

@app.errorhandler(503)
def service_unavailable(error):
    return jsonify({"error": "Service Unavailable", "message": error.description or "Server temporarily down", "code": 503}), 503

# Force 500 handler to work even in debug mode
@app.errorhandler(Exception)
def handle_exception(e):
    # Pass through HTTP exceptions (like 404, 401, etc.)
    from werkzeug.exceptions import HTTPException
    if isinstance(e, HTTPException):
        return e
    
    # Now handle non-HTTP exceptions (like our simulated crash)
    return jsonify({
        "error": "Internal Server Error",
        "message": "Something went wrong, try again later",
        "code": 500
    }), 500

# ============================================
# MAIN ENDPOINTS
# ============================================
@app.get("/health")
def health():
    return jsonify({"status": "ok"}), 200

@app.get("/")
def root():
    return jsonify({"message": "TerraScope API is running", "status": "ok"}), 200

@app.post("/auth/login")
def login():
    data = request.get_json() or {}
    username = data.get("username")
    password = data.get("password")
    if username != DEMO_USER["username"] or password != DEMO_USER["password"]:
        return jsonify({"error": "Invalid credentials"}), 401
    token = create_token(username)
    return jsonify({"access_token": token, "token_type": "Bearer", "expires_in": "1 hour"})

# US-07: Standard HTTP Methods on /items

# -----------------------------
# DUMMY ITEM ROUTES
# -----------------------------
@app.get("/items")
def get_items():
    return jsonify({"message": "GET OK", "items": []}), 200

@app.post("/items")
def create_item():
    return jsonify({"message": "POST OK", "details": "Item created (dummy)"}), 201

@app.put("/items/<int:item_id>")
def update_item(item_id):
    return jsonify({"message": "PUT OK", "id": item_id, "details": "Full update completed (dummy)"}), 200

@app.patch("/items/<int:item_id>")
def patch_item(item_id):
    return jsonify({"message": "PATCH OK", "id": item_id, "details": "Partial update completed (dummy)"}), 200

@app.delete("/items/<int:item_id>")
def delete_item(item_id):
    return jsonify({"message": "DELETE OK", "id": item_id, "details": "Item deleted (dummy)"}), 200

# US-09: GET /observations with filtering support

@app.get("/observations")
def get_observations():
    # Start with all records
    query = Observation.query

    # US-09: Parameter-based filtering via query params
    start_date_str = request.args.get('start_date')  # e.g., "2025-11-01T00:00:00"
    end_date_str = request.args.get('end_date')      # e.g., "2025-11-30T23:59:59"
    lat_str = request.args.get('lat')               # e.g., "40.7"
    long_str = request.args.get('long')             # e.g., "-74.0"

    # Date range filtering
    if start_date_str:
        try:
            start_date = datetime.fromisoformat(start_date_str.replace('Z', '+00:00'))
            query = query.filter(Observation.timestamp >= start_date)
        except ValueError:
            return jsonify({
                "error": "Invalid start_date format. Use ISO 8601 (e.g., 2025-11-01T00:00:00)",
                "code": 400
            }), 400

    if end_date_str:
        try:
            end_date = datetime.fromisoformat(end_date_str.replace('Z', '+00:00'))
            query = query.filter(Observation.timestamp <= end_date)
        except ValueError:
            return jsonify({
                "error": "Invalid end_date format. Use ISO 8601 (e.g., 2025-11-30T23:59:59)",
                "code": 400
            }), 400

    # Location filtering
    if lat_str and long_str:
        location_filter = f"lat={lat_str},long={long_str}"
        query = query.filter(Observation.coordinates == location_filter)
    elif lat_str or long_str:
        return jsonify({
            "error": "Both 'lat' and 'long' parameters are required for location filtering",
            "code": 400
        }), 400

    # Execute query and serialize to JSON
    results = query.all()
    return jsonify(observations_schema.dump(results)), 200

# ============================================
# TEST ENDPOINTS (For verifying error handlers)
# ============================================
@app.post("/test-bad-request")
def test_bad_request():
    from werkzeug.exceptions import BadRequest
    raise BadRequest("Invalid JSON format or missing required fields")

@app.get("/test-unauthorized")
def test_unauthorized():
    from werkzeug.exceptions import Unauthorized
    raise Unauthorized("Invalid or missing authentication token")

@app.get("/test-forbidden")
def test_forbidden():
    from werkzeug.exceptions import Forbidden
    raise Forbidden("You do not have permission to access this resource")

@app.post("/test-validate")
def test_validate():
    from werkzeug.exceptions import UnprocessableEntity
    raise UnprocessableEntity("Data validation failed")

@app.get("/test-rate-limit")
def test_rate_limit():
    from werkzeug.exceptions import TooManyRequests
    raise TooManyRequests("You have made too many requests. Please wait before trying again")

@app.get("/test-server-error")
def test_server_error():
    raise Exception("Simulated server crash")

@app.get("/test-unavailable")
def test_unavailable():
    from werkzeug.exceptions import ServiceUnavailable
    raise ServiceUnavailable("Service is temporarily unavailable")

# -----------------------------
# EXAMPLE PROTECTED ROUTE
# -----------------------------
@app.get("/secure-data")
@jwt_required
def secure_data():
    return jsonify({
        "message": "You are authenticated",
        "user": request.user,
        "data": ["secret-1", "secret-2"]
    })

# -----------------------------
# RUN SERVER
# -----------------------------
if __name__ == "__main__":
    app.run(debug=True)