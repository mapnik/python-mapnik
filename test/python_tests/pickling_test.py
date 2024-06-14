import os
import pickle
import pytest
import mapnik
from .utilities import execution_path

@pytest.fixture(scope="module")
def setup():
    # All of the paths used are relative, if we run the tests
    # from another directory we need to chdir()
    os.chdir(execution_path('.'))
    yield


def test_color_pickle():
    c = mapnik.Color('blue')
    assert pickle.loads(pickle.dumps(c)) == c
    c = mapnik.Color(0, 64, 128)
    assert pickle.loads(pickle.dumps(c)) == c
    c = mapnik.Color(0, 64, 128, 192)
    assert pickle.loads(pickle.dumps(c)) == c


def test_envelope_pickle():
    e = mapnik.Box2d(100, 100, 200, 200)
    assert pickle.loads(pickle.dumps(e)) == e

def test_projection_pickle():
    p = mapnik.Projection("epsg:4326")
    assert pickle.loads(pickle.dumps(p)).definition() == p.definition()

def test_coord_pickle():
    c = mapnik.Coord(-1, 52)
    assert pickle.loads(pickle.dumps(c)) == c
