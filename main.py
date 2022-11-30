# This is a sample Python script.

# Press Shift+F10 to execute it or replace it with your code.
# Press Double Shift to search everywhere for classes, files, tool windows, actions, and settings.

import sys

class Point:
    xMin = sys.float_info.max
    xMax = sys.float_info.min
    yMin = sys.float_info.max
    yMax = sys.float_info.min
    zMin = sys.float_info.max
    zMax = sys.float_info.min

    EPS = 0.1

    def __init__(self, i_row:str):
        lValues = i_row.split(" ")

        self.x = (float)(lValues[0])
        self.y = (float)(lValues[1])
        self.z = (float)(lValues[2])

        self.r = (int)(lValues[3])
        self.g = (int)(lValues[4])
        self.b = (int)(lValues[5])
        self.a = (float)(lValues[6])

        Point.xMin = min(Point.xMin, self.x)
        Point.xMax = max(Point.xMax, self.x)
        Point.yMin = min(Point.yMin, self.y)
        Point.yMax = max(Point.yMax, self.y)
        Point.zMin = min(Point.zMin, self.z)
        Point.zMax = max(Point.zMax, self.z)

    def __str__(self):
        return (str)(self.x) + " " + (str)(self.y) + " " + (str)(self.z) + " " + (str)(self.r) + " " + (str)(self.g) + " " + (str)(self.b) + " " +  (str)(self.a) + " "

    def zFit(self, i_Z)->bool:
        return i_Z - Point.EPS < self.z < i_Z + Point.EPS

if __name__ == "__main__":
    f = open("Data\\Scan 0 BIG.txt", "r")

    with open("Data\\Cloud_filtered.txt", "w") as fResult:
        for row in f.readlines():
            p = Point (row)

            if p.zFit(260):
                fResult.write(p.__str__() + "\n")



