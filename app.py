from flask import Flask, request, redirect, url_for, session, render_template_string
from flask_sqlalchemy import SQLAlchemy
from flask_bcrypt import Bcrypt

app = Flask(__name__)
app.secret_key = "super_secret_key"
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///users.db'

db = SQLAlchemy(app)
bcrypt = Bcrypt(app)

# 📂 Модель пользователя
class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    login = db.Column(db.String(150), unique=True, nullable=False)
    password = db.Column(db.String(150), nullable=False)
    nickname = db.Column(db.String(150))
    sub = db.Column(db.String(50))
    mem = db.Column(db.String(50))
    ident = db.Column(db.String(50))

# 📌 создаём таблицу и тестового аккаунта
@app.before_first_request
def create_tables():
    db.create_all()
    if not User.query.filter_by(login="user").first():
        hashed_pw = bcrypt.generate_password_hash("1234").decode("utf-8")
        db.session.add(User(
            login="user",
            password=hashed_pw,
            nickname="axmetalls",
            sub="02-06-2025",
            mem="3772Mb",
            ident="202"
        ))
        db.session.commit()

# ================= HTML ====================

login_html = """
<!DOCTYPE html>
<html lang="ru">
<head>
<meta charset="UTF-8">
<title>Вход</title>
<style>
    body { background:#121212; color:#fff; font-family:Arial; text-align:center; }
    input, button { width:250px; padding:10px; margin:8px; border-radius:5px; border:none; }
    button { background:#6A5ACD; color:white; cursor:pointer; }
</style>
</head>
<body>
    <h2>Добро пожаловать!</h2>
    <form method="post">
        <input name="login" placeholder="Введите логин"><br>
        <input name="password" type="password" placeholder="Введите пароль"><br>
        <button type="submit">Авторизоваться →</button>
    </form>
    {% if error %}<p style="color:red">{{ error }}</p>{% endif %}
</body>
</html>
"""

loading_html = """
<!DOCTYPE html>
<html lang="ru">
<head>
<meta charset="UTF-8">
<title>Загрузка...</title>
<style>
    body { background:#121212; color:white; font-family:Arial; text-align:center; }
    .dots span { font-size:30px; animation: blink 1s infinite; }
    .dots span:nth-child(2){animation-delay:.2s;}
    .dots span:nth-child(3){animation-delay:.4s;}
    @keyframes blink { 0% {opacity:.2;} 50% {opacity:1;} 100% {opacity:.2;} }
</style>
<meta http-equiv="refresh" content="2;url=/profile">
</head>
<body>
    <h2>Загрузка вашего профиля...</h2>
    <div class="dots">
        <span>●</span><span>●</span><span>●</span>
    </div>
</body>
</html>
"""

profile_html = """
<!DOCTYPE html>
<html lang="ru">
<head>
<meta charset="UTF-8">
<title>Профиль</title>
<style>
    body { background:#121212; color:#fff; font-family:Arial; text-align:center; }
    .box { margin:50px auto; width:400px; padding:20px; background:#1e1e1e; border-radius:10px; }
    button { background:#6A5ACD; padding:10px; color:white; border:none; border-radius:5px; cursor:pointer; }
</style>
</head>
<body>
<div class="box">
    <h2>👤 Профиль</h2>
    <p><b>Никнейм:</b> {{nickname}}</p>
    <p><b>Подписка:</b> {{sub}}</p>
    <p><b>Память:</b> {{mem}}</p>
    <p><b>ID:</b> {{ident}}</p>
    <a href="/logout"><button>Выйти</button></a>
</div>
</body>
</html>
"""

# =============== РОУТЫ =================

@app.route("/", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        login = request.form["login"]
        password = request.form["password"]
        user = User.query.filter_by(login=login).first()

        if user and bcrypt.check_password_hash(user.password, password):
            session["user"] = user.login
            return render_template_string(loading_html)
        else:
            return render_template_string(login_html, error="❌ Неверный логин или пароль")
    return render_template_string(login_html)

@app.route("/profile")
def profile():
    if "user" not in session:
        return redirect(url_for("login"))
    user = User.query.filter_by(login=session["user"]).first()
    return render_template_string(profile_html,
                                  nickname=user.nickname,
                                  sub=user.sub,
                                  mem=user.mem,
                                  ident=user.ident)

@app.route("/logout")
def logout():
    session.pop("user", None)
    return redirect(url_for("login"))

# ========================================

if __name__ == "__main__":
    app.run(debug=True)
