import pickle
from pathlib import Path
from igit.util import search


def test__pyano0_2_0():
    with open(Path(__file__).parent / 'search_dirs.pickle', mode='rb') as pickled:
        dirs = pickle.load(pickled)
    res = search.fuzzy('pyano0-2.0', dirs)
    print(res)
    assert res.best()[0] == './pyano-2.0'
