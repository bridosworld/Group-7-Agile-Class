from flask import Flask, jsonify, request
import datetime
import jwt
from functools import wraps
from flask_sqlalchemy import SQLAlchemy
from flask_marshmallow import Marshmallow
from flasgger import Swagger
from datetime import datetime  # For date parsing in filtering
from werkzeug.security import generate_password_hash, check_password_hash  # For password hashing
from flask_jwt_extended import JWTManager, jwt_required, create_access_token, get_jwt_identity, verify_jwt_in_request

app = Flask(__name__)
# Swagger config
app.config['SWAGGER'] = {
    'title': 'TerraScope API',
    'uiversion': 3
}

swagger = Swagger(app)


# US-13: JWT Configuration (use a strong secret in production; generate via os.urandom(24))
app.config['JWT_SECRET_KEY'] = 'terra-scope-super-secret-key-2025'  # Dev key; change for prod
jwt = JWTManager(app)

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

# US-13: User Model (for authentication; stores hashed passwords)
class User(db.Model):
    __tablename__ = "users"

    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    password_hash = db.Column(db.String(120), nullable=False)  # Hashed password

    def __repr__(self):
        return f"<User {self.username}>"

    # Helper to set hashed password
    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    # Helper to check password
    def check_password(self, password):
        return check_password_hash(self.password_hash, password)

# US-13: Marshmallow schema for User (for potential serialization; not strictly needed but aligns with style)
class UserSchema(ma.SQLAlchemyAutoSchema):
    class Meta:
        model = User
        load_instance = True
        exclude = ('password_hash',)  # Never expose hash

user_schema = UserSchema()
users_schema = UserSchema(many=True)

# US-19: Create database tables once (now includes users)
tables_created = False
@app.before_request
def create_tables_once():
    global tables_created
    if not tables_created:
        db.create_all()  # Creates datasets, observations, and users tables
        # US-13: Seed a test user if none exist (username: 'testuser', password: 'testpass' – remove for prod)
        if User.query.count() == 0:
            test_user = User(username='testuser')
            test_user.set_password('testpass')
            db.session.add(test_user)
            db.session.commit()
        tables_created = True

# ============================================
# JWT IMPLEMENTATION (now using flask-jwt-extended)
# ============================================
# JWT config and User model are above; login endpoint and protected routes below

# US-11: Helper function for quarter boundary checks
def get_current_quarter_start():
    """
    US-11: Returns the start date of the current quarter (e.g., Oct 1 for Q4).
    """
    now = datetime.now()
    # Adjust to first day of current quarter
    if now.month <= 3:
        quarter_start = datetime(now.year, 1, 1)
    elif now.month <= 6:
        quarter_start = datetime(now.year, 4, 1)
    elif now.month <= 9:
        quarter_start = datetime(now.year, 7, 1)
    else:  # 10-12
        quarter_start = datetime(now.year, 10, 1)
    return quarter_start

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
    """
    Health check
    ---
    tags:
      - System
    responses:
      200:
        description: API is running
        schema:
          type: object
          properties:
            status:
              type: string
              example: ok
    """
    return jsonify({"status": "ok"}), 200


@app.get("/")
def root():
    return jsonify({"message": "TerraScope API is running", "status": "ok"}), 200

@app.post("/auth/login")
def login():
    data = request.get_json()
    if not data or 'username' not in data or 'password' not in data:
        return jsonify({
            "error": "Missing username or password",
            "code": 400
        }), 400

    username = data['username']
    password = data['password']

    user = User.query.filter_by(username=username).first()
    if user and user.check_password(password):
        # Create access token - MUST convert user.id to string
        access_token = create_access_token(identity=str(user.id))  # Changed: str(user.id)
        return jsonify({
            "access_token": access_token,
            "token_type": "Bearer",
            "user_id": user.id,
            "message": "Login successful"
        }), 200
    else:
        return jsonify({
            "error": "Invalid username or password",
            "code": 401
        }), 401

# US-13: GET /protected (simple protected endpoint for testing)
@app.get("/protected")
@jwt_required()
def protected():
    current_user_id = get_jwt_identity()  # This is now a string
    return jsonify({
        "message": "Access granted",
        "user_id": int(current_user_id)  # Convert back to int for display
    }), 200

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

# ============================================
# US-10: OBSERVATIONS CRUD (Create + Read with Filtering)
# ============================================

# US-10: POST /observations - Store geospatial observation data
@app.post("/observations")
@jwt_required()  # US-13: Protect with JWT (same as GET)
def create_observation():
    # US-10: Parse JSON payload
    data = request.get_json()
    if not data:
        return jsonify({
            "error": "No JSON payload provided",
            "code": 400
        }), 400

    try:
        # US-10: Extract and validate timestamp (required field)
        timestamp_str = data.get('timestamp')
        if not timestamp_str:
            return jsonify({
                "error": "Validation failed",
                "message": "Missing or invalid required fields",
                "details": {"timestamp": ["Missing data for required field."]},
                "code": 400
            }), 400
        
        # Parse timestamp to datetime object
        try:
            timestamp_dt = datetime.fromisoformat(timestamp_str.replace('Z', '+00:00'))
        except ValueError:
            return jsonify({
                "error": "Invalid timestamp format. Use ISO 8601 (e.g., 2025-11-27T12:00:00)",
                "code": 400
            }), 400
        
        #  -----------------------------
        # US-10: Determine quarter start (not stored, just for demo)
        # Step 1: Determine the start of the current quarter
        # -----------------------------
        month = datetime.utcnow().month
        year = datetime.utcnow().year
        if month in [1, 2, 3]:
            quarter_start = datetime(year, 1, 1)
        elif month in [4, 5, 6]:
            quarter_start = datetime(year, 4, 1)
        elif month in [7, 8, 9]:
            quarter_start = datetime(year, 7, 1)
        else:  # 10,11,12
            quarter_start = datetime(year, 10, 1)

       # Step 2: Reject observations before current quarter
        if timestamp_dt < quarter_start:
            return jsonify({
                "error": "Cannot create observation before current quarter",
                "code": 400
            }), 400


        # Create new Observation instance
        new_observation = Observation(
            timestamp=timestamp_dt,
            timezone=data.get('timezone'),
            coordinates=data.get('coordinates'),  # e.g., "lat=40.7,long=-74.0"
            satellite_id=data.get('satellite_id'),
            spectral_indices=data.get('spectral_indices'),  # e.g., JSON string like '{"ndvi": 0.5}'
            notes=data.get('notes')
        )
        
        # Persist to DB
        db.session.add(new_observation)
        db.session.commit()
        
        # US-10: Return persisted data as JSON with ISO timestamp (schema handles serialization)
        return jsonify(observation_schema.dump(new_observation)), 201  # 201 Created
        
    except Exception as e:
        db.session.rollback()
        return jsonify({
            "error": "Failed to store observation",
            "code": 500
        }), 500  # Uses existing handler

# US-11: PUT /observations/<id> - Full update (protected from historical edits)
@app.put("/observations/<int:obs_id>")
@jwt_required()  # US-13: Protect with JWT
def update_observation_full(obs_id):
    # Fetch existing observation
    obs = Observation.query.get_or_404(obs_id)
    
    # US-11: Check if historical (before current quarter)
    current_quarter_start = get_current_quarter_start()
    if obs.timestamp < current_quarter_start:
        return jsonify({
            "error": "Historical data cannot be modified",
            "message": f"Records before {current_quarter_start.date()} are immutable",
            "code": 403
        }), 403  # Uses existing 403 handler
    
    # US-10: Parse JSON payload for update
    data = request.get_json()
    if not data:
        return jsonify({
            "error": "No JSON payload provided",
            "code": 400
        }), 400
    
    try:
        # Update fields (allow partial, but since PUT, assume full; validate timestamp if provided)
        timestamp_str = data.get('timestamp')
        if timestamp_str:
            try:
                new_timestamp = datetime.fromisoformat(timestamp_str.replace('Z', '+00:00'))
                obs.timestamp = new_timestamp
            except ValueError:
                return jsonify({
                    "error": "Invalid timestamp format. Use ISO 8601 (e.g., 2025-11-27T12:00:00)",
                    "code": 400
                }), 400
        
        obs.timezone = data.get('timezone', obs.timezone)
        obs.coordinates = data.get('coordinates', obs.coordinates)
        obs.satellite_id = data.get('satellite_id', obs.satellite_id)
        obs.spectral_indices = data.get('spectral_indices', obs.spectral_indices)
        obs.notes = data.get('notes', obs.notes)
        
        # Persist update
        db.session.commit()
        
        # Return updated data as JSON with ISO timestamp
        return jsonify(observation_schema.dump(obs)), 200
        
    except Exception as e:
        db.session.rollback()
        return jsonify({
            "error": "Failed to update observation",
            "code": 500
        }), 500

# US-11: PATCH /observations/<id> - Partial update (protected from historical edits)
@app.patch("/observations/<int:obs_id>")
@jwt_required()  # US-13: Protect with JWT
def update_observation_partial(obs_id):
    # Fetch existing observation
    obs = Observation.query.get_or_404(obs_id)
    
    # US-11: Check if historical (before current quarter)
    current_quarter_start = get_current_quarter_start()
    if obs.timestamp < current_quarter_start:
        return jsonify({
            "error": "Historical data cannot be modified",
            "message": f"Records before {current_quarter_start.date()} are immutable",
            "code": 403
        }), 403  # Uses existing 403 handler
    
    # US-10: Parse JSON payload for partial update
    data = request.get_json()
    if not data:
        return jsonify({
            "error": "No JSON payload provided",
            "code": 400
        }), 400
    
    try:
        # Update only provided fields
        if 'timestamp' in data:
            try:
                new_timestamp = datetime.fromisoformat(data['timestamp'].replace('Z', '+00:00'))
                obs.timestamp = new_timestamp
            except ValueError:
                return jsonify({
                    "error": "Invalid timestamp format. Use ISO 8601 (e.g., 2025-11-27T12:00:00)",
                    "code": 400
                }), 400
        
        if 'timezone' in data:
            obs.timezone = data['timezone']
        if 'coordinates' in data:
            obs.coordinates = data['coordinates']
        if 'satellite_id' in data:
            obs.satellite_id = data['satellite_id']
        if 'spectral_indices' in data:
            obs.spectral_indices = data['spectral_indices']
        if 'notes' in data:
            obs.notes = data['notes']
        
        # Persist update
        db.session.commit()
        
        # Return updated data as JSON with ISO timestamp
        return jsonify(observation_schema.dump(obs)), 200
        
    except Exception as e:
        db.session.rollback()
        return jsonify({
            "error": "Failed to update observation",
            "code": 500
        }), 500

# US-09: GET /observations with filtering support
@app.get("/observations")
@jwt_required()
def get_observations():
    current_user_id = get_jwt_identity()  # This is now a string
    # Convert to int if you need to query by user_id: int(current_user_id)
    
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

# US-12: Bulk create observations
@app.post("/observations/bulk")
def bulk_create_observations():
    data = request.get_json()

    if not isinstance(data, list):
        return jsonify({
            "error": "Bad Request",
            "message": "Expected a list of observation objects",
            "code": 400
        }), 400

    created = []
    errors = []

    for index, item in enumerate(data):
        # Validate required fields
        required = ["timestamp", "timezone", "coordinates", "satellite_id"]
        missing = [f for f in required if f not in item]

        if missing:
            errors.append({
                "record": index,
                "error": f"Missing required fields: {', '.join(missing)}"
            })
            continue

        # Parse timestamp safely
        try:
            timestamp = datetime.fromisoformat(item["timestamp"].replace("Z", "+00:00"))
        except ValueError:
            errors.append({
                "record": index,
                "error": "Invalid timestamp format. Use ISO 8601"
            })
            continue

        # Create record
        obs = Observation(
            timestamp=timestamp,
            timezone=item.get("timezone"),
            coordinates=item.get("coordinates"),
            satellite_id=item.get("satellite_id"),
            spectral_indices=json.dumps(item.get("spectral_indices")),
            notes=item.get("notes")
        )

        db.session.add(obs)
        created.append(obs)

    # If ANY errors → rollback everything
    if errors:
        db.session.rollback()
        return jsonify({
            "message": "Bulk insert failed",
            "errors": errors
        }), 400

    # Otherwise commit all
    db.session.commit()

    return jsonify({
        "message": "Bulk insert successful",
        "created_count": len(created),
        "records": observations_schema.dump(created)
    }), 201

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

# ============================================
# NOTES
# ============================================
# Use @jwt_required() decorator on any endpoint that needs JWT protection
# Test with: curl -H "Authorization: Bearer <token>" http://localhost:5000/observations
# Get token from /auth/login endpoint (POST with username and password)

# -----------------------------
# RUN SERVER
# -----------------------------
if __name__ == "__main__":
    app.run(debug=True)