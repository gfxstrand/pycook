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

from . import latex, recipe, rst, yaml_util
import os

class Chapter(object):
    def __init__(self, title, description=None, recipes=[]):
        self.title = title
        self.description = description=None
        self.recipes = recipes

class Cookbook(object):
    def __init__(self, title, author, chapters=[]):
        self.title = title
        self.author = author
        self.chapters = chapters

    @staticmethod
    def load(path):
        config = yaml_util.read_yaml_file(path)
        cb_title = config['title']
        cb_author = config['author']
        cb_dir = config.get('path', os.path.dirname(os.path.abspath(path)))

        chapters = []
        with os.scandir(cb_dir) as cit:
            for c in cit:
                if not c.is_dir():
                    continue

                index_path = os.path.join(c.path, 'index.yaml')
                try:
                    index = yaml_util.read_yaml_file(index_path)
                except FileNotFoundError:
                    continue

                c_title = index['title']
                c_description = index.get('description')

                recipes = []
                with os.scandir(c.path) as rit:
                    for r in rit:
                        if not r.name.endswith('.yaml'):
                            continue

                        if r.name == 'index.yaml':
                            continue

                        recipes.append(recipe.Recipe.load(r.path))

                recipes.sort(key=lambda r : r.name)
                chapters.append(Chapter(c_title, c_description, recipes))

        return Cookbook(cb_title, cb_author, chapters)

    def to_latex(self, **kwargs):
        return latex.render_cookbook(self, **kwargs)

    def dump_rst(self, path):
        rst.dump_cookbook(self, path)
