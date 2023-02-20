from flask import Flask, request
from flask_socketio import SocketIO, emit
from flask_cors import CORS

app = Flask(__name__)
app.config["SECRET_KEY"] = "secret!"
CORS(app, resources={r"/*":{"origins":"*"}})
socketio = SocketIO(app, cors_allowed_origins="*")
users = []

@app.route("/")
def hello():
    return "Hello World"

@socketio.on("connect")
def connected():
    print(request.sid)
    print("Connected")
    emit("connect", {"data":f"id: {request.sid} is connected"})

@socketio.on("requestJoin")
def requestJoin(json):
    username = json["user"]
    users.append(username)
    for u in users:
        print(u)
    if len(users) == 2:
        emit("informBeginning", {"users": [{"user": username} for username in users]}, broadcast=True)

@socketio.on("changeTurn")
def changeTurn(json):
    print(json)
    nextWord = json["nextWord"]
    username = json["user"]
    emit("changeTurn", {"nextWord": nextWord, "user": username}, broadcast=True)

@socketio.on("disconnect")
def disconnected():
    """event listener when client disconnects to the server"""
    print("user disconnected")
    users.clear()
    emit("disconnect",f"user {request.sid} disconnected",broadcast=True)

if __name__ == "__main__":
    socketio.run(app, debug=True, port=5001)
