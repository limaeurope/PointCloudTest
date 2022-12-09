from Classes.S_Line import S_Line
from sympy import geometry as g


class S_CompositeLine(S_Line):
    def __init__(self, *args, index = 0):
        if len(args) == 1:
            super().__init__(args[0].p1, args[0].p2)
            if isinstance(args[0], S_Line):
                self.lineList = [args[0]]
                self._p1 = args[0].p1
                self._p2 = args[0].p2
        if len(args) == 2:
            super().__init__(args[0], args[1])
            self.lineList = [S_Line(args[0], args[1])]
            self._p1 = args[0]
            self._p2 = args[1]
        self.index = index
        self.toBeUsed = True
        self.added = False
        self.segment = g.Segment2D(self.p1, self.p2)
        self.temporary = False
        self.previousSegment = None
        self.nextSegment = None

    def __repr__(self):
        return f"CL {'O' if self.toBeUsed else 'X'}:({float(self.p1.x)},{float(self.p1.y)})->({float(self.p2.x)},{float(self.p2.y)})"

    def __lt__(self, other):
        if self.index == other.index:
            return other.temporary
        return self.index < other.index

    def __gt__(self, other):
        if self.index == other.index:
            return self.temporary
        return self.index > other.index

    @property
    def p1(self):
        return self._p1

    @p1.setter
    def p1(self, p_p1):
        self._p1 = p_p1
        self.segment = g.Segment2D(self._p1, self._p2)
        if self.previousSegment:
            self.previousSegment._p2 = self._p1

    @property
    def p2(self):
        return self._p2

    @p2.setter
    def p2(self, p_p2):
        self._p2 = p_p2
        self.segment = g.Segment2D(self._p1, self._p2)
        if self.nextSegment:
            self.nextSegment._p1 = self._p2

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

    def addDetached(self, other:S_Line):
        #FIXME a better algorithm
        if not self.segment.contains(other.p1):
            #On the same side of p1:
            if (other.p1.x - self.p1.x) * (self.p2.x - self.p1.x) > 0:
                self.p2 = other.p1
            else:
                self.p1 = other.p1
        if not self.segment.contains(other.p2):
            # On the same side of p2:
            if (other.p2.x - self.p1.x) * (self.p2.x - self.p1.x) > 0:
                self.p2 = other.p2
            else:
                self.p1 = other.p2

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

