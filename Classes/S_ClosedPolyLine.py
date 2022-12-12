from Classes.S_CompositeLine import S_CompositeLine
from Classes.S_Line import S_Line
from sympy import geometry as g
from Classes.S_Point import S_Point
import math
import json


class S_ClosedPolyLine:
    def __init__(self, p_list):
        localizedPList = self.pointsToLocal(p_list)
        self.compositeLines = []
        pPrev = localizedPList[0]
        self.maxIndex = 0
        prevSeg = None

        #FIXME not elegant
        for p in localizedPList[1:]:
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
        if pPrev != localizedPList[0]:
            _cline = S_CompositeLine(S_Line(pPrev, localizedPList[0]), index=self.maxIndex)
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

    def toDict(self):
        """As a server response in JSON"""
        result = []
        for p in self.polygon.vertices:
            result.append([float(p.x), float(p.y)])
        return result

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

    @staticmethod
    def getBBCentroid(p_pointList):
        xMax = max(map(lambda p:p.x, p_pointList))
        xMin = min(map(lambda p:p.x, p_pointList))
        yMax = max(map(lambda p:p.y, p_pointList))
        yMin = min(map(lambda p:p.y, p_pointList))
        return S_Point((xMin + xMax) / 2, (yMin + yMax) / 2)

    def pointsToLocal(self, p_pointList):
        pCen = self.getBBCentroid(p_pointList)

        return list(map(lambda p:p-pCen, p_pointList))

    def toJSON(self):
        result = {'points': []}
        for point in self.polygon.vertices:
            result['points'].append([point.x, point.y])

        return json.dumps(result)