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

def test_datasource_template_is_working(setup):
    m = mapnik.Map(256, 256)
    mapnik.load_map(m, '../data/good_maps/datasource.xml')
    for layer in m.layers:
        layer_bbox = layer.envelope()
        bbox = None
        first = True
        for feature in layer.datasource:
            assert feature.envelope() == feature.geometry.envelope()
            assert layer_bbox.contains(feature.envelope())
            if first:
                first = False
                bbox = feature.envelope()
            else:
                bbox += feature.envelope()
        assert layer_bbox == bbox
