import os
import mapnik
import pytest
from .utilities import execution_path, images_almost_equal

@pytest.fixture(scope="module")
def setup():
    # All of the paths used are relative, if we run the tests
    # from another directory we need to chdir()
    os.chdir(execution_path('.'))
    yield

if 'shape' in mapnik.DatasourceCache.plugin_names():

    def test_zoom_all_will_fail(setup):
        m = mapnik.Map(512, 512)
        mapnik.load_map(m, '../data/good_maps/wgs842merc_reprojection.xml')
        m.zoom_all()

    def test_zoom_all_will_work_with_max_extent():
        m = mapnik.Map(512, 512)
        mapnik.load_map(m, '../data/good_maps/wgs842merc_reprojection.xml')
        merc_bounds = mapnik.Box2d(-20037508.34, -20037508.34, 20037508.34, 20037508.34)
        m.maximum_extent = merc_bounds
        m.zoom_all()
        # note - fixAspectRatio is being called, then re-clipping to maxextent
        # which makes this hard to predict
        #assert m.envelope() == merc_bounds

        m = mapnik.Map(512,512)
        mapnik.load_map(m,'../data/good_maps/wgs842merc_reprojection.xml')
        merc_bounds = mapnik.Box2d(-20037508.34,-20037508.34,20037508.34,20037508.34)
        m.zoom_to_box(merc_bounds)
        assert m.envelope() == merc_bounds

    def test_visual_zoom_all_rendering1():
        m = mapnik.Map(512, 512)
        mapnik.load_map(m, '../data/good_maps/wgs842merc_reprojection.xml')
        merc_bounds = mapnik.Box2d(-20037508.34, -20037508.34, 20037508.34, 20037508.34)
        m.maximum_extent = merc_bounds
        m.zoom_all()
        im = mapnik.Image(512, 512)
        mapnik.render(m, im)
        actual = '/tmp/mapnik-wgs842merc-reprojection-render.png'
        expected = 'images/support/mapnik-wgs842merc-reprojection-render.png'
        im.save(actual, 'png32')
        expected_im = mapnik.Image.open(expected)
        images_almost_equal(im, expected_im)

    def test_visual_zoom_all_rendering2():
        m = mapnik.Map(512, 512)
        mapnik.load_map(m, '../data/good_maps/merc2wgs84_reprojection.xml')
        m.zoom_all()
        im = mapnik.Image(512, 512)
        mapnik.render(m, im)
        expected_im = mapnik.Image.open('images/support/mapnik-merc2wgs84-reprojection-render.png')
        images_almost_equal(im, expected_im)

    # maximum-extent read from map.xml
    def test_visual_zoom_all_rendering3():
        m = mapnik.Map(512, 512)
        mapnik.load_map(m, '../data/good_maps/bounds_clipping.xml')
        m.zoom_all()
        im = mapnik.Image(512, 512)
        mapnik.render(m, im)
        expected = 'images/support/mapnik-merc2merc-reprojection-render1.png'
        expected_im = mapnik.Image.open(expected)
        images_almost_equal(im, expected_im)

    # no maximum-extent
    def test_visual_zoom_all_rendering4():
        m = mapnik.Map(512, 512)
        mapnik.load_map(m, '../data/good_maps/bounds_clipping.xml')
        m.maximum_extent = None
        m.zoom_all()
        im = mapnik.Image(512, 512)
        mapnik.render(m, im)
        expected = 'images/support/mapnik-merc2merc-reprojection-render2.png'
        expected_im = mapnik.Image.open(expected)
        images_almost_equal(im, expected_im)
