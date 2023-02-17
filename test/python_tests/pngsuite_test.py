import os
import mapnik
import pytest
from .utilities import execution_path

datadir = '../data/pngsuite'

@pytest.fixture(scope="module")
def setup():
    # All of the paths used are relative, if we run the tests
    # from another directory we need to chdir()
    os.chdir(execution_path('.'))
    yield

def assert_broken_file(fname):
    with pytest.raises(RuntimeError):
        mapnik.Image.open(fname)


def assert_good_file(fname):
    assert mapnik.Image.open(fname)


def get_pngs(good):
    files = [x for x in os.listdir(datadir) if x.endswith('.png')]
    return [os.path.join(datadir, x)
            for x in files if good != x.startswith('x')]


def test_good_pngs(setup):
    for x in get_pngs(True):
        assert_good_file, x


def test_broken_pngs():
    for x in get_pngs(False):
        assert_broken_file, x
