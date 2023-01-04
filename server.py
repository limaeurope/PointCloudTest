import os.path
import uuid
from http import server
import json
import sys
import tempfile

from Classes.S_Point import S_Point
from Classes.S_Line import S_Line
from Classes.S_ClosedPolyLine import S_ClosedPolyLine


class LineCollector:
    """First step:
    processes raw point list into multiple lines of multiple points"""
    def __init__(self, p_messageBody):
        S_Line.setEPS(p_messageBody['xEPS'])
        S_Line.setAngularEPS(p_messageBody['aEPS'])
        areaDiff = p_messageBody['aDiff']

        self.pointList = []

        for coordPair in p_messageBody['points']:
            _point = S_Point(coordPair[0], coordPair[1])
            self.pointList.append(_point)
        self.closedPolyLine  = S_ClosedPolyLine(self.pointList)

        """Second step:
        Remove short edges by reconnecting the long ones
        """
        self.closedPolyLine.autoPurge(areaDiff)

    def getPointTree(self):
        return self.closedPolyLine.toJSON()

    def setEPS(self, p_eps):
        S_Line.setEPS(p_eps)

    def setAngularEPS(self, p_angularEPS):
        S_Line.setAngularEPS(p_angularEPS)

    def toDict(self):
        return self.closedPolyLine.toDict()


# class AutoPurger:
#
#     pass
#
#
# class CollectByAngleAndDist:
#     """Third step:
#
#     """
#     pass


class requestHandler(server.CGIHTTPRequestHandler):
    def do_POST(self) -> None:
        content_len = int(self.headers.get('Content-Length'))
        body = self.rfile.read(content_len).decode()
        body = json.loads(body)

        lc = LineCollector(body)

        self.send_response(200)
        self.send_header('Content-type', 'text/html')
        self.end_headers()
        response = {'resultPoints': lc.toDict()}

        if True:
            sTemp = str(uuid.uuid4())
            with open(f"Dumps\\{sTemp}.json", "w") as fTemp:
                json.dump({**body, **response}, fTemp, indent=4)

        json_str = json.dumps(response)
        self.wfile.write(bytes(json_str, "utf-8"))

with server.HTTPServer(("127.0.0.1", 1975), requestHandler) as s:
    s.serve_forever()