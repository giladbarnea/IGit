#!/usr/bin/env python3.8
import re
from dataclasses import dataclass, asdict
from pprint import pprint as pp
from typing import Optional, Union


# ResetKey = Literal['normal', 'italic', 'underline', 'inverse', 'strike']

# https://docs.python.org/3/library/typing.html#typing.TypedDict
# class Point2D(TypedDict):  # this works with PyCharm
#     x: int
#     y: int
#     label: str


# Point2D = TypedDict('Point2D', dict(x=int, y=int, label=str)) # this misses bad types
# Point2D = TypedDict('Point2D', {'x': int, 'y': int, 'label': str})  # this misses good types
# a: Point2D = {'x': 1, 'y': 2, 'label': 'hi'}  # OK


# b: Point2D = {'z': 3, 'label': 'bad'}  # NOT OK


@dataclass
class Indexable:
    def __getitem__(self, item):
        t = asdict(self)
        try:
            return t[item]
        except KeyError:
            pp(t)
            if item == 'normal':
                return 0


@dataclass
class Reset(Indexable):
    normal = 0
    italic = 23
    underline = 24
    inverse = 27
    strike = 29


@dataclass
class SatBG(Indexable):
    grey = 100
    red = 101
    green = 102
    yellow = 103
    blue = 104
    purple = 105
    turquoise = 106
    white = 107


@dataclass
class Sat(Indexable):
    bg: SatBG = SatBG()
    red = 91
    green = 92
    yellow = 93
    blue = 94
    purple = 95
    turquoise = 96
    white = 97


@dataclass
class BG(Indexable):
    grey = 40
    red = 41
    green = 42
    yellow = 43
    blue = 44
    purple = 45
    turquoise = 46
    white = 47


@dataclass
class ColorCodes(Indexable):
    bg: BG = BG()
    sat: Sat = Sat()
    reset: Reset = Reset()
    bold = 1
    grey = 2
    italic = 3
    ul = 4
    inverse = 7
    strike = 9
    doubleul = 21
    red = 31
    green = 32
    yellow = 33
    blue = 34
    purple = 35
    turquoise = 36
    white = 37
    darkgrey = 90


# COLOR_CODES = ColorCodes()

"""class Reset(TypedDict):
    normal: Literal[0]
    italic: Literal[23]
    underline: Literal[24]
    inverse: Literal[27]
    strike: Literal[29]


class SatBG(TypedDict):
    grey: Literal[100]
    red: Literal[101]
    green: Literal[102]
    yellow: Literal[103]
    blue: Literal[104]
    purple: Literal[105]
    turquoise: Literal[106]
    white: Literal[107]


class Sat(TypedDict):
    red: Literal[91]
    green: Literal[92]
    yellow: Literal[93]
    blue: Literal[94]
    purple: Literal[95]
    turquoise: Literal[96]
    white: Literal[97]
    bg: SatBG


class BG(TypedDict):
    grey: Literal[40]
    red: Literal[41]
    green: Literal[42]
    yellow: Literal[43]
    blue: Literal[44]
    purple: Literal[45]
    turquoise: Literal[46]
    white: Literal[47]


class ColorCodes(TypedDict):
    bold: Literal[1]
    grey: Literal[2]
    italic: Literal[3]
    ul: Literal[4]
    inverse: Literal[7]
    strike: Literal[9]
    reset: Reset
    doubleul: Literal[21]
    red: Literal[31]
    green: Literal[32]
    yellow: Literal[33]
    blue: Literal[34]
    purple: Literal[35]
    turquoise: Literal[36]
    white: Literal[37]
    bg: BG
    sat: Sat
    darkgrey: Literal[90]"""

COLOR_CODES = dict(
        bold=1,
        grey=2,
        italic=3,
        ul=4,
        inverse=7,
        strike=9,
        reset=dict(normal=0,
                   italic=23,
                   ul=24,
                   inverse=27,
                   strike=29,
                   ),
        doubleul=21,
        red=31,
        green=32,
        yellow=33,
        blue=34,
        purple=35,
        turquoise=36,
        white=37,
        bg=dict(grey=40,
                red=41,
                green=42,
                yellow=43,
                blue=44,
                purple=45,
                turquoise=46,
                white=47, ),
        sat=dict(red=91,
                 green=92,
                 yellow=93,
                 blue=94,
                 purple=95,
                 turquoise=96,
                 white=97,
                 bg=dict(grey=100,
                         red=101,
                         green=102,
                         yellow=103,
                         blue=104,
                         purple=105,
                         turquoise=106,
                         white=107)
                 ),
        lightgrey=90,
        
        )

options = dict(print=False)


def get_color_by_code(_code: int, _obj=None) -> Optional[str]:
    if _obj is None:
        _obj = COLOR_CODES
    for k, v in _obj.items():
        if not isinstance(v, dict):
            if v == _code:
                return k
        else:
            nested = get_color_by_code(_code, _obj[k])
            if nested is not None:
                return f'{k} {nested}'
    return None  # recursive stop cond


def get_code_by_color(_color: str, _obj=None) -> int:
    """Example:
    ::
        get_code_by_color('green')
        get_code_by_color('sat bg yellow')"""
    if _obj is None:
        _obj = COLOR_CODES
    if ' ' in _color:
        keys = _color.split()
        for key in keys:
            _obj = _obj[key]
        return _obj
    else:
        return _obj[_color]


def ascii_of_code(_code: int) -> str:
    """
        >>> print(ascii_of_code(97))
    """
    return f'\033[{_code}m'


def ascii_of_color(_color: str) -> str:
    return f'\033[{get_code_by_color(_color)}m'


def ascii_of_reset(_reset='normal') -> str:
    return f'\033[{COLOR_CODES["reset"][_reset]}m'


def reset_text(text: str, reset_color='normal'):
    return f'{text}{ascii_of_reset(reset_color)}'


def _termcolors():
    for i in range(1, 108):
        if i in [5, 6, 8, 30, 38, 39, 98, 99] or (10 <= i <= 20) or (22 <= i <= 29) or (48 <= i <= 89):
            continue
        
        print(color(f'{i}\thello\t', get_color_by_code(i)))


def set_option(**kwargs):
    if set(kwargs) > set(options):
        return print(yellow(f'at least one unknown key: {set(kwargs)}'))
    options.update(kwargs)


def yellow(text: any, reset_normal: bool = True):
    return color(text, 'yellow', reset='normal' if reset_normal is True else False)


def red(text: any, reset_normal: bool = True):
    # text = re.sub(r'(?<=\033)(.*)(\[\d{,3}m)', lambda m: m.groups()[0] + '[31m', text)
    return color(text, 'red', reset='normal' if reset_normal is True else False)


def green(text: any, reset_normal: bool = True):
    return color(text, 'green', reset='normal' if reset_normal is True else False)


def bold(text: any, reset_normal: bool = True):
    # bold: 1, white: 37
    return color(text, 'bold', 'white', reset='normal' if reset_normal is True else False)


def grey(text: any, reset_normal: bool = True):
    return color(text, 'grey', reset='normal' if reset_normal is True else False)


def lightgrey(text: any, reset_normal: bool = True):
    return color(text, 'lightgrey', reset='normal' if reset_normal is True else False)


def white(text: any):  # h4 in myman
    # sat white
    return color(text, 97)


def ul(text, reset_normal: bool = True):
    """
    If specified `True` (default), `reset_normal` passes `{ 'reset' : 'normal' }` which resets `normal` (everything).
    Otherwise, passes `{ 'reset' : 'ul' }` which resets only ul
    """
    return color(text, 'ul', reset='normal' if reset_normal is True else 'ul')


def italic(text, reset_normal: bool = True):
    """
    If specified `True` (default), `reset_normal` passes `{ 'reset' : 'normal' }` which resets `normal` (everything).
    Otherwise, passes `{ 'reset' : 'italic' }` which resets only italic
    """
    return color(text, 'italic', reset='normal' if reset_normal is True else 'italic')


def fix_internal_colors(m: re.Match):
    return ''.join(m.groups()[0:2]) + m.groups()[-1] + ''.join(m.groups()[2:5]) + m.groups()[0] + ''.join(m.groups()[-2:])


def color(text: any, *colors: Union[str, int], reset: Union[str, bool] = 'normal', debug=False):
    if debug:
        print(f'text: {text}', f'colors: {colors}', f'reset: {reset}')
    start = ''
    for clr in colors:
        if isinstance(clr, int):
            # * 31
            start_code = clr
        else:
            # * 'red'
            start_code = get_code_by_color(clr)
        start_ascii = ascii_of_code(start_code)
        start += start_ascii
        if debug:
            print(rf'code: {start_code}, askii: {repr(start_ascii)}, start: {start}')
    # this also works: '\033[01;97mHI'
    
    if reset is not False:
        # this means reset is a string.
        # otherwise, (when reset is False), not resetting at all
        reset_ascii = ascii_of_reset(reset)
        # colored = reset_text(f'{start}{text}', reset)
        colored = f'{start}{text}{reset_ascii}'
        if len(colors) == 1:
            # currently only works for single color
            # pass
            try:
                # in colored substrings, replace their reset start_code with current's start start_code
                # [RED]bla[PURPLE]plurp[/PURPLE]bzorg[/RED] → [RED]bla[PURPLE]plurp[RED]bzorg[/RED]
                # what's needed:
                # [RED]bla[PURPLE]plurp[/PURPLE]bzorg[/RED] → [RED]bla[/RED][PURPLE]plurp[/PURPLE][RED]bzorg[/RED]
                # text = re.sub(r'(?<=\033)(.*)(\[\d{,3}m)', lambda m: m.groups()[0] + f'[{start_code}m', text)
                regex = r'(\033\[\d{,3}m)(.*)(\033\[\d{,3}m)(.*)(\033\[\d{,3}m)(.*)(\033\[\d{,3}m)'
                colored = re.sub(regex, fix_internal_colors, colored)
            except TypeError as e:
                pass
        if debug:
            print(f'reset: {repr(reset)}, colored: {repr(colored)}')
    else:
        colored = f'{start}{text}'
    if options.get('print'):
        print(colored)
    return colored


if __name__ == '__main__':
    _termcolors()
