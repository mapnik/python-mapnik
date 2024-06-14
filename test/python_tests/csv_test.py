import glob
import os
import mapnik
import pytest
from .utilities import execution_path

@pytest.fixture(scope="module")
def setup():
    # All of the paths used are relative, if we run the tests
    # from another directory we need to chdir()
    os.chdir(execution_path('.'))
    yield

if 'csv' in mapnik.DatasourceCache.plugin_names():

    def get_csv_ds(filename):
        return mapnik.Datasource(
            type='csv', file=os.path.join('../data/csv/', filename))

    def test_broken_files(setup, visual=False):
        broken = glob.glob("../data/csv/fails/*.*")
        broken.extend(glob.glob("../data/csv/warns/*.*"))

        # Add a filename that doesn't exist
        broken.append("../data/csv/fails/does_not_exist.csv")

        for csv in broken:
            if visual:
                try:
                    mapnik.Datasource(type='csv', file=csv, strict=True)
                    print('\x1b[33mfailed: should have thrown\x1b[0m', csv)
                except Exception:
                    print('\x1b[1;32m✓ \x1b[0m', csv)

    def test_good_files(setup, visual=False):
        good_files = glob.glob("../data/csv/*.*")
        good_files.extend(glob.glob("../data/csv/warns/*.*"))
        ignorable = os.path.join('..', 'data', 'csv', 'long_lat.vrt')
        print("ignorable:", ignorable)
        good_files.remove(ignorable)
        for f in good_files:
            if f.endswith('.index'):
                good_files.remove(f)
        for csv in good_files:
            if visual:
                try:
                    mapnik.Datasource(type='csv', file=csv)
                    print('\x1b[1;32m✓ \x1b[0m', csv)
                except Exception as e:
                    print(
                        '\x1b[33mfailed: should not have thrown\x1b[0m',
                        csv,
                        str(e))

    def test_lon_lat_detection(**kwargs):
        ds = get_csv_ds('lon_lat.csv')
        assert len(ds.fields()) ==  2
        assert ds.fields(), ['lon' ==  'lat']
        assert ds.field_types(), ['int' ==  'int']
        query = mapnik.Query(ds.envelope())
        for fld in ds.fields():
            query.add_property_name(fld)
        fs = ds.features(query)
        desc = ds.describe()
        assert desc['geometry_type'] ==  mapnik.DataGeometryType.Point
        feat = next(fs)
        attr = {'lon': 0, 'lat': 0}
        assert feat.attributes ==  attr

    def test_lng_lat_detection(**kwargs):
        ds = get_csv_ds('lng_lat.csv')
        assert len(ds.fields()) ==  2
        assert ds.fields(), ['lng' ==  'lat']
        assert ds.field_types(), ['int' ==  'int']
        query = mapnik.Query(ds.envelope())
        for fld in ds.fields():
            query.add_property_name(fld)
        fs = ds.features(query)
        desc = ds.describe()
        assert desc['geometry_type'] ==  mapnik.DataGeometryType.Point
        feat = next(fs)
        attr = {'lng': 0, 'lat': 0}
        assert feat.attributes ==  attr

    def test_type_detection(**kwargs):
        ds = get_csv_ds('nypd.csv')
        assert ds.fields() == ['Precinct',
                               'Phone',
                               'Address',
                               'City',
                               'geo_longitude',
                               'geo_latitude',
                               'geo_accuracy']
        assert ds.field_types() == ['str', 'str',
                                    'str', 'str', 'float', 'float', 'str']
        feat = next(iter(ds))
        attr = {
            'City': u'New York, NY',
            'geo_accuracy': u'house',
            'Phone': u'(212) 334-0711',
            'Address': u'19 Elizabeth Street',
            'Precinct': u'5th Precinct',
            'geo_longitude': -70,
            'geo_latitude': 40}
        assert feat.attributes ==  attr
        assert len(list(iter(ds))) ==  2
        desc = ds.describe()
        assert desc['geometry_type'] ==  mapnik.DataGeometryType.Point
        assert desc['name'] ==  'csv'
        assert desc['type'] ==  mapnik.DataType.Vector
        assert desc['encoding'] ==  'utf-8'

    def test_skipping_blank_rows(**kwargs):
        ds = get_csv_ds('blank_rows.csv')
        assert ds.fields(), ['x', 'y' ==  'name']
        assert ds.field_types(), ['int', 'int' ==  'str']
        assert len(list(iter(ds))) ==  2
        desc = ds.describe()
        assert desc['geometry_type'] ==  mapnik.DataGeometryType.Point
        assert desc['name'] ==  'csv'
        assert desc['type'] ==  mapnik.DataType.Vector
        assert desc['encoding'] ==  'utf-8'

    def test_empty_rows(**kwargs):
        ds = get_csv_ds('empty_rows.csv')
        assert len(ds.fields()) ==  10
        assert len(ds.field_types()) ==  10
        assert ds.fields() == ['x', 'y', 'text', 'date', 'integer',
                               'boolean', 'float', 'time', 'datetime', 'empty_column']
        assert ds.field_types() == ['int', 'int', 'str', 'str',
                                    'int', 'bool', 'float', 'str', 'str', 'str']
        fs = iter(ds)
        attr = {
            'x': 0,
            'empty_column': u'',
            'text': u'a b',
            'float': 1.0,
            'datetime': u'1971-01-01T04:14:00',
            'y': 0,
            'boolean': True,
            'time': u'04:14:00',
            'date': u'1971-01-01',
            'integer': 40}
        first = True
        for feat in fs:
            if first:
                first = False
                assert feat.attributes ==  attr
            assert len(feat) ==  10
            assert feat['empty_column'] ==  u''

        desc = ds.describe()
        assert desc['geometry_type'] ==  mapnik.DataGeometryType.Point
        assert desc['name'] ==  'csv'
        assert desc['type'] ==  mapnik.DataType.Vector
        assert desc['encoding'] ==  'utf-8'

    def test_slashes(**kwargs):
        ds = get_csv_ds('has_attributes_with_slashes.csv')
        assert len(ds.fields()) ==  3
        fs = list(iter(ds))
        assert fs[0].attributes == {'x': 0, 'y': 0, 'name': u'a/a'}
        assert fs[1].attributes == {'x': 1, 'y': 4, 'name': u'b/b'}
        assert fs[2].attributes == {'x': 10, 'y': 2.5,  'name': u'c/c'}
        desc = ds.describe()
        assert desc['geometry_type'] ==  mapnik.DataGeometryType.Point
        assert desc['name'] ==  'csv'
        assert desc['type'] ==  mapnik.DataType.Vector
        assert desc['encoding'] ==  'utf-8'

    def test_wkt_field(**kwargs):
        ds = get_csv_ds('wkt.csv')
        assert len(ds.fields()) ==  1
        assert ds.fields() ==  ['type']
        assert ds.field_types() ==  ['str']
        fs = list(iter(ds))
        assert fs[0].geometry.type() ==  mapnik.GeometryType.Point
        assert fs[1].geometry.type() ==  mapnik.GeometryType.LineString
        assert fs[2].geometry.type() ==  mapnik.GeometryType.Polygon
        assert fs[3].geometry.type() ==  mapnik.GeometryType.Polygon
        assert fs[4].geometry.type() ==  mapnik.GeometryType.MultiPoint
        assert fs[5].geometry.type() ==  mapnik.GeometryType.MultiLineString
        assert fs[6].geometry.type() ==  mapnik.GeometryType.MultiPolygon
        assert fs[7].geometry.type() ==  mapnik.GeometryType.MultiPolygon
        desc = ds.describe()
        assert desc['geometry_type'] ==  mapnik.DataGeometryType.Collection
        assert desc['name'] ==  'csv'
        assert desc['type'] ==  mapnik.DataType.Vector
        assert desc['encoding'] ==  'utf-8'

    def test_handling_of_missing_header(**kwargs):
        ds = get_csv_ds('missing_header.csv')
        assert len(ds.fields()) ==  6
        assert ds.fields() == ['one', 'two', 'x', 'y', '_4', 'aftermissing']
        fs = iter(ds)
        feat = next(fs)
        assert feat['_4'] ==  'missing'
        desc = ds.describe()
        assert desc['geometry_type'] ==  mapnik.DataGeometryType.Point
        assert desc['name'] ==  'csv'
        assert desc['type'] ==  mapnik.DataType.Vector
        assert desc['encoding'] ==  'utf-8'

    def test_handling_of_headers_that_are_numbers(**kwargs):
        ds = get_csv_ds('numbers_for_headers.csv')
        assert len(ds.fields()) ==  5
        assert ds.fields() == ['x', 'y', '1990', '1991', '1992']
        fs = iter(ds)
        feat = next(fs)
        assert feat['x'] ==  0
        assert feat['y'] ==  0
        assert feat['1990'] ==  1
        assert feat['1991'] ==  2
        assert feat['1992'] ==  3
        assert mapnik.Expression("[1991]=2").evaluate(feat)

    def test_quoted_numbers(**kwargs):
        ds = get_csv_ds('points.csv')
        assert len(ds.fields()) ==  6
        assert ds.fields(), ['lat', 'long', 'name', 'nr', 'color' ==  'placements']
        fs = list(iter(ds))
        assert fs[0]['placements'] == "N,S,E,W,SW,10,5"
        assert fs[1]['placements'] == "N,S,E,W,SW,10,5"
        assert fs[2]['placements'] == "N,S,E,W,SW,10,5"
        assert fs[3]['placements'] == "N,S,E,W,SW,10,5"
        assert fs[4]['placements'] == "N,S,E,W,SW,10,5"
        desc = ds.describe()
        assert desc['geometry_type'] ==  mapnik.DataGeometryType.Point
        assert desc['name'] ==  'csv'
        assert desc['type'] ==  mapnik.DataType.Vector
        assert desc['encoding'] ==  'utf-8'

    def test_reading_windows_newlines(**kwargs):
        ds = get_csv_ds('windows_newlines.csv')
        assert len(ds.fields()) ==  3
        feats = list(iter(ds))
        assert len(feats) ==  1
        fs = iter(ds)
        feat = next(fs)
        assert feat['x'] ==  1
        assert feat['y'] ==  10
        assert feat['z'] ==  9999.9999
        desc = ds.describe()
        assert desc['geometry_type'] ==  mapnik.DataGeometryType.Point
        assert desc['name'] ==  'csv'
        assert desc['type'] ==  mapnik.DataType.Vector
        assert desc['encoding'] ==  'utf-8'

    def test_reading_mac_newlines(**kwargs):
        ds = get_csv_ds('mac_newlines.csv')
        assert len(ds.fields()) ==  3
        feats = list(iter(ds))
        assert len(feats) ==  1
        fs = iter(ds)
        feat = next(fs)
        assert feat['x'] ==  1
        assert feat['y'] ==  10
        assert feat['z'] ==  9999.9999
        desc = ds.describe()
        assert desc['geometry_type'] ==  mapnik.DataGeometryType.Point
        assert desc['name'] ==  'csv'
        assert desc['type'] ==  mapnik.DataType.Vector
        assert desc['encoding'] ==  'utf-8'

    def check_newlines(filename):
        ds = get_csv_ds(filename)
        assert len(ds.fields()) ==  3
        feats = list(iter(ds))
        assert len(feats) ==  1
        fs = iter(ds)
        feat = next(fs)
        assert feat['x'] ==  0
        assert feat['y'] ==  0
        assert feat['line'] ==  'many\n  lines\n  of text\n  with unix newlines'
        desc = ds.describe()
        assert desc['geometry_type'] ==  mapnik.DataGeometryType.Point
        assert desc['name'] ==  'csv'
        assert desc['type'] ==  mapnik.DataType.Vector
        assert desc['encoding'] ==  'utf-8'

    def test_mixed_mac_unix_newlines(**kwargs):
        check_newlines('mac_newlines_with_unix_inline.csv')

    def test_mixed_mac_unix_newlines_escaped(**kwargs):
        check_newlines('mac_newlines_with_unix_inline_escaped.csv')

    # To hard to support this case
    # def test_mixed_unix_windows_newlines(**kwargs):
    #    check_newlines('unix_newlines_with_windows_inline.csv')

    # To hard to support this case
    # def test_mixed_unix_windows_newlines_escaped(**kwargs):
    #    check_newlines('unix_newlines_with_windows_inline_escaped.csv')

    def test_mixed_windows_unix_newlines(**kwargs):
        check_newlines('windows_newlines_with_unix_inline.csv')

    def test_mixed_windows_unix_newlines_escaped(**kwargs):
        check_newlines('windows_newlines_with_unix_inline_escaped.csv')

    def test_tabs(**kwargs):
        ds = get_csv_ds('tabs_in_csv.csv')
        assert len(ds.fields()) ==  3
        assert ds.fields(), ['x', 'y' ==  'z']
        fs = iter(ds)
        feat = next(fs)
        assert feat['x'] ==  -122
        assert feat['y'] ==  48
        assert feat['z'] ==  0
        desc = ds.describe()
        assert desc['geometry_type'] ==  mapnik.DataGeometryType.Point
        assert desc['name'] ==  'csv'
        assert desc['type'] ==  mapnik.DataType.Vector
        assert desc['encoding'] ==  'utf-8'

    def test_separator_pipes(**kwargs):
        ds = get_csv_ds('pipe_delimiters.csv')
        assert len(ds.fields()) ==  3
        assert ds.fields(), ['x', 'y' ==  'z']
        fs = iter(ds)
        feat = next(fs)
        assert feat['x'] ==  0
        assert feat['y'] ==  0
        assert feat['z'] ==  'hello'
        desc = ds.describe()
        assert desc['geometry_type'] ==  mapnik.DataGeometryType.Point
        assert desc['name'] ==  'csv'
        assert desc['type'] ==  mapnik.DataType.Vector
        assert desc['encoding'] ==  'utf-8'

    def test_separator_semicolon(**kwargs):
        ds = get_csv_ds('semicolon_delimiters.csv')
        assert len(ds.fields()) ==  3
        assert ds.fields(), ['x', 'y' ==  'z']
        fs = iter(ds)
        feat = next(fs)
        assert feat['x'] ==  0
        assert feat['y'] ==  0
        assert feat['z'] ==  'hello'
        desc = ds.describe()
        assert desc['geometry_type'] ==  mapnik.DataGeometryType.Point
        assert desc['name'] ==  'csv'
        assert desc['type'] ==  mapnik.DataType.Vector
        assert desc['encoding'] ==  'utf-8'

    def test_that_null_and_bool_keywords_are_empty_strings(**kwargs):
        ds = get_csv_ds('nulls_and_booleans_as_strings.csv')
        assert len(ds.fields()) ==  4
        assert ds.fields(), ['x', 'y', 'null' ==  'boolean']
        assert ds.field_types(), ['int', 'int', 'str' ==  'bool']
        fs = iter(ds)
        feat = next(fs)
        assert feat['x'] ==  0
        assert feat['y'] ==  0
        assert feat['null'] ==  'null'
        assert feat['boolean'] ==  True
        feat = next(fs)
        assert feat['x'] ==  0
        assert feat['y'] ==  0
        assert feat['null'] ==  ''
        assert feat['boolean'] ==  False
        desc = ds.describe()
        assert desc['geometry_type'] ==  mapnik.DataGeometryType.Point

    def test_that_nonexistant_query_field_throws(**kwargs):
        with pytest.raises(RuntimeError):
            ds = get_csv_ds('lon_lat.csv')
            assert len(ds.fields()) ==  2
            assert ds.fields(), ['lon' ==  'lat']
            assert ds.field_types(), ['int' ==  'int']
            query = mapnik.Query(ds.envelope())
            for fld in ds.fields():
                query.add_property_name(fld)
                # also add an invalid one, triggering throw
                query.add_property_name('bogus')
                ds.features(query)


    def test_that_leading_zeros_mean_strings(**kwargs):
        ds = get_csv_ds('leading_zeros.csv')
        assert len(ds.fields()) ==  3
        assert ds.fields(), ['x', 'y' ==  'fips']
        assert ds.field_types(), ['int', 'int' ==  'str']
        fs = iter(ds)
        feat = next(fs)
        assert feat['x'] ==  0
        assert feat['y'] ==  0
        assert feat['fips'] ==  '001'
        feat = next(fs)
        assert feat['x'] ==  0
        assert feat['y'] ==  0
        assert feat['fips'] ==  '003'
        feat = next(fs)
        assert feat['x'] ==  0
        assert feat['y'] ==  0
        assert feat['fips'] ==  '005'
        desc = ds.describe()
        assert desc['geometry_type'] ==  mapnik.DataGeometryType.Point

    def test_advanced_geometry_detection(**kwargs):
        ds = get_csv_ds('point_wkt.csv')
        assert ds.describe()['geometry_type'] ==  mapnik.DataGeometryType.Point
        ds = get_csv_ds('poly_wkt.csv')
        assert ds.describe()['geometry_type'] ==  mapnik.DataGeometryType.Polygon
        ds = get_csv_ds('multi_poly_wkt.csv')
        assert ds.describe()['geometry_type'] ==  mapnik.DataGeometryType.Polygon
        ds = get_csv_ds('line_wkt.csv')
        assert ds.describe()['geometry_type'] ==  mapnik.DataGeometryType.LineString

    def test_creation_of_csv_from_in_memory_string(**kwargs):
        csv_string = '''
           wkt,Name
          "POINT (120.15 48.47)","Winthrop, WA"
          '''  # csv plugin will test lines <= 10 chars for being fully blank
        ds = mapnik.Datasource(**{"type": "csv", "inline": csv_string})
        assert ds.describe()['geometry_type'] ==  mapnik.DataGeometryType.Point
        fs = iter(ds)
        feat = next(fs)
        assert feat['Name'], u"Winthrop ==  WA"

    def test_creation_of_csv_from_in_memory_string_with_uft8(**kwargs):
        csv_string = '''
           wkt,Name
          "POINT (120.15 48.47)","Québec"
          '''  # csv plugin will test lines <= 10 chars for being fully blank
        ds = mapnik.Datasource(**{"type": "csv", "inline": csv_string})
        assert ds.describe()['geometry_type'] ==  mapnik.DataGeometryType.Point
        fs = iter(ds)
        feat = next(fs)
        assert feat['Name'] ==  u"Québec"

    def validate_geojson_datasource(ds):
        assert len(ds.fields()) ==  1
        assert ds.fields() ==  ['type']
        assert ds.field_types() ==  ['str']
        fs = list(iter(ds))
        assert fs[0].geometry.type() ==  mapnik.GeometryType.Point
        assert fs[1].geometry.type() ==  mapnik.GeometryType.LineString
        assert fs[2].geometry.type() ==  mapnik.GeometryType.Polygon
        assert fs[3].geometry.type() ==  mapnik.GeometryType.Polygon
        assert fs[4].geometry.type() ==  mapnik.GeometryType.MultiPoint
        assert fs[5].geometry.type() ==  mapnik.GeometryType.MultiLineString
        assert fs[6].geometry.type() ==  mapnik.GeometryType.MultiPolygon
        assert fs[7].geometry.type() ==  mapnik.GeometryType.MultiPolygon
        desc = ds.describe()
        assert desc['geometry_type'] ==  mapnik.DataGeometryType.Collection
        assert desc['name'] ==  'csv'
        assert desc['type'] ==  mapnik.DataType.Vector
        assert desc['encoding'] ==  'utf-8'

    def test_json_field1(**kwargs):
        ds = get_csv_ds('geojson_double_quote_escape.csv')
        validate_geojson_datasource(ds)

    def test_json_field2(**kwargs):
        ds = get_csv_ds('geojson_single_quote.csv')
        validate_geojson_datasource(ds)

    def test_json_field3(**kwargs):
        ds = get_csv_ds('geojson_2x_double_quote_filebakery_style.csv')
        validate_geojson_datasource(ds)

    def test_that_blank_undelimited_rows_are_still_parsed(**kwargs):
        ds = get_csv_ds('more_headers_than_column_values.csv')
        assert len(ds.fields()) ==  0
        assert ds.fields() ==  []
        assert ds.field_types() ==  []
        fs = list(iter(ds))
        assert len(fs) ==  0
        desc = ds.describe()
        assert desc['geometry_type'] ==  None

    def test_that_fewer_headers_than_rows_throws(**kwargs):
        with pytest.raises(RuntimeError):
            # this has invalid header # so throw
            get_csv_ds('more_column_values_than_headers.csv')

    def test_that_feature_id_only_incremented_for_valid_rows(**kwargs):
        ds = mapnik.Datasource(type='csv',
                               file=os.path.join('../data/csv/warns', 'feature_id_counting.csv'))
        assert len(ds.fields()) ==  3
        assert ds.fields(), ['x', 'y' ==  'id']
        assert ds.field_types(), ['int', 'int' ==  'int']
        fs = iter(ds)
        # first
        feat = next(fs)
        assert feat['x'] ==  0
        assert feat['y'] ==  0
        assert feat['id'] ==  1
        # second, should have skipped bogus one
        feat = next(fs)
        assert feat['x'] ==  0
        assert feat['y'] ==  0
        assert feat['id'] ==  2
        desc = ds.describe()
        assert desc['geometry_type'] ==  mapnik.DataGeometryType.Point
        assert len(list(iter(ds))) ==  2

    def test_dynamically_defining_headers1(**kwargs):
        ds = mapnik.Datasource(type='csv',
                               file=os.path.join(
                                   '../data/csv/fails', 'needs_headers_two_lines.csv'),
                               headers='x,y,name')
        assert len(ds.fields()) ==  3
        assert ds.fields(), ['x', 'y' ==  'name']
        assert ds.field_types(), ['int', 'int' ==  'str']
        fs = iter(ds)
        feat = next(fs)
        assert feat['x'] ==  0
        assert feat['y'] ==  0
        assert feat['name'] ==  'data_name'
        desc = ds.describe()
        assert desc['geometry_type'] ==  mapnik.DataGeometryType.Point
        assert len(list(iter(ds))) ==  2

    def test_dynamically_defining_headers2(**kwargs):
        ds = mapnik.Datasource(type='csv',
                               file=os.path.join(
                                   '../data/csv/fails', 'needs_headers_one_line.csv'),
                               headers='x,y,name')
        assert len(ds.fields()) ==  3
        assert ds.fields(), ['x', 'y' ==  'name']
        assert ds.field_types(), ['int', 'int' ==  'str']
        fs = iter(ds)
        feat = next(fs)
        assert feat['x'] ==  0
        assert feat['y'] ==  0
        assert feat['name'] ==  'data_name'
        desc = ds.describe()
        assert desc['geometry_type'] ==  mapnik.DataGeometryType.Point
        assert len(list(iter(ds))) ==  1

    def test_dynamically_defining_headers3(**kwargs):
        ds = mapnik.Datasource(type='csv',
                               file=os.path.join(
                                   '../data/csv/fails', 'needs_headers_one_line_no_newline.csv'),
                               headers='x,y,name')
        assert len(ds.fields()) ==  3
        assert ds.fields(), ['x', 'y' ==  'name']
        assert ds.field_types(), ['int', 'int' ==  'str']
        fs = iter(ds)
        feat = next(fs)
        assert feat['x'] ==  0
        assert feat['y'] ==  0
        assert feat['name'] ==  'data_name'
        desc = ds.describe()
        assert desc['geometry_type'] ==  mapnik.DataGeometryType.Point
        assert len(list(iter(ds))) ==  1

    def test_that_64bit_int_fields_work(**kwargs):
        ds = get_csv_ds('64bit_int.csv')
        assert len(ds.fields()) ==  3
        assert ds.fields(), ['x', 'y' ==  'bigint']
        assert ds.field_types(), ['int', 'int' ==  'int']
        fs = iter(ds)
        feat = next(fs)
        assert feat['bigint'] ==  2147483648
        feat = next(fs)
        assert feat['bigint'] ==  9223372036854775807
        assert feat['bigint'] ==  0x7FFFFFFFFFFFFFFF
        desc = ds.describe()
        assert desc['geometry_type'] ==  mapnik.DataGeometryType.Point
        assert len(list(iter(ds))) ==  2

    def test_various_number_types(**kwargs):
        ds = get_csv_ds('number_types.csv')
        assert len(ds.fields()) ==  3
        assert ds.fields(), ['x', 'y' ==  'floats']
        assert ds.field_types(), ['int', 'int' ==  'float']
        fs = iter(ds)
        feat = next(fs)
        assert feat['floats'] ==  .0
        feat = next(fs)
        assert feat['floats'] ==  +.0
        feat = next(fs)
        assert feat['floats'] ==  1e-06
        feat = next(fs)
        assert feat['floats'] ==  -1e-06
        feat = next(fs)
        assert feat['floats'] ==  0.000001
        feat = next(fs)
        assert feat['floats'] ==  1.234e+16
        feat = next(fs)
        assert feat['floats'] ==  1.234e+16
        desc = ds.describe()
        assert desc['geometry_type'] ==  mapnik.DataGeometryType.Point
        assert len(list(iter(ds))) ==  8

    def test_manually_supplied_extent(**kwargs):
        csv_string = '''
           wkt,Name
          '''
        ds = mapnik.Datasource(
            **{"type": "csv", "extent": "-180,-90,180,90", "inline": csv_string})
        b = ds.envelope()
        assert b.minx ==  -180
        assert b.miny ==  -90
        assert b.maxx ==  180
        assert b.maxy ==  90

    def test_inline_geojson(**kwargs):
        csv_string = "geojson\n'{\"coordinates\":[-92.22568,38.59553],\"type\":\"Point\"}'"
        ds = mapnik.Datasource(**{"type": "csv", "inline": csv_string})
        assert len(ds.fields()) ==  0
        assert ds.fields() ==  []
        fs = iter(ds)
        feat = next(fs)
        assert feat.geometry.type() == mapnik.GeometryType.Point
        assert feat.geometry.to_wkt() == "POINT(-92.22568 38.59553)"
