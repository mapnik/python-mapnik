import mapnik

def test_datasource_template_is_working():
    m = mapnik.Map(256, 256)
    mapnik.load_map(m, './test/data/good_maps/datasource.xml')
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
