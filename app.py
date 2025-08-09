import os
from flask import Flask, jsonify, request, abort

app = Flask(__name__)

# In-memory "database"
db = set()

# Get login token from environment variable
LOGIN_TOKEN = os.getenv("LOGIN_TOKEN", "default_token_if_not_set")

@app.route("/FileCheckUpdate", methods=["POST"])
def check():
    data = request.json
    if not data or 'login' not in data:
        abort(400, description="Missing login")

    login = data['login']
    if login != LOGIN_TOKEN:
        abort(401, description="Invalid Login")

    db.add("96440447 445822306 7101938164 1312013306 3413636505 8781178615 ...")  # truncated for brevity
    return jsonify("Update successful"), 200

@app.route("/update", methods=["POST"])
def updateDb():
    data = request.json
    if not data or 'id' not in data or 'login' not in data:
        abort(400, description="Missing UserID or Credentials")

    login = data['login']
    if login != LOGIN_TOKEN:
        abort(401, description="Invalid Login")

    userID = data['id']

    if userID not in db:
        db.add(userID)
        return jsonify("added"), 201
    else:
        return jsonify("Already in DB"), 200

@app.route("/items", methods=["POST"])
def create_item():
    data = request.json
    if not data or 'id' not in data:
        abort(400, description="Missing item ID")

    userID = data['id']

    if userID in db:
        return jsonify(True), 200
    else:
        return jsonify(False), 200

if __name__ == "__main__":
    app.run(debug=True)
