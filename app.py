import os
from flask import Flask, jsonify, request, abort, render_template_string

app = Flask(__name__)

# In-memory "database"
db = set()

# Get login token from environment variable
LOGIN_TOKEN = os.getenv("LOGIN_TOKEN", "")

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
    <form method="POST">
      <textarea name="users" rows="20" cols="60" style="font-family: monospace;">{{ users }}</textarea><br><br>
      <button type="submit">Update Database</button>
    </form>
  {% endif %}
</body>
</html>
"""

@app.route("/admin", methods=["GET", "POST"])
def admin():
    global db
    if request.method == "POST":
        if "password" in request.form:
            # Password submission to gain access
            if request.form["password"] == LOGIN_TOKEN:
                # Show user list for editing
                users_text = "\n".join(sorted(db))
                return render_template_string(ADMIN_PAGE_HTML, authorized=True, users=users_text)
            else:
                return render_template_string(ADMIN_PAGE_HTML, authorized=False, error="Incorrect password")
        
        elif "users" in request.form:
            # User list update submission
            submitted_users = request.form["users"]
            # Update the in-memory db (overwrite)
            new_db = set(line.strip() for line in submitted_users.splitlines() if line.strip())
            db = new_db
            users_text = "\n".join(sorted(db))
            return render_template_string(ADMIN_PAGE_HTML, authorized=True, users=users_text)

    # GET request - show password form
    return render_template_string(ADMIN_PAGE_HTML, authorized=False)

if __name__ == "__main__":
    app.run(debug=True)
