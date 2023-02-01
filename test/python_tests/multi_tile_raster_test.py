import mapnik

def test_multi_tile_policy():
    srs = 'epsg:4326'
    lyr = mapnik.Layer('raster')
    if 'raster' in mapnik.DatasourceCache.plugin_names():
        lyr.datasource = mapnik.Raster(
            file='./test/data/raster_tiles/${x}/${y}.tif',
            lox=-180,
            loy=-90,
            hix=180,
            hiy=90,
            multi=1,
            tile_size=256,
            x_width=2,
            y_width=2
        )
        lyr.srs = srs
        _map = mapnik.Map(256, 256, srs)
        style = mapnik.Style()
        rule = mapnik.Rule()
        sym = mapnik.RasterSymbolizer()
        rule.symbols.append(sym)
        style.rules.append(rule)
        _map.append_style('foo', style)
        lyr.styles.append('foo')
        _map.layers.append(lyr)
        _map.zoom_to_box(lyr.envelope())

        im = mapnik.Image(_map.width, _map.height)
        mapnik.render(_map, im)

        # test green chunk
        assert im.view(0, 64, 1, 1).tostring() ==  b'\x00\xff\x00\xff'
        assert im.view(127, 64, 1, 1).tostring() ==  b'\x00\xff\x00\xff'
        assert im.view(0, 127, 1, 1).tostring() ==  b'\x00\xff\x00\xff'
        assert im.view(127, 127, 1, 1).tostring() ==  b'\x00\xff\x00\xff'

        # test blue chunk
        assert im.view(128, 64, 1, 1).tostring() ==  b'\x00\x00\xff\xff'
        assert im.view(255, 64, 1, 1).tostring() ==  b'\x00\x00\xff\xff'
        assert im.view(128, 127, 1, 1).tostring() ==  b'\x00\x00\xff\xff'
        assert im.view(255, 127, 1, 1).tostring() ==  b'\x00\x00\xff\xff'

        # test red chunk
        assert im.view(0, 128, 1, 1).tostring() ==  b'\xff\x00\x00\xff'
        assert im.view(127, 128, 1, 1).tostring() ==  b'\xff\x00\x00\xff'
        assert im.view(0, 191, 1, 1).tostring() ==  b'\xff\x00\x00\xff'
        assert im.view(127, 191, 1, 1).tostring() ==  b'\xff\x00\x00\xff'

        # test magenta chunk
        assert im.view(128, 128, 1, 1).tostring() ==  b'\xff\x00\xff\xff'
        assert im.view(255, 128, 1, 1).tostring() ==  b'\xff\x00\xff\xff'
        assert im.view(128, 191, 1, 1).tostring() ==  b'\xff\x00\xff\xff'
        assert im.view(255, 191, 1, 1).tostring() ==  b'\xff\x00\xff\xff'
