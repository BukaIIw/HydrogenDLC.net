from flask import Flask, request, redirect, url_for, session, render_template_string
from flask_sqlalchemy import SQLAlchemy
from flask_bcrypt import Bcrypt

app = Flask(__name__)
app.secret_key = "супер_секретный_ключ"
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///users.db'

db = SQLAlchemy(app)
bcrypt = Bcrypt(app)

# 📂 Модель пользователей
class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    login = db.Column(db.String(150), unique=True, nullable=False)
    password = db.Column(db.String(150), nullable=False)

# ⚙️ Создаём БД и тестового юзера
@app.before_first_request
def create_tables():
    db.create_all()
    if not User.query.filter_by(login="user").first():
        hashed_pw = bcrypt.generate_password_hash("1234").decode("utf-8")
        db.session.add(User(login="user", password=hashed_pw))
        db.session.commit()

# HTML шаблоны как строки
login_html = """
<!DOCTYPE html>
<html lang="ru">
<head>
<meta charset="UTF-8">
<title>Вход</title>
<style>
    body { background:#121212; color:#fff; font-family:Arial; text-align:center; }
    input,button{width:250px;padding:10px;margin:5px;border-radius:5px;border:none;}
    button{background:#6A5ACD;color:white;cursor:pointer;}
</style>
</head>
<body>
    <h2>Добро пожаловать!</h2>
    <form method="post">
        <input name="login" placeholder="Логин"><br>
        <input name="password" type="password" placeholder="Пароль"><br>
        <button type="submit">Авторизоваться</button>
    </form>
    {% if error %}<p style="color:red">{{ error }}</p>{% endif %}
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
    .box { margin:50px auto;width:400px;padding:20px;background:#1e1e1e;border-radius:10px; }
    button{background:#6A5ACD;padding:10px;color:white;border:none;border-radius:5px;cursor:pointer;}
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

@app.route("/", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        login = request.form["login"]
        password = request.form["password"]
        user = User.query.filter_by(login=login).first()

        if user and bcrypt.check_password_hash(user.password, password):
            session["user"] = user.login
            return redirect(url_for("profile"))
        else:
            return render_template_string(login_html, error="❌ Неверный логин или пароль")

    return render_template_string(login_html)

@app.route("/profile")
def profile():
    if "user" not in session:
        return redirect(url_for("login"))
    return render_template_string(profile_html, nickname=session["user"], sub="02-06-2025", mem="3772Mb", ident="202")

@app.route("/logout")
def logout():
    session.pop("user", None)
    return redirect(url_for("login"))

if __name__ == "__main__":
    app.run(debug=True)
