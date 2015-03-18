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


OUTPUT_RE = re.compile\
    ( r'[^\d]*(?P<conn_active>\d+)'
      r'[^\d]*(?P<conn_accepted>\d+)\s(?P<conn_total>\d+)\s(?P<req_total>\d+)'
      r'[^\d]*\s(?P<reading>\d+)[^\d]*\s(?P<writing>\d+)[^\d]*(?P<waiting>\d+)'
    )


def main(name=None, url='http://127.0.0.1/stub_status'):
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
        match = OUTPUT_RE.match(response_data)
        data = match.groupdict() or {}

        if {'conn_total', 'conn_accepted', 'req_total'} & set(data.keys()):
            data['conn_failed'] = \
                str(int(data['conn_total']) - int(data['conn_accepted']))
            data['req_avg_total'] = \
                '%.4f' % (float(data['req_total']) / int(data['conn_total']) if int(data['conn_total']) else 0)
            data['req_avg_accepted'] = \
                '%.4f' % (float(data['req_total']) / int(data['conn_accepted']) if int(data['conn_accepted']) else 0)
        try:
            result = data[name]
        except KeyError:
            result = json.dumps(data, indent=2)

    print result

if __name__ == '__main__':
    main(*sys.argv[1:3])