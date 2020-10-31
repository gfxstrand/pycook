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

import os
import shutil
import subprocess
import tempfile

from ..cookbook import Cookbook

def main(args):
    tmpdir = tempfile.mkdtemp(prefix='cookbook')
    pkgpath = os.path.dirname(os.path.abspath(os.path.join(__file__, '..')))
    try:
        c = Cookbook.load(args.input)
        c.dump_rst(tmpdir)
        shutil.copyfile(os.path.join(pkgpath, 'sphinx_conf_py'),
                        os.path.join(tmpdir, 'conf.py'))

        subprocess.run([
            'sphinx-build',
            '-b', 'html',
            tmpdir,
            args.output
        ])

    except:
        shutil.rmtree(tmpdir)
        raise

    shutil.rmtree(tmpdir)

def setup_subparser(subparser):
    subparser.add_argument('input', help='Name of input file', )
    subparser.add_argument('output', help='Name of output directory')
    subparser.set_defaults(func=main)
