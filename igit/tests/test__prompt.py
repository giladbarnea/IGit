import pytest

from igit import prompt

import subprocess as sp
# from contextlib import redirect_stdout
# from prompt_toolkit import patch_stdout
# from prompt_toolkit.shortcuts import confirm
from igit.tests import common


@pytest.mark.skip
def _test__confirm():
    p = sp.Popen(f'input("hi\t")', shell=True, executable='python3.8')
    pass


# *** Deliberate Exceptions
def test__confirm():
    with common.assert_raises(ValueError, 'Confirmation cannot have free input'):
        prompt.confirm('foo', free_input=True)
    with common.assert_raises(ValueError, "'n' in kw_opts but was already in"):
        prompt.confirm('foo', n='confirm')


def test__action():
    with common.assert_raises(ValueError, 'At least one action is required'):
        prompt.action('foo')
    with common.assert_raises(ValueError, "Actions cannot include a 'yes' or 'no'"):
        prompt.action('foo', 'yes')
        prompt.action('foo', 'no')
        prompt.action('foo', 'YES')
        prompt.action('foo', 'NO')
        prompt.action('foo', no='no')
        prompt.action('foo', no='bar')


def test__choose():
    with common.assert_raises(ValueError, 'At least one option is required when using Choice'):
        prompt.choose('foo')
        prompt.confirm('foo', n='confirm')


def test__generic():
    with common.simulate_input('n'):
        key, item = prompt.generic('foo', no='what')
    assert item.is_yes_or_no is True


def test__LexicPrompt():
    with common.assert_raises(ValueError):
        prompt.LexicPrompt('hi', 'continue')
