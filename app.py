from flask import Flask, render_template, request, redirect, url_for

app = Flask(__name__)

# Temporary user storage (username: password)
users = {}

@app.route("/")
def index():
    return render_template("index.html")

@app.route("/register", methods=["POST"])
def register():
    username = request.form.get("username")
    password = request.form.get("password")

    if not username or not password:
        return render_template("index.html", error="All fields are required")

    if username in users:
        return render_template("index.html", error="User already exists")

    users[username] = password
    return render_template("index.html", success="Registration successful! Please login.")

@app.route("/login", methods=["POST"])
def login():
    username = request.form.get("username")
    password = request.form.get("password")

    if username in users and users[username] == password:
        return redirect(url_for("home", user=username))
    else:
        return render_template("index.html", error="Invalid username or password")

@app.route("/home")
def home():
    user = request.args.get("user")
    return render_template("home.html", username=user)

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=True)
