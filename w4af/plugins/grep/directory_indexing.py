"""
directory_indexing.py

Copyright 2006 Andres Riancho

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
import w4af.core.data.constants.severity as severity

from w4af.core.controllers.plugins.grep_plugin import GrepPlugin
from w4af.core.data.bloomfilter.scalable_bloom import ScalableBloomFilter
from w4af.core.data.quick_match.multi_in import MultiIn
from w4af.core.data.kb.vuln import Vuln


class directory_indexing(GrepPlugin):
    """
    Grep every response for directory indexing problems.

    :author: Andres Riancho (andres.riancho@gmail.com)
    """

    DIR_INDEXING = (
        "<title>Index of /",
        '<a href="?C=N;O=D">Name</a>',
        '<A HREF="?M=A">Last modified</A>',
        "Last modified</a>",
        "Parent Directory</a>",
        "Directory Listing for",
        "<TITLE>Folder Listing.",
        '<table summary="Directory Listing" ',
        "- Browsing directory ",
        # IIS 6.0 and 7.0
        '">[To Parent Directory]</a><br><br>',
        # IIS 5.0
        '<A HREF=".*?">.*?</A><br></pre><hr></body></html>'
    )
    _multi_in = MultiIn(DIR_INDEXING)

    def __init__(self):
        GrepPlugin.__init__(self)

        self._already_visited = ScalableBloomFilter()

    def grep(self, request, response):
        """
        Plugin entry point, search for directory indexing.
        :param request: The HTTP request object.
        :param response: The HTTP response object
        :return: None
        """
        if not response.is_text_or_html():
            return
        
        if response.get_url().get_domain_path() in self._already_visited:
            return

        self._already_visited.add(response.get_url().get_domain_path())
        
        html_string = response.get_body()

        for _ in self._multi_in.query(html_string):
            
            desc = 'The URL: "%s" has a directory indexing vulnerability.'
            desc = desc % response.get_url()
            
            v = Vuln('Directory indexing', desc, severity.LOW, response.id,
                     self.get_name())
            v.set_url(response.get_url())

            self.kb_append_uniq(self, 'directory', v, 'URL')
            break

    def get_long_desc(self):
        """
        :return: A DETAILED description of the plugin functions and features.
        """
        return """
        This plugin greps every response directory indexing problems.
        """
