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