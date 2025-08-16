from flask import Flask, request, jsonify, session, render_template, redirect, url_for
from flask_cors import CORS
from flask_sqlalchemy import SQLAlchemy
import os
from datetime import datetime

app = Flask(__name__)
app.secret_key = "supersecretkey"
CORS(app)

# -------------------
# Database config
# -------------------
app.config['SQLALCHEMY_DATABASE_URI'] = os.getenv("DATABASE_URL").replace("postgres://", "postgresql://")
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)

# -------------------
# Models
# -------------------
class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password = db.Column(db.String(120), nullable=False)
    is_admin = db.Column(db.Boolean, default=False)


class Message(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(120), nullable=False)
    message = db.Column(db.Text, nullable=False)
    delivery_date = db.Column(db.DateTime, nullable=False)


# -------------------
# Routes
# -------------------
@app.route('/')
def index():
    if "user_id" in session:
        user = User.query.get(session["user_id"])
        if user.is_admin:
            return redirect(url_for("admin_panel"))
        return redirect(url_for("home"))
    return render_template("index.html")


@app.route('/register', methods=["GET", "POST"])
def register():
    if request.method == "POST":
        email = request.form["email"]
        password = request.form["password"]

        # Check if user exists
        existing = User.query.filter_by(email=email).first()
        if existing:
            return "Bu e-posta zaten kayıtlı!"

        user = User(email=email, password=password, is_admin=(email == "admin@test.com"))
        db.session.add(user)
        db.session.commit()
        session["user_id"] = user.id
        return redirect(url_for("home"))

    return render_template("register.html")


@app.route('/login', methods=["GET", "POST"])
def login():
    if request.method == "POST":
        email = request.form["email"]
        password = request.form["password"]

        user = User.query.filter_by(email=email, password=password).first()
        if user:
            session["user_id"] = user.id
            if user.is_admin:
                return redirect(url_for("admin_panel"))
            return redirect(url_for("home"))
        return "Geçersiz giriş!"

    return render_template("login.html")


@app.route('/logout')
def logout():
    session.pop("user_id", None)
    return redirect(url_for("index"))


@app.route('/home')
def home():
    if "user_id" not in session:
        return redirect(url_for("login"))
    return render_template("home.html")


@app.route('/send_message', methods=["POST"])
def send_message():
    if "user_id" not in session:
        return jsonify({"error": "Giriş yapmalısınız!"}), 403

    data = request.json
    msg = Message(
        email=data["email"],
        message=data["message"],
        delivery_date=datetime.strptime(data["delivery_date"], "%Y-%m-%d %H:%M")
    )
    db.session.add(msg)
    db.session.commit()
    return jsonify({"status": "success"})


@app.route('/admin')
def admin_panel():
    if "user_id" not in session:
        return redirect(url_for("login"))

    user = User.query.get(session["user_id"])
    if not user.is_admin:
        return "Yetkiniz yok!"

    messages = Message.query.all()
    return render_template("admin.html", messages=messages)


if __name__ == "__main__":
    with app.app_context():
        db.create_all()  # ilk çalıştırmada tabloyu oluşturur
    app.run(host="0.0.0.0", port=5000)
