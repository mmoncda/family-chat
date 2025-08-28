from flask import Flask, render_template, request, redirect, session
from flask_socketio import SocketIO, send
import sqlite3
import os

app = Flask(__name__)
app.secret_key = "supersecretfamilykey"
socketio = SocketIO(app, cors_allowed_origins="*", async_mode="eventlet")

DB_FILE = "chat.db"

# ---------- DATABASE ----------
def init_db():
    if not os.path.exists(DB_FILE):
        conn = sqlite3.connect(DB_FILE)
        c = conn.cursor()
        c.execute("CREATE TABLE messages (id INTEGER PRIMARY KEY AUTOINCREMENT, username TEXT, message TEXT)")
        c.execute("CREATE TABLE users (id INTEGER PRIMARY KEY AUTOINCREMENT, family_code TEXT)")
        # Insert default family code
        c.execute("INSERT INTO users (family_code) VALUES (?)", ("FAMILY123",))
        conn.commit()
        conn.close()

def save_message(username, msg):
    conn = sqlite3.connect(DB_FILE)
    c = conn.cursor()
    c.execute("INSERT INTO messages (username, message) VALUES (?, ?)", (username, msg))
    conn.commit()
    conn.close()

def get_all_messages():
    conn = sqlite3.connect(DB_FILE)
    c = conn.cursor()
    c.execute("SELECT username, message FROM messages ORDER BY id ASC")
    messages = c.fetchall()
    conn.close()
    return messages

def verify_family_code(code):
    conn = sqlite3.connect(DB_FILE)
    c = conn.cursor()
    c.execute("SELECT * FROM users WHERE family_code=?", (code,))
    res = c.fetchone()
    conn.close()
    return res is not None

# ---------- ROUTES ----------
@app.route("/", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        code = request.form.get("code")
        if verify_family_code(code):
            session["logged_in"] = True
            session["family_code"] = code
            return redirect("/chat")
        else:
            return render_template("login.html", error="Invalid family code")
    return render_template("login.html", error=None)

@app.route("/chat")
def chat():
    if not session.get("logged_in"):
        return redirect("/")
    messages = get_all_messages()
    return render_template("index.html", messages=messages)

# ---------- SOCKET.IO ----------
@socketio.on("message")
def handle_message(msg):
    username, message_text = msg.split(":", 1)
    save_message(username.strip(), message_text.strip())
    send(msg, broadcast=True)

# ---------- MAIN ----------
if __name__ == "__main__":
    init_db()
    socketio.run(app, host="0.0.0.0", port=5001, debug=True, allow_unsafe_werkzeug=True)

