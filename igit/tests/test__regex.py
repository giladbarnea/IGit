import re

import pytest

from igit.util.cache import memoize
from igit.util.regex import (strip_trailing_path_wildcards,
                             strip_leading_path_wildcards,
                             strip_surrounding_path_wildcards,
                             endswith_regex,
                             is_only_regex,
                             has_regex,
                             has_glob,
                             has_adv_regex,
                             make_word_separators_optional,
                             GLOB_CHAR,
                             ADV_REGEX_CHAR,
                             REGEX_CHAR)
from igit.tests import common
from igit.tests.common import mixed_suffixes, split_iter_by, get_permutations, nonregex, has_regex_and_nonregex, iter_permutations
from itertools import chain


@memoize
def get_end_with_re_split():
    print('generating end / dont end with re...')
    _end_with_re, _dont_end_with_re = split_iter_by(mixed_suffixes(),
                                                    lambda x: x[-1] in REGEX_CHAR)
    print('done generating end / dont end with re')
    return _end_with_re, _dont_end_with_re


@memoize
def end_with_re():
    return get_end_with_re_split()[0]


@memoize
def dont_end_with_re():
    return get_end_with_re_split()[1]


# ** has_regex
def test__has_regex__nonregex_char():
    for c in nonregex:
        assert has_regex(c) is False


def test__has_regex__regex_char():
    for c in REGEX_CHAR:
        assert has_regex(c) is True


def test__has_regex__regex_string():
    regex_strings = get_permutations(REGEX_CHAR + '.', 3)
    for stryng in regex_strings:
        assert has_regex(stryng) is True


def test__has_regex__nonregex_string():
    nonregex_strings = get_permutations(nonregex + '.', 3)
    for stryng in nonregex_strings:
        assert has_regex(stryng) is False


def test__has_regex__mixed_string():
    mixed_strings = iter_permutations(nonregex + '.', 3, has_regex_and_nonregex)
    for stryng in mixed_strings:
        assert has_regex(stryng) is True


# ** has_adv_regex
def test__has_adv_regex__nonregex_char():
    for c in nonregex:
        assert has_adv_regex(c) is False


def test__has_adv_regex__glob_char():
    for c in GLOB_CHAR:
        assert has_adv_regex(c) is False


def test__has_adv_regex__adv_regex_char():
    for c in ADV_REGEX_CHAR:
        assert has_adv_regex(c) is True


def test__has_adv_regex__glob__manual():
    globs = [
        "*.py",
        
        "*/**",
        "f*le.py",
        "f*le?.py",
        "f*le?.p*y",
        
        "file*",
        "*file",
        "*fi?le",
        "*fi?le*",
        
        ]
    for glob in globs:
        assert has_adv_regex(glob) is False


def test__has_adv_regex__truth_cases__manual():
    adv_regexes = [
        ".*steam.*",
        "*.**",
        "f*le?.*",
        ".*fi?le*",
        "[^.]*.ts"
        ]
    
    for regex in adv_regexes:
        assert has_adv_regex(regex) is True


def test__has_adv_regex__nonregex_string():
    nonregex_strings = get_permutations(nonregex + '.', 3)
    for stryng in nonregex_strings:
        assert has_adv_regex(stryng) is False


def test__has_adv_regex__mixed_string():
    mixed_strings = iter_permutations(nonregex + '.', 3, has_regex_and_nonregex)
    for stryng in mixed_strings:
        assert has_adv_regex(stryng) is True


# ** has_glob
def test__is_glob__nonregex_char():
    for c in nonregex:
        assert has_glob(c) is False


def test__is_glob__glob_char():
    for c in GLOB_CHAR:
        assert has_glob(c) is True


def test__is_glob__adv_regex_char():
    for c in ADV_REGEX_CHAR:
        assert has_glob(c) is False


def test__is_glob__glob__manual():
    globs = [
        "*.py",
        
        "*/**",
        "f*le.py",
        "f*le?.py",
        "f*le?.p*y",
        
        "file*",
        "*file",
        "*fi?le",
        "*fi?le*",
        
        ]
    for glob in globs:
        assert has_glob(glob) is True


def test__is_glob__truth_cases__manual():
    globes = [
        ".*steam.*",
        "*.**",
        "f*le?.*",
        ".*fi?le*",
        "[^.]*.ts"
        ]
    
    for regex in globes:
        assert has_glob(regex) is False


def test__is_glob__nonregex_string():
    nonregex_strings = get_permutations(nonregex + '.', 3)
    for stryng in nonregex_strings:
        assert has_glob(stryng) is False


# ** is_only_regex
def test__is_only_regex__nonregex_char():
    for c in nonregex:
        assert is_only_regex(c) is False


def test__is_only_regex__regex_char():
    for c in REGEX_CHAR:
        actual = is_only_regex(c)
        assert actual is True


def test__is_only_regex__regex_string():
    regex_strings = get_permutations(REGEX_CHAR + '.', 3)
    for stryng in regex_strings:
        assert is_only_regex(stryng) is True


def test__is_only_regex__nonregex_string():
    nonregex_strings = get_permutations(nonregex + '.', 3)
    for stryng in nonregex_strings:
        assert is_only_regex(stryng) is False


def test__is_only_regex__mixed_string():
    assert is_only_regex(nonregex + '.') is False
    mixed_strings = iter_permutations(nonregex + '.', 3, has_regex_and_nonregex)
    for stryng in mixed_strings:
        assert is_only_regex(stryng) is False


def test__is_only_regex__truth_cases__manual():
    vals = ('.?', '\\.?')
    for val in vals:
        actual = is_only_regex(val)
        assert actual is True


def test__is_only_regex__false_cases__manual():
    vals = ('[',)
    for val in vals:
        actual = is_only_regex(val)
        assert actual is False


# ** endswith_regex
def test__endswith_regex__false_cases():
    for x in dont_end_with_re():
        assert endswith_regex(x) is False


def test__endswith_regex__true_cases():
    for x in end_with_re():
        assert endswith_regex(x) is True


def test__make_word_separators_optional():
    expectations = {
        'hi_there':  r'hi[-_. ]there',
        'hi there':  r'hi[-_. ]there',
        'hi-there':  r'hi[-_. ]there',
        'hi.there':  r'hi[-_. ]there',
        'hi.the_re': r'hi[-_. ]the[-_. ]re',
        }
    for val, expected in expectations.items():
        actual = make_word_separators_optional(val)
        assert actual == expected


def test__strip_trailing_path_wildcards():
    name = 'env'
    assert strip_trailing_path_wildcards(name) == name
    for reg in common.path_regexes():
        # strip all trailing
        val = f'{name}{reg}'
        actual = strip_trailing_path_wildcards(val)
        assert actual == name
    
    for reg in common.path_regexes():
        # dont strip any leading
        expected = f'{reg}{name}'
        actual = strip_trailing_path_wildcards(expected)
        assert actual == expected
    
    for reg in common.path_regexes():
        # strip only trailing
        val = f'{reg}{name}{reg}'
        expected = f'{reg}{name}'
        actual = strip_trailing_path_wildcards(val)
        assert actual == expected


def test__strip_trailing_path_wildcards__file__basename__with_suffix():
    name = 'py_venv.xml'
    actual = strip_trailing_path_wildcards(name)
    assert actual == name
    for reg in common.path_regexes():
        # strip all trailing
        val = f'{name}{reg}'
        actual = strip_trailing_path_wildcards(val)
        assert actual == name
    
    for reg in common.path_regexes():
        # dont strip any leading
        expected = f'{reg}{name}'
        actual = strip_trailing_path_wildcards(expected)
        assert actual == expected
    
    for reg in common.path_regexes():
        # strip only trailing
        val = f'{reg}{name}{reg}'
        expected = f'{reg}{name}'
        actual = strip_trailing_path_wildcards(val)
        assert actual == expected


def test__dont_strip_leading__nonpath_regex():
    names = ('^read', 'read[.]', 'read[./]*')
    for name in names:
        actual = strip_leading_path_wildcards(name)
        assert actual == name


def test__dont_strip_trailing__nonpath_regex():
    names = ('read$', 'read[.]*', 'read[./]*', 'read/?', 'reads+')
    for name in names:
        actual = strip_trailing_path_wildcards(name)
        assert actual == name


def test__dont_strip_trailing__nonregex():
    for nonreg in nonregex:
        name = f'foo{nonreg}'
        actual = strip_trailing_path_wildcards(name)
        assert actual == name


def test__dont_strip_leading__nonregex():
    for nonreg in nonregex:
        name = f'{nonreg}foo'
        actual = strip_leading_path_wildcards(name)
        assert actual == name


def test__dont_strip_leading__manual():
    vals = ('.git',)
    for val in vals:
        actual = strip_leading_path_wildcards(val)
        assert actual == val


def test__strip_leading_path_wildcards__dir():
    name = 'env_3-'
    assert strip_leading_path_wildcards(name) == name
    for reg in common.path_regexes():
        # strip all leading
        val = f'{reg}{name}'
        actual = strip_leading_path_wildcards(val)
        assert actual == name
    
    for reg in common.path_regexes():
        # dont strip any trailing
        expected = f'{name}{reg}'
        actual = strip_leading_path_wildcards(expected)
        assert actual == expected
    
    for reg in common.path_regexes():
        # strip only leading
        val = f'{reg}{name}{reg}'
        expected = f'{name}{reg}'
        actual = strip_leading_path_wildcards(val)
        assert actual == expected


def test__strip_leading_path_wildcards__file__basename():
    name = 'py_venv'
    assert strip_leading_path_wildcards(name) == name
    for reg in common.path_regexes():
        # strip all leading
        val = f'{reg}{name}'
        actual = strip_leading_path_wildcards(val)
        assert actual == name
    
    for reg in common.path_regexes():
        # dont strip any trailing
        expected = f'{name}{reg}'
        actual = strip_leading_path_wildcards(expected)
        assert actual == expected
    
    for reg in common.path_regexes():
        # strip only leading
        val = f'{reg}{name}{reg}'
        expected = f'{name}{reg}'
        actual = strip_leading_path_wildcards(val)
        assert actual == expected


def test__strip_leading_path_wildcards__file__basename__with_suffix():
    name = 'py_venv.xml'
    assert strip_leading_path_wildcards(name) == name
    for reg in common.path_regexes():
        # strip all leading
        val = f'{reg}{name}'
        actual = strip_leading_path_wildcards(val)
        assert actual == name
    
    for reg in common.path_regexes():
        # dont strip any trailing
        expected = f'{name}{reg}'
        actual = strip_leading_path_wildcards(expected)
        assert actual == expected
    
    for reg in common.path_regexes():
        # strip only leading
        val = f'{reg}{name}{reg}'
        expected = f'{name}{reg}'
        actual = strip_leading_path_wildcards(val)
        assert actual == expected


def test__strip_surrounding_path_wildcards():
    names = ('py_venv', 'env_3-', 'env')
    for name in names:
        assert strip_surrounding_path_wildcards(name) == name
        for reg in common.path_regexes():
            val = f'{reg}{name}{reg}'
            actual = strip_surrounding_path_wildcards(val)
            assert actual == name
