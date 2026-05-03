from flask import Flask, request, jsonify
from flask_cors import CORS
import sqlite3

app = Flask(__name__)
CORS(app)

def get_db():
    conn = sqlite3.connect("DB_forum.db")
    return conn

# Функция для создания таблиц (если их нет)
def create_tables():
    conn = get_db()
    cur = conn.cursor()
    
    # Таблица пользователей
    cur.execute("""CREATE TABLE IF NOT EXISTS User_and_password (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        user_name TEXT,
        password TEXT
    )""")
    
    # Таблица сообщений
    cur.execute("""CREATE TABLE IF NOT EXISTS User_and_massage (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        user_name TEXT,
        massage TEXT
    )""")
    
    conn.commit()
    conn.close()
    print("Таблицы проверены/созданы")

# Вызываем создание таблиц при запуске
create_tables()

@app.route('/api/register', methods=['POST'])
def register():
    data = request.json
    username = data.get('username')
    password = data.get('password')
    
    conn = get_db()
    cur = conn.cursor()
    cur.execute("SELECT * FROM User_and_password WHERE user_name = ?", (username,))
    if cur.fetchone():
        conn.close()
        return jsonify({"error": "Имя уже занято"}), 400
    
    cur.execute("INSERT INTO User_and_password(user_name, password) VALUES (?,?)", (username, password))
    conn.commit()
    conn.close()
    return jsonify({"message": "Регистрация успешна!"}), 201

@app.route('/api/login', methods=['POST'])
def login():
    data = request.json
    username = data.get('username')
    password = data.get('password')
    
    conn = get_db()
    cur = conn.cursor()
    cur.execute("SELECT id FROM User_and_password WHERE user_name = ? AND password = ?", (username, password))
    user = cur.fetchone()
    conn.close()
    
    if user:
        return jsonify({"user_id": user[0], "username": username})
    else:
        return jsonify({"error": "Неверное имя или пароль"}), 401

@app.route('/api/posts', methods=['GET'])
def get_posts():
    conn = get_db()
    cur = conn.cursor()
    cur.execute("SELECT id, user_name, massage FROM User_and_massage ORDER BY id DESC")
    posts = cur.fetchall()
    conn.close()
    
    result = []
    for p in posts:
        result.append({"id": p[0], "username": p[1], "text": p[2]})
    return jsonify(result)

@app.route('/api/posts', methods=['POST'])
def add_post():
    data = request.json
    username = data.get('username')
    text = data.get('text')
    
    conn = get_db()
    cur = conn.cursor()
    cur.execute("INSERT INTO User_and_massage(user_name, massage) VALUES (?,?)", (username, text))
    conn.commit()
    conn.close()
    return jsonify({"message": "Пост добавлен!"}), 201

if __name__ == '__main__':
    app.run(port=5000)