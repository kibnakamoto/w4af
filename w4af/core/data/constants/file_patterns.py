"""
file_patterns.py

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

FILE_PATTERNS = (
        "root:x:0:0:",
        "daemon:x:1:1:",
        ":/bin/bash",
        ":/bin/sh",

        # /etc/passwd in AIX
        "root:!:x:0:0:",
        "daemon:!:x:1:1:",
        ":usr/bin/ksh",

        # boot.ini
        "[boot loader]",
        "default=multi(",
        "[operating systems]",

        # win.ini
        "[fonts]",

        # PHP script
        "<?php",

        # Executable script"
        "#!/",
    )
