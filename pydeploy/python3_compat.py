import platform

IS_PY3 = (platform.python_version() >= '3')

if IS_PY3:
    from urllib.parse import urlparse
    from urllib.request import urlopen
    basestring = str
    from io import BytesIO
    def make_str(s):
        if isinstance(s, bytes):
            s = s.decode('utf-8')
        return s
    def make_bytes(s):
        if isinstance(s, str):
            s = s.encode('utf-8')
        return s
else:
    from urlparse import urlparse
    from urllib2 import urlopen
    from __builtin__ import basestring
    from cStringIO import StringIO as BytesIO
    make_bytes = make_str = str
