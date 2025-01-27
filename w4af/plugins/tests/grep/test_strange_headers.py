"""
test_strange_headers.py

Copyright 2012 Andres Riancho

This file is part of w4af, https://w4af.net/ .

w4af is free software; you can redistribute it and/or modify
it under the terms of the GNU General Public License as published by
the Free Software Foundation version 2 of the License.

w4af is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
GNU General Public License for more details.

You should have received a copy of the GNU General Public License
along with w4af; if not, write to the Free Software
Foundation, Inc., 51 Franklin St, Fifth Floor, Boston, MA  02110-1301  USA

"""
import time
import unittest

import w4af.core.data.kb.knowledge_base as kb

from w4af.core.data.url.HTTPResponse import HTTPResponse
from w4af.core.data.request.fuzzable_request import FuzzableRequest
from w4af.core.data.parsers.doc.url import URL
from w4af.core.data.dc.headers import Headers
from w4af.core.controllers.misc.temp_dir import create_temp_dir
from w4af.plugins.grep.strange_headers import strange_headers


class TestStrangeHeaders(unittest.TestCase):

    def setUp(self):
        create_temp_dir()
        kb.kb.cleanup()
        self.plugin = strange_headers()

    def tearDown(self):
        self.plugin.end()

    def test_strange_headers_positive(self):
        body = 'Hello world'
        url = URL('http://www.w4af.com/')
        headers = Headers([('content-type', 'text/html'),
                           ('hello-world', 'yes!')])
        request = FuzzableRequest(url, method='GET')

        resp_positive = HTTPResponse(200, body, headers, url, url, _id=1)
        self.plugin.grep(request, resp_positive)

        info_sets = kb.kb.get('strange_headers', 'strange_headers')
        self.assertEqual(len(info_sets), 1)

        info = info_sets[0]
        expected_desc = ('The remote web server sent 1 HTTP responses with'
                         ' the uncommon response header "hello-world", one'
                         ' of the received header values is "yes!". The'
                         ' first ten URLs which sent the uncommon header'
                         ' are:\n - http://www.w4af.com/\n')
        self.assertEqual(info.get_name(), 'Strange header')
        self.assertEqual(info.get_url(), url)
        self.assertEqual(info.get_desc(), expected_desc)

    def test_strange_headers_timing(self):
        body = 'Hello world'
        url = URL('http://www.w4af.com/')
        headers = Headers([('content-type', 'text/html'),
                           ('hello-world', 'yes!')])
        request = FuzzableRequest(url, method='GET')

        resp_positive = HTTPResponse(200, body, headers, url, url, _id=1)

        start = time.time()

        for _ in range(5):
            self.plugin.grep(request, resp_positive)

        spent = time.time() - start
        # print('Profiling run in %s seconds' % spent)

    def test_strange_headers_no_group(self):
        body = 'Hello world'

        url_1 = URL('http://www.w4af.com/1')
        headers_1 = Headers([('content-type', 'text/html'),
                             ('hello-world', 'yes!')])
        request_1 = FuzzableRequest(url_1, method='GET')
        resp_1 = HTTPResponse(200, body, headers_1, url_1, url_1, _id=1)
        self.plugin.grep(request_1, resp_1)

        url_2 = URL('http://www.w4af.com/2')
        headers_2 = Headers([('content-type', 'text/html'),
                             ('bye-bye', 'chau')])
        request_2 = FuzzableRequest(url_2, method='GET')
        resp_2 = HTTPResponse(200, body, headers_2, url_2, url_2, _id=2)
        self.plugin.grep(request_2, resp_2)

        info_sets = kb.kb.get('strange_headers', 'strange_headers')
        self.assertEqual(len(info_sets), 2)

    def test_strange_headers_group(self):
        body = 'Hello world'

        url_1 = URL('http://www.w4af.com/1')
        headers_1 = Headers([('content-type', 'text/html'),
                           ('hello-world', 'yes!')])
        request_1 = FuzzableRequest(url_1, method='GET')
        resp_1 = HTTPResponse(200, body, headers_1, url_1, url_1, _id=1)
        self.plugin.grep(request_1, resp_1)

        url_2 = URL('http://www.w4af.com/2')
        headers_2 = Headers([('content-type', 'text/html'),
                           ('hello-world', 'nope')])
        request_2 = FuzzableRequest(url_2, method='GET')
        resp_2 = HTTPResponse(200, body, headers_2, url_2, url_2, _id=2)
        self.plugin.grep(request_2, resp_2)

        info_sets = kb.kb.get('strange_headers', 'strange_headers')
        self.assertEqual(len(info_sets), 1)

    def test_strange_headers_negative(self):
        body = 'Hello world'
        url = URL('http://www.w4af.com/')
        headers = Headers([('content-type', 'text/html'),
                           ('x-pad', 'yes!')])
        request = FuzzableRequest(url, method='GET')

        resp_positive = HTTPResponse(200, body, headers, url, url, _id=1)
        self.plugin.grep(request, resp_positive)

        infos = kb.kb.get('strange_headers', 'strange_headers')
        self.assertEqual(len(infos), 0)
