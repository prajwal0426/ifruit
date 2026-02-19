from flask import (
    Flask, render_template, request,
    redirect, url_for, session,
    send_from_directory
)
import sqlite3, os, random, uuid
from authlib.integrations.flask_client import OAuth
from dotenv import load_dotenv
from werkzeug.security import generate_password_hash, check_password_hash
from werkzeug.utils import secure_filename

# -------------------------------------------------
# Load env
# -------------------------------------------------
load_dotenv()

app = Flask(__name__)
app.secret_key = os.getenv("FLASK_SECRET_KEY", "dev_secret_key")

# -------------------------------------------------
# Upload config
# -------------------------------------------------
UPLOAD_FOLDER = "uploads"
ALLOWED_EXTENSIONS = {"png", "jpg", "jpeg"}

app.config["UPLOAD_FOLDER"] = UPLOAD_FOLDER
app.config["MAX_CONTENT_LENGTH"] = 2 * 1024 * 1024
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

# -------------------------------------------------
# Default avatars
# -------------------------------------------------
DEFAULT_AVATARS = [
    "avatars/avatar1.png",
    "avatars/avatar2.png",
    "avatars/avatar3.png",
]

def random_avatar():
    return random.choice(DEFAULT_AVATARS)

# -------------------------------------------------
# Database
# -------------------------------------------------
def get_db():
    conn = sqlite3.connect("database.db")
    conn.row_factory = sqlite3.Row
    return conn

def init_db():
    db = get_db()
    db.execute("""
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT UNIQUE,
            email TEXT UNIQUE,
            password TEXT,
            google_id TEXT UNIQUE,
            mobile TEXT,
            dob TEXT,
            address TEXT,
            avatar TEXT
        )
    """)
    db.commit()

init_db()

# -------------------------------------------------
# Helpers
# -------------------------------------------------
def allowed_file(filename):
    return "." in filename and filename.rsplit(".", 1)[1].lower() in ALLOWED_EXTENSIONS

# -------------------------------------------------
# Google OAuth
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
        return render_template("index.html", error="All fields required")

    hashed = generate_password_hash(password)
    avatar = random_avatar()

    db = get_db()
    try:
        db.execute(
            "INSERT INTO users (username, password, avatar) VALUES (?, ?, ?)",
            (username, hashed, avatar)
        )
        db.commit()
    except sqlite3.IntegrityError:
        return render_template("index.html", error="User already exists")

    session["username"] = username
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

    if not user or not check_password_hash(user["password"], password):
        return render_template("index.html", error="Invalid credentials")

    session["username"] = user["username"]
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

    email = user_info.get("email")
    google_id = user_info.get("id")
    name = user_info.get("name")

    db = get_db()
    user = db.execute(
        "SELECT * FROM users WHERE email=?",
        (email,)
    ).fetchone()

    if not user:
        db.execute("""
            INSERT INTO users (username, email, google_id, avatar)
            VALUES (?, ?, ?, ?)
        """, (
            name[:7],
            email,
            google_id,
            random_avatar()
        ))
        db.commit()

    session["username"] = email
    return redirect("/home")

# ---------------- Home ----------------
@app.route("/home")
def home():
    if "username" not in session:
        return redirect("/")

    db = get_db()
    user = db.execute(
        "SELECT * FROM users WHERE username=? OR email=?",
        (session["username"], session["username"])
    ).fetchone()

    return render_template(
        "home.html",
        user=user,
        short_name=user["username"][:7]
    )

# ---------------- Profile ----------------
@app.route("/profile")
def profile():
    if "username" not in session:
        return redirect("/")

    db = get_db()
    user = db.execute(
        "SELECT * FROM users WHERE username=? OR email=?",
        (session["username"], session["username"])
    ).fetchone()

    return render_template("profile.html", user=user)

# ---------------- Profile Update ----------------
@app.route("/profile/update", methods=["POST"])
def update_profile():
    if "username" not in session:
        return redirect("/")

    mobile = request.form.get("mobile")
    dob = request.form.get("dob")
    address = request.form.get("address")

    avatar_file = request.files.get("avatar")
    avatar_path = None

    if avatar_file and allowed_file(avatar_file.filename):
        filename = f"{uuid.uuid4().hex}_{secure_filename(avatar_file.filename)}"
        avatar_file.save(os.path.join(UPLOAD_FOLDER, filename))
        avatar_path = filename

    db = get_db()

    if avatar_path:
        db.execute("""
            UPDATE users
            SET mobile=?, dob=?, address=?, avatar=?
            WHERE username=? OR email=?
        """, (
            mobile, dob, address, avatar_path,
            session["username"], session["username"]
        ))
    else:
        db.execute("""
            UPDATE users
            SET mobile=?, dob=?, address=?
            WHERE username=? OR email=?
        """, (
            mobile, dob, address,
            session["username"], session["username"]
        ))

    db.commit()
    return redirect("/profile")

# ---------------- Serve uploads ----------------
@app.route("/uploads/<filename>")
def uploads(filename):
    return send_from_directory(UPLOAD_FOLDER, filename)

# ---------------- Logout ----------------
@app.route("/logout")
def logout():
    session.clear()
    return redirect("/")

# -------------------------------------------------
# Run app (PORT 10000 ✅)
# -------------------------------------------------
if __name__ == "__main__":
    port = int(os.environ.get("PORT", 10000))
    app.run(host="0.0.0.0", port=port)
