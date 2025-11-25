from flask import Flask, jsonify

app = Flask(__name__)

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
