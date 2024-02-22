import os
import mapnik
import pytest
from .utilities import execution_path

@pytest.fixture
def setup():
    # All of the paths used are relative, if we run the tests
    # from another directory we need to chdir()
    os.chdir(execution_path('.'))
    yield

if 'shape' in mapnik.DatasourceCache.plugin_names():
    def test_query_tolerance(setup):
        srs = 'epsg:4326'
        lyr = mapnik.Layer('test')
        ds = mapnik.Shapefile(file='../data/shp/arrows.shp')
        lyr.datasource = ds
        lyr.srs = srs
        _width = 256
        _map = mapnik.Map(_width, _width, srs)
        _map.layers.append(lyr)
        # zoom determines tolerance
        _map.zoom_all()
        _map_env = _map.envelope()
        tol = (_map_env.maxx - _map_env.minx) / _width * 3
        # 0.046875 for arrows.shp and zoom_all
        assert tol == 0.046875
        # check point really exists
        x, y = 2.0, 4.0
        features = _map.query_point(0, x, y)
        assert len(list(features)) == 1
        # check inside tolerance limit
        x = 2.0 + tol * 0.9
        features = _map.query_point(0, x, y)
        assert len(list(features)) == 1
        # check outside tolerance limit
        x = 2.0 + tol * 1.1
        features = _map.query_point(0, x, y)
        assert len(list(features)) == 0
