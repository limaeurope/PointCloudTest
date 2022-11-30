import csv
import math
from shapely import geometry as g
from matplotlib import pyplot as plt
import uuid
import pprint


# class Tangent(float):
#     EPS = 0.1
#
#     # def __eq__(self, other):
#         # return


class Point(g.Point):
    EPS = 0.001
    def __init__(self, p_x, p_y):
        _x = float(p_x)
        _y = float(p_y)
        super().__init__(_x, _y)

    def __str__(self):
        return f"Point({self.x}, {self.y})"

    def __eq__(self, other):
        EPS = Point.EPS
        return self.x - EPS < other.x < self.x + EPS and self.y - EPS < other.y < self.y + EPS


class Line(g.LineString):
    EPS = 0.1

    @classmethod
    def setEPS(cls, p_eps):
        cls.EPS = p_eps

    def __init__(self, p_p1:Point, p_p2:Point, ):
        self.p1 = p_p1
        self.p2 = p_p2
        _list = [(p_p1.x, p_p1.y), (p_p2.x, p_p2.y), ]
        super().__init__(_list)
        self.guid = uuid.uuid4()
        self.l1 = None
        self.l2 = None

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
    def __init__(self, p_seg:Line):
        super().__init__(p_seg.p1, p_seg.p2)
        self.lineList = [p_seg]
        self.p1 = p_seg.p1
        self.p2 = p_seg.p2

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


class ClosedPolyLine(g.LinearRing):
    def __init__(self, p_list:list[Point]):
        super(ClosedPolyLine, self).__init__([(p.x, p.y) for p in p_list])
        self.compositeLines = []
        pPrev = p_list[0]
        for p in p_list[1:]:
            seg = Line(pPrev, p)

            if len(self.compositeLines) and self.compositeLines[-1] == seg:
                self.compositeLines[-1].add(seg)
            else:
                self.compositeLines.append(CompositeLine(seg))
            pPrev = p

    def toPlot(self):
        pL = []
        cols = "rgbcymk"
        i = 0
        for cl in self.compositeLines:
            pL.append([cl.p1.x, cl.p2.x, ])
            pL.append([cl.p1.y, cl.p2.y, ])
            pL.append(cols[i%len(cols)])
            i += 1

        return pL


class Arc:
    pass


def getSimilarItems(p_item, p_fromItems: set = None):
    result = set()
    rest = set()

    if not p_fromItems:
        if p_item.l1 and p_item == p_item.l1:
            result.add(p_item)
        if p_item.l2 and p_item == p_item.l2:
            result.add(p_item)
    else:
        for i in p_fromItems:
            if p_item == i:
                result.add(i)
            else:
                rest.add(i)

    _result = set()
    for i in result:
        _r = getSimilarItems(i, rest)
        _result |= _r
        rest -= _r

    result |= _result
    result |= {p_item}
    rest -= _result

    return result

def getClusters(p_listOfItems, p_listOfClusters):
    if not p_listOfItems:
        return

    result = getSimilarItems(p_listOfItems[0])
    rest = set(p_listOfItems) - result
    p_listOfClusters.append(result)

    getClusters(list(rest), p_listOfClusters)

def readCSV(p_fileName):
    with open(p_fileName, "r") as csvFile:
        lines = []

        _prevLine = None

        # for row in csv.reader(csvFile):
        #     _l = Line(Point((float)(row[0]), (float)(row[1])), Point((float)(row[2]), (float)(row[3])))
        #     if _prevLine:
        #         _prevLine.connect(_l)
        #     lines.append(_l)
        #     _prevLine = _l

        Line.setEPS(0.3)

        _pointList = []
        for row in csv.reader(csvFile):
            _pointList.append(Point(row[0], row[1]))

        _pl = ClosedPolyLine(_pointList)
        print(_pl.bounds)

        _p = _pl.toPlot()
        plt.axis('equal')
        plt.plot(*_p)

        # listOfClusters = []
        # getClusters(lines, listOfClusters)
        #
        # print(len(listOfClusters))
        #
        # listOfClusters  = filter(lambda l: len(l) > 1, listOfClusters)

        # for c in listOfClusters:
        #     _pl1 = []
        #     _pl2 = []
        #
        #     i = 0
        #
        #     for l in c:
        #         _pl1.append(l.distToPoint(Point(0,0)))
        #         _pl2.append(l.slope())
        #         plt.plot(_pl1, _pl2, cols[i % len(cols)] + "." )
        #         i+=1
        plt.show()

if __name__ == "__main__":
    readCSV("Data/Table.csv")

