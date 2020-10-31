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

import io
import yaml
try:
    from yaml import CLoader as Loader
except ImportError:
    from yaml import Loader

def read_yaml_file(f):
    if isinstance(f, str):
        with io.open(f, "r") as stream:
            return read_yaml_file(stream)
    return yaml.load(f, Loader=Loader)
