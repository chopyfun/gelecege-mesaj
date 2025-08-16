from flask import Flask, render_template, request, redirect, url_for, session, jsonify
from flask_cors import CORS
from datetime import datetime

app = Flask(__name__)
app.secret_key = "supersecretkey"
CORS(app)

# Basit kullanıcı veritabanı (örnek)
users = {
    "admin@test.com": {"password": "1234", "role": "admin"},
    "normal@test.com": {"password": "1234", "role": "user"}
}

# Mesajları burada saklıyoruz (şimdilik RAM üzerinde)
messages = []

# ---------------- ROUTES ----------------

# Landing page
@app.route("/")
def index():
    return render_template("index.html")

# Register
@app.route("/register", methods=["GET", "POST"])
def register():
    if request.method == "POST":
        email = request.form["email"]
        password = request.form["password"]

        if email in users:
            return "❌ Bu kullanıcı zaten var!"

        users[email] = {"password": password, "role": "user"}
        return redirect(url_for("login"))

    return render_template("register.html")

# Login
@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        email = request.form["email"]
        password = request.form["password"]

        if email in users and users[email]["password"] == password:
            session["user"] = email
            session["role"] = users[email]["role"]

            if session["role"] == "admin":
                return redirect(url_for("admin"))
            elif session["role"] == "user":
                return redirect(url_for("home"))

        return "❌ Geçersiz giriş!"

    return render_template("login.html")

# Kullanıcı ana sayfası (mesaj gönderme)
@app.route("/home")
def home():
    if "user" not in session or session["role"] != "user":
        return redirect(url_for("login"))
    return render_template("home.html")

# Admin sayfası (mesajları listele)
@app.route("/admin")
def admin():
    if "user" not in session or session["role"] != "admin":
        return redirect(url_for("login"))
    return render_template("admin.html", messages=messages)

# Mesaj gönderme API
@app.route("/send", methods=["POST"])
def send_message():
    if "user" not in session:
        return jsonify({"success": False, "error": "Giriş yapmalısın!"}), 401

    data = request.get_json()
    email = data.get("email")
    message = data.get("message")
    delivery_date = data.get("delivery_date")

    new_message = {
        "user": session["user"],
        "email": email,
        "message": message,
        "delivery_date": delivery_date
    }
    messages.append(new_message)

    print(f"✅ Mesaj kaydedildi: {new_message}")
    return jsonify({"success": True, "message": "Mesaj kaydedildi!"})

# Logout
@app.route("/logout")
def logout():
    session.clear()
    return redirect(url_for("index"))

# ---------------------------------------

if __name__ == "__main__":
    app.run(debug=True)
