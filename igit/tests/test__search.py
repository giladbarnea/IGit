import pickle
from pathlib import Path
from igit import search


def test__pyano0_2_0():
    with open(Path(__file__).parent / 'pyano0-2.0-find-output.pickle', mode='rb') as pickled:
        dirs = pickle.load(pickled)
    res = search.fuzzy('pyano0-2.0', dirs)
    print(res)
    assert res.best()[0] == './pyano-2.0'


def test__Video_ob():
    with open(Path(__file__).parent / 'Video-ob-find-output.pickle', mode='rb') as pickled:
        # alternatively, from ~/: collection=!find . -type d ! -path "*/.git/*" ! -path "*/.idea/*" ! -path "*/.vscode/*" ! -path "*/env/*" ! -path "*/node_modules/*"
        dirs = pickle.load(pickled)
    res = search.nearest('Video/ob', dirs)
    print(res)
    assert res.best()[0] == './Videos/obs'
