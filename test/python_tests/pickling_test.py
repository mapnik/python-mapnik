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


def test_parameters_pickle():
    params = mapnik.Parameters()
    params.append(mapnik.Parameter('oh', str('yeah')))

    params2 = pickle.loads(pickle.dumps(params, pickle.HIGHEST_PROTOCOL))

    assert params[0][0] == params2[0][0]
    assert params[0][1] == params2[0][1]
