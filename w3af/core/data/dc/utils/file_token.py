# -*- coding: utf-8 -*-
"""
file_token.py

Copyright 2014 Andres Riancho

This file is part of w3af, http://w3af.org/ .

w3af is free software; you can redistribute it and/or modify
it under the terms of the GNU General Public License as published by
the Free Software Foundation version 2 of the License.

w3af is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
GNU General Public License for more details.

You should have received a copy of the GNU General Public License
along with w3af; if not, write to the Free Software
Foundation, Inc., 51 Franklin St, Fifth Floor, Boston, MA  02110-1301  USA

"""
import w3af.core.data.kb.config as cf

from w3af.core.data.constants.file_templates.file_templates import get_template_with_payload
from w3af.core.data.dc.utils.token import DataToken
from w3af.core.controllers.misc.io import NamedStringIO


class FileDataToken(DataToken):
    def __init__(self, name, value, filename):
        super(FileDataToken, self).__init__(name, value)

        default_extension = cf.cf.get('fuzzed_files_extension', 'gif')

        if filename is None:
            extension = default_extension
        else:
            extension = filename.rsplit('.', 1)[-1]
            extension = extension or default_extension

        self.extension = extension
        self.filename = filename
        self.original_value = self.value = self.build_file(value)

    def build_file(self, value):

        if isinstance(value, basestring):
            _, file_content, fname = get_template_with_payload(self.extension,
                                                               value)

            # I have to create the NamedStringIO with a "name",
            # required for MultipartContainer to properly encode this as
            # multipart/post
            return NamedStringIO(file_content, name=fname)

        return value

    def set_value(self, new_value):
        self.value = self.build_file(new_value)
