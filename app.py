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
# Initialize database (Render-safe)
# -------------------------------------------------
def init_db():
    db = get_db()
    db.execute("""
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT UNIQUE,
            email TEXT UNIQUE,
            password TEXT,
            google_id TEXT UNIQUE,
            avatar TEXT,
            mobile TEXT,
            dob TEXT,
            address TEXT
        )
    """)
    db.commit()
    db.close()

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
@app.route("/register", methods=["POST"])
def register():
    username = request.form.get("username")
    password = request.form.get("password")

    if not username or not password:
        return render_template("index.html", error="All fields are required")

    db = get_db()
    try:
        cursor = db.execute(
            "INSERT INTO users (username, password) VALUES (?, ?)",
            (username, password)
        )
        db.commit()
        session["user_id"] = cursor.lastrowid
    except sqlite3.IntegrityError:
        return render_template("index.html", error="User already exists")
    finally:
        db.close()

    return redirect("/home")

# ---------------- Login ----------------
@app.route("/login", methods=["POST"])
def login():
    username = request.form.get("username")
    password = request.form.get("password")

    db = get_db()
    user = db.execute(
        "SELECT * FROM users WHERE username = ? AND password = ?",
        (username, password)
    ).fetchone()
    db.close()

    if not user:
        return render_template("index.html", error="Invalid username or password")

    session["user_id"] = user["id"]
    return redirect("/home")

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

    google_id = user_info.get("id")
    email = user_info.get("email")
    name = user_info.get("name")
    avatar = user_info.get("picture")

    if not email:
        return redirect("/")

    db = get_db()
    user = db.execute(
        "SELECT * FROM users WHERE google_id = ? OR email = ?",
        (google_id, email)
    ).fetchone()

    if not user:
        cursor = db.execute("""
            INSERT INTO users (username, email, google_id, avatar)
            VALUES (?, ?, ?, ?)
        """, (
            name or email.split("@")[0],
            email,
            google_id,
            avatar
        ))
        db.commit()
        session["user_id"] = cursor.lastrowid
    else:
        session["user_id"] = user["id"]

    db.close()
    return redirect("/home")

# ---------------- Home ----------------
@app.route("/home")
def home():
    if "user_id" not in session:
        return redirect("/")

    db = get_db()
    user = db.execute(
        "SELECT * FROM users WHERE id = ?",
        (session["user_id"],)
    ).fetchone()
    db.close()

    if not user:
        session.clear()
        return redirect("/")

    return render_template(
        "home.html",
        user=user,
        short_name=user["username"][:7] if user["username"] else ""
    )

# ---------------- Profile ----------------
@app.route("/profile")
def profile():
    if "user_id" not in session:
        return redirect("/")

    db = get_db()
    user = db.execute(
        "SELECT * FROM users WHERE id = ?",
        (session["user_id"],)
    ).fetchone()
    db.close()

    if not user:
        return redirect("/")

    return render_template("profile.html", user=user)

# ---------------- Profile Update ----------------
@app.route("/profile/update", methods=["POST"])
def update_profile():
    if "user_id" not in session:
        return redirect("/")

    mobile = request.form.get("mobile")
    dob = request.form.get("dob")
    address = request.form.get("address")

    db = get_db()
    db.execute("""
        UPDATE users
        SET mobile = ?, dob = ?, address = ?
        WHERE id = ?
    """, (mobile, dob, address, session["user_id"]))

    db.commit()
   
    return redirect("/profile")

# ---------------- Logout ----------------
@app.route("/logout")
def logout():
    session.clear()
    return redirect("/")

# -------------------------------------------------
# Run app (Local + Render)
# -------------------------------------------------
if __name__ == "__main__":
    port = int(os.environ.get("PORT", 10000))
    app.run(host="0.0.0.0", port=port, debug=True)