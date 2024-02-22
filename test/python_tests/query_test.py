import os
import mapnik
import pytest
from .utilities import execution_path

@pytest.fixture(scope="module")
def setup():
    # All of the paths used are relative, if we run the tests
    # from another directory we need to chdir()
    os.chdir(execution_path('.'))
    yield

def test_query_init(setup):
    bbox = (-180, -90, 180, 90)
    query = mapnik.Query(mapnik.Box2d(*bbox))
    r = query.resolution
    assert r[0] == pytest.approx(1.0, abs=1e-7)
    assert r[1] == pytest.approx(1.0, abs=1e-7)
    # https://github.com/mapnik/mapnik/issues/1762
    assert query.property_names == []
    query.add_property_name('migurski')
    assert query.property_names == ['migurski']

# Converting *from* tuples *to* resolutions is not yet supported

def test_query_resolution():
    with pytest.raises(TypeError):
        bbox = (-180, -90, 180, 90)
        init_res = (4.5, 6.7)
        query = mapnik.Query(mapnik.Box2d(*bbox), init_res)
        r = query.resolution
        assert r[0] == pytest.approx(init_res[0], abs=1e-7)
        assert r[1] == pytest.approx(init_res[1], abs=1e-7)
