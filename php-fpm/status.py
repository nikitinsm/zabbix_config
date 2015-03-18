#!/usr/bin/env python
"""
@todo: check with nginx -V 2>&1 | grep -o with-http_stub_status_module
@todo: error handling, I found this shit in github but there is no official doc reference
    ERROR_NO_ACCESS_FILE="-0.9900"
    ERROR_NO_ACCESS="-0.9901"
    ERROR_WRONG_PARAM="-0.9902"
    ERROR_DATA="-0.9903" # either can not connect /	bad host / bad port


Nginx output example:
Active connections: 43
server accepts handled requests
 7368 7368 10993
Reading: 0 Writing: 5 Waiting: 38
"""
import json
import re
import sys
import urllib2
import urlparse


OUTPUT_RE = re.compile(r'(?P<name>[\w ]+):\s+(?P<value>.+)')


def main(name=None, url='http://127.0.0.1/status'):
    result = ''

    url_parsed = urlparse.urlparse(url)
    scheme = url_parsed.scheme or 'http'
    netloc = url_parsed.netloc or '127.0.0.1'
    path = '/' + url_parsed.path if not url_parsed.path.startswith('/') else url_parsed.path

    url = '%s://%s%s%s' % \
        ( scheme
        , netloc
        , path
        , '?' + url_parsed.query if url_parsed.query else ''
        )

    try:
        response = urllib2.urlopen(url)
    except urllib2.HTTPError:
        pass
    else:
        response_data = response.read()

        data = dict()
        for k, v in OUTPUT_RE.findall(response_data):
            k = k.replace(' ', '_').lower()
            if k:
                data[k] = v

        try:
            result = data[name]
        except KeyError:
            result = json.dumps(data, indent=2)

    print result


if __name__ == '__main__':
    main(*sys.argv[1:3])