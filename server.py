from http import server
import json
import sys
import urllib
from urllib.parse import parse_qsl


from Classes.S_Point import S_Point
from Classes.S_Line import S_Line
from Classes.S_ClosedPolyLine import S_ClosedPolyLine


class LineCollector:
    """First step:
    processes raw point list into multiple lines of multiple points"""
    def __init__(self, p_messageBody):
        S_Line.setEPS(p_messageBody['xEPS'])
        S_Line.setAngularEPS(p_messageBody['aEPS'])

        self.pointList = []

        for coordPair in p_messageBody['points']:
            _point = S_Point(coordPair[0], coordPair[1])
            self.pointList.append(_point)

            self.closedPolyLine  = S_ClosedPolyLine(self.pointList)

    def getPointTree(self):
        return self.closedPolyLine.toJSON()

    def setEPS(self, p_eps):
        S_Line.setEPS(p_eps)

    def setAngularEPS(self, p_angularEPS):
        S_Line.setAngularEPS(p_angularEPS)


class requestHandler(server.CGIHTTPRequestHandler):
    def do_POST(self) -> None:
        content_len = int(self.headers.get('Content-Length'))
        body = self.rfile.read(content_len).decode("UTF-8")
        body = dict(parse_qsl(body))

        lc = LineCollector(body)

        self.send_response(200)
        self.send_header('Content-type', 'text/html')
        self.end_headers()
        response = {'resultPoints': lc.getPointTree()}

        json_str = json.dumps(response)
        self.wfile.write(bytes(json_str, "utf-8"))

with server.HTTPServer(("127.0.0.1", 1975), requestHandler) as s:
    s.serve_forever()