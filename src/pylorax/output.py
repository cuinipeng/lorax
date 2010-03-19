#
# output.py
#
# Copyright (C) 2009  Red Hat, Inc.
#
# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation; either version 2 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.
#
# Red Hat Author(s):  Martin Gracik <mgracik@redhat.com>
#

import sys
import re

from decorators import singleton


# color codes
C_DEFAULT = "\x1b[39m"
C_RESET = "\x1b[0m"

C_BLACK = "\x1b[0;30m"
C_WHITE = "\x1b[1;37m"
C_RED = "\x1b[0;31m"
C_GREEN = "\x1b[0;32m"
C_BLUE = "\x1b[0;34m"
C_LIGHTRED = "\x1b[1;31m"
C_LIGHTGREEN = "\x1b[1;32m"
C_LIGHTBLUE = "\x1b[1;34m"

C_BOLD = "\x1b[1m"
C_UNDERLINE = "\x1b[4m"


# format tags
TAGS = [(re.compile(r"<b>"), C_BOLD),
        (re.compile(r"<u>"), C_UNDERLINE),
        (re.compile(r"<red>"), C_RED),
        (re.compile(r"<green>"), C_GREEN),
        (re.compile(r"<blue>"), C_BLUE),
        (re.compile(r"</(b|u|red|green|blue)>"), C_RESET)]


# output levels
CRITICAL = 50
ERROR = 40
WARNING = 30
INFO = 20
DEBUG = 10
NOTSET = 0


@singleton
class LoraxOutput(object):

    def __init__(self):
        self._colors = True
        self._encoding = "utf-8"
        self._output_level = INFO
        self._indent_level = 0

        self._ignore_errors = set()

    def basic_config(self, colors=None, encoding=None, output_level=None):
        if colors is not None:
            self._colors = colors

        if encoding is not None:
            self._encoding = encoding

        if output_level is not None:
            self._output_level = output_level

    @property
    def ignore(self):
        return self._ignore_errors

    @ignore.setter
    def ignore(self, errors):
        self._ignore_errors = errors

    def indent(self):
        self._indent_level += 1

    def unindent(self):
        if self._indent_level > 0:
            self._indent_level -= 1

    def write(self, s, file=sys.stdout):
        if self._colors:
            s = self.__format(s)
        else:
            s = self.__raw(s)

        file.write(s)
        file.flush()

    def writeline(self, s, file=sys.stdout):
        s = "{0}{1}\n".format("    " * self._indent_level, s)
        self.write(s, file=file)

    def critical(self, s, file=sys.stdout):
        s = "** critical: {0}".format(s)
        if (self._output_level <= CRITICAL and
            self.__raw(s) not in self.ignore):
            self.writeline(s, file=file)

    def error(self, s, file=sys.stdout):
        s = "** error: {0}".format(s)
        if (self._output_level <= ERROR and
            self.__raw(s) not in self.ignore):
            self.writeline(s, file=file)

    def warning(self, s, file=sys.stdout):
        s = "** warning: {0}".format(s)
        if (self._output_level <= WARNING and
            self.__raw(s) not in self.ignore):
            self.writeline(s, file=file)

    def info(self, s, file=sys.stdout):
        if self._output_level <= INFO:
            self.writeline(s, file=file)

    def debug(self, s, file=sys.stdout):
        if self._output_level <= DEBUG:
            self.writeline(s, file=file)

    def __raw(self, s):
        for tag, ccode in TAGS:
            s = tag.sub("", s)
        return s

    def __format(self, s):
        for tag, ccode in TAGS:
            s = tag.sub(ccode, s)
        return s