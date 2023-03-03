from flask import Flask, request
from flask_socketio import SocketIO, emit
from flask_cors import CORS

class Position:

    def __init__(self):
        self.x = 0
        self.y = 0
        self.z = 0

    def __init__(self, x, y, z):
        self.x = x
        self.y = y
        self.z = z

    def __add__(self, other):
        # 同じクラスかどうかの判定
        if type(other) == Position: 
            self.x += other.x
            self.y += other.y
            self.z += other.z
            return self
        raise TypeError()

    def set(self, a, b):
        self.a = a
        self.b = b

app = Flask(__name__)
app.config["SECRET_KEY"] = "secret!"
CORS(app, resources={r"/*":{"origins":"*"}})
socketio = SocketIO(app, cors_allowed_origins="*")
users = []
skipUserIndices = []
positions = []
OKCount = 0
informCount = 0
nextUserIndex = 0

@app.route("/")
def hello():
    return "Hello World"

@socketio.on("connect")
def connected():
    print(request.sid)
    print("Connected")

@socketio.on("disconnect")
def disconnected(json):
    #TODO: ぶち切ってくる場合usernameがないのでrequest.sidで名前とのmapを用意しておいて、適宜削除する必要あり
    global OKCount
    """event listener when client disconnects to the server"""
    print("user disconnected")
    username = json["user"]
    users.remove(username)
    emit("s2cInformUsers", {"users": [{"user": username} for username in users]}, broadcast=True)

@socketio.on("c2sRequestJoin")
def c2sRequestJoin(json):
    print(json)
    username = json["user"]
    users.append(username)
    emit("s2cInformUsers", {"users": [{"user": username} for username in users]}, broadcast=True)


@socketio.on("c2sOK")
def c2sok(json):
    print(json)
    global OKCount, nextUserIndex
    OKCount += 1
    if OKCount == len(users) :
        firstUser = users[nextUserIndex]
        emit("s2cStart", {"users": [{"user": username} for username in users], "firstUser": firstUser}, broadcast=True)

@socketio.on("c2sPull")
def c2spull(json):
    print(json)
    username = json["user"]
    directionX = json["pullInfo"]["directionX"]
    directionY = json["pullInfo"]["directionY"]
    rotation = json["pullInfo"]["rotation"]
    emit("s2cSharePull", {"user": username ,"PullInfo": {"directionX": directionX , "directionY": directionY , "rotation": rotation}}, broadcast=True)

@socketio.on("c2sInformPositions")
def c2sinformpositions(json):
    print(json)
    global informCount
    informCount += 1
    for position in json["positions"]:
        username = json["user"]
        userPosition = Position(position["positionX"], position["positionY"], position["positionZ"])
        if username in positions.keys():
            positions[username]["userPosition"] = positions[username]["userPosition"] + userPosition
            positions[username]["count"] += 1
        else:
            positions.append({username: {"userPosition" : userPosition, "count" : 1}})
    if informCount == len(users):
        aliveUsers = []
        for pi in range(len(positions)):

            username, position = positions[pi].items()
            #positon = 1, 0, 1
            if position["count"] >= len(users) / 2:
                position["userPosition"].x = position["userPosition"].x / position["count"]
                position["userPosition"].y = position["userPosition"].y / position["count"]
                position["userPosition"].z = position["userPosition"].z / position["count"]
                aliveUsers.append({ "user": username, "positionX": position["userPosition"].x, "positionY": position["userPosition"].y, "positionZ": position["userPosition"].z})
            else:
                skipUserIndices.append(users.index(username))
        nextUserIndex = (nextUserIndex + 1) % len(users)
        while nextUserIndex in skipUserIndices:
            nextUserIndex = (nextUserIndex + 1) % len(users)
        nextUser = users[nextUserIndex] 
        emit("s2cAveragePositions", {"positions": aliveUsers, "nextUser": nextUser}, broadcast=True)

if __name__ == "__main__":
    socketio.run(app, debug=True, port=5001)
