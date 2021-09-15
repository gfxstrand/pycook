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
import decimal
import fractions
import mako.template
import os
import re

_LATEX_SPECIAL_RE = re.compile(r'([\\\$\#\^&%_{}°])')

def escape_str_for_latex(s):
    # https://tex.stackexchange.com/questions/34580/escape-character-in-latex
    def repl(m):
        if m.group(0) == '\\':
            return '$\\backslash$'
        elif m.group(0) == '~':
            return '\\texttt{\\~{}}'
        if m.group(0) == '°':
            return '{\\textdegree}'
        else:
            return '\\' + m.group(0)

    return _LATEX_SPECIAL_RE.sub(repl, s)

def to_latex(t):
    if isinstance(t, list):
        return ''.join(to_latex(i) for i in t)
    elif isinstance(t, units.Unit):
        return escape_str_for_latex(t.to_str())
    elif isinstance(t, units.Quantity):
        s = to_latex(t.num)
        if t.unit:
            s += ' ' + escape_str_for_latex(t.unit.to_str(num=t.num))
        return s
    elif isinstance(t, units.Range):
        return to_latex(t.min_num) + '--' + to_latex(t.max_num)
    elif isinstance(t, (int, decimal.Decimal)):
        return str(t)
    elif isinstance(t, fractions.Fraction):
        whole = t.numerator // t.denominator
        num = t.numerator % t.denominator
        denom = t.denominator
        if whole == 0 and num == 0:
            return '0'
        s = ''
        if whole > 0:
            s += str(whole)
        if num > 0:
            s += r'\nicefrac{{{0}}}{{{1}}}'.format(num, denom)
        return s
    elif isinstance(t, str):
        return escape_str_for_latex(t)
    else:
        assert False, 'Unknown token'


_RECIPE_TEMPLATE = mako.template.Template(r"""
\recipesection{${to_latex(recipe.name)}}
\begin{recipe}
% if recipe.from_name:
%% ${to_latex(recipe.from_name)}
% endif
% if recipe.from_url:
%% ${recipe.from_url}
% endif
\begin{rscol}
\begin{ingredientlist}
% for i in ingredient_shuffle(recipe.ingredients):
    <%
        if i.qty:
            qty_num = to_latex(i.qty.num)
        else:
            qty_num = ''
        if i.qty and i.qty.unit:
            qty_unit = i.qty.unit.to_str(num=i.qty.num)
        else:
            qty_unit = ''
    %>
    \ingredient{${to_latex(i.name)}}{${qty_num}}{${qty_unit}}
% endfor
\end{ingredientlist}
% if recipe.note:
\begin{recipenotes}
    ${to_latex(recipe.note)}
\end{recipenotes}
% endif
\end{rscol}
\begin{recipesteps}
% for i in recipe.instructions:
    \item ${to_latex(i)}
% endfor
\end{recipesteps}
\end{recipe}
""")

def render_recipe(r, ingredient_shuffle=lambda i : i):
    try:
        return _RECIPE_TEMPLATE.render(recipe=r, to_latex=to_latex,
                                       ingredient_shuffle=ingredient_shuffle)
    except Exception:
        # In the event there's an error, this imports some helpers from mako
        # to print a useful stack trace and prints it, then exits with
        # status 1, if python is run with debug; otherwise it just raises
        # the exception
        if __debug__:
            import sys
            from mako import exceptions
            sys.stderr.write(exceptions.text_error_template().render() + '\n')
            sys.exit(1)
        raise

_COOKBOOK_TEMPLATE = mako.template.Template(r"""
\documentclass[letterpaper]{report}

\usepackage{units}
\usepackage{gensymb}
\usepackage[headings]{fullpage}
\usepackage[letterpaper]{hyperref}
\usepackage{url}
\usepackage{${pkgpath}/cookbook}

\title{${to_latex(cookbook.title)}}
\author{${to_latex(cookbook.author)}}

\begin{document}
\maketitle
\tableofcontents

% for chapter in cookbook.chapters:
\clearpage
\chapter{${to_latex(chapter.title)}}
% for recipe in chapter.recipes:
${recipe.to_latex()}
% endfor
% endfor

\end{document}
""")

_RECIPE_CARD_TEMPLATE = mako.template.Template(r"""
\documentclass[letterpaper]{report}

\usepackage{units}
\usepackage{gensymb}
\usepackage[headings]{fullpage}
\usepackage[letterpaper]{hyperref}
\usepackage{url}
\usepackage{${pkgpath}/recipecards}


\title{${to_latex(cookbook.title)}}
\author{${to_latex(cookbook.author)}}

\pagestyle{empty}

<%
def shuffle_two_columns(list):
    half_len = (len(list) + 1) // 2
    for i in range(half_len):
        yield list[i]
        if half_len + i < len(list):
            yield list[half_len + i]
%>

\begin{document}
% for chapter in cookbook.chapters:
% for recipe in chapter.recipes:
\clearpage
\ifodd\value{page}\else\hbox{}\newpage\fi
${recipe.to_latex(ingredient_shuffle=shuffle_two_columns)}
% endfor
% endfor

\end{document}
""")

def render_cookbook(b, style='cookbook'):
    pkgpath = os.path.dirname(os.path.abspath(__file__))
    if style == 'cookbook':
        return _COOKBOOK_TEMPLATE.render(cookbook=b, to_latex=to_latex,
                                         pkgpath=pkgpath)
    elif style == '4x6cards':
        return _RECIPE_CARD_TEMPLATE.render(cookbook=b, to_latex=to_latex,
                                            pkgpath=pkgpath)
    else:
        assert False
