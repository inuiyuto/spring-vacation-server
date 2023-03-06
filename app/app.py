from flask import Flask, request
from flask_socketio import SocketIO, emit
from flask_cors import CORS
from app.myPackage import Position, GameState, DisconnectManager

app = Flask(__name__)
app.config["SECRET_KEY"] = "secret!"
CORS(app, resources={r"/*":{"origins":"*"}})
socketio = SocketIO(app, cors_allowed_origins="*")
disconnectManager = DisconnectManager()
users = []
skipUserIndices = []
disconnectedUserIndices = []
aliveUserPositions = {}
OKCount = 0
informCount = 0
nextUserIndex = 0

@app.route("/")
def hello():
    return "Hello World"

@socketio.on("connect")
def connected():
    print("Connected")

@socketio.on("disconnect")
def disconnected():
    global OKCount, nextUserIndex


    # TODO: KeyError
    print(disconnectManager.userFromSocketIDs)
    username = disconnectManager.userFromSocketIDs[request.sid]


    userGameState = disconnectManager.userGameStates[username]
    print(f"disconnected: username {username} , gameState: {userGameState}")
    if userGameState == GameState.JOINED:
        users.remove(username)
        if OKCount == len(users) and OKCount != 0:
            OKCount = 0
            disconnectManager.changeAllStates(users, GameState.START)
            firstUser = users[nextUserIndex]
            disconnectManager.setPuller(firstUser)
            emit("s2cStart", {"users": [username for username in users], "firstUser": firstUser}, broadcast=True)
        else:
            emit("s2cInformUsers", {"users": [{"user": username} for username in users]}, broadcast=True)
    elif userGameState == GameState.READY:
        users.remove(username)
        OKCount -= 1
        if OKCount == len(users) and OKCount != 0:
            OKCount = 0
            disconnectManager.changeAllStates(users, GameState.START)
            firstUser = users[nextUserIndex]
            disconnectManager.setPuller(firstUser)
            emit("s2cStart", {"users": [username for username in users], "firstUser": firstUser}, broadcast=True)
        else:
            emit("s2cInformUsers", {"users": [{"user": username} for username in users]}, broadcast=True)
    elif userGameState == GameState.START:
        skipUserIndices.append(users.index(username))
        disconnectedUserIndices.append(users.index(username))

        if len(users) - len(skipUserIndices) <= 1:
            result = makeResult()
            emit("s2cInformResult", {"result" : result}, broadcast=True)
            ## TODO: clearGame()

        firstUser = disconnectManager.puller
        if username == disconnectManager.puller:
            nextUserIndex = (nextUserIndex + 1) % len(users)
            while nextUserIndex in skipUserIndices:
                nextUserIndex = (nextUserIndex + 1) % len(users)
            firstUser = users[nextUserIndex]
            disconnectManager.setPuller(firstUser)
        emit("s2cStart", {"users": [username for username in users], "firstUser": firstUser}, broadcast=True)
    elif userGameState == GameState.PLAYING:
        skipUserIndices.append(users.index(username))
        disconnectedUserIndices.append(users.index(username))

        if len(users) - len(skipUserIndices) <= 1:
            result = makeResult()
            emit("s2cInformResult", {"result" : result}, broadcast=True)
            ## TODO: clearGame()

        nextUser = disconnectManager.puller
        averagedUserPositions = disconnectManager.userPositions
        if username == disconnectManager.puller:
            nextUserIndex = (nextUserIndex + 1) % len(users)
            while nextUserIndex in skipUserIndices:
                nextUserIndex = (nextUserIndex + 1) % len(users)
            nextUser = users[nextUserIndex]
            disconnectManager.setPuller(nextUser)
        emit("s2cAveragePositions", {"positions": [averagedUserPosition for averagedUserPosition in averagedUserPositions if averagedUserPosition["user"] != username], "nextUser": nextUser}, broadcast=True)


@socketio.on("c2sRequestJoin")
def c2sRequestJoin(json):
    print(json)
    username = json["user"]
    users.append(username)
    disconnectManager.append(username, request.sid)
    print(users)
    emit("s2cInformUsers", {"users": [username for username in users]}, broadcast=True)


@socketio.on("c2sOK")
def c2sOK(json):
    print(json)
    username = json["user"]
    global OKCount, nextUserIndex
    OKCount += 1
    disconnectManager.changeState(username, GameState.READY)
    if OKCount == len(users):
        OKCount = 0
        disconnectManager.changeAllStates(users, GameState.START)
        firstUser = users[nextUserIndex]
        disconnectManager.setPuller(firstUser)
        emit("s2cStart", {"users": [username for username in users], "firstUser": firstUser}, broadcast=True)

@socketio.on("c2sPull")
def c2sPull(json):
    print(json)
    username = json["user"]
    directionX = json["pullInfo"]["directionX"]
    directionY = json["pullInfo"]["directionY"]
    rotation = json["pullInfo"]["rotation"]
    emit("s2cSharePull", {"user": username ,"pullInfo": {"directionX": directionX , "directionY": directionY , "rotation": rotation}}, broadcast=True)

@socketio.on("c2sInformPositions")
def c2sInformPositions(json):
    print(json)
    global informCount, nextUserIndex

    informCount += 1

    for position in json["positions"]:
        username = position["user"]
        userPosition = Position(position["positionX"], position["positionY"], position["positionZ"])
        if username in aliveUserPositions.keys():
            prevUserPosition = aliveUserPositions[username]["position"]
            count = aliveUserPositions[username]["count"]
            aliveUserPositions[username] = { "user": username, "position": prevUserPosition + userPosition, "count" : count + 1}
        else:
            aliveUserPositions[username] = { "user": username, "position" : userPosition , "count" : 1}

    if informCount == len(users) - len(disconnectedUserIndices):
        informCount = 0
        averagedUserPositions = []
        for aliveUserPosition in aliveUserPositions.values():
            if aliveUserPosition["count"] >= len(users) / 2:
                username = aliveUserPosition["user"]
                x = aliveUserPosition["position"].x / aliveUserPosition["count"]
                y = aliveUserPosition["position"].y / aliveUserPosition["count"]
                z = aliveUserPosition["position"].z / aliveUserPosition["count"]
                averagedUserPositions.append({"user" : username, "positionX" : x, "positionY": y, "positionZ" : z})
        
        aliveUsers = []
        for averagedUserPosition in averagedUserPositions:
            username = averagedUserPosition["user"]
            aliveUsers.append(username)
        for username in users:
            if username not in aliveUsers:
                if users.index(username) not in skipUserIndices:
                    skipUserIndices.append(users.index(username))

        if len(aliveUsers) <= 1:
            result = makeResult()
            emit("s2cInformResult", {"result" : result}, broadcast=True)
            ## TODO: clearGame()
        
        nextUserIndex = (nextUserIndex + 1) % len(users)
        while nextUserIndex in skipUserIndices:
            nextUserIndex = (nextUserIndex + 1) % len(users)
        nextUser = users[nextUserIndex]
        disconnectManager.setPuller(nextUser)
        disconnectManager.setUserPositions(averagedUserPositions)
        disconnectManager.changeAllStates(users, GameState.PLAYING)
        emit("s2cAveragePositions", {"positions": averagedUserPositions, "nextUser": nextUser}, broadcast=True)
        aliveUserPositions.clear()


def makeResult():
    ranking = []
    disconnectedUsers = []
    for i in skipUserIndices:
        if i in disconnectedUserIndices:
            disconnectedUsers.append(users[i])
        else:
            ranking.append(users[i])
    for user in users:
        if users.index(user) not in skipUserIndices:
            ranking.append(user)
    ranking = disconnectedUsers + ranking
    ranking.reverse()
    result = [{"user": ranking[i], "rank": i + 1} for i in range(len(ranking))]
    return result

        
if __name__ == "__main__":
    socketio.run(app, debug=True, port=5001)