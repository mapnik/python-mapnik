import mapnik

def test_add_feature():
    md = mapnik.MemoryDatasource()
    assert md.num_features() ==  0
    context = mapnik.Context()
    context.push('foo')
    feature = mapnik.Feature(context, 1)
    feature['foo'] = 'bar'
    feature.geometry = mapnik.Geometry.from_wkt('POINT(2 3)')
    md.add_feature(feature)
    assert md.num_features() ==  1

    featureset = md.features_at_point(mapnik.Coord(2, 3))
    retrieved = []

    for feat in featureset:
        retrieved.append(feat)

    assert len(retrieved) ==  1
    f = retrieved[0]
    assert f['foo'] ==  'bar'

    featureset = md.features_at_point(mapnik.Coord(20, 30))
    retrieved = []
    for feat in featureset:
        retrieved.append(feat)
    assert len(retrieved) ==  0
