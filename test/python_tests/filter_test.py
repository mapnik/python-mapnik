import mapnik
import pytest

if hasattr(mapnik, 'Expression'):
    mapnik.Filter = mapnik.Expression

map_ = '''<Map>
    <Style name="s">
        <Rule>
            <Filter><![CDATA[(([region]>=0) and ([region]<=50))]]></Filter>
        </Rule>
        <Rule>
            <Filter><![CDATA[([region]>=0) and ([region]<=50)]]></Filter>
        </Rule>
        <Rule>
            <Filter>

            <![CDATA[

            ([region] >= 0)

            and

            ([region] <= 50)
            ]]>

            </Filter>
        </Rule>
        <Rule>
            <Filter>([region]&gt;=0) and ([region]&lt;=50)</Filter>
        </Rule>
        <Rule>
            <Filter>
            ([region] &gt;= 0)
             and
            ([region] &lt;= 50)
            </Filter>
        </Rule>

    </Style>
    <Style name="s2" filter-mode="first">
        <Rule>
        </Rule>
        <Rule>
        </Rule>
    </Style>
</Map>'''


def test_filter_init():
    m = mapnik.Map(1, 1)
    mapnik.load_map_from_string(m, map_)
    filters = []
    filters.append(mapnik.Filter("([region]>=0) and ([region]<=50)"))
    filters.append(mapnik.Filter("(([region]>=0) and ([region]<=50))"))
    filters.append(mapnik.Filter("((([region]>=0) and ([region]<=50)))"))
    filters.append(mapnik.Filter('((([region]>=0) and ([region]<=50)))'))
    filters.append(mapnik.Filter('''((([region]>=0) and ([region]<=50)))'''))
    filters.append(mapnik.Filter('''
    ((([region]>=0)
    and
    ([region]<=50)))
    '''))
    filters.append(mapnik.Filter('''
    ([region]>=0)
    and
    ([region]<=50)
    '''))
    filters.append(mapnik.Filter('''
    ([region]
    >=
    0)
    and
    ([region]
    <=
    50)
    '''))

    s = m.find_style('s')

    for r in s.rules:
        filters.append(r.filter)

    first = filters[0]
    for f in filters:
        assert str(first) ==  str(f)

    s = m.find_style('s2')

    assert s.filter_mode ==  mapnik.filter_mode.FIRST


def test_geometry_type_eval():
    # clashing field called 'mapnik::geometry'
    context2 = mapnik.Context()
    context2.push('mapnik::geometry_type')
    f = mapnik.Feature(context2, 0)
    f["mapnik::geometry_type"] = 'sneaky'
    expr = mapnik.Expression("[mapnik::geometry_type]")
    assert expr.evaluate(f) ==  0

    expr = mapnik.Expression("[mapnik::geometry_type]")
    context = mapnik.Context()

    # no geometry
    f = mapnik.Feature(context, 0)
    assert expr.evaluate(f) ==  0
    assert mapnik.Expression("[mapnik::geometry_type]=0").evaluate(f)

    # POINT = 1
    f = mapnik.Feature(context, 0)
    f.geometry = mapnik.Geometry.from_wkt('POINT(10 40)')
    assert expr.evaluate(f) ==  1
    assert mapnik.Expression("[mapnik::geometry_type]=point").evaluate(f)

    # LINESTRING = 2
    f = mapnik.Feature(context, 0)
    f.geometry = mapnik.Geometry.from_wkt('LINESTRING (30 10, 10 30, 40 40)')
    assert expr.evaluate(f) ==  2
    assert mapnik.Expression("[mapnik::geometry_type] = linestring").evaluate(f)

    # POLYGON = 3
    f = mapnik.Feature(context, 0)
    f.geometry = mapnik.Geometry.from_wkt(
        'POLYGON ((30 10, 10 20, 20 40, 40 40, 30 10))')
    assert expr.evaluate(f) ==  3
    assert mapnik.Expression("[mapnik::geometry_type] = polygon").evaluate(f)

    # COLLECTION = 4
    f = mapnik.Feature(context, 0)
    geom = mapnik.Geometry.from_wkt(
        'GEOMETRYCOLLECTION(POLYGON((1 1,2 1,2 2,1 2,1 1)),POINT(2 3),LINESTRING(2 3,3 4))')
    f.geometry = geom
    assert expr.evaluate(f) ==  4
    assert mapnik.Expression("[mapnik::geometry_type] = collection").evaluate(f)


def test_regex_match():
    context = mapnik.Context()
    context.push('name')
    f = mapnik.Feature(context, 0)
    f["name"] = 'test'
    expr = mapnik.Expression("[name].match('test')")
    assert expr.evaluate(f)  # 1 == True


def test_unicode_regex_match():
    context = mapnik.Context()
    context.push('name')
    f = mapnik.Feature(context, 0)
    f["name"] = 'Québec'
    expr = mapnik.Expression("[name].match('Québec')")
    assert expr.evaluate(f) # 1 == True


def test_regex_replace():
    context = mapnik.Context()
    context.push('name')
    f = mapnik.Feature(context, 0)
    f["name"] = 'test'
    expr = mapnik.Expression("[name].replace('(\\B)|( )','$1 ')")
    assert expr.evaluate(f) ==  't e s t'


def test_unicode_regex_replace_to_str():
    expr = mapnik.Expression("[name].replace('(\\B)|( )','$1 ')")
    assert str(expr), "[name].replace('(\\B)|( )' == '$1 ')"


def test_unicode_regex_replace():
    context = mapnik.Context()
    context.push('name')
    f = mapnik.Feature(context, 0)
    f["name"] = 'Québec'
    expr = mapnik.Expression("[name].replace('(\\B)|( )','$1 ')")
    # will fail if -DBOOST_REGEX_HAS_ICU is not defined
    assert expr.evaluate(f) ==  u'Q u é b e c'


def test_float_precision():
    context = mapnik.Context()
    context.push('num')
    f = mapnik.Feature(context, 0)
    f["num1"] = 1.0000
    f["num2"] = 1.0001
    assert f["num1"] ==  1.0000
    assert f["num2"] ==  1.0001
    expr = mapnik.Expression("[num1] = 1.0000")
    assert expr.evaluate(f)
    expr = mapnik.Expression("[num1].match('1')")
    assert expr.evaluate(f)
    expr = mapnik.Expression("[num2] = 1.0001")
    assert expr.evaluate(f)
    expr = mapnik.Expression("[num2].match('1.0001')")
    assert expr.evaluate(f)


def test_string_matching_on_precision():
    context = mapnik.Context()
    context.push('num')
    f = mapnik.Feature(context, 0)
    f["num"] = "1.0000"
    assert f["num"] ==  "1.0000"
    expr = mapnik.Expression("[num].match('.*(^0|00)$')")
    assert expr.evaluate(f)


def test_creation_of_null_value():
    context = mapnik.Context()
    context.push('nv')
    f = mapnik.Feature(context, 0)
    f["nv"] = None
    assert f["nv"] ==  None
    assert f["nv"] is None
    # test boolean
    f["nv"] = 0
    assert f["nv"] ==  0
    assert f["nv"] is not None


def test_creation_of_bool():
    context = mapnik.Context()
    context.push('bool')
    f = mapnik.Feature(context, 0)
    f["bool"] = True
    assert f["bool"]
    # TODO - will become int of 1 do to built in boost python conversion
    # https://github.com/mapnik/mapnik/issues/1873
    assert isinstance(f["bool"], bool) or isinstance(f["bool"], int)
    f["bool"] = False
    assert f["bool"] ==  False
    assert isinstance(f["bool"], bool) or isinstance(f["bool"], int)
    # test NoneType
    f["bool"] = None
    assert f["bool"] ==  None
    assert not isinstance(f["bool"], bool) or isinstance(f["bool"], int)
    # test integer
    f["bool"] = 0
    assert f["bool"] ==  0
    # https://github.com/mapnik/mapnik/issues/1873
    # ugh, boost_python's built into converter does not work right
    # assert isinstance(f["bool"],bool) == False

null_equality = [
    ['hello', False, str],
    [u'', False, str],
    [0, False, int],
    [123, False, int],
    [0.0, False, float],
    [123.123, False, float],
    [.1, False, float],
    # TODO - should become bool: https://github.com/mapnik/mapnik/issues/1873
    [False, False, int],
    # TODO - should become bool: https://github.com/mapnik/mapnik/issues/1873
    [True, False, int],
    [None, True, None],
    [2147483648, False, int],
    [922337203685477580, False, int]
]


def test_expressions_with_null_equality():
    for eq in null_equality:
        context = mapnik.Context()
        f = mapnik.Feature(context, 0)
        f["prop"] = eq[0]
        assert f["prop"] ==  eq[0]
        if eq[0] is None:
            assert f["prop"] is None
        else:
            assert isinstance(f['prop'], eq[2]), '%s is not an instance of %s' % (f['prop'], eq[2])
        expr = mapnik.Expression("[prop] = null")
        assert expr.evaluate(f) ==  eq[1]
        expr = mapnik.Expression("[prop] is null")
        assert expr.evaluate(f) ==  eq[1]


def test_expressions_with_null_equality2():
    for eq in null_equality:
        context = mapnik.Context()
        f = mapnik.Feature(context, 0)
        f["prop"] = eq[0]
        assert f["prop"] ==  eq[0]
        if eq[0] is None:
            assert f["prop"] is None
        else:
            assert isinstance(f['prop'],  eq[2]), '%s is not an instance of %s' % (f['prop'], eq[2])
        # TODO - support `is not` syntax:
        # https://github.com/mapnik/mapnik/issues/796
        expr = mapnik.Expression("not [prop] is null")
        assert not expr.evaluate(f) == eq[1]
        # https://github.com/mapnik/mapnik/issues/1642
        expr = mapnik.Expression("[prop] != null")
        assert not expr.evaluate(f) == eq[1]

truthyness = [
    [u'hello', True, str],
    [u'', False, str],
    [0, False, int],
    [123, True, int],
    [0.0, False, float],
    [123.123, True, float],
    [.1, True, float],
    # TODO - should become bool: https://github.com/mapnik/mapnik/issues/1873
    [False, False, int],
    # TODO - should become bool: https://github.com/mapnik/mapnik/issues/1873
    [True, True, int],
    [None, False, None],
    [2147483648, True, int],
    [922337203685477580, True, int]
]


def test_expressions_for_thruthyness():
    context = mapnik.Context()
    for eq in truthyness:
        f = mapnik.Feature(context, 0)
        f["prop"] = eq[0]
        assert f["prop"] ==  eq[0]
        if eq[0] is None:
            assert f["prop"] is None
        else:
            assert isinstance(f['prop'], eq[2]), '%s is not an instance of %s' % (f['prop'], eq[2])
        expr = mapnik.Expression("[prop]")
        assert expr.to_bool(f) ==  eq[1]
        expr = mapnik.Expression("not [prop]")
        assert not expr.to_bool(f) ==  eq[1]
        expr = mapnik.Expression("! [prop]")
        assert not expr.to_bool(f) == eq[1]
    # also test if feature does not have property at all
    f2 = mapnik.Feature(context, 1)
    # no property existing will return value_null since
    # https://github.com/mapnik/mapnik/commit/562fada9d0f680f59b2d9f396c95320a0d753479#include/mapnik/feature.hpp
    assert f2["prop"] is None
    expr = mapnik.Expression("[prop]")
    assert expr.evaluate(f2) ==  None
    assert expr.to_bool(f2) ==  False

# https://github.com/mapnik/mapnik/issues/1859


def test_if_null_and_empty_string_are_equal():
    context = mapnik.Context()
    f = mapnik.Feature(context, 0)
    f["empty"] = u""
    f["null"] = None
    # ensure base assumptions are good
    assert mapnik.Expression("[empty] = ''").to_bool(f)
    assert mapnik.Expression("[null] = null").to_bool(f)
    assert not mapnik.Expression("[empty] != ''").to_bool(f)
    assert not mapnik.Expression("[null] != null").to_bool(f)
    # now test expected behavior
    assert not mapnik.Expression("[null] = ''").to_bool(f)
    assert not mapnik.Expression("[empty] = null").to_bool(f)
    assert mapnik.Expression("[empty] != null").to_bool(f)
    # this one is the back compatibility shim
    assert not mapnik.Expression("[null] != ''").to_bool(f)


def test_filtering_nulls_and_empty_strings():
    context = mapnik.Context()
    f = mapnik.Feature(context, 0)
    f["prop"] = u"hello"
    assert f["prop"] ==  u"hello"
    assert mapnik.Expression("[prop]").to_bool(f)
    assert not mapnik.Expression("! [prop]").to_bool(f)
    assert mapnik.Expression("[prop] != null").to_bool(f)
    assert mapnik.Expression("[prop] != ''").to_bool(f)
    assert mapnik.Expression("[prop] != null and [prop] != ''").to_bool(f)
    assert mapnik.Expression("[prop] != null or [prop] != ''").to_bool(f)
    f["prop2"] = u""
    assert f["prop2"] ==  u""
    assert not mapnik.Expression("[prop2]").to_bool(f)
    assert mapnik.Expression("! [prop2]").to_bool(f)
    assert mapnik.Expression("[prop2] != null").to_bool(f)
    assert not mapnik.Expression("[prop2] != ''").to_bool(f)
    assert mapnik.Expression("[prop2] = ''").to_bool(f)
    assert mapnik.Expression("[prop2] != null or [prop2] != ''").to_bool(f)
    assert not mapnik.Expression("[prop2] != null and [prop2] != ''").to_bool(f)
    f["prop3"] = None
    assert f["prop3"] ==  None
    assert not mapnik.Expression("[prop3]").to_bool(f)
    assert mapnik.Expression("! [prop3]").to_bool(f)
    assert not mapnik.Expression("[prop3] != null").to_bool(f)
    assert mapnik.Expression("[prop3] = null").to_bool(f)

    # https://github.com/mapnik/mapnik/issues/1859
    #assert mapnik.Expression("[prop3] != ''").to_bool(f) == True
    assert not mapnik.Expression("[prop3] != ''").to_bool(f)

    assert not mapnik.Expression("[prop3] = ''").to_bool(f)

    # https://github.com/mapnik/mapnik/issues/1859
    #assert mapnik.Expression("[prop3] != null or [prop3] != ''").to_bool(f) == True
    assert not mapnik.Expression("[prop3] != null or [prop3] != ''").to_bool(f)

    assert not mapnik.Expression("[prop3] != null and [prop3] != ''").to_bool(f)
    # attr not existing should behave the same as prop3
    assert not mapnik.Expression("[prop4]").to_bool(f)
    assert mapnik.Expression("! [prop4]").to_bool(f)
    assert not mapnik.Expression("[prop4] != null").to_bool(f)
    assert mapnik.Expression("[prop4] = null").to_bool(f)

    # https://github.com/mapnik/mapnik/issues/1859
    ##assert mapnik.Expression("[prop4] != ''").to_bool(f) == True
    assert not mapnik.Expression("[prop4] != ''").to_bool(f)

    assert not mapnik.Expression("[prop4] = ''").to_bool(f)

    # https://github.com/mapnik/mapnik/issues/1859
    ##assert mapnik.Expression("[prop4] != null or [prop4] != ''").to_bool(f) == True
    assert not mapnik.Expression("[prop4] != null or [prop4] != ''").to_bool(f)

    assert not mapnik.Expression("[prop4] != null and [prop4] != ''").to_bool(f)
    f["prop5"] = False
    assert f["prop5"] ==  False
    assert not mapnik.Expression("[prop5]").to_bool(f)
    assert mapnik.Expression("! [prop5]").to_bool(f)
    assert mapnik.Expression("[prop5] != null").to_bool(f)
    assert not mapnik.Expression("[prop5] = null").to_bool(f)
    assert mapnik.Expression("[prop5] != ''").to_bool(f)
    assert not mapnik.Expression("[prop5] = ''").to_bool(f)
    assert mapnik.Expression("[prop5] != null or [prop5] != ''").to_bool(f)
    assert mapnik.Expression("[prop5] != null and [prop5] != ''").to_bool(f)
    # note, we need to do [prop5] != 0 here instead of false due to this bug:
    # https://github.com/mapnik/mapnik/issues/1873
    assert not mapnik.Expression("[prop5] != null and [prop5] != '' and [prop5] != 0").to_bool(f)

# https://github.com/mapnik/mapnik/issues/1872


def test_falseyness_comparision():
    context = mapnik.Context()
    f = mapnik.Feature(context, 0)
    f["prop"] = 0
    assert not mapnik.Expression("[prop]").to_bool(f)
    assert mapnik.Expression("[prop] = false").to_bool(f)
    assert mapnik.Expression("not [prop] != false").to_bool(f)
    assert mapnik.Expression("not [prop] = true").to_bool(f)
    assert not mapnik.Expression("[prop] = true").to_bool(f)
    assert mapnik.Expression("[prop] != true").to_bool(f)

# https://github.com/mapnik/mapnik/issues/1806, fixed by
# https://github.com/mapnik/mapnik/issues/1872


def test_truthyness_comparision():
    context = mapnik.Context()
    f = mapnik.Feature(context, 0)
    f["prop"] = 1
    assert mapnik.Expression("[prop]").to_bool(f) ==  True
    assert mapnik.Expression("[prop] = false").to_bool(f) ==  False
    assert mapnik.Expression("not [prop] != false").to_bool(f) ==  False
    assert mapnik.Expression("not [prop] = true").to_bool(f) ==  False
    assert mapnik.Expression("[prop] = true").to_bool(f) ==  True
    assert mapnik.Expression("[prop] != true").to_bool(f) ==  False


def test_division_by_zero():
    expr = mapnik.Expression('[a]/[b]')
    c = mapnik.Context()
    c.push('a')
    c.push('b')
    f = mapnik.Feature(c, 0)
    f['a'] = 1
    f['b'] = 0
    assert expr.evaluate(f) ==  None


def test_invalid_syntax1():
    with pytest.raises(RuntimeError):
        mapnik.Expression('abs()')
