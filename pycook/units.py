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

import decimal
import fractions
import numbers
import re

class Unit(object):
    RE = re.compile(r'\[\w+\]')
    _RE = re.compile(r'\[(?P<unit>\w+)\]')

    _name_to_unit = {}

    def __init__(self, name, text, plural=None,
                 is_english=False, is_metric=False):
        self.name = name
        self.text = text
        self.plural = plural if plural else text
        assert not (is_metric and is_english)
        self.is_english = is_english,
        self.is_metric = is_metric

        # Register this unit
        assert name not in Unit._name_to_unit
        Unit._name_to_unit[name] = self

        # TODO: Once we get auto-plurals working, get rid of this
        if plural:
            Unit._name_to_unit[plural] = self

    def __repr__(self):
        return '[' + self.name + ']'

    def __str__(self):
        return self.text

    def to_str(self, num=None, plural=False):
        # If specified, num overrides plural
        if num is not None:
            if isinstance(num, Range):
                plural = num.max_num > 1
            else:
                plural = num > 1
        return self.plural if plural else self.text

    @staticmethod
    def from_name(name):
        return Unit._name_to_unit[name]

    @staticmethod
    def from_match(m):
        if isinstance(m, re.Match):
            m = m.group(0)
        m = Unit._RE.match(m)
        return Unit.from_name(m.group('unit'))

# TODO: These are really bad units; we should get rid of them
BAG = Unit('bag', 'bag')
CAN = Unit('can', 'can', plural='cans')
PACKAGE = Unit('pkg', 'pkg.')

# General units
MINUTE = Unit('min', 'min.')
HOUR = Unit('hour', 'hour')
DAY = Unit('day', 'day', plural='days')
CLOVE = Unit('clove', 'clove', plural='cloves')
STRIP = Unit('strip', 'strip', plural='strips')

# English Units
CUP = Unit('cup', 'cup', plural='cups', is_english=True)
TABLESPOON = Unit('tbsp', 'tbsp.', is_english=True)
TEASPOON = Unit('tsp', 'tsp.', is_english=True)
POUND = Unit('lb', 'lb.', is_english=True)
OUNCE = Unit('oz', 'oz.', is_english=True)
DEGREES_FAHRENHEIT = Unit('degF', '°F', is_english=True)
INCH = Unit('in', 'in.', is_english=True)
GALLON = Unit('gal', 'gal.', is_english=True)

# Metric Units
GRAM = Unit('g', 'g', is_metric=True)
MILLILETER = Unit('ml', 'ml', is_metric=True)
DEGREES_CELSIUS = Unit('degC', '°C', is_metric=True)
CENTIMETER = Unit('cm', 'cm', is_metric=True)


NUMBER_RE = re.compile(r'(?:\d+\s+)?\d/\d|\d*\.\d+|\d+')
_FRAC_RE = re.compile(r'(?:(?P<whole>\d+)\s+)?(?P<frac>\d/\d)')

def number_from_str(s):
    try:
        return int(s)
    except ValueError:
        pass

    m = _FRAC_RE.match(s)
    if m:
        n = fractions.Fraction(m.group('frac'))
        if m.group('whole'):
            n += int(m.group('whole'))
        return n

    return decimal.Decimal(s)


_VULGAR_FRACTIONSS = {
    (1, 2): '½',
    (1, 3): '⅓',
    (2, 3): '⅔',
    (1, 4): '¼',
    (3, 4): '¾',
    (1, 5): '⅕',
    (2, 5): '⅖',
    (3, 5): '⅗',
    (4, 5): '⅘',
    (1, 6): '⅙',
    (5, 6): '⅚',
    (1, 8): '⅛',
    (3, 8): '⅜',
    (5, 8): '⅝',
    (7, 8): '⅞',
}

class Range(object):
    def __init__(self, min_num, max_num):
        assert isinstance(min_num, (int, fractions.Fraction, decimal.Decimal))
        assert isinstance(max_num, (int, fractions.Fraction, decimal.Decimal))
        self.min_num = min_num
        self.max_num = max_num

def number_to_str(n, vulgar=False):
    if isinstance(n, Range):
        dash = '--' if vulgar else ' -- '
        return number_to_str(n.min_num, vulgar) + dash + \
               number_to_str(n.max_num, vulgar)
    elif isinstance(n, (int, decimal.Decimal)):
        return str(n)
    elif isinstance(n, fractions.Fraction):
        whole = n.numerator // n.denominator
        num = n.numerator % n.denominator
        denom = n.denominator
        if whole == 0 and denom == 0:
            return '0'
        s = ''
        if whole > 0:
            s += str(whole)
        if num > 0:
            if vulgar:
                s += _VULGAR_FRACTIONSS[(num, denom)]
            else:
                if whole:
                    s += ' '
                s += str(num) + '/' + str(denom)
        return s
    else:
        assert False, 'Not a number type'

class Quantity(object):
    RE = re.compile(r'(?:(?:' + NUMBER_RE.pattern + r')\s*-+\s*)?' +
                    r'(?:' + NUMBER_RE.pattern + r')' +
                    r'(?:\s*' + Unit.RE.pattern + r')?')
    _RE = re.compile(r'(?:(?P<min_num>' + NUMBER_RE.pattern + r')\s*-+\s*)?' +
                     r'(?P<num>' + NUMBER_RE.pattern + r')' +
                     r'(?:\s*(?P<unit>' + Unit.RE.pattern + r'))?')

    def __init__(self, num, unit=None):
        assert isinstance(num, (Range, int, fractions.Fraction,
                                decimal.Decimal))
        assert num != 0
        assert unit is None or isinstance(unit, Unit)
        self.num = num
        self.unit = unit

    def __repr__(self):
        return 'Quantity("' + self.to_str() + '")'

    def to_str(self, vulgar=False):
        s = number_to_str(self.num, vulgar)
        if self.unit:
            s += ' ' + self.unit.to_str(num=self.num)
        return s

    @staticmethod
    def from_match(m):
        if isinstance(m, re.Match):
            m = m.group(0)
        m = Quantity._RE.match(m)
        num = number_from_str(m.group('num'))
        if m.group('min_num'):
            min_num = number_from_str(m.group('min_num'))
            num = Range(min_num, num)
        if m.group('unit'):
            unit = Unit.from_match(m.group('unit'))
        else:
            unit = None
        return Quantity(num, unit)

    @staticmethod
    def from_str(s):
        return Quantity.from_match(Quantity.RE.match(s))
