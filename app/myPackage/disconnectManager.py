from gameState import GameState

class DisconnectManager:
    def __init__(self):
        self.userFromSocketIDs = {}
        self.userGameStates = {}
        self.userPositions = []
        self.puller = ""

    def append(self, username, socketID):
        self.userFromSocketIDs[socketID] = username
        self.userGameStates[username] = GameState.JOINED

    def changeState(self, username, state):
        self.userGameStates[username] = state

    def changeAllStates(self, users, state):
        for username in users:
            self.changeState(username, state)

    def setPuller(self, username):
        self.puller = username

    def setUserPositions(self, positions):
        self.userPositions = positions
