import mapnik
import pytest

# map has no layers
def test_map_query_throw1():
    with pytest.raises(IndexError):
        m = mapnik.Map(256, 256)
        m.zoom_to_box(mapnik.Box2d(-1, -1, 0, 0))
        m.query_point(0, 0, 0)

# only positive indexes
def test_map_query_throw2():
    with pytest.raises(IndexError):
        m = mapnik.Map(256, 256)
        m.query_point(-1, 0, 0)

# map has never been zoomed (nodata)
def test_map_query_throw3():
    with pytest.raises(RuntimeError):
        m = mapnik.Map(256, 256)
        m.query_point(0, 0, 0)

if 'shape' in mapnik.DatasourceCache.plugin_names():
    # map has never been zoomed (even with data)
    def test_map_query_throw4():
        with pytest.raises(RuntimeError):
            m = mapnik.Map(256, 256)
            mapnik.load_map(m, './test/data/good_maps/agg_poly_gamma_map.xml')
            m.query_point(0, 0, 0)

    # invalid coords in general (do not intersect)
    def test_map_query_throw5():
        with pytest.raises(RuntimeError):
            m = mapnik.Map(256, 256)
            mapnik.load_map(m, './test/data/good_maps/agg_poly_gamma_map.xml')
            m.zoom_all()
            m.query_point(0, 9999999999999999, 9999999999999999)

    def test_map_query_works1():
        m = mapnik.Map(256, 256)
        mapnik.load_map(m, './test/data/good_maps/wgs842merc_reprojection.xml')
        merc_bounds = mapnik.Box2d(-20037508.34, -
                                   20037508.34, 20037508.34, 20037508.34)
        m.maximum_extent = merc_bounds
        m.zoom_all()
        # somewhere in kansas
        fs = m.query_point(0, -11012435.5376, 4599674.6134)
        feat = fs.next()
        assert feat.attributes['NAME_FORMA'] ==  u'United States of America'

    def test_map_query_works2():
        m = mapnik.Map(256, 256)
        mapnik.load_map(m, './test/data/good_maps/merc2wgs84_reprojection.xml')
        wgs84_bounds = mapnik.Box2d(-179.999999975, -
                                    85.0511287776, 179.999999975, 85.0511287776)
        m.maximum_extent = wgs84_bounds
        # caution - will go square due to evil aspect_fix_mode backhandedness
        m.zoom_all()
        # mapnik.render_to_file(m,'works2.png')
        # validate that aspect_fix_mode modified the bbox reasonably
        e = m.envelope()
        assert e.minx == pytest.approx(-179.999999975, abs=1e-7)
        assert e.miny == pytest.approx(-167.951396161, abs=1e-7)
        assert e.maxx == pytest.approx(179.999999975, abs=1e-7)
        assert e.maxy == pytest.approx(192.048603789, abs=1e-7)
        fs = m.query_point(0, -98.9264, 38.1432)  # somewhere in kansas
        feat = fs.next()
        assert feat.attributes['NAME'] ==  u'United States'

    def test_map_query_in_pixels_works1():
        m = mapnik.Map(256, 256)
        mapnik.load_map(m, './test/data/good_maps/wgs842merc_reprojection.xml')
        merc_bounds = mapnik.Box2d(-20037508.34, -
                                   20037508.34, 20037508.34, 20037508.34)
        m.maximum_extent = merc_bounds
        m.zoom_all()
        fs = m.query_map_point(0, 55, 100)  # somewhere in middle of us
        feat = fs.next()
        assert feat.attributes['NAME_FORMA'] ==  u'United States of America'

    def test_map_query_in_pixels_works2():
        m = mapnik.Map(256, 256)
        mapnik.load_map(m, './test/data/good_maps/merc2wgs84_reprojection.xml')
        wgs84_bounds = mapnik.Box2d(-179.999999975, -
                                    85.0511287776, 179.999999975, 85.0511287776)
        m.maximum_extent = wgs84_bounds
        # caution - will go square due to evil aspect_fix_mode backhandedness
        m.zoom_all()
        # validate that aspect_fix_mode modified the bbox reasonably
        e = m.envelope()
        assert e.minx == pytest.approx(-179.999999975, abs=1e-7)
        assert e.miny == pytest.approx(-167.951396161, abs=1e-7)
        assert e.maxx == pytest.approx(179.999999975, abs=1e-7)
        assert e.maxy == pytest.approx(192.048603789, abs=1e-7)
        fs = m.query_map_point(0, 55, 100)  # somewhere in Canada
        feat = fs.next()
        assert feat.attributes['NAME'] ==  u'Canada'
