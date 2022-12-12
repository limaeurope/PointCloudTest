import csv
import pickle
import sys

from matplotlib import pyplot as plt

from Classes.S_Point import S_Point
from Classes.S_Line import S_Line
from Classes.S_LineContainer import S_LineContainer
from Classes.S_ClosedPolyLine import S_ClosedPolyLine


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

        plt.axis('equal')
        # plt.plot([p.x for p in _pointList], [p.y for p in _pointList], ["rgbcmk"[i % len("rgbcmk")] for i in range(len(_pointList))])
        plt.plot(_pl.toPlot())
        plt.show()

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

