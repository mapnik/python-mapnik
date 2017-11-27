#!/usr/bin/env python

import os

from nose.tools import eq_

import mapnik

from .utilities import execution_path, get_unique_colors, run_all, datasources_available


def setup():
    # All of the paths used are relative, if we run the tests
    # from another directory we need to chdir()
    os.chdir(execution_path('.'))


def test_dataraster_coloring():
    srs = '+init=epsg:32630'
    lyr = mapnik.Layer('dataraster')
    if 'gdal' in mapnik.DatasourceCache.plugin_names():
        lyr.datasource = mapnik.Gdal(
            file='../data/raster/dataraster.tif',
            band=1,
        )
        lyr.srs = srs
        _map = mapnik.Map(256, 256, srs)
        style = mapnik.Style()
        rule = mapnik.Rule()
        sym = mapnik.RasterSymbolizer()
        # Assigning a colorizer to the RasterSymbolizer tells the later
        # that it should use it to colorize the raw data raster
        colorizer = mapnik.RasterColorizer(
            mapnik.COLORIZER_DISCRETE,
            mapnik.Color("transparent"))

        for value, color in [
            (0, "#0044cc"),
            (10, "#00cc00"),
            (20, "#ffff00"),
            (30, "#ff7f00"),
            (40, "#ff0000"),
            (50, "#ff007f"),
            (60, "#ff00ff"),
            (70, "#cc00cc"),
            (80, "#990099"),
            (90, "#660066"),
            (200, "transparent"),
        ]:
            colorizer.add_stop(value, mapnik.Color(color))
        sym.colorizer = colorizer
        rule.symbols.append(sym)
        style.rules.append(rule)
        _map.append_style('foo', style)
        lyr.styles.append('foo')
        _map.layers.append(lyr)
        _map.zoom_to_box(lyr.envelope())

        im = mapnik.Image(_map.width, _map.height)
        mapnik.render(_map, im)
        expected_file = './images/support/dataraster_coloring.png'
        actual_file = '/tmp/' + os.path.basename(expected_file)
        im.save(actual_file, 'png32')
        if not os.path.exists(expected_file) or os.environ.get('UPDATE'):
            im.save(expected_file, 'png32')
        actual = mapnik.Image.open(actual_file)
        expected = mapnik.Image.open(expected_file)
        eq_(actual.tostring('png32'),
            expected.tostring('png32'),
            'failed comparing actual (%s) and expected (%s)' % (actual_file,
                                                                expected_file))


def test_dataraster_query_point():
    srs = '+init=epsg:32630'
    lyr = mapnik.Layer('dataraster')
    if 'gdal' in mapnik.DatasourceCache.plugin_names():
        lyr.datasource = mapnik.Gdal(
            file='../data/raster/dataraster.tif',
            band=1,
        )
        lyr.srs = srs
        _map = mapnik.Map(256, 256, srs)
        _map.layers.append(lyr)

        x, y = 556113.0, 4381428.0  # center of extent of raster
        _map.zoom_all()
        features = list(_map.query_point(0, x, y))
        assert len(features) == 1
        feat = features[0]
        center = feat.envelope().center()
        assert center.x == x and center.y == y, center
        value = feat['value']
        assert value == 18.0, value

        # point inside map extent but outside raster extent
        current_box = _map.envelope()
        current_box.expand_to_include(-427417, 4477517)
        _map.zoom_to_box(current_box)
        features = _map.query_point(0, -427417, 4477517)
        assert len(list(features)) == 0

        # point inside raster extent with nodata
        features = _map.query_point(0, 126850, 4596050)
        assert len(list(features)) == 0


def test_load_save_map():
    m = mapnik.Map(256, 256)
    in_map = "../data/good_maps/raster_symbolizer.xml"
    if datasources_available(in_map):
        mapnik.load_map(m, in_map)
        out_map = mapnik.save_map_to_string(m)
        assert 'RasterSymbolizer' in out_map
        assert 'RasterColorizer' in out_map
        assert 'stop' in out_map


def test_raster_with_alpha_blends_correctly_with_background():
    WIDTH = 500
    HEIGHT = 500

    m = mapnik.Map(WIDTH, HEIGHT)
    WHITE = mapnik.Color(255, 255, 255)
    m.background = WHITE

    style = mapnik.Style()
    rule = mapnik.Rule()
    symbolizer = mapnik.RasterSymbolizer()
    symbolizer.scaling = mapnik.scaling_method.BILINEAR

    rule.symbols.append(symbolizer)
    style.rules.append(rule)

    m.append_style('raster_style', style)

    map_layer = mapnik.Layer('test_layer')
    filepath = '../data/raster/white-alpha.png'
    if 'gdal' in mapnik.DatasourceCache.plugin_names():
        map_layer.datasource = mapnik.Gdal(file=filepath)
        map_layer.styles.append('raster_style')
        m.layers.append(map_layer)

        m.zoom_all()

        mim = mapnik.Image(WIDTH, HEIGHT)

        mapnik.render(m, mim)
        mim.tostring()
        # All white is expected
        eq_(get_unique_colors(mim), ['rgba(254,254,254,255)'])


def test_raster_warping():
    lyrSrs = "+init=epsg:32630"
    mapSrs = '+proj=longlat +ellps=WGS84 +datum=WGS84 +no_defs'
    lyr = mapnik.Layer('dataraster', lyrSrs)
    if 'gdal' in mapnik.DatasourceCache.plugin_names():
        lyr.datasource = mapnik.Gdal(
            file='../data/raster/dataraster.tif',
            band=1,
        )
        sym = mapnik.RasterSymbolizer()
        sym.colorizer = mapnik.RasterColorizer(
            mapnik.COLORIZER_DISCRETE, mapnik.Color(255, 255, 0))
        rule = mapnik.Rule()
        rule.symbols.append(sym)
        style = mapnik.Style()
        style.rules.append(rule)
        _map = mapnik.Map(256, 256, mapSrs)
        _map.append_style('foo', style)
        lyr.styles.append('foo')
        _map.layers.append(lyr)
        map_proj = mapnik.Projection(mapSrs)
        layer_proj = mapnik.Projection(lyrSrs)
        prj_trans = mapnik.ProjTransform(map_proj,
                                         layer_proj)
        _map.zoom_to_box(prj_trans.backward(lyr.envelope()))

        im = mapnik.Image(_map.width, _map.height)
        mapnik.render(_map, im)
        expected_file = './images/support/raster_warping.png'
        actual_file = '/tmp/' + os.path.basename(expected_file)
        im.save(actual_file, 'png32')
        if not os.path.exists(expected_file) or os.environ.get('UPDATE'):
            im.save(expected_file, 'png32')
        actual = mapnik.Image.open(actual_file)
        expected = mapnik.Image.open(expected_file)
        eq_(actual.tostring('png32'),
            expected.tostring('png32'),
            'failed comparing actual (%s) and expected (%s)' % (actual_file,
                                                                expected_file))


def test_raster_warping_does_not_overclip_source():
    lyrSrs = "+init=epsg:32630"
    mapSrs = '+proj=longlat +ellps=WGS84 +datum=WGS84 +no_defs'
    lyr = mapnik.Layer('dataraster', lyrSrs)
    if 'gdal' in mapnik.DatasourceCache.plugin_names():
        lyr.datasource = mapnik.Gdal(
            file='../data/raster/dataraster.tif',
            band=1,
        )
        sym = mapnik.RasterSymbolizer()
        sym.colorizer = mapnik.RasterColorizer(
            mapnik.COLORIZER_DISCRETE, mapnik.Color(255, 255, 0))
        rule = mapnik.Rule()
        rule.symbols.append(sym)
        style = mapnik.Style()
        style.rules.append(rule)
        _map = mapnik.Map(256, 256, mapSrs)
        _map.background = mapnik.Color('white')
        _map.append_style('foo', style)
        lyr.styles.append('foo')
        _map.layers.append(lyr)
        _map.zoom_to_box(mapnik.Box2d(3, 42, 4, 43))

        im = mapnik.Image(_map.width, _map.height)
        mapnik.render(_map, im)
        expected_file = './images/support/raster_warping_does_not_overclip_source.png'
        actual_file = '/tmp/' + os.path.basename(expected_file)
        im.save(actual_file, 'png32')
        if not os.path.exists(expected_file) or os.environ.get('UPDATE'):
            im.save(expected_file, 'png32')
        actual = mapnik.Image.open(actual_file)
        expected = mapnik.Image.open(expected_file)
        eq_(actual.tostring('png32'),
            expected.tostring('png32'),
            'failed comparing actual (%s) and expected (%s)' % (actual_file,
                                                                expected_file))

if __name__ == "__main__":
    setup()
    exit(run_all(eval(x) for x in dir() if x.startswith("test_")))
