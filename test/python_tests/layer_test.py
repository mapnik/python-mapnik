import mapnik

# Map initialization

def test_layer_init():
    l = mapnik.Layer('test')
    assert l.name ==  'test'
    assert l.srs ==  'epsg:4326'
    assert l.envelope() ==  mapnik.Box2d()
    assert not l.clear_label_cache
    assert not l.cache_features
    assert l.visible(1)
    assert l.active
    assert l.datasource ==  None
    assert not l.queryable
    assert l.minimum_scale_denominator ==  0.0
    assert l.maximum_scale_denominator > 1e+6
    assert l.group_by ==  ""
    assert l.maximum_extent ==  None
    assert l.buffer_size ==  None
    assert len(l.styles) ==  0
