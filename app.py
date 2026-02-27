from flask import Flask, render_template, request, redirect, url_for, session
import sqlite3
import os
from authlib.integrations.flask_client import OAuth
from dotenv import load_dotenv
from werkzeug.utils import secure_filename
from flask import send_from_directory


# -------------------------------------------------
# Load environment variables
# -------------------------------------------------
load_dotenv()

# -------------------------------------------------
# Flask app setup
# -------------------------------------------------
app = Flask(__name__)
app.secret_key = os.getenv("FLASK_SECRET_KEY", "dev_secret_key")

UPLOAD_FOLDER = "uploads"
ALLOWED_EXTENSIONS = {"png", "jpg", "jpeg"}


app.config["UPLOAD_FOLDER"] = UPLOAD_FOLDER

# -------------------------------------------------
# Database helper
# -------------------------------------------------
def get_db():
    conn = sqlite3.connect("database.db")
    conn.row_factory = sqlite3.Row
    return conn

# -------------------------------------------------
# File helper
# -------------------------------------------------
def allowed_file(filename):
    return "." in filename and filename.rsplit(".", 1)[1].lower() in ALLOWED_EXTENSIONS

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
# ---------------- REGISTER PAGE ----------------
@app.route("/register", methods=["GET"])
def register_page():
    return render_template("register.html")


# ---------------- REGISTER SAVE ----------------
@app.route("/register/save", methods=["POST"])
def register_save():
    username = request.form.get("username")
    password = request.form.get("password")
    avatar = request.form.get("avatar")

    if not username or not password or not avatar:
        return render_template("register.html", error="All fields are required")

    db = get_db()
    try:
        cur = db.execute(
            "INSERT INTO users (username, password, avatar) VALUES (?, ?, ?)",
            (username, password, avatar)
        )
        db.commit()
        session["user_id"] = cur.lastrowid
    except sqlite3.IntegrityError:
      
        db.close()
        return render_template("register.html", error="Username already exists")

    db.close()
    return redirect("/home")

# ---------------- Login ----------------
@app.route("/login", methods=["POST"])
def login():
    username = request.form.get("username")
    password = request.form.get("password")

    db = get_db()
    user = db.execute(
        "SELECT * FROM users WHERE username=?",
        (username,)
    ).fetchone()
    db.close()

    print("LOGIN DATA:", username, password)
    print("DB USER:", dict(user) if user else None)

    if not user:
        return render_template("index.html", error="User not found")

    if user["password"] != password:
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
        short_name=(user["username"] or "")[:7]
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

    avatar_file = request.files.get("avatar")
    avatar_filename = None

    if avatar_file and allowed_file(avatar_file.filename):
        filename = secure_filename(avatar_file.filename)
        avatar_path = os.path.join(app.config["UPLOAD_FOLDER"], filename)
        avatar_file.save(avatar_path)
        avatar_filename = filename

    db = get_db()

    if avatar_filename:
        db.execute("""
            UPDATE users
            SET mobile = ?, dob = ?, address = ?, avatar = ?
            WHERE id = ?
        """, (mobile, dob, address, avatar_filename, session["user_id"]))
    else:
        db.execute("""
            UPDATE users
            SET mobile = ?, dob = ?, address = ?
            WHERE id = ?
        """, (mobile, dob, address, session["user_id"]))

    db.commit()
    db.close()

    return redirect("/profile")

# ---------------- Avatar Upload ----------------
@app.route("/profile/avatar", methods=["POST"])
def upload_avatar():
    if "user_id" not in session:
        return redirect("/")

    file = request.files.get("avatar")
    if not file or file.filename == "":
        return redirect("/profile")

    if allowed_file(file.filename):
        filename = secure_filename(file.filename)
        filename = f"user_{session['user_id']}_{filename}"
        path = os.path.join(app.config["UPLOAD_FOLDER"], filename)
        file.save(path)

        db = get_db()
        db.execute(
            "UPDATE users SET avatar = ? WHERE id = ?",
            (filename, session["user_id"])
        )
        db.commit()
        db.close()

    return redirect("/profile")

@app.route("/uploads/<avatar>")
def uploaded_file(filename):
    return send_from_directory(app.config["UPLOAD_FOLDER"], filename)

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