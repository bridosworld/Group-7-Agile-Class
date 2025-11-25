from flask import Flask, jsonify

# Create the Flask app
app = Flask(__name__)

# Health check endpoint for US-05
@app.get("/health")
def health():
    # Must return 200 OK with {"status": "ok"}
    return jsonify({"status": "ok"}), 200


# Optional root endpoint, handy for quick checks
@app.get("/")
def root():
    return jsonify({
        "message": "TerraScope API is running",
        "status": "ok"
    }), 200


if __name__ == "__main__":
    app.run(debug=True)
