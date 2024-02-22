import os
import mapnik

def test_clearing_image_data():
    im = mapnik.Image(256, 256)
    # make sure it equals itself
    bytes = im.tostring()
    assert im.tostring() == bytes
    # set background, then clear
    im.fill(mapnik.Color('green'))
    assert not im.tostring() == bytes
    # clear image, should now equal original
    im.clear()
    assert im.tostring() == bytes

def make_map():
    ds = mapnik.MemoryDatasource()
    context = mapnik.Context()
    context.push('Name')
    pixel_key = 1
    f = mapnik.Feature(context, pixel_key)
    f['Name'] = str(pixel_key)
    f.geometry = mapnik.Geometry.from_wkt(
        'POLYGON ((0 0, 0 256, 256 256, 256 0, 0 0))')
    ds.add_feature(f)
    s = mapnik.Style()
    r = mapnik.Rule()
    symb = mapnik.PolygonSymbolizer()
    r.symbols.append(symb)
    s.rules.append(r)
    lyr = mapnik.Layer('Places')
    lyr.datasource = ds
    lyr.styles.append('places_labels')
    width, height = 256, 256
    m = mapnik.Map(width, height)
    m.append_style('places_labels', s)
    m.layers.append(lyr)
    m.zoom_all()
    return m

if mapnik.has_grid_renderer():
    def test_clearing_grid_data():
        g = mapnik.Grid(256, 256)
        utf = g.encode()
        # make sure it equals itself
        assert g.encode() == utf
        m = make_map()
        mapnik.render_layer(m, g, layer=0, fields=['__id__', 'Name'])
        assert g.encode() != utf
        # clear grid, should now match original
        g.clear()
        assert g.encode() == utf
