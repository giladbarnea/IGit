import os
from igit.ignore import Gitignore

os.chdir('/home/gilad')

gi = Gitignore()


# TODO: decide which functionality should be ExPath's בכלל
def test____contains__():
    assert '.oh-my-zsh/lib' in gi


def test__is_subpath_of_ignored():
    # test handling of rel / abs paths, and expanding ~/
    assert gi.is_subpath_of_ignored('.oh-my-zsh/lib') is True
    assert gi.is_subpath_of_ignored('.oh-my-zsh/lib/FOO') is True
    assert gi.is_subpath_of_ignored('/home/gilad/oh-my-zsh/lib') is True
    assert gi.is_subpath_of_ignored('/home/gilad/oh-my-zsh/lib/FOO') is True
    assert gi.is_subpath_of_ignored('~/oh-my-zsh/lib') is True
    assert gi.is_subpath_of_ignored('~/oh-my-zsh/lib/FOO') is True
