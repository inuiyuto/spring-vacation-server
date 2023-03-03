from flask import Flask, request
from flask_socketio import SocketIO, emit
from flask_cors import CORS

app = Flask(__name__)
app.config["SECRET_KEY"] = "secret!"
CORS(app, resources={r"/*":{"origins":"*"}})
socketio = SocketIO(app, cors_allowed_origins="*")
users = []
OKusers = []
OKnum = 0
informNum = 0
nextUserNum = 0
positionX = []
positionY = []
positionZ = []
#TODO : declare global for global variable(primitive)(参照ならできる)

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
    global OKnum
    """event listener when client disconnects to the server"""
    print("user disconnected")
    username = json["user"]
    if username in OKusers :
        OKnum -= 1
        OKusers.remove(username)
    users.remove(username)
    emit("s2cInformUsers", {"users": [{"user": username} for username in users]}, broadcast=True)

@socketio.on("c2sRequestJoin")
def c2srequestjoin(json):
    print(json)
    username = json["user"]
    users.append(username)
    emit("s2cInformUsers", {"users": [{"user": username} for username in users]}, broadcast=True)


@socketio.on("c2sOK")
def c2sok(json):
    print(json)
    global OKnum, nextUserNum
    username = json["user"]
    if username not in OKusers :
        OKusers.append(username)
        OKnum += 1
    if OKnum == len(users) :
        firstUser = users[nextUserNum]
        nextUserNum += 1
        while True :
            if nextUserNum > len(users) :
                nextUserNum = 0
            #elif 次の人が死んでいた場合
                #nextUserNum += 1
            else :
                break
        emit("s2cStart", {"users": [{"user": username} for username in users], "firstUser": firstUser}, broadcast=True)

@socketio.on("c2sPull")
def c2spull(json):
    print(json)
    #書き方違う?
    username = json["user"]
    directionX = json["pullInfo"]["directionX"]
    directionY = json["pullInfo"]["directionY"]
    rotation = json["pullInfo"]["rotation"]
    emit("s2cSharePull", {"user": username ,"PullInfo": {"directionX": directionX , "directionY": directionY , "rotation": rotation}}, broadcast=True)

@socketio.on("c2sInformPositions")
def c2sinformpositions(json):
    print(json)
    #書き方違う?
    global informNum
    positions = json["positions"]
    informNum += 1
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
        if i == len(users) :
            break

    if informNum == len(users) :
        i = 0
        while True :
            positionX[i] = positionX[i] / len(users)
            positionY[i] = positionY[i] / len(users)
            positionZ[i] = positionZ[i] / len(users)
            i += 1
            if i == len(users) :
                break
        
        #死んだ処理、ゲーム終了と結果送信の処理

        #次の人を決める
        nextUser = users[nextUserNum] 
        nextUserNum += 1
        while True :
            if nextUserNum > len(users) :
                nextUserNum = 0
            #elif 次の人が死んでいた場合
                #nextUserNum += 1
            else :
                break
        #書き方違う?
        emit("s2cAveragePositions", {"positions": 
                                     [{"user": username for username in users}, {"positionX": positionX for positionX in positionX} , 
                                      {"potisionY": positionY for positionY in positionY} , {"positionZ": positionZ for positionZ in positionZ}],
                                        "nextUser": nextUser }, broadcast=True)


if __name__ == "__main__":
    socketio.run(app, debug=True, port=5001)
