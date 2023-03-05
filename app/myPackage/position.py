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
