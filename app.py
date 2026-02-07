from flask import Flask, render_template, request, redirect, url_for

app = Flask(__name__)

PASSWORD = "iamhear123"

@app.route("/")
def login_page():
    return render_template("index.html")

@app.route("/login", methods=["POST"])
def login():
    username = request.form.get("username")
    password = request.form.get("password")

    if password == PASSWORD and username:
        return redirect(url_for("home", user=username))
    else:
        return render_template("index.html", error="Wrong password")

@app.route("/home")
def home():
    user = request.args.get("user")
    return render_template("home.html", username=user)

if __name__ == "__main__":
    app.run(debug=True)
