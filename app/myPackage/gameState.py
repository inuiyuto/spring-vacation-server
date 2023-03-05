from enum import Enum, auto

class GameState(Enum):
    JOINED = auto()
    READY = auto()
    START = auto()
    PLAYING = auto()
    FINISH = auto()
