"""
is_source_file.py

Copyright 2010 Andres Riancho

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
import re
import string

from w4af.core.data.quick_match.multi_re import MultiRE

PHP = 'PHP'
ASP = 'ASP'
JSP = 'JSP'
ASPX = 'ASPX'
UNKNOWN = 'Unknown'
SHELL = 'Shell script'
JAVA = 'Java'
RUBY = 'Ruby'
PYTHON = 'Python'
GROOVY = 'Groovy'


SOURCE_CODE = (
    (r'<\?php .*?\?>', {PHP}),
    (r'<\?php\n.*?\?>', {PHP}),       # These two are required for perf #2129
    (r'<\?php\r.*?\?>', {PHP}),       # and are repeated over the list

    # Need to review how to re-add these in the future
    # https://github.com/andresriancho/w3af/issues/2129
    #
    #('<\? .*?\?>', {PHP}),
    #('<\?\n.*?\?>', {PHP}),
    #('<\?\r.*?\?>', {PHP}),

    (r'<% .*?%>', {ASP, JSP}),
    (r'<%\n.*?%>', {ASP, JSP}),
    (r'<%\r.*?%>', {ASP, JSP}),

    (r'<%@ .*?%>', {ASPX}),          # http://goo.gl/zEjHA4
    (r'<%@\n.*?%>', {ASPX}),
    (r'<%@\r.*?%>', {ASPX}),

    (r'<asp:.*?%>', {ASPX}),
    (r'<jsp:.*?>', {JSP}),

    (r'<%! .*%>', {JSP}),
    (r'<%!\n.*%>', {JSP}),
    (r'<%!\r.*%>', {JSP}),
    (r'<%=.*%>', {JSP, PHP, RUBY}),

    (r'<!--\s*%.*?%(--)?>', {PHP}),
    (r'<!--\s*\?.*?\?(--)?>', {ASP, JSP}),
    (r'<!--\s*jsp:.*?(--)?>', {JSP}),

    (r'#include <', {UNKNOWN}),

    (r'#!/usr/', {SHELL}),
    (r'#!/opt/', {SHELL}),
    (r'#!/bin/', {SHELL}),

    (r'(^|\W)import java\.', {JAVA}),
    (r'(^|\W)public class \w{1,60}\s?\{\s.*\Wpublic', {JAVA}),
    (r'(^|\W)package\s\w+\;', {JAVA}),

    (r'<!--g:render', {GROOVY}),

    # Python
    (r'(^|\W)def .*?\(.*?\):(\n|\r)', {PYTHON}),

    # Ruby
    (r'(^|\W)class \w{1,60}\s*<?\s*[a-zA-Z0-9_:]{0,90}.*?\W(def|validates)\s.*?\send($|\W)', {RUBY}),
)

BLACKLIST = {'xml', 'xpacket'}

_multi_re = MultiRE(SOURCE_CODE, re.IGNORECASE | re.DOTALL, hint_len=2)
if _multi_re._regexes_with_no_keywords != []:
    print("Warning, possible performance issue in MultiRE", _multi_re._regexes_with_no_keywords)


def contains_source_code(http_response):
    """
    :param http_response: The HTTP response object
    :return: A tuple with:
                - re.match object if the file_content matches a source code file
                - A tuple containing the programming language names
    """
    body = http_response.get_body()
    if isinstance(body, bytes):
        if http_response.charset is not None:
            body = http_response.get_body().decode(http_response.charset, errors="ignore")
        else:
            body = http_response.decode('utf-8', errors="ignore")

    for match, _, _, lang in _multi_re.query(body):

        if is_false_positive(http_response, match, lang):
            continue

        return match, lang

    return None, None


def is_false_positive(http_response, match, detected_langs):
    """
    :param http_response: The HTTP response object
    :param match: The regular expression match object
    :param detected_langs: Language names
    :return: True if this match is a false positive and should be ignored
    """
    match_str = match.group(0)

    for blacklist_str in BLACKLIST:
        if blacklist_str in match_str:
            return True

    # Avoid some (rather common) false positives that appear in JS files
    # https://github.com/andresriancho/w3af/issues/5379
    # https://github.com/andresriancho/w3af/issues/12379
    #
    # The detection for some languages is weaker, thus we don't fully trust
    # them:
    for lang in detected_langs:
        if lang in {PHP, ASP, JSP, ASPX}:
            if 'javascript' in http_response.content_type:
                return True

    # Avoid some false positives in large binary files where we might
    # have <% , then 182837 binary chars, and finally %>.
    printable = 0.0
    ratio = 0.9

    for char in match_str:
        if char in string.printable:
            printable += 1

    if (printable / len(match_str)) < ratio:
        return True

    return False
