from flask import Flask, request
from flask_socketio import SocketIO, emit
from flask_cors import CORS

app = Flask(__name__)
app.config["SECRET_KEY"] = "secret!"
CORS(app, resources={r"/*":{"origins":"*"}})
socketio = SocketIO(app, cors_allowed_origins="*")
users = []
OKusers = []
alive = 0
OKnum = 0
nextUsernum = 0
positionX = []
positionY = []
positionZ = []

@app.route("/")
def hello():
    return "Hello World"

@socketio.on("connect")
def connected():
    print(request.sid)
    print("Connected")
    emit("connect", {"data":f"id: {request.sid} is connected"})

@socketio.on("c2sRequestJoin")
def c2srequestjoin(json):
    username = json["username"]
    users.append(username)
    for u in users:
        print(u)
    emit("s2cInformUsers", {"users": [{"user": username} for username in users]}, broadcast=True)

@socketio.on("disconnect")
def disconnected(json):
    """event listener when client disconnects to the server"""
    print("user disconnected")
    username = json["username"]
    if username in OKusers :
        OKnum -= 1
        OKusers.remove(username)
    users.remove(username)
    emit("s2cInformUsers", {"users": [{"user": username} for username in users]}, broadcast=True)

@socketio.on("c2sOK")
def c2sok(json):
    username = json["username"]
    if not username in OKusers :
        OKusers.append(username)
        OKnum += 1
    if OKnum == len(users) :
        alive = OKnum
        firstUser = users[nextUsernum]
        nextUsernum += 1
        while True :
            if nextUsernum > len(users) :
                nextUsernum = 0
            elif users[nextUsernum] == "NoName":
                nextUsernum += 1
            else :
                break       
        emit("s2cStart", {"users": [{"user": username} for username in users], "firstUser": firstUser}, broadcast=True)

@socketio.on("c2sPull")
def c2spull(json):
    divnum = 0
    #書き方違う?
    username = json["username"]
    deltaX = json["pullInfo"]["deltaX"]
    deltaY = json["pullInfo"]["deltaY"]
    rotation = json["pullInfo"]["rotation"]
    emit("s2cSharePull", {"user": username ,"PullInfo": {"deltaX": deltaX , "deltaY": deltaY , "rotation": rotation}}, broadcast=True)

@socketio.on("c2sInformPositions")
def c2sinformpositions(json):
    positions = json["positions"]
    divnum += 1
    i = 0
    while True :
        i += 1
        #書き方違う?
        for position in positions :
            username = position["user"]
            l = users.index(username)
            positionX[l] = position["positionX"]
            positionY[l] = position["positionY"]
            positionZ[l] = position["positionZ"]
        if i == alive :
            break
    if divnum == len(users) :
        #平均をとる処理、死んだ処理、ゲーム終了の処理、次の人を決める処理
        emit("s2cAveragePositions", {"user": username ,"PullInfo": {"strength": strength , "angle": angle , "rotation": rotatinon}}, broadcast=True)


if __name__ == "__main__":
    socketio.run(app, debug=True, port=5001)
