from Classes.S_Point import *
import math
import uuid
from sympy import geometry as g


class S_Line(g.Segment2D):
    EPS = 0.1

    def __new__(cls, *args):
        _r = super(S_Line, cls).__new__(cls, *args)
        return _r

    def __init__(self, p_p1: S_Point, p_p2: S_Point, ):
        _list = [(p_p1.x, p_p1.y), (p_p2.x, p_p2.y), ]
        self.guid = uuid.uuid4()
        self.l1 = None
        self.l2 = None

    def __str__(self):
        return f"S_Line {self.p1} - {self.p2}"

    @classmethod
    def setEPS(cls, p_eps):
        cls.EPS = p_eps

    def connect(self, p_line):
        if self.p1 == p_line.p1:
            self.l1 = p_line
            p_line.l1 = self
        if self.p1 == p_line.p2:
            self.l1 = p_line
            p_line.l2 = self

        if self.p2 == p_line.p1:
            self.l2 = p_line
            p_line.l1 = self
        if self.p2 == p_line.p2:
            self.l2 = p_line
            p_line.l2 = self

    def _dx(self)->float:
        return self.p2.x - self.p1.x

    def _dy(self)->float:
        return self.p2.y - self.p1.y

    def toList(self):
        return [self.p1.x, self.p2.x], [self.p1.y, self.p2.y]

    def getLength(self)->float:
        return math.sqrt((self._dx()) ** 2 + (self._dy()) ** 2)

    def distToPoint(self, p_point:S_Point) -> float:
        return (math.fabs((self._dx()) * (self.p1.y-p_point.y) - (self._dy()) * (self.p1.x-p_point.x)))  / self.getLength()

    def slope(self)->float:
        if math.fabs(self._dx()) > 0:
            return math.atan(self._dy() / self._dx())
        else:
            return math.pi/2

    def __eq__(self, other):
        EPS = S_Line.EPS
        _d1 = self.distToPoint(S_Point(0, 0))
        _d2 = other.distToPoint(S_Point(0, 0))
        _s1 = self.slope()
        _s2 = other.slope()
        if _s1 > math.pi/2 - EPS and _s2 < -math.pi/2 + EPS:
            _s2 += math.pi
        if _s1 < -math.pi/2 + EPS and _s2 > math.pi/2 - EPS:
            _s1 += math.pi

        return _d1 - EPS < _d2 < _d1 + EPS \
        and _s1 - EPS < _s2 < _s1 + EPS

    def getSimilarLines(self, p_list:list, p_aEps, p_dEps)->list:
        return [l for l in p_list if l == self]

    def __hash__(self):
        return self.guid.int