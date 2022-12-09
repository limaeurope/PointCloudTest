import csv
import math
import pickle

from matplotlib import pyplot as plt
from sympy import geometry as g

from Classes.S_Point import S_Point
from Classes.S_Line import S_Line
from Classes.S_CompositeLine import S_CompositeLine


class S_LineContainer:
    EPS = 0.01
    EPS_ANG = 0.01

    def __init__(self):
        self.m_dictByAngAndDist = {}
        self.m_dictByAng = {}
        self.m_dictByDist = {}

    def __str__(self):
        for i, v in self.m_dictByAngAndDist.items():
            if len(v) > 2:
                print(i, v)

    def collectByAngAndDist(self, p:S_CompositeLine):
        _s = (p.slope() - S_LineContainer.EPS_ANG/2) // S_LineContainer.EPS_ANG
        _d = (p.distToOrigo() - S_LineContainer.EPS/2) // S_LineContainer.EPS

        if (_s, _d) not in self.m_dictByAngAndDist:
            self.m_dictByAngAndDist[(_s, _d)] = [p]
        else:
            self.m_dictByAngAndDist[(_s, _d)].append(p)

    def collectByAng(self, p:S_CompositeLine):
        if p.toBeUsed:
            _s = (p.slope() - S_LineContainer.EPS_ANG/2) // S_LineContainer.EPS_ANG
            if _s not in self.m_dictByAng:
                self.m_dictByAng[_s] = [p]
            else:
                self.m_dictByAng[_s].append(p)

    def collectByDist(self, p:S_CompositeLine):
        _d = (p.distToOrigo() - S_LineContainer.EPS/2) // S_LineContainer.EPS
        if _d not in self.m_dictByAngAndDist:
            self.m_dictByDist[_d] = [p]
        else:
            self.m_dictByDist[_d].append(p)

    def toPlot(self, p_moreThan = 1):
        plotList = []

        for k, v in self.m_dictByAngAndDist.items():
            if len(list(filter(lambda i:i.toBeUsed, v))) > p_moreThan:
                seg = S_CompositeLine(v[0])
                for s in v[1:]:
                    seg.addDetached(s)
                seg.lengthen(0.1, isProportion=True)

                plotList += [[seg.p1.x, seg.p2.x, ], [seg.p1.y, seg.p2.y, ], 'y']
        return plotList

    def regularizeAllEdges(self, p_moreThan = 1):
        for k, v in self.m_dictByAngAndDist.items():
            if len(v) > p_moreThan:
                self.regularizeEdgeList(v)

    def regularizeEdgeList(self, p_edgeList, p_moreThan = 1):
        if len(list(filter(lambda i: i.toBeUsed, p_edgeList))) > p_moreThan:
            seg = S_CompositeLine(p_edgeList[0])
            for s in p_edgeList[1:]:
                seg.addDetached(s)

            for s in p_edgeList:
                s.projectToOtherLine(seg)
                s.previousSegment.p2 = s.p1
                s.nextSegment.p1 = s.p2

    def parallelizeEdgesList(self, p_list, p_moreThan = 1):
        if len(p_list) > p_moreThan:
            averageSlope = sum(map(lambda x:x.slope()*x.getLength(), p_list)) / sum(map(lambda x:x.getLength(), p_list))

            for l in p_list:
                m = l.getMidPoint()
                v = S_Line(m, S_Point(m.x + 1 * math.cos(averageSlope), m.y + 1 * math.sin(averageSlope)))
                l.projectToOtherLine(v)


class S_ClosedPolyLine:
    def __init__(self, p_list):
        self.compositeLines = []
        pPrev = p_list[0]
        self.maxIndex = 0
        prevSeg = None

        #FIXME not elegant
        for p in p_list[1:]:
            seg = S_Line(pPrev, p)

            if len(self.compositeLines) and self.compositeLines[-1] == seg:
                self.compositeLines[-1].add(seg)
            else:
                _cLine = S_CompositeLine(seg, index=self.maxIndex)
                _cLine.previousSegment = prevSeg
                if prevSeg:
                    prevSeg.nextSegment = _cLine
                self.compositeLines.append(_cLine)
                self.maxIndex += 1
                prevSeg = _cLine
            pPrev = p
        if pPrev != p_list[0]:
            _cline = S_CompositeLine(S_Line(pPrev, p_list[0]), index=self.maxIndex)
            self.compositeLines.append(_cline)
            self.maxIndex += 1
        self.compositeLines[0].previousSegment = self.compositeLines[-1]
        self.compositeLines[-1].nextSegment = self.compositeLines[0]

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
        cols = "rgbcmk"
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
                    _CL.previousSegment = _prevCL
                    _prevCL.nextSegment = _CL
                    if _CL.getLength() == 0:
                        _CL.toBeUsed = False
                    else:
                        _prevCL = _CL
                except IndexError:
                    cl = S_CompositeLine(_prevCL.p2, _CL.p1)
                    cl.added = True
                    cl.index = _prevCL.index
                    cl.previousSegment = _prevCL
                    _prevCL.nextSegment = cl
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

        _prevDiff = 0
        _iPrev = len(self.polygon.vertices)

        print(_iPrev)

        while (_r := math.fabs((math.fabs(self.polygon.area)  - aOriginal)) / aOriginal) < p_aDiff \
                and len(self.polygon.vertices) > 3:
            try:
                print(len(self.polygon.vertices))
                self.removeOneSegmentAndReconnect()
                _prevDiff = _r
                # if _iPrev == len(self.polygon.vertices):
                #     break
                _iPrev = len(self.polygon.vertices)
            except KeyboardInterrupt:
                break

        print(float(self.polygon.area))

    # def getPreviousEdge(self, p_edge):
    #     _compositeLinesOrdered = filter(lambda cl: cl.toBeUsed, self.compositeLines)
    #     _compositeLinesOrdered = sorted(_compositeLinesOrdered, key=lambda i: i.order, reverse=True)
    #     _i = _compositeLinesOrdered.index(p_edge)
    #     if _i == len(_compositeLinesOrdered) - 1:
    #         return _compositeLinesOrdered[0]
    #     else:
    #         return _compositeLinesOrdered[_i+1]

def readCSV(p_fileName):
    with open(p_fileName, "r") as csvFile:
        _pointList = []

        for row in csv.reader(csvFile):
            _point = S_Point(row[0], row[1])
            _pointList.append(_point)

        # plt.axis('equal')
        # plt.plot([p.x for p in _pointList], [p.y for p in _pointList])
        # plt.show()

        S_Line.setEPS(10)
        S_Line.setAngularEPS(0.5)
        _pl = S_ClosedPolyLine(_pointList)

        _jp = pickle.dumps(_pl)

        print(1)

        _pl.autoPurge(0.004)

        # pickle.dump(_pl, open("Data/pl.pickle", "wb"))
        #
        # _pl = pickle.load(open("Data/1.pickle", "rb"))

        S_LineContainer.EPS = .5
        S_LineContainer.EPS_ANG = .5
        _lc = S_LineContainer()

        # pickle.dump(_lc, open("Data/lc.pickle", "wb"))
        #
        # _lc = pickle.load(open("Data/lc.pickle", "rb"))

        # for l in _pl:
        #     _lc.collectByAngAndDist(l)

        # _lc.regularizeAllEdges()

        #----------------------------------------

        for l in _pl:
            _lc.collectByAng(l)

        for k, v in _lc.m_dictByAng.items():
            _lc.parallelizeEdgesList(v)

        #----------------------------------------

        _p = _pl.toPlot()
        _p2 = _lc.toPlot()

        plt.axis('equal')
        plt.plot(*(_p + _p2 ))
        plt.show()

if __name__ == "__main__":
    readCSV("Data/Table7.csv")

