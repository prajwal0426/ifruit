from flask import Flask, render_template, request, redirect, url_for, session
import sqlite3, os
from authlib.integrations.flask_client import OAuth
from dotenv import load_dotenv
from werkzeug.utils import secure_filename

load_dotenv()

app = Flask(__name__)
app.secret_key = os.getenv("FLASK_SECRET_KEY", "dev_key")

UPLOAD_FOLDER = "uploads"
os.makedirs(UPLOAD_FOLDER, exist_ok=True)
app.config["UPLOAD_FOLDER"] = UPLOAD_FOLDER

# ---------------- DB ----------------
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
            avatar TEXT,
            mobile TEXT,
            dob TEXT,
            address TEXT
        )
    """)
    db.commit()

init_db()

# ---------------- OAuth ----------------
oauth = OAuth(app)

google = oauth.register(
    name="google",
    client_id=os.getenv("GOOGLE_CLIENT_ID"),
    client_secret=os.getenv("GOOGLE_CLIENT_SECRET"),
    server_metadata_url="https://accounts.google.com/.well-known/openid-configuration",
    client_kwargs={"scope": "openid email profile"},
)

# ---------------- Routes ----------------
@app.route("/")
def index():
    return render_template("index.html")

@app.route("/register", methods=["POST"])
def register():
    username = request.form["username"]
    password = request.form["password"]

    try:
        db = get_db()
        db.execute("INSERT INTO users (username, password) VALUES (?,?)",
                   (username, password))
        db.commit()
        session["user"] = username
        return redirect("/home")
    except:
        return render_template("index.html", error="User exists")

@app.route("/login", methods=["POST"])
def login():
    db = get_db()
    user = db.execute(
        "SELECT * FROM users WHERE username=? AND password=?",
        (request.form["username"], request.form["password"])
    ).fetchone()

    if user:
        session["user"] = user["username"]
        return redirect("/home")
    return render_template("index.html", error="Invalid login")

@app.route("/login/google")
def login_google():
    return google.authorize_redirect(url_for("google_callback", _external=True))

@app.route("/auth/google")
def google_callback():
    token = google.authorize_access_token()
    info = google.get("https://www.googleapis.com/oauth2/v2/userinfo").json()

    db = get_db()
    user = db.execute(
        "SELECT * FROM users WHERE email=?",
        (info["email"],)
    ).fetchone()

    if not user:
        db.execute("""
            INSERT INTO users (username, email, google_id, avatar)
            VALUES (?,?,?,?)
        """, (
            info["name"][:7],
            info["email"],
            info["id"],
            info["picture"]
        ))
        db.commit()

    session["user"] = info["email"]
    return redirect("/home")

@app.route("/home")
def home():
    if "user" not in session:
        return redirect("/")
    db = get_db()
    user = db.execute(
        "SELECT * FROM users WHERE username=? OR email=?",
        (session["user"], session["user"])
    ).fetchone()
    return render_template("home.html", user=user)

@app.route("/profile")
def profile():
    db = get_db()
    user = db.execute(
        "SELECT * FROM users WHERE username=? OR email=?",
        (session["user"], session["user"])
    ).fetchone()
    return render_template("profile.html", user=user)

@app.route("/profile/update", methods=["POST"])
def profile_update():
    avatar = request.files.get("avatar")
    filename = None

    if avatar:
        filename = secure_filename(avatar.filename)
        avatar.save(os.path.join(app.config["UPLOAD_FOLDER"], filename))

    db = get_db()
    db.execute("""
        UPDATE users SET
        mobile=?, dob=?, address=?, avatar=COALESCE(?, avatar)
        WHERE username=? OR email=?
    """, (
        request.form["mobile"],
        request.form["dob"],
        request.form["address"],
        filename,
        session["user"],
        session["user"]
    ))
    db.commit()
    return redirect("/profile")

@app.route("/logout")
def logout():
    session.clear()
    return redirect("/")

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=int(os.environ.get("PORT", 10000)))
