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

from . import latex, rst, tokenizer, units, yaml_util
import decimal
import fractions
import re

class _NumberTokenizer:
    RE = units.NUMBER_RE
    from_match = units.number_from_str

_TOKENIZER = tokenizer.Tokenizer([
    units.Quantity,
    units.Unit,
    _NumberTokenizer,
])

def _tokenize_str(s):
    return _TOKENIZER.tokenize(s)

class Ingredient(object):
    def __init__(self, name, qty=None):
        self.name = name
        self.qty = qty

    @staticmethod
    def parse(s):
        m = units.Quantity.RE.match(s)
        if m:
            name = s[m.end():]
            qty = units.Quantity.from_match(m)
        else:
            name = s
            qty = None

        return Ingredient(name.strip(), qty)

class Recipe(object):
    _SECTIONS = set([
        'name',
        'from',
        'url',
        'ingredients',
        'instructions',
        'note',
    ])

    def __init__(self):
        pass

    @staticmethod
    def load(f):
        data = yaml_util.read_yaml_file(f)

        for section in data.keys():
            if section not in Recipe._SECTIONS:
                raise Exception('Invalid section "{}"'.format(section))

        r = Recipe()
        r.name = _tokenize_str(str(data['name']))
        r.from_name = str(data['from']) if 'from' in data else None
        r.from_url = str(data['url']) if 'url' in data else None
        r.ingredients = [Ingredient.parse(i) for i in data['ingredients']]
        r.instructions = [_tokenize_str(s) for s in data['instructions']]
        if 'note' in data:
            r.note = _tokenize_str(data['note'])
        else:
            r.note = None

        return r

    def to_latex(self, **kwargs):
        return latex.render_recipe(self, **kwargs)

    def to_rst(self, **kwargs):
        return rst.render_recipe(self, **kwargs)
