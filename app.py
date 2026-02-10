from flask import Flask, render_template, request, redirect, url_for, session
import sqlite3

app = Flask(__name__)
app.secret_key = "secret123"  # needed for sessions


# Database helper
def get_db():
    conn = sqlite3.connect("database.db")
    conn.row_factory = sqlite3.Row
    return conn


@app.route("/")
def index():
    return render_template("index.html")


@app.route("/register", methods=["POST"])
def register():
    username = request.form.get("username")
    password = request.form.get("password")

    if not username or not password:
        return render_template("index.html", error="All fields are required")

    db = get_db()

    try:
        db.execute(
            "INSERT INTO users (username, password) VALUES (?, ?)",
            (username, password)
        )
        db.commit()
    except:
        return render_template("index.html", error="User already exists")

    # auto login
    session["username"] = username
    return redirect("/home")


@app.route("/login", methods=["POST"])
def login():
    username = request.form.get("username")
    password = request.form.get("password")

    db = get_db()
    user = db.execute(
        "SELECT * FROM users WHERE username = ? AND password = ?",
        (username, password)
    ).fetchone()

    if user:
        session["username"] = username
        return redirect("/home")

    return render_template("index.html", error="Invalid username or password")


@app.route("/home")
def home():
    if "username" not in session:
        return redirect("/")
    return render_template("home.html", username=session["username"])


@app.route("/logout")
def logout():
    session.clear()
    return redirect("/")


if __name__ == "__main__":
    app.run(debug=True)
