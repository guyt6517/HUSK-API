import os
from flask import Response, Flask, jsonify, request, abort, render_template_string, session
import random
from flask_cors import CORS

app = Flask(__name__)
CORS(app)

DB_FILE = "db.txt"
LOGIN_TOKEN = os.getenv("LOGIN_TOKEN")

app.secret_key = LOGIN_TOKEN 
if not app.secret_key or app.secret_key == "":
    app.secret_key = random.randint(1, 10000)

# The DB is now a dict: userID (str) -> reason (str or None)
if os.path.exists(DB_FILE):
    with open(DB_FILE, "r", encoding="utf-8") as f:
        db = {}
        for line in f:
            line = line.strip()
            if not line or line.startswith("#"):
                continue
            parts = line.split(",", 1)
            user_id = parts[0].strip()
            reason = parts[1].strip() if len(parts) > 1 else None
            db[user_id] = reason
else:
    db = {}

def save_db():
    print(f"[DEBUG] Saving DB with {len(db)} users")
    with open(DB_FILE, "w", encoding="utf-8") as f:
        for user_id, reason in sorted(db.items()):
            if reason:
                f.write(f"{user_id}, {reason}\n")
            else:
                f.write(f"{user_id}\n")

@app.route("/FileCheckUpdate", methods=["POST"])
def check():
    data = request.json
    if not data or 'login' not in data:
        abort(400, description="Missing login")

    login = data['login']
    if login != LOGIN_TOKEN:
        abort(401, description="Invalid Login")

    # Add initial IDs (no reasons for these)
    initial_ids = {
        "96440447": None,
        "445822306": None,
        "7101938164": None,
        "1312013306": None,
        "3413636505": None,
        "8781178615": None,
    }
    db.update(initial_ids)
    save_db()

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
    reason = data.get('reason')  # Optional

    if userID not in db:
        db[userID] = reason
        save_db()
        return jsonify("added"), 201
    else:
        # Update reason if provided and different
        if reason and db.get(userID) != reason:
            db[userID] = reason
            save_db()
            return jsonify("reason updated"), 200
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

ADMIN_PAGE_HTML = """
<!doctype html>
<html lang="en">
<head>
  <meta charset="utf-8">
  <title>Admin User Database</title>
</head>
<body>
  {% if not authorized %}
    <h2>Enter Admin Password</h2>
    {% if error %}
      <p style="color:red;">{{ error }}</p>
    {% endif %}
    <form method="POST">
      <input type="password" name="password" placeholder="Password" required>
      <button type="submit">Submit</button>
    </form>
  {% else %}
    <h2>Editable User Database</h2>
    <p>Format: <code>userID, reason (optional)</code> one per line.</p>
    <form method="POST">
      <textarea name="users" rows="20" cols="60" style="font-family: monospace;">{{ users }}</textarea><br><br>
      <button type="submit">Update Database</button>
    </form>
  {% endif %}
</body>
</html>
"""

@app.route("/GetCurrentDB", methods=["GET"])
def passDB():
    with open(DB_FILE, "r", encoding="utf-8") as o:
        db_content = o.read()
    return Response(db_content, mimetype="text/plain")

@app.route("/admin", methods=["GET", "POST"])
def admin():
    global db
    error = None

    if request.method == "POST":
        if "password" in request.form:
            if request.form["password"] == LOGIN_TOKEN:
                session["authorized"] = True
                users_text = "\n".join(
                    f"{uid}, {reason}" if reason else uid for uid, reason in sorted(db.items())
                )
                return render_template_string(ADMIN_PAGE_HTML, authorized=True, users=users_text)
            else:
                error = "Incorrect password"
                return render_template_string(ADMIN_PAGE_HTML, authorized=False, error=error)
        
        elif "users" in request.form:
            if not session.get("authorized"):
                error = "Unauthorized"
                return render_template_string(ADMIN_PAGE_HTML, authorized=False, error=error)
            
            submitted_users = request.form["users"]
            print(f"[DEBUG] Received updated users:\n{submitted_users}")
            new_db = {}
            for line in submitted_users.splitlines():
                line = line.strip()
                if not line or line.startswith("#"):
                    continue
                parts = line.split(",", 1)
                user_id = parts[0].strip()
                reason = parts[1].strip() if len(parts) > 1 else None
                new_db[user_id] = reason
            db = new_db
            save_db()
            users_text = "\n".join(
                f"{uid}, {reason}" if reason else uid for uid, reason in sorted(db.items())
            )
            return render_template_string(ADMIN_PAGE_HTML, authorized=True, users=users_text)

    # For GET or unauthorized POST
    if session.get("authorized"):
        users_text = "\n".join(
            f"{uid}, {reason}" if reason else uid for uid, reason in sorted(db.items())
        )
        return render_template_string(ADMIN_PAGE_HTML, authorized=True, users=users_text)
    else:
        return render_template_string(ADMIN_PAGE_HTML, authorized=False, error=error)

if __name__ == "__main__":
    app.run(debug=True)
