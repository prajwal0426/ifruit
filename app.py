from flask import Flask, render_template, request, redirect, url_for, session
import sqlite3
import os
from authlib.integrations.flask_client import OAuth
from dotenv import load_dotenv

# -------------------------------------------------
# Load environment variables
# -------------------------------------------------
load_dotenv()

# -------------------------------------------------
# Flask app setup
# -------------------------------------------------
app = Flask(__name__)
app.secret_key = os.getenv("FLASK_SECRET_KEY", "dev_secret_key")

# -------------------------------------------------
# Database helper
# -------------------------------------------------
def get_db():
    conn = sqlite3.connect("database.db")
    conn.row_factory = sqlite3.Row
    return conn

# -------------------------------------------------
# Initialize database (IMPORTANT for Render)
# -------------------------------------------------
def init_db():
    db = get_db()
    db.execute("""
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT UNIQUE,
            password TEXT
        )
    """)
    db.commit()

init_db()

# -------------------------------------------------
# Google OAuth setup
# -------------------------------------------------
oauth = OAuth(app)

google = oauth.register(
    name="google",
    client_id=os.getenv("GOOGLE_CLIENT_ID"),
    client_secret=os.getenv("GOOGLE_CLIENT_SECRET"),
    server_metadata_url="https://accounts.google.com/.well-known/openid-configuration",
    client_kwargs={"scope": "openid email profile"},
)

# -------------------------------------------------
# Routes
# -------------------------------------------------

@app.route("/")
def index():
    return render_template("index.html")

# ---------------- Register ----------------
@app.route("/register", methods=["GET", "POST"])
def register():
    if request.method == "GET":
        return redirect("/")

    username = request.form.get("username")
    password = request.form.get("password")

    if not username or not password:
        return render_template("index.html", error="All fields are required")

    db = get_db()
    try:
        db.execute(
            "INSERT INTO users (username, password) VALUES (?, ?)",
            (username, password),
        )
        db.commit()
    except sqlite3.IntegrityError:
        return render_template("index.html", error="User already exists")

    session["username"] = username
    return redirect("/home")

# ---------------- Login ----------------
@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "GET":
        return redirect("/")

    username = request.form.get("username")
    password = request.form.get("password")

    db = get_db()
    user = db.execute(
        "SELECT * FROM users WHERE username = ? AND password = ?",
        (username, password),
    ).fetchone()

    if user:
        session["username"] = username
        return redirect("/home")

    return render_template("index.html", error="Invalid username or password")

# ---------------- Google Login ----------------
@app.route("/login/google")
def login_google():
    redirect_uri = url_for("google_callback", _external=True)
    return google.authorize_redirect(redirect_uri)

@app.route("/auth/google")
def google_callback():
    google.authorize_access_token()

  
    user_info = google.get(
        "https://www.googleapis.com/oauth2/v2/userinfo"
    ).json()
   
    email = user_info.get("email")
   
    if not email:
        return redirect("/")

    session["username"] = email
    return redirect("/home")

# ---------------- Home ----------------
@app.route("/home")
def home():
    if "username" not in session:
        return redirect("/")
    return render_template("home.html", username=session["username"])

# ---------------- Logout ----------------
@app.route("/logout")
def logout():
    session.clear()
    return redirect("/")

# -------------------------------------------------
# Run app (Local + Render compatible)
# -------------------------------------------------
if __name__ == "__main__":
    port = int(os.environ.get("PORT", 10000))
    app.run(host="0.0.0.0", port=port)
