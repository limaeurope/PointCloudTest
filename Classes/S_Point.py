# from sympy import geometry as g
from shapely import geometry as g


class S_Point(g.Point):
    EPS = 0.001
    def __init__(self, *args):
        if len(args) == 1:
            _x = float(args[0].x)
            _y = float(args[0].y)
        else:
        # if len(args) == 2:
            _x = float(args[0])
            _y = float(args[1])
        result = super().__init__(_x, _y)
        # return result

    def __str__(self):
        return f"S_Point({float(self.x)}, {float(self.y)})"

    def __repr__(self):
        return self.__str__()

    def __eq__(self, other):
        EPS = S_Point.EPS
        return  self.x - EPS < other.x < self.x + EPS \
            and self.y - EPS < other.y < self.y + EPS

    def __sub__(self, other):
        return S_Point(self.x - other.x, self.y - other.y)

