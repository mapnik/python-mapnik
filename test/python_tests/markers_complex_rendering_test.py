# coding=utf8
import os

from nose.tools import eq_
from nose.plugins.skip import SkipTest

import mapnik

from .utilities import execution_path, run_all


def setup():
    # All of the paths used are relative, if we run the tests
    # from another directory we need to chdir()
    os.chdir(execution_path('.'))

if 'csv' in mapnik.DatasourceCache.plugin_names():
    def test_marker_ellipse_render1():
        if not os.path.exists('../data/good_maps/marker_ellipse_transform.xml'):
            raise SkipTest

        m = mapnik.Map(256, 256)
        mapnik.load_map(m, '../data/good_maps/marker_ellipse_transform.xml')
        m.zoom_all()
        im = mapnik.Image(m.width, m.height)
        mapnik.render(m, im)
        actual = '/tmp/mapnik-marker-ellipse-render1.png'
        expected = 'images/support/mapnik-marker-ellipse-render1.png'
        im.save(actual, 'png32')
        if os.environ.get('UPDATE'):
            im.save(expected, 'png32')
        expected_im = mapnik.Image.open(expected)
        eq_(im.tostring('png32'),
            expected_im.tostring('png32'),
            'failed comparing actual (%s) and expected (%s)' % (actual,
                                                                'test/python_tests/' + expected))

    def test_marker_ellipse_render2():
        if not os.path.exists('../data/good_maps/marker_ellipse_transform2.xml'):
            raise SkipTest

        m = mapnik.Map(256, 256)
        mapnik.load_map(m, '../data/good_maps/marker_ellipse_transform2.xml')
        m.zoom_all()
        im = mapnik.Image(m.width, m.height)
        mapnik.render(m, im)
        actual = '/tmp/mapnik-marker-ellipse-render2.png'
        expected = 'images/support/mapnik-marker-ellipse-render2.png'
        im.save(actual, 'png32')
        if os.environ.get('UPDATE'):
            im.save(expected, 'png32')
        expected_im = mapnik.Image.open(expected)
        eq_(im.tostring('png32'),
            expected_im.tostring('png32'),
            'failed comparing actual (%s) and expected (%s)' % (actual,
                                                                'test/python_tests/' + expected))

if __name__ == "__main__":
    setup()
    exit(run_all(eval(x) for x in dir() if x.startswith("test_")))
