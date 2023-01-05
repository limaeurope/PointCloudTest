from Classes.S_CompositeLine import S_CompositeLine
from Classes.S_Line import S_Line
# from sympy import geometry as g
from shapely import geometry as g
# import sympy
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
        _l = [(_cl.p1.x, _cl.p1.y) for _cl in self.compositeLines if _cl.toBeUsed]
        _l.append([(_cl.p1.x, _cl.p1.y) for _cl in self.compositeLines if _cl.toBeUsed][-1])
        _p = g.Polygon(_l)
        return _p

    def toPlot(self):
        """For pyplot plotting"""
        pL = []
        cols = "rgbcmk"
        i = 0
        for l, m in zip(self.polygon.exterior.coords, [*self.polygon.exterior.coords[1:], self.polygon[0], ]):
            pL.append([l.x, m.x])
            pL.append([l.y, m.y])
            pL.append(cols[i % len(cols)])
            i += 1
        return pL

    def toDict(self):
        """As a server response in JSON"""
        result = []
        for p in self.polygon.exterior.coords:
            result.append([float(p[0] + self.pCen.x), float(p[1] + self.pCen.y)])
        return result

    def reconnectAllEdges(self):
        _compositeLines = list(filter(lambda _cl: _cl.toBeUsed and not _cl.added, self.compositeLines))
        _unusedLines = list(filter(lambda _cl: not _cl.toBeUsed and not _cl.added, self.compositeLines))

        _prevCL = _compositeLines[-1]

        for _CL in _compositeLines:
            if not _CL.isNextTo(_prevCL) and not _CL.added:
                try:
                    p = _CL.intersect(_prevCL)
                    if _prevCL.p2.distance(p) > _prevCL.p2.distance(_CL.p1) \
                    or _CL.p1.distance(p) > _CL.p1.distance(_prevCL.p2):
                        raise Exception
                    _prevCL.p2 = S_Point(p.x, p.y)
                    _CL.p1 = S_Point(p.x, p.y)
                    _CL.previousSegment = _prevCL
                    _prevCL.nextSegment = _CL
                    if _CL.getLength() == 0:
                        _CL.toBeUsed = False
                    else:
                        _prevCL = _CL
                except (IndexError, AttributeError, Exception):
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
        _i = 0
        _iPrev = len(self.polygon.exterior.coords)

        print(_iPrev)

        while (_r := math.fabs((math.fabs(self.polygon.area)  - aOriginal)) / aOriginal) < p_aDiff \
                and len(self.polygon.exterior.coords) > 3:
            try:
                print(len(self.polygon.exterior.coords))
                self.removeOneSegmentAndReconnect()
                _prevDiff = _r

                if False:
                    with open(f"Dumps\\{_i}_.json", "w") as j:
                        j.write(self.toJSON())
                        _i += 1

            except KeyboardInterrupt:
                break

        print(float(self.polygon.area))

    @staticmethod
    def getBB(p_pointList):
        xMax = max(map(lambda p:p.x, p_pointList))
        xMin = min(map(lambda p:p.x, p_pointList))
        yMax = max(map(lambda p:p.y, p_pointList))
        yMin = min(map(lambda p:p.y, p_pointList))

        return S_Point((xMin + xMax) / 2, (yMin + yMax) / 2), S_Point(xMin, yMin), S_Point(xMax, yMax)

    def pointsToLocal(self, p_pointList):
        self.pCen, self.pMin, self.pMax = self.getBB(p_pointList)

        return list(map(lambda p:p-self.pCen, p_pointList))

    def toJSON(self, p_indent=4, BBoxToOrigo=False):
        result = {'points': []}
        for point in self.polygon.exterior.coords:
            result['points'].append([float(point[0] + (self.pCen.x if BBoxToOrigo else 0)), float(point[1] + (self.pCen.y if BBoxToOrigo else 0))])

        return json.dumps(result, indent=p_indent)