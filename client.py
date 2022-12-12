import httplib
import json
from  urllib import urlencode


h1 = httplib.HTTPConnection('localhost:1975', timeout=1)

h1.connect()
d = {'1': 'teszt'}
dd = urlencode(d)
h1.request('POST', 'localhost:1975', dd, {} )
result = h1.getresponse().read()
print(json.loads(result))

