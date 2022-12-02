import csv
import math
# from shapely import geometry as g
from matplotlib import pyplot as plt
import uuid
from sympy import geometry as g


class Point(g.Point2D):
    EPS = 0.001
    def __new__(cls, p_x, p_y):
        _x = float(p_x)
        _y = float(p_y)
        result = super().__new__(cls, _x, _y)
        return result

    def __str__(self):
        return f"Point({self.x}, {self.y})"

    def __eq__(self, other):
        EPS = Point.EPS
        return self.x - EPS < other.x < self.x + EPS and self.y - EPS < other.y < self.y + EPS


class Slope(float):
    EPS = 0.1

    def __eq__(self, other):
        EPS = Slope.EPS
        _s = float(self)

        if self > math.pi/2 - EPS and other < -math.pi/2 + EPS:
            other += math.pi
        if self < -math.pi/2 + EPS and other > math.pi/2 - EPS:
            _s += math.pi

        return _s - EPS < other < _s + EPS

    def isParallel(self, p_other):
        return self == p_other

    def isAngleAt(self, p_other, p_angle, p_checkBothSides = False):
        EPS = Slope.EPS
        _s = float(self)

        if p_other - _s <= -math.pi/2:
            p_other += math.pi/2

        result = p_angle -EPS <= p_other - _s <= p_angle + EPS

        if p_checkBothSides:
            if _s - p_other <= -math.pi / 2:
                _s += math.pi / 2

            result |= p_angle - EPS <= _s - p_other <= p_angle + EPS

        return result

    def isPerpendicular(self, p_other):
        return self.isAngleAt(p_other, p_checkBothSides=True)


class Line(g.Line):
    EPS = 0.1

    def __new__(cls, p_p1, p_p2):
        _r = super(g.Line, cls).__new__(cls, p_p1, p_p2)
        return _r

    def __init__(self, p_p1: Point, p_p2: Point, ):
        _list = [(p_p1.x, p_p1.y), (p_p2.x, p_p2.y), ]
        self.guid = uuid.uuid4()
        self.l1 = None
        self.l2 = None

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

    def __str__(self):
        return f"Line {self.p1} - {self.p2}"

    def __repr__(self):
        return f"Line {self.p1} - {self.p2}"

    def _dx(self)->float:
        return self.p2.x - self.p1.x

    def _dy(self)->float:
        return self.p2.y - self.p1.y

    def toList(self):
        return [self.p1.x, self.p2.x], [self.p1.y, self.p2.y]

    def getLength(self)->float:
        return math.sqrt((self._dx()) ** 2 + (self._dy()) ** 2)

    def distToPoint(self, p_point:Point) -> float:
        return (math.fabs((self._dx()) * (self.p1.y-p_point.y) - (self._dy()) * (self.p1.x-p_point.x)))  / self.getLength()

    def slope(self)->float:
        if math.fabs(self._dx()) > 0:
            return math.atan(self._dy() / self._dx())
        else:
            return math.pi/2

    def __eq__(self, other):
        EPS = Line.EPS
        _d1 = self.distToPoint(Point(0,0))
        _d2 = other.distToPoint(Point(0,0))
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


class CompositeLine(Line):
    def __new__(cls, p_seg:Line):
        _r = super(g.Line, cls).__new__(cls, p_seg.p1, p_seg.p2)
        return _r

    def __init__(self, p_seg:Line, p_index = 0):
        self.lineList = [p_seg]
        self.p1 = p_seg.p1
        self.p2 = p_seg.p2
        self.index = p_index
        self.toBeUsed = True

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

    def add(self, other:Line):
        if self.p1 == other.p1:
            self.p1 = other.p2
            self.lineList = [Line(other.p2, other.p1)] + self.lineList
        elif self.p1 == other.p2:
            self.p1 = other.p1
            self.lineList = [Line(other.p1, other.p2)] + self.lineList
        elif self.p2 == other.p1:
            self.p2 = other.p2
            self.lineList = self.lineList + [Line(other.p1, other.p2)]
        elif self.p2 == other.p2:
            self.p2 = other.p1
            self.lineList = self.lineList + [Line(other.p2, other.p1)]

    def getPoint(self):
        return self.length

    def isNextTo(self, p_other):
        return self.p2 == p_other.p1


class ClosedPolyLine(g.Polygon):
    def __new__(cls, p_list):
        result = super().__new__(cls, *p_list)
        return result

    def __init__(self, p_list):
        self.compositeLines = []
        pPrev = p_list[0]
        self.maxIndex = 0

        for p in p_list[1:]:
            seg = Line(pPrev, p)

            if len(self.compositeLines) and self.compositeLines[-1] == seg:
                self.compositeLines[-1].add(seg)
            else:
                _cLine = CompositeLine(seg)
                self.compositeLines.append(_cLine)
                self.maxIndex += 1
            pPrev = p

    def toPlot(self):
        '''For pyplot plotting'''
        pL = []
        cols = "rgbcymk"
        i = 0
        for cl in self.compositeLines:
            pL.append([cl.p1.x, cl.p2.x, ])
            pL.append([cl.p1.y, cl.p2.y, ])
            pL.append(cols[i%len(cols)])
            i += 1
        return pL

    # def autoPurge(self):
    #     _compositeLinesOrdered = sorted(self.compositeLines, key=lambda i: i.length)
    #     _compositeLinesOrdered[-1].toBeUsed = False
    #     _compositeLinesOrdered = sorted(self.compositeLines, key=lambda i: i.index)
    #
    #     _prevCL = _compositeLinesOrdered[0]
    #     for _CL in _compositeLinesOrdered[1:]:
    #         if not _CL.toBeUsed:
    #             continue
    #
    #         if not _CL.isNextTo(_prevCL):
    #             _CL.intersect(_prevCL)
    #             _prevCL.intersect(_CL)
    #
    #         _prevCL = _CL


def readCSV(p_fileName):
    with open(p_fileName, "r") as csvFile:
        _prevLine = None

        Line.setEPS(1)

        _pointList = []

        for row in csv.reader(csvFile):

            _point = Point(row[0], row[1])
            _pointList.append(_point)

        _pl = ClosedPolyLine(_pointList)
        # _pl.autoPurge()

        _p = _pl.toPlot()
        plt.axis('equal')
        plt.plot(*_p)
        plt.show()

if __name__ == "__main__":
    readCSV("Data/Table.csv")

