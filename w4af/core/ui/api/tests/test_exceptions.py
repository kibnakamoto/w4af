"""
test_exceptions.py

Copyright 2015 Andres Riancho

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
import json

from w4af.core.ui.api.tests.utils.test_api import APIUnitTest
from w4af.core.ui.api.tests.utils.test_profile import get_test_profile


class ScanExceptionResourceTest(APIUnitTest):

    def test_query_exceptions(self):
        profile, target_url = get_test_profile()
        data = {'scan_profile': profile,
                'target_urls': [target_url]}

        response = self.app.post('/scans/',
                                 data=json.dumps(data),
                                 headers=self.HEADERS)

        scan_id = json.loads(response.data)['id']
        self.wait_until_running()

        # Create an exception in the w4af scan
        response = self.app.post('/scans/%s/exceptions/' % scan_id,
                                 headers=self.HEADERS,
                                 data='{}')

        self.assertEqual(response.status_code, 201)

        # And now query it using the REST API
        response = self.app.get('/scans/%s/exceptions/' % scan_id,
                                headers=self.HEADERS)

        exceptions = json.loads(response.data)['items']
        self.assertEqual(len(exceptions), 1)

        exception = exceptions[0]
        self.assertIsInstance(exception['lineno'], int)
        exception.pop('lineno')

        expected_summary = {'exception': 'unittest',
                            'function_name': 'exception_creator()',
                            'href': '/scans/0/exceptions/0',
                            'id': 0,
                            #u'lineno': 123,
                            'phase': 'phase',
                            'plugin': 'plugin'}
        self.assertEqual(exception, expected_summary)

        response = self.app.get('/scans/%s/exceptions/0' % scan_id,
                                headers=self.HEADERS)

        self.assertIn('traceback', json.loads(response.data))