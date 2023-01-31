import mapnik

if 'sqlite' in mapnik.DatasourceCache.plugin_names():

    # the negative buffer on the layer should
    # override the postive map buffer leading
    # only one point to be rendered in the map
    def test_layer_buffer_size_1():
        m = mapnik.Map(512, 512)
        assert m.buffer_size ==  0
        mapnik.load_map(m, './test/data/good_maps/layer_buffer_size_reduction.xml')
        assert m.buffer_size ==  256
        assert m.layers[0].buffer_size ==  -150
        m.zoom_all()
        im = mapnik.Image(m.width, m.height)
        mapnik.render(m, im)
        actual = '/tmp/mapnik-layer-buffer-size.png'
        expected = './test/python_tests/images/support/mapnik-layer-buffer-size.png'
        im.save(actual, "png32")
        expected_im = mapnik.Image.open(expected)
        assert im.tostring('png32') == expected_im.tostring('png32'),'failed comparing actual (%s) and expected (%s)' % (actual,
                                                                'tests/python_tests/' + expected)
