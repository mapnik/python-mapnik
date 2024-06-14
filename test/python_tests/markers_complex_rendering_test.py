import pytest
import mapnik
import os
from .utilities import execution_path

@pytest.fixture(scope="module")
def setup():
    # All of the paths used are relative, if we run the tests
    # from another directory we need to chdir()
    os.chdir(execution_path('.'))
    yield

if 'csv' in mapnik.DatasourceCache.plugin_names():
    def test_marker_ellipse_render1(setup):
        m = mapnik.Map(256, 256)
        mapnik.load_map(m, '../data/good_maps/marker_ellipse_transform.xml')
        m.zoom_all()
        im = mapnik.Image(m.width, m.height)
        mapnik.render(m, im)
        actual = '/tmp/mapnik-marker-ellipse-render1.png'
        expected = './images/support/mapnik-marker-ellipse-render1.png'
        im.save(actual, 'png32')
        if os.environ.get('UPDATE'):
            im.save(expected, 'png32')
        expected_im = mapnik.Image.open(expected)
        assert im.to_string('png32') == expected_im.to_string('png32'), 'failed comparing actual (%s) and expected (%s)' % (actual, expected)

    def test_marker_ellipse_render2():
        m = mapnik.Map(256, 256)
        mapnik.load_map(m, '../data/good_maps/marker_ellipse_transform2.xml')
        m.zoom_all()
        im = mapnik.Image(m.width, m.height)
        mapnik.render(m, im)
        actual = '/tmp/mapnik-marker-ellipse-render2.png'
        expected = './images/support/mapnik-marker-ellipse-render2.png'
        im.save(actual, 'png32')
        if os.environ.get('UPDATE'):
            im.save(expected, 'png32')
        expected_im = mapnik.Image.open(expected)
        assert im.to_string('png32') == expected_im.to_string('png32'), 'failed comparing actual (%s) and expected (%s)' % (actual, expected)
