import csv
import os.path
import pickle
import sys

import jsonpickle
import json
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


def f1(p_sPath):
    with open(f"Dumps\\{p_sPath}.json", "r") as j:
        _dict = json.load(j)

        S_Line.setEPS(_dict['xEPS'])
        S_Line.setAngularEPS(_dict['aEPS'])

    pointList = []

    for coordPair in _dict['points']:
        _point = S_Point(coordPair[0], coordPair[1])
        pointList.append(_point)
    closedPolyLine = S_ClosedPolyLine(pointList)

    with open(f"Dumps\\{p_sPath}_f1.json", "w") as j:
        j.write(closedPolyLine.toJSON())

def f2(p_sPath):
    """Second step:
    Remove short edges by reconnecting the long ones
    """
    with open(f"Dumps\\{p_sPath}.json", "r") as j:
        _dict = json.load(j)

    areaDiff = _dict['aDiff']

    _lPoints = [S_Point(p[0], p[1]) for p in _dict["resultPoints"]]

    _closedPolyLine = S_ClosedPolyLine(_lPoints)

    _closedPolyLine.autoPurge(areaDiff)

    with open(f"Dumps\\{p_sPath}_f2.json", "w") as j:
        j.write(_closedPolyLine.toJSON())


def pyPlot(p_sFilePath, p_tag="", *args):
    COLORS = "gbcmkr"

    with open(p_sFilePath, "r") as j:
        _pointList = json.load(j)[p_tag]

    plt.axis('equal')
    v1, v2 = [*[p[0] for p in _pointList], _pointList[0][0]], [*[p[1] for p in _pointList], _pointList[0][1]]
    plt.plot(v1, v2, "r")
    if len(args):
        for f, t, c in zip(args[::2], args[1::2], COLORS):
            with open(f, "r") as j:
                _pointList = json.load(j)[t]

            v1, v2 = [*[p[0] for p in _pointList], _pointList[0][0]], [*[p[1] for p in _pointList], _pointList[0][1]]
            plt.plot(v1, v2, c)
    plt.show()


if __name__ == "__main__":
    # f1("1")
    f2("1")
    # pyPlot("Dumps\\1_f1.json", "points", "Dumps\\1_f2.json", "points")

    _i = 0
    _l = []

    while os.path.exists(f"Dumps\\{_i}_.json"):
        _l += [f"Dumps\\{_i}_.json", "points"]
        _i += 1

    print(*_l)
    pyPlot(*_l)


