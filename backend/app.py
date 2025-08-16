from flask import Flask, request, jsonify, render_template, redirect, url_for, session
from flask_sqlalchemy import SQLAlchemy
from flask_mail import Mail
from werkzeug.security import generate_password_hash, check_password_hash
from datetime import datetime
import os

app = Flask(__name__)
app.secret_key = "supersecretkey"

# --- Database Ayarları ---
app.config['SQLALCHEMY_DATABASE_URI'] = os.environ.get("DATABASE_URL").replace("postgres://", "postgresql://")
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)

# --- Mail Ayarları (ileride kullanılacak) ---
app.config['MAIL_SERVER'] = 'smtp.example.com'
app.config['MAIL_PORT'] = 587
app.config['MAIL_USERNAME'] = 'your-email@example.com'
app.config['MAIL_PASSWORD'] = 'your-password'
app.config['MAIL_USE_TLS'] = True
app.config['MAIL_USE_SSL'] = False
mail = Mail(app)

# --- MODELLER ---
class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password = db.Column(db.String(200), nullable=False)
    is_admin = db.Column(db.Boolean, default=False)

class Message(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(120), nullable=False)
    message = db.Column(db.Text, nullable=False)
    delivery_date = db.Column(db.DateTime, nullable=False)

# --- ROUTELAR ---
@app.route('/')
def index():
    if "user_id" in session:
        user = User.query.get(session["user_id"])
        if user and user.is_admin:
            return redirect(url_for("admin_panel"))
        return redirect(url_for("home"))
    return render_template("index.html")

@app.route('/register', methods=["GET", "POST"])
def register():
    if request.method == "POST":
        email = request.form["email"]
        password = generate_password_hash(request.form["password"])
        if User.query.filter_by(email=email).first():
            return "Bu e-posta ile zaten kayıtlı bir kullanıcı var!"
        user = User(email=email, password=password, is_admin=(email == "admin@test.com"))
        db.session.add(user)
        db.session.commit()
        return redirect(url_for("login"))
    return render_template("register.html")

@app.route('/login', methods=["GET", "POST"])
def login():
    if request.method == "POST":
        email = request.form["email"]
        password = request.form["password"]
        user = User.query.filter_by(email=email).first()
        if user and check_password_hash(user.password, password):
            session["user_id"] = user.id
            if user.is_admin:
                return redirect(url_for("admin_panel"))
            return redirect(url_for("home"))
        return "Hatalı giriş!"
    return render_template("login.html")

@app.route('/logout')
def logout():
    session.clear()
    return redirect(url_for("index"))

@app.route('/home')
def home():
    if "user_id" not in session:
        return redirect(url_for("login"))
    return render_template("home.html")

@app.route('/send', methods=["POST"])
def send_message():
    if "user_id" not in session:
        return jsonify({"error": "Yetkisiz erişim"}), 403

    data = request.json
    email = data.get('email')
    message = data.get('message')
    delivery_date = datetime.strptime(data.get('delivery_date'), "%Y-%m-%d")

    new_message = Message(email=email, message=message, delivery_date=delivery_date)
    db.session.add(new_message)
    db.session.commit()

    return jsonify({"status": "success", "message": "Mesaj kaydedildi!"})

@app.route('/admin')
def admin_panel():
    if "user_id" not in session:
        return redirect(url_for("login"))
    user = User.query.get(session["user_id"])
    if not user.is_admin:
        return "Erişim reddedildi!"
    messages = Message.query.all()
    return render_template("admin.html", messages=messages)

# --- ANA ÇALIŞTIRMA ---
if __name__ == '__main__':
    with app.app_context():
        db.create_all()  # ⬅️ Tablolar deploy sırasında otomatik oluşacak
    app.run(host="0.0.0.0", port=5000)
