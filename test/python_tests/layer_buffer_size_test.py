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

if 'sqlite' in mapnik.DatasourceCache.plugin_names():

    # the negative buffer on the layer should
    # override the postive map buffer leading
    # only one point to be rendered in the map
    def test_layer_buffer_size_1(setup):
        m = mapnik.Map(512, 512)
        assert m.buffer_size ==  0
        mapnik.load_map(m, '../data/good_maps/layer_buffer_size_reduction.xml')
        assert m.buffer_size ==  256
        assert m.layers[0].buffer_size ==  -150
        m.zoom_all()
        im = mapnik.Image(m.width, m.height)
        mapnik.render(m, im)
        actual = '/tmp/mapnik-layer-buffer-size.png'
        expected = 'images/support/mapnik-layer-buffer-size.png'
        im.save(actual, "png32")
        expected_im = mapnik.Image.open(expected)
        assert im.tostring('png32') == expected_im.tostring('png32'),'failed comparing actual (%s) and expected (%s)' % (actual,'tests/python_tests/' + expected)
