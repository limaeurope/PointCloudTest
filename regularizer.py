import csv
import math
from matplotlib import pyplot as plt
from sympy import geometry as g

from Classes.S_Point import S_Point
from Classes.S_Line import S_Line, S_CompositeLine


class S_ClosedPolyLine:
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
                _cLine = S_CompositeLine(seg, index=self.maxIndex)
                self.compositeLines.append(_cLine)
                self.maxIndex += 1
            pPrev = p
        if pPrev != p_list[0]:
            _line = S_CompositeLine(S_Line(pPrev, p_list[0]), index=self.maxIndex)
            self.compositeLines.append(_line)
            self.maxIndex += 1

    @property
    def polygon(self):
        _l = [cl.p1 for cl in self.compositeLines if cl.toBeUsed]
        _l.append([cl.p2 for cl in self.compositeLines if cl.toBeUsed][-1])
        _p = g.Polygon(*_l)
        return _p

    def toPlot(self):
        """For pyplot plotting"""
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
        _compositeLines = list(filter(lambda cl: cl.toBeUsed, self.compositeLines))
        _unusedLines = filter(lambda cl: not cl.toBeUsed, self.compositeLines)

        _prevCL = _compositeLines[-1]

        for _CL in _compositeLines:
            if not _CL.isNextTo(_prevCL):
                p = _CL.toLine().intersection(_prevCL.toLine())[0]
                _prevCL.p2 = S_Point(p.x, p.y)
                _CL.p1 = S_Point(p.x, p.y)
                if _CL.getLength() == 0:
                    _CL.toBeUsed = False
                else:
                    _prevCL = _CL
            else:
                _prevCL = _CL

        lines_ = [*_compositeLines, *_unusedLines]
        self.compositeLines = lines_

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
        S_Line.setAngularEPS(0.1)
        _pl = S_ClosedPolyLine(_pointList)
        print(1)
        _pl.autoPurge()

        _p = _pl.toPlot()
        plt.axis('equal')
        plt.plot(*_p)
        plt.show()

if __name__ == "__main__":
    readCSV("Data/Table.csv")

