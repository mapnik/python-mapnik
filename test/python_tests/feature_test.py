from binascii import unhexlify
import mapnik
import pytest

def test_default_constructor():
    f = mapnik.Feature(mapnik.Context(), 1)
    assert f is not None


def test_feature_geo_interface():
    ctx = mapnik.Context()
    feat = mapnik.Feature(ctx, 1)
    feat.geometry = mapnik.Geometry.from_wkt('Point (0 0)')
    assert feat.__geo_interface__['geometry'] == {u'type': u'Point', u'coordinates': [0, 0]}


def test_python_extended_constructor():
    context = mapnik.Context()
    context.push('foo')
    context.push('foo')
    f = mapnik.Feature(context, 1)
    wkt = 'POLYGON ((35 10, 10 20, 15 40, 45 45, 35 10),(20 30, 35 35, 30 20, 20 30))'
    f.geometry = mapnik.Geometry.from_wkt(wkt)
    f['foo'] = 'bar'
    assert f['foo'] ==  'bar'
    assert f.envelope(), mapnik.Box2d(10.0, 10.0, 45.0 ==  45.0)
    # reset
    f['foo'] = u"avión"
    assert f['foo'] ==  u"avión"
    f['foo'] = 1.4
    assert f['foo'] ==  1.4
    f['foo'] = True
    assert f['foo'] ==  True


def test_add_geom_wkb():
    # POLYGON ((30 10, 10 20, 20 40, 40 40, 30 10))
    wkb = '010300000001000000050000000000000000003e4000000000000024400000000000002440000000000000344000000000000034400000000000004440000000000000444000000000000044400000000000003e400000000000002440'
    geometry = mapnik.Geometry.from_wkb(unhexlify(wkb))
    if hasattr(geometry, 'is_valid'):
        # Those are only available when python-mapnik has been built with
        # boost >= 1.56.
        assert geometry.is_valid() ==  True
        assert geometry.is_simple() ==  True
    assert geometry.envelope(), mapnik.Box2d(10.0, 10.0, 40.0 ==  40.0)
    geometry.correct()
    if hasattr(geometry, 'is_valid'):
        # valid after calling correct
        assert geometry.is_valid() ==  True


def test_feature_expression_evaluation():
    context = mapnik.Context()
    context.push('name')
    f = mapnik.Feature(context, 1)
    f['name'] = 'a'
    assert f['name'] ==  u'a'
    expr = mapnik.Expression("[name]='a'")
    evaluated = expr.evaluate(f)
    assert evaluated ==  True
    num_attributes = len(f)
    assert num_attributes ==  1
    assert f.id() ==  1

# https://github.com/mapnik/mapnik/issues/933


def test_feature_expression_evaluation_missing_attr():
    context = mapnik.Context()
    context.push('name')
    f = mapnik.Feature(context, 1)
    f['name'] = u'a'
    assert f['name'] ==  u'a'
    expr = mapnik.Expression("[fielddoesnotexist]='a'")
    assert not 'fielddoesnotexist' in f
    try:
        expr.evaluate(f)
    except Exception as e:
        assert "Key does not exist" in str(e) ==  True
    num_attributes = len(f)
    assert num_attributes ==  1
    assert f.id() ==  1

# https://github.com/mapnik/mapnik/issues/934


def test_feature_expression_evaluation_attr_with_spaces():
    context = mapnik.Context()
    context.push('name with space')
    f = mapnik.Feature(context, 1)
    f['name with space'] = u'a'
    assert f['name with space'] ==  u'a'
    expr = mapnik.Expression("[name with space]='a'")
    assert str(expr) ==  "([name with space]='a')"
    assert expr.evaluate(f) ==  True

# https://github.com/mapnik/mapnik/issues/2390

def test_feature_from_geojson():
    with pytest.raises(RuntimeError):
        ctx = mapnik.Context()
        inline_string = """
        {
        "geometry" : {
        "coordinates" : [ 0,0 ]
        "type" : "Point"
        },
        "type" : "Feature",
        "properties" : {
        "this":"that"
        "known":"nope because missing comma"
        }
        }
        """
        mapnik.Feature.from_geojson(inline_string, ctx)
