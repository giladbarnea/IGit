from pathlib import Path

import pytest
from igit.tests.common import get_permutations_in_size_range, has_letters_and_punc, path_regexes, mixed_suffixes
from igit.util.path import has_file_suffix, ExPath

# ** has_file_suffix
from igit.util.regex import REGEX_CHAR


def test__has_file_suffix__with_suffix__startswith_path_reg():
    # e.g. '.*/py_venv.xml'. should return has suffix (True)
    with_suffix = 'py_venv.xml'
    assert has_file_suffix(with_suffix) is True
    for reg in path_regexes():
        val = f'{reg}{with_suffix}'
        actual = has_file_suffix(val)
        assert actual is True


def test__has_file_suffix__with_suffix__no_stem__startswith_path_reg():
    # e.g. '*.xml'. should return has suffix (True)
    with_suffix = '*.xml'
    actual = has_file_suffix(with_suffix)
    assert actual is True
    for reg in path_regexes():
        val = f'{reg}{with_suffix}'
        actual = has_file_suffix(val)
        assert actual is True


def test__has_file_suffix__with_mixed_regex_suffix():
    # e.g. 'py_venv.xm?l'. should return has suffix (True)
    for suffix in mixed_suffixes():
        with_suffix = f'py_venv.{suffix}'
        actual = has_file_suffix(with_suffix)
        assert actual is True


def test__has_file_suffix__everything_mixed_with_regex():
    # e.g. '.*/py_v[en]*v.xm?l'. should return has suffix (True)
    assert has_file_suffix('.*/py_v[en]*v.xm?l') is True
    mixed_stems = get_permutations_in_size_range(f'{REGEX_CHAR}.py_venv-1257', slice(5), has_letters_and_punc)
    for stem in mixed_stems:
        for suffix in mixed_suffixes():
            name = f'{stem}.{suffix}'
            actual = has_file_suffix(name)
            assert actual is True
            for reg in path_regexes():
                val = f'{reg}{name}'
                actual = has_file_suffix(val)
                assert actual is True


def test__has_file_suffix__no_suffix__startswith_path_reg():
    # e.g. '.*/py_venv'. should return no suffix (False)
    no_suffix = 'py_venv'
    assert has_file_suffix(no_suffix) is False
    for reg in path_regexes():
        val = f'{reg}{no_suffix}'
        actual = has_file_suffix(val)
        assert actual is False


def test__has_file_suffix__no_suffix__endswith_path_reg():
    # e.g. 'py_venv.*/'. should return no suffix (False)
    no_suffix = 'py_venv'
    assert has_file_suffix(no_suffix) is False
    for reg in path_regexes():
        val = f'{no_suffix}{reg}'
        actual = has_file_suffix(val)
        assert actual is False


def test__has_file_suffix__no_suffix__surrounded_by_path_reg():
    # e.g. '.*/py_venv.*/'. should return no suffix (False)
    no_suffix = 'py_venv'
    assert has_file_suffix(no_suffix) is False
    for reg in path_regexes():
        for morereg in path_regexes():
            val = f'{morereg}{no_suffix}{reg}'
            actual = has_file_suffix(val)
            assert actual is False


# ** ExPath
def test__ExPath__parent_of__sanity():
    home = ExPath('/home')
    gilad = ExPath('/home/gilad')
    assert home.parent_of(gilad)
    assert home.parent_of('/home/gilad')
    assert home.parent_of(Path('/home/gilad'))


def test__ExPath__subpath_of__sanity():
    home = ExPath('/home')
    gilad = ExPath('/home/gilad')
    assert gilad.subpath_of(home)
    assert gilad.subpath_of('/home/')
    assert gilad.subpath_of(Path('/home'))


def test__ExPath__parent_of__wildcard():
    home = ExPath('/home/*')
    gilad = ExPath('/home/gilad')
    home_parent_of_gilad = home.parent_of(gilad)
    assert home_parent_of_gilad is True
    home_parent_of_home_gilad = home.parent_of('/home/gilad')
    assert home_parent_of_home_gilad
    home_parent_of_Path_home_gilad = home.parent_of(Path('/home/gilad'))
    assert home_parent_of_Path_home_gilad


def test__ExPath__subpath_of__wildcard():
    home = ExPath('/home/*')
    gilad = ExPath('/home/gilad')
    assert gilad.subpath_of(home)
    assert gilad.subpath_of('/home/')
    assert gilad.subpath_of(Path('/home'))
