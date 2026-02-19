from flask import Flask, render_template, request, redirect, url_for, session, send_from_directory
import sqlite3, os, random, uuid
from dotenv import load_dotenv
from werkzeug.security import generate_password_hash, check_password_hash
from werkzeug.utils import secure_filename
from authlib.integrations.flask_client import OAuth

# -------------------------------------------------
# Load env
# -------------------------------------------------
load_dotenv()

app = Flask(__name__)
app.secret_key = os.getenv("FLASK_SECRET_KEY", "dev_key")

# -------------------------------------------------
# Config
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
    username = request.form["username"]
    password = request.form["password"]

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

    user = db.execute("SELECT id FROM users WHERE username=?", (username,)).fetchone()
    session["user_id"] = user["id"]
    return redirect("/home")

# ---------------- Login ----------------
@app.route("/login", methods=["POST"])
def login():
    username = request.form["username"]
    password = request.form["password"]

    db = get_db()
    user = db.execute(
        "SELECT * FROM users WHERE username=?",
        (username,)
    ).fetchone()

    if not user or not check_password_hash(user["password"], password):
        return render_template("index.html", error="Invalid credentials")

    session["user_id"] = user["id"]
    return redirect("/home")



# ---------------- Google Login ----------------
@app.route("/login/google")
def login_google():
    return google.authorize_redirect(url_for("google_callback", _external=True))

@app.route("/auth/google")
def google_callback():
    google.authorize_access_token()
    info = google.get("https://www.googleapis.com/oauth2/v2/userinfo").json()

    email = info["email"]
    google_id = info["id"]
    name = info["name"]

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

        user = db.execute(
            "SELECT * FROM users WHERE email=?",
            (email,)
        ).fetchone()

    session["user_id"] = user["id"]
    return redirect("/home")

# ---------------- Home ----------------
@app.route("/home")
def home():
    if "user_id" not in session:
        return redirect("/")

    db = get_db()
    user = db.execute(
        "SELECT * FROM users WHERE id=?",
        (session["user_id"],)
    ).fetchone()

    return render_template(
        "home.html",
        user=user,
        short_name=user["username"][:7]
    )

# ---------------- Profile ----------------
@app.route("/profile")
def profile():
    if "user_id" not in session:
        return redirect("/")

    db = get_db()
    user = db.execute(
        "SELECT * FROM users WHERE id=?",
        (session["user_id"],)
    ).fetchone()

    return render_template("profile.html", user=user)

# ---------------- Update Profile ----------------
@app.route("/profile/update", methods=["POST"])
def update_profile():
    if "user_id" not in session:
        return redirect("/")

    mobile = request.form["mobile"]
    dob = request.form["dob"]
    address = request.form["address"]

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
            WHERE id=?
        """, (mobile, dob, address, avatar_path, session["user_id"]))
    else:
        db.execute("""
            UPDATE users
            SET mobile=?, dob=?, address=?
            WHERE id=?
        """, (mobile, dob, address, session["user_id"]))

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
if __name__ == "__main__":
    app.run(debug=True)
