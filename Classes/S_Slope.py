import math


class S_Slope(float):
    EPS = 0.1

    def __hash__(self):
        _r = self // S_Slope.EPS

    def __eq__(self, other):
        EPS = S_Slope.EPS
        _s = float(self)

        if self > math.pi/2 - EPS and other < -math.pi/2 + EPS:
            other += math.pi
        if self < -math.pi/2 + EPS and other > math.pi/2 - EPS:
            _s += math.pi

        return _s - EPS < other < _s + EPS

    def isParallel(self, p_other):
        return self == p_other

    def isAngleAt(self, p_other, p_angleInRads, p_checkBothSides = False):
        EPS = S_Slope.EPS
        _s = float(self)

        if p_other - _s <= -math.pi/2:
            p_other += math.pi/2

        result = p_angleInRads - EPS <= p_other - _s <= p_angleInRads + EPS

        if p_checkBothSides:
            if _s - p_other <= -math.pi / 2:
                _s += math.pi / 2

            result |= p_angleInRads - EPS <= _s - p_other <= p_angleInRads + EPS

        return result

    def isPerpendicular(self, p_other):
        return self.isAngleAt(p_other, math.pi/2, p_checkBothSides=True)

