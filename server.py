from flask import Flask, render_template
from flask_socketio import SocketIO, send

app = Flask(__name__)
socketio = SocketIO(app)

@app.route("/")
def index():
    print("Rendering index.html")  # debug print
    return render_template("index.html")

@socketio.on("message")
def handle_message(msg):
    print("Message received:", msg)
    send(msg, broadcast=True)

@socketio.on("message")
def handle_message(msg):
    print("Message received:", msg)
    send(msg, broadcast=True)

if __name__ == "__main__":
    socketio.run(app, host="0.0.0.0", port=5001, debug=True)

