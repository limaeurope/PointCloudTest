import csv
import math
from matplotlib import pyplot as plt
from sympy import geometry as g

from Classes.S_Point import S_Point
from Classes.S_Line import S_Line


class S_CompositeLine(S_Line):
    def __new__(cls, *args):
        if isinstance(args[0], S_Line):
            _r = super(S_Line, cls).__new__(cls, args[0].p1, args[0].p2)
        else:
                _r = super(S_Line, cls).__new__(cls, *args)
        return _r

    def __init__(self, *args, p_index = 0):
        super(g.Segment, self).__init__()
        if len(args) == 1:
            if isinstance(args[0], S_Line):
                self.lineList = [args[0]]
                self.p1 = args[0].p1
                self.p2 = args[0].p2
        if len(args) == 2:
            self.lineList = [S_Line(args[0], args[1])]
            self.p1 = args[0]
            self.p2 = args[1]
        self.index = p_index
        self.toBeUsed = True
        self.added = False

    def __repr__(self):
        return f"CL {'O' if self.toBeUsed else 'X'}:({float(self.p1.x)},{float(self.p1.y)})->({float(self.p2.x)},{float(self.p2.y)})"

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
        return self.length

    def isNextTo(self, p_other):
        return self.p1 == p_other.p2

    def toLine(self):
        _r = g.Line(self.p1, self.p2)
        return _r

    @property
    def order(self):
        return self.length


class S_ClosedPolyLine():
    def __init__(self, p_list):
        self.compositeLines = []
        pPrev = p_list[0]
        self.maxIndex = 0

        #FIXME not elegant
        for p in p_list[1:]:
            seg = S_Line(pPrev, p)

            if len(self.compositeLines) and self.compositeLines[-1] == seg:
                self.compositeLines[-1].add(seg)
            else:
                _cLine = S_CompositeLine(seg)
                self.compositeLines.append(_cLine)
                self.maxIndex += 1
            pPrev = p
        if pPrev != p_list[0]:
            _line = S_CompositeLine(S_Line(pPrev, p_list[0]))
            self.compositeLines.append(_line)

    @property
    def polygon(self):
        _l = [cl.p1 for cl in self.compositeLines if cl.toBeUsed]
        _l.append([cl.p2 for cl in self.compositeLines if cl.toBeUsed][-1])
        _p = g.Polygon(*_l)
        return _p

    def toPlot(self):
        '''For pyplot plotting'''
        pL = []
        cols = "rgbcymk"
        i = 0
        for l, m in zip(self.polygon.vertices, [*self.polygon.vertices[1:], self.polygon.vertices[0], ]):
            pL.append([l.x, m.x])
            pL.append([l.y, m.y])
            pL.append(cols[i % len(cols)])
            i += 1
        return pL

    def reconnectAllEdges(self):
        _prevCL = None

        for _CL in [*self.compositeLines, *self.compositeLines, ]:
            if not _CL.toBeUsed:
                continue
            elif _prevCL and not _CL.isNextTo(_prevCL):
                p = _CL.toLine().intersection(_prevCL.toLine())[0]
                _prevCL.p2 = S_Point(p.x, p.y)
                _CL.p1 = S_Point(p.x, p.y)
            _prevCL = _CL

    def removeOneSegmentAndReconnect(self):
        _compositeLinesOrdered = sorted(self.compositeLines, key=lambda i: i.order)
        _i = len(list(filter(lambda i: not i.toBeUsed, _compositeLinesOrdered)))
        _compositeLinesOrdered[_i].toBeUsed = False
        _compositeLinesOrdered = sorted(self.compositeLines, key=lambda i: i.index)

        self.compositeLines = _compositeLinesOrdered
        self.reconnectAllEdges()

    def autoPurge(self, p_aDiff = 0.01):
        aOriginal = math.fabs(self.polygon.area)

        print(len(self.polygon.vertices))

        while (_r := math.fabs((math.fabs(self.polygon.area)  - aOriginal)) / aOriginal) < p_aDiff and len(self.polygon.vertices) > 3:
            print(len(self.polygon.vertices))
            self.removeOneSegmentAndReconnect()

        print(float(self.polygon.area))

def readCSV(p_fileName):
    with open(p_fileName, "r") as csvFile:
        _prevLine = None

        _pointList = []

        for row in csv.reader(csvFile):
            _point = S_Point(row[0], row[1])
            _pointList.append(_point)

        S_Line.setEPS(1)
        _pl = S_ClosedPolyLine(_pointList)
        print(1)
        _pl.autoPurge()

        _p = _pl.toPlot()
        plt.axis('equal')
        plt.plot(*_p)
        plt.show()

if __name__ == "__main__":
    readCSV("Data/Table.csv")

