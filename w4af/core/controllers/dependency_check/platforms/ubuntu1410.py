"""
ubuntu1410.py

Copyright 2014 Andres Riancho

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
import distro 

from .ubuntu1204 import Ubuntu1204


class Ubuntu1410(Ubuntu1204):
    SYSTEM_NAME = 'Ubuntu 14.10'

    @staticmethod
    def is_current_platform():
        return 'Ubuntu' in distro.name() and '14.10' in distro.version()

