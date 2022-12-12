from Classes.S_CompositeLine import S_CompositeLine
from Classes.S_Point import S_Point
from Classes.S_Line import S_Line
import math


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