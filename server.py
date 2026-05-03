from flask import Flask, request, jsonify
from flask_cors import CORS
from flask_sqlalchemy import SQLAlchemy
import os
from datetime import datetime

app = Flask(__name__)
CORS(app)

# Подключаемся к PostgreSQL (база данных не пропадает при перезапуске)
# Render сам подставит DATABASE_URL из переменных окружения
database_url = os.environ.get('DATABASE_URL')
if database_url and database_url.startswith('postgres://'):
    database_url = database_url.replace('postgres://', 'postgresql://', 1)

app.config['SQLALCHEMY_DATABASE_URI'] = database_url or 'sqlite:///DB_forum.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)

# --- МОДЕЛИ БАЗЫ ДАННЫХ ---
class User_and_password(db.Model):
    __tablename__ = 'User_and_password'
    id = db.Column(db.Integer, primary_key=True)
    user_name = db.Column(db.String(100), nullable=False)
    password = db.Column(db.String(100), nullable=False)

class User_and_massage(db.Model):
    __tablename__ = 'User_and_massage'
    id = db.Column(db.Integer, primary_key=True)
    user_name = db.Column(db.String(100), nullable=False)
    massage = db.Column(db.Text, nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

# Создаём таблицы при первом запуске
with app.app_context():
    db.create_all()
    print("Таблицы проверены/созданы в PostgreSQL")

# --- HTML СТРАНИЦЫ ---
@app.route('/')
def index():
    with open('index.html', 'r', encoding='utf-8') as f:
        return f.read()

@app.route('/login')
def login_page():
    with open('login.html', 'r', encoding='utf-8') as f:
        return f.read()

@app.route('/register')
def register_page():
    with open('register.html', 'r', encoding='utf-8') as f:
        return f.read()

@app.route('/wall')
def wall_page():
    with open('wall.html', 'r', encoding='utf-8') as f:
        return f.read()

# --- API МАРШРУТЫ ---
@app.route('/api/register', methods=['POST'])
def register():
    data = request.json
    username = data.get('username')
    password = data.get('password')
    
    # Проверяем, не занят ли ник
    existing_user = User_and_password.query.filter_by(user_name=username).first()
    if existing_user:
        return jsonify({"error": "Имя уже занято"}), 400
    
    # Добавляем пользователя
    new_user = User_and_password(user_name=username, password=password)
    db.session.add(new_user)
    db.session.commit()
    
    return jsonify({"message": "Регистрация успешна!"}), 201

@app.route('/api/login', methods=['POST'])
def login():
    data = request.json
    username = data.get('username')
    password = data.get('password')
    
    user = User_and_password.query.filter_by(user_name=username, password=password).first()
    
    if user:
        return jsonify({"user_id": user.id, "username": username})
    else:
        return jsonify({"error": "Неверное имя или пароль"}), 401

@app.route('/api/posts', methods=['GET'])
def get_posts():
    posts = User_and_massage.query.order_by(User_and_massage.id.desc()).all()
    
    result = []
    for p in posts:
        result.append({"id": p.id, "username": p.user_name, "text": p.massage})
    return jsonify(result)

@app.route('/api/posts', methods=['POST'])
def add_post():
    data = request.json
    username = data.get('username')
    text = data.get('text')
    
    new_post = User_and_massage(user_name=username, massage=text)
    db.session.add(new_post)
    db.session.commit()
    
    return jsonify({"message": "Пост добавлен!"}), 201

if __name__ == '__main__':
    app.run(port=5000)