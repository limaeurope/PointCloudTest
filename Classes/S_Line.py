from Classes.S_Point import *
import math
import uuid
from sympy import geometry as g


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

    def slope(self)->float:
        if math.fabs(self._dx()) > 0:
            return math.atan(self._dy() / self._dx())
        else:
            return math.pi/2

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


class S_CompositeLine(S_Line):
    def __init__(self, *args, index = 0):
        super().__init__(args[0].p1, args[0].p2)
        if len(args) == 1:
            if isinstance(args[0], S_Line):
                self.lineList = [args[0]]
                self._p1 = args[0].p1
                self._p2 = args[0].p2
        if len(args) == 2:
            self.lineList = [S_Line(args[0], args[1])]
            self._p1 = args[0]
            self._p2 = args[1]
        self.index = index
        self.toBeUsed = True
        self.added = False
        self.segment = g.Segment2D(self.p1, self.p2)

    def __repr__(self):
        return f"CL {'O' if self.toBeUsed else 'X'}:({float(self.p1.x)},{float(self.p1.y)})->({float(self.p2.x)},{float(self.p2.y)})"

    @property
    def p1(self):
        return self._p1

    @p1.setter
    def p1(self, p_p1):
        self._p1 = p_p1
        self.segment = g.Segment2D(self._p1, self._p2)

    @property
    def p2(self):
        return self._p2

    @p2.setter
    def p2(self, p_p2):
        self._p2 = p_p2
        self.segment = g.Segment2D(self._p1, self._p2)

    def add(self, other:S_Line):
        if self.p1 == other.p1:
            self.p1 = other.p2
            self.lineList = [S_Line(other.p2, other.p1)] + self.lineList
        elif self.p1 == other.p2:
            self.p1 = other.p1
            self.lineList = [S_Line(other.p1, other.p2)] + self.lineList
        elif self.p2 == other.p1:
            self.p2 = other.p2
            self.lineList = self.lineList + [S_Line(other.p1, other.p2)]
        elif self.p2 == other.p2:
            self.p2 = other.p1
            self.lineList = self.lineList + [S_Line(other.p2, other.p1)]

    def getPoint(self):
        return self.segment.length

    def isNextTo(self, p_other):
        return self.p1 == p_other.p2

    def toLine(self):
        _r = g.Line(self.p1, self.p2)
        return _r

    @property
    def order(self):
        return self.segment.length

