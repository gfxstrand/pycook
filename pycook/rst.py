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

from . import units
import mako.template
import decimal
import fractions
import re
import textwrap
import os

def escape_str_for_rst(s):
    return s

def to_rst(t):
    if isinstance(t, list):
        return ''.join(to_rst(i) for i in t)
    elif isinstance(t, units.Unit):
        return t.to_str()
    elif isinstance(t, units.Quantity):
        return t.to_str(vulgar=True)
    elif isinstance(t, (int, fractions.Fraction, decimal.Decimal)):
        return units.number_to_str(t, vulgar=True)
    elif isinstance(t, str):
        return escape_str_for_rst(t)
    else:
        assert False, 'Unknown token'

_RECIPE_TEMPLATE = mako.template.Template(r"""
${to_rst(recipe.name)}
${'='*len(to_rst(recipe.name))}

% if recipe.from_name:
From ${to_rst(recipe.from_name)} ${'[#ref]_' if recipe.from_url else ''}
% elif recipe.from_url:
From ${recipe.from_url}
% endif

Ingredients
-----------

% for i in recipe.ingredients:
- ${to_rst(i.qty) if i.qty else ''} ${to_rst(i.name)}
% endfor


Instructions
------------

% for i in recipe.instructions:
#. ${to_rst(i)}
% endfor

% if recipe.note:
.. note::
${textwrap.indent(to_rst(recipe.note), '  ')}
% endif

% if recipe.from_name and recipe.from_url:
.. [#ref] ${recipe.from_url}
% endif
""")

def render_recipe(r):
    return _RECIPE_TEMPLATE.render(recipe=r, to_rst=to_rst,
                                   textwrap=textwrap)

_CHAPTER_TEMPLATE = mako.template.Template(r"""
${to_rst(chapter.title)}
${'='*len(to_rst(chapter.title))}

.. toctree::
   :maxdepth: 1
   :caption: Contents:
   :glob:

% for r in chapter.recipes:
   ${to_filename(chapter.title)}/${to_filename(r.name)}
% endfor
""")

_COOKBOOK_TEMPLATE = mako.template.Template(r"""
${to_rst(cookbook.title)}
${'='*len(to_rst(cookbook.title))}

.. toctree::
   :maxdepth: 2
   :caption: Contents:

% for c in cookbook.chapters:
   ${to_filename(c.title)}.rst
% endfor
""")

def to_filename(s):
    return re.sub(r'\W+', '-', to_rst(s).lower())

def dump_cookbook(cb, path):
    os.makedirs(path, exist_ok=True)
    with open(os.path.join(path, 'index.rst'), 'w') as f:
        f.write(_COOKBOOK_TEMPLATE.render(cookbook=cb, to_rst=to_rst,
                                          to_filename=to_filename))

    for c in cb.chapters:
        chapter_path = os.path.join(path, to_filename(c.title))
        os.makedirs(chapter_path, exist_ok=True)
        with open(chapter_path + '.rst', 'w') as f:
            f.write(_CHAPTER_TEMPLATE.render(chapter=c, to_rst=to_rst,
                                             to_filename=to_filename))

        for r in c.recipes:
            recipe_path = os.path.join(chapter_path, to_filename(r.name))
            with open(recipe_path + '.rst', 'w') as f:
                f.write(render_recipe(r))
