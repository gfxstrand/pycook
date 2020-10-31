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

import argparse as _argparse
from . import pdf as _pdf
from . import html as _html

def run():
    parser = _argparse.ArgumentParser()
    subparsers = parser.add_subparsers()
    _pdf.setup_subparser(subparsers.add_parser('pdf', help='PDF help'))
    _html.setup_subparser(subparsers.add_parser('html', help='HTML help'))
    args = parser.parse_args()
    try:
        args.func(args)
    except AttributeError:
        parser.print_help()
