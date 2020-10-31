#! /usr/bin/env python3
#
# Copyright © 2020 Jason Ekstrand
#
# PyCook is free software: you can redistribute it and/or modify it under the
# terms of the GNU General Public License as published by the Free Software
# Foundation, either version 3 of the License, or (at your option) any later
# version.
#
# PyCook is distributed in the hope that it will be useful, but WITHOUT ANY
# WARRANTY; without even the implied warranty of MERCHANTABILITY or FITNESS
# FOR A PARTICULAR PURPOSE.  See the GNU General Public License for more
# details.
#
# You should have received a copy of the GNU General Public License along with
# PyCook.  If not, see <https://www.gnu.org/licenses/>.

import re

class Tokenizer(object):
    def __init__(self, classes):
        self.classes = classes
        chunks = []
        for c in classes:
            chunks.append(r'(?:' + c.RE.pattern + ')')
        self.re = re.compile('(' + '|'.join(chunks) + ')')

    def _str_to_token(self, s):
        for c in self.classes:
            if c.RE.match(s):
                return c.from_match(s)
        return s

    def _tokenize(self, s):
        for c in self.re.split(s):
            if not c:
                continue
            yield self._str_to_token(c)

    def tokenize(self, s):
        t = list(self._tokenize(s))
        return t
