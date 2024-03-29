from sympy import geometry as g


class S_Point(g.Point2D):
    EPS = 0.001
    def __new__(cls, p_x, p_y):
        _x = float(p_x)
        _y = float(p_y)
        result = super().__new__(cls, _x, _y)
        return result

    def __str__(self):
        return f"S_Point({float(self.x)}, {float(self.y)})"

    def __repr__(self):
        return self.__str__()

    def __eq__(self, other):
        EPS = S_Point.EPS
        return self.x - EPS < other.x < self.x + EPS and self.y - EPS < other.y < self.y + EPS

