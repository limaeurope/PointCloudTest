import csv
import math
from matplotlib import pyplot as plt
from sympy import geometry as g

from Classes.S_Point import S_Point
from Classes.S_Line import S_Line
from Classes.S_CompositeLine import S_CompositeLine


class S_LineContainer:
    EPS = 0.01
    EPS_ANG = 0.01

    def __init__(self):
        self.m_dict = {}

    def __setitem__(self, key, value):
        if key not in self.m_dict:
            self.m_dict[key] = [value]
        else:
            self.m_dict[key].append(value)

    def __str__(self):
        for i, v in self.m_dict.items():
            if len(v) > 2:
                print(i, v)

    def add(self, p:S_CompositeLine):
        _s = (p.slope() - S_LineContainer.EPS_ANG) // S_LineContainer.EPS_ANG
        _d = (p.distToOrigo() - S_LineContainer.EPS) // S_LineContainer.EPS
        self[(_s, _d)] = p

    def toPlot(self, p_moreThan = 1):
        plotList = []

        for k, v in self.m_dict.items():
            if len(list(filter(lambda i:i.toBeUsed, v))) > p_moreThan:
                seg = S_CompositeLine(v[0])
                for s in v[1:]:
                    seg.addDetached(s)
                seg.lengthen(0.1, isProportion=True)

                plotList += [[seg.p1.x, seg.p2.x, ], [seg.p1.y, seg.p2.y, ], 'y']
        return plotList


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

    def __getitem__(self, item):
        return self.compositeLines[item]

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
        _compositeLines = list(filter(lambda cl: cl.toBeUsed and not cl.added, self.compositeLines))
        _unusedLines = list(filter(lambda cl: not cl.toBeUsed and not cl.added, self.compositeLines))

        _prevCL = _compositeLines[-1]

        for _CL in _compositeLines:
            if not _CL.isNextTo(_prevCL) and not _CL.added:
                try:
                    p = _CL.toLine().intersection(_prevCL.toLine())[0]
                    _prevCL.p2 = S_Point(p.x, p.y)
                    _CL.p1 = S_Point(p.x, p.y)
                    if _CL.getLength() == 0:
                        _CL.toBeUsed = False
                    else:
                        _prevCL = _CL
                except IndexError:
                    cl = S_CompositeLine(_prevCL.p2, _CL.p1)
                    cl.added = True
                    cl.index = _prevCL.index
                    _unusedLines.append(cl)
                    _prevCL = _CL
            else:
                _prevCL = _CL

        lines_ = [*_compositeLines, *_unusedLines]
        self.compositeLines = sorted(lines_)

    def removeOneSegmentAndReconnect(self):
        _compositeLinesOrdered = filter(lambda cl:not cl.added, self.compositeLines)
        _compositeLinesOrdered = sorted(_compositeLinesOrdered, key=lambda i: i.order)
        _i = len(list(filter(lambda i: not i.toBeUsed, _compositeLinesOrdered)))
        _compositeLinesOrdered[_i].toBeUsed = False
        _compositeLinesOrdered = sorted(self.compositeLines, key=lambda i: i.index)

        self.compositeLines = _compositeLinesOrdered
        self.reconnectAllEdges()

    def autoPurge(self, p_aDiff = 0.01):
        aOriginal = math.fabs(self.polygon.area)

        print(len(self.polygon.vertices))

        _prevDiff = 0
        while (_r := math.fabs((math.fabs(self.polygon.area)  - aOriginal)) / aOriginal) < p_aDiff \
                and len(self.polygon.vertices) > 3:
            print(len(self.polygon.vertices))
            self.removeOneSegmentAndReconnect()
            _prevDiff = _r

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
        _pl.autoPurge(0.004)
        _p = _pl.toPlot()

        S_LineContainer.EPS = 1
        S_LineContainer.EPS_ANG = .3
        _lc = S_LineContainer()

        for l in _pl:
            _lc.add(l)

        _p2 = _lc.toPlot()

        plt.axis('equal')
        plt.plot(*(_p + _p2 ))
        plt.show()

if __name__ == "__main__":
    readCSV("Data/Table.csv")

