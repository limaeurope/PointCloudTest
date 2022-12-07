from Classes.S_Point import *
import math
import uuid


class S_Line:
    EPS = 0.1
    EPS_ANG = 0.01

    def __init__(self, p_p1: S_Point, p_p2: S_Point, ):
        _list = [(p_p1.x, p_p1.y), (p_p2.x, p_p2.y), ]
        self.guid = uuid.uuid4()
        self.l1 = None
        self.l2 = None
        self._p1 = p_p1
        self._p2 = p_p2

    def __str__(self):
        return f"S_Line {self._p1} - {self._p2}"

    @classmethod
    def setEPS(cls, p_eps):
        cls.EPS = p_eps

    @classmethod
    def setAngularEPS(cls, p_eps):
        cls.EPS_ANG = p_eps

    @property
    def p1(self):
        return self._p1

    @p1.setter
    def p1(self, p_p1):
        self._p1 = p_p1

    @property
    def p2(self):
        return self._p2

    @p2.setter
    def p2(self, p_p2):
        self._p2 = p_p2

    def connect(self, p_line):
        if self._p1 == p_line.p1:
            self.l1 = p_line
            p_line.l1 = self
        if self._p1 == p_line.p2:
            self.l1 = p_line
            p_line.l2 = self

        if self._p2 == p_line.p1:
            self.l2 = p_line
            p_line.l1 = self
        if self._p2 == p_line.p2:
            self.l2 = p_line
            p_line.l2 = self

    def _dx(self)->float:
        return self._p2.x - self._p1.x

    def _dy(self)->float:
        return self._p2.y - self._p1.y

    def toList(self):
        return [self._p1.x, self._p2.x], [self._p1.y, self._p2.y]

    def getLength(self)->float:
        return math.sqrt((self._dx()) ** 2 + (self._dy()) ** 2)

    def distToPoint(self, p_point:S_Point) -> float:
        return (math.fabs((self._dx()) * (self._p1.y-p_point.y) - (self._dy()) * (self._p1.x-p_point.x)))  / self.getLength()

    def distToOrigo(self):
        return self.distToPoint(S_Point(0,0))

    def slope(self)->float:
        #FIXME to use sympy slope
        if math.fabs(self._dx()) > 0:
            return math.atan(self._dy() / self._dx())
        else:
            return math.pi/2

    def lengthen(self, p_dist, begin=True, end=True, isProportion=False):
        if not isProportion:
            ratio = p_dist / self.getLength()
        else:
            ratio = p_dist
        _dX = self._p2.x - self._p1.x
        _dY = self._p2.y - self._p1.y
        _p1 = self._p1
        _p2 = self._p2
        if begin:
            _p1x = self._p2.x - (1 + ratio) * _dX
            _p1y = self._p2.y - (1 + ratio) * _dY
            _p1 = S_Point(_p1x, _p1y)
        if end:
            _p2x = self._p1.x + (1 + ratio) * _dX
            _p2y = self._p1.y + (1 + ratio) * _dY
            _p2 = S_Point(_p2x, _p2y)
        self._p1 = _p1
        self._p2 = _p2

    def __eq__(self, other):
        EPS = S_Line.EPS
        EPS_ANG = S_Line.EPS_ANG
        _d1 = self.distToPoint(S_Point(0, 0))
        _d2 = other.distToPoint(S_Point(0, 0))
        _s1 = self.slope()
        _s2 = other.slope()
        if _s1 > math.pi/2 - EPS and _s2 < -math.pi/2 + EPS:
            _s2 += math.pi
        if _s1 < -math.pi/2 + EPS and _s2 > math.pi/2 - EPS:
            _s1 += math.pi

        return _d1 - EPS < _d2 < _d1 + EPS \
        and _s1 - EPS_ANG < _s2 < _s1 + EPS_ANG

    def getSimilarLines(self, p_list:list, p_aEps, p_dEps)->list:
        return [l for l in p_list if l == self]

    def __hash__(self):
        return self.guid.int



