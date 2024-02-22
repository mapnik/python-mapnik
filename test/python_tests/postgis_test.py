import atexit
import os
import sys
import threading
from subprocess import PIPE, Popen
import mapnik
import pytest
from .utilities import execution_path

MAPNIK_TEST_DBNAME = 'mapnik-tmp-postgis-test-db'
POSTGIS_TEMPLATE_DBNAME = 'template_postgis'
SHAPEFILE = os.path.join(execution_path('.'), '../data/shp/world_merc.shp')

def call(cmd, silent=False):
    stdin, stderr = Popen(cmd, shell=True, stdout=PIPE,
                          stderr=PIPE).communicate()
    if not stderr:
        return stdin.strip()
    msg = str(stderr).lower()
    if not silent and 'error' in msg\
       or 'not found' in msg or 'not recognized as an internal' in msg\
       or 'bad connection' in msg or 'could not connect' in msg:
        raise RuntimeError(msg.strip())


def psql_can_connect():
    """Test ability to connect to a postgis template db with no options.

    Basically, to run these tests your user must have full read
    access over unix sockets without supplying a password. This
    keeps these tests simple and focused on postgis not on postgres
    auth issues.
    """
    try:
        call('psql %s -c "select postgis_version()"' % POSTGIS_TEMPLATE_DBNAME)
        return True
    except RuntimeError:
        print('Notice: skipping postgis tests (connection)')
        return False


def shp2pgsql_on_path():
    """Test for presence of shp2pgsql on the user path.

    We require this program to load test data into a temporarily database.
    """
    try:
        call('shp2pgsql')
        return True
    except RuntimeError:
        print('Notice: skipping postgis tests (shp2pgsql)')
        return False


def createdb_and_dropdb_on_path():
    """Test for presence of dropdb/createdb on user path.

    We require these programs to setup and teardown the testing db.
    """
    try:
        call('createdb --help')
        call('dropdb --help')
        return True
    except RuntimeError:
        print('Notice: skipping postgis tests (createdb/dropdb)')
        return False

insert_table_1 = """
CREATE TABLE test(gid serial PRIMARY KEY, geom geometry);
INSERT INTO test(geom) values (GeomFromEWKT('SRID=4326;POINT(0 0)'));
INSERT INTO test(geom) values (GeomFromEWKT('SRID=4326;POINT(-2 2)'));
INSERT INTO test(geom) values (GeomFromEWKT('SRID=4326;MULTIPOINT(2 1,1 2)'));
INSERT INTO test(geom) values (GeomFromEWKT('SRID=4326;LINESTRING(0 0,1 1,1 2)'));
INSERT INTO test(geom) values (GeomFromEWKT('SRID=4326;MULTILINESTRING((1 0,0 1,3 2),(3 2,5 4))'));
INSERT INTO test(geom) values (GeomFromEWKT('SRID=4326;POLYGON((0 0,4 0,4 4,0 4,0 0),(1 1, 2 1, 2 2, 1 2,1 1))'));
INSERT INTO test(geom) values (GeomFromEWKT('SRID=4326;MULTIPOLYGON(((1 1,3 1,3 3,1 3,1 1),(1 1,2 1,2 2,1 2,1 1)), ((-1 -1,-1 -2,-2 -2,-2 -1,-1 -1)))'));
INSERT INTO test(geom) values (GeomFromEWKT('SRID=4326;GEOMETRYCOLLECTION(POLYGON((1 1, 2 1, 2 2, 1 2,1 1)),POINT(2 3),LINESTRING(2 3,3 4))'));
"""

insert_table_2 = """
CREATE TABLE test2(manual_id int4 PRIMARY KEY, geom geometry);
INSERT INTO test2(manual_id, geom) values (0, GeomFromEWKT('SRID=4326;POINT(0 0)'));
INSERT INTO test2(manual_id, geom) values (1, GeomFromEWKT('SRID=4326;POINT(0 0)'));
INSERT INTO test2(manual_id, geom) values (1000, GeomFromEWKT('SRID=4326;POINT(0 0)'));
INSERT INTO test2(manual_id, geom) values (-1000, GeomFromEWKT('SRID=4326;POINT(0 0)'));
INSERT INTO test2(manual_id, geom) values (2147483647, GeomFromEWKT('SRID=4326;POINT(0 0)'));
INSERT INTO test2(manual_id, geom) values (-2147483648, GeomFromEWKT('SRID=4326;POINT(0 0)'));
"""

insert_table_3 = """
CREATE TABLE test3(non_id bigint, manual_id int4, geom geometry);
INSERT INTO test3(non_id, manual_id, geom) values (9223372036854775807, 0, GeomFromEWKT('SRID=4326;POINT(0 0)'));
INSERT INTO test3(non_id, manual_id, geom) values (9223372036854775807, 1, GeomFromEWKT('SRID=4326;POINT(0 0)'));
INSERT INTO test3(non_id, manual_id, geom) values (9223372036854775807, 1000, GeomFromEWKT('SRID=4326;POINT(0 0)'));
INSERT INTO test3(non_id, manual_id, geom) values (9223372036854775807, -1000, GeomFromEWKT('SRID=4326;POINT(0 0)'));
INSERT INTO test3(non_id, manual_id, geom) values (9223372036854775807, 2147483647, GeomFromEWKT('SRID=4326;POINT(0 0)'));
INSERT INTO test3(non_id, manual_id, geom) values (9223372036854775807, -2147483648, GeomFromEWKT('SRID=4326;POINT(0 0)'));
"""

insert_table_4 = """
CREATE TABLE test4(non_id int4, manual_id int8 PRIMARY KEY, geom geometry);
INSERT INTO test4(non_id, manual_id, geom) values (0, 0, GeomFromEWKT('SRID=4326;POINT(0 0)'));
INSERT INTO test4(non_id, manual_id, geom) values (0, 1, GeomFromEWKT('SRID=4326;POINT(0 0)'));
INSERT INTO test4(non_id, manual_id, geom) values (0, 1000, GeomFromEWKT('SRID=4326;POINT(0 0)'));
INSERT INTO test4(non_id, manual_id, geom) values (0, -1000, GeomFromEWKT('SRID=4326;POINT(0 0)'));
INSERT INTO test4(non_id, manual_id, geom) values (0, 2147483647, GeomFromEWKT('SRID=4326;POINT(0 0)'));
INSERT INTO test4(non_id, manual_id, geom) values (0, -2147483648, GeomFromEWKT('SRID=4326;POINT(0 0)'));
"""

insert_table_5 = """
CREATE TABLE test5(non_id int4, manual_id numeric PRIMARY KEY, geom geometry);
INSERT INTO test5(non_id, manual_id, geom) values (0, -1, GeomFromEWKT('SRID=4326;POINT(0 0)'));
INSERT INTO test5(non_id, manual_id, geom) values (0, 1, GeomFromEWKT('SRID=4326;POINT(0 0)'));
"""

insert_table_5b = '''
CREATE TABLE "tableWithMixedCase"(gid serial PRIMARY KEY, geom geometry);
INSERT INTO "tableWithMixedCase"(geom) values (ST_MakePoint(0,0));
INSERT INTO "tableWithMixedCase"(geom) values (ST_MakePoint(0,1));
INSERT INTO "tableWithMixedCase"(geom) values (ST_MakePoint(1,0));
INSERT INTO "tableWithMixedCase"(geom) values (ST_MakePoint(1,1));
'''

insert_table_6 = '''
CREATE TABLE test6(first_id int4, second_id int4,PRIMARY KEY (first_id,second_id), geom geometry);
INSERT INTO test6(first_id, second_id, geom) values (0, 0, GeomFromEWKT('SRID=4326;POINT(0 0)'));
'''

insert_table_7 = '''
CREATE TABLE test7(gid serial PRIMARY KEY, geom geometry);
INSERT INTO test7(gid, geom) values (1, GeomFromEWKT('SRID=4326;GEOMETRYCOLLECTION(MULTILINESTRING((10 10,20 20,10 40),(40 40,30 30,40 20,30 10)),LINESTRING EMPTY)'));
'''

insert_table_8 = '''
CREATE TABLE test8(gid serial PRIMARY KEY,int_field bigint, geom geometry);
INSERT INTO test8(gid, int_field, geom) values (1, 2147483648, ST_MakePoint(1,1));
INSERT INTO test8(gid, int_field, geom) values (2, 922337203685477580, ST_MakePoint(1,1));
'''

insert_table_9 = '''
CREATE TABLE test9(gid serial PRIMARY KEY, name varchar, geom geometry);
INSERT INTO test9(gid, name, geom) values (1, 'name', ST_MakePoint(1,1));
INSERT INTO test9(gid, name, geom) values (2, '', ST_MakePoint(1,1));
INSERT INTO test9(gid, name, geom) values (3, null, ST_MakePoint(1,1));
'''

insert_table_10 = '''
CREATE TABLE test10(gid serial PRIMARY KEY, bool_field boolean, geom geometry);
INSERT INTO test10(gid, bool_field, geom) values (1, TRUE, ST_MakePoint(1,1));
INSERT INTO test10(gid, bool_field, geom) values (2, FALSE, ST_MakePoint(1,1));
INSERT INTO test10(gid, bool_field, geom) values (3, null, ST_MakePoint(1,1));
'''

insert_table_11 = """
CREATE TABLE test11(gid serial PRIMARY KEY, label varchar(40), geom geometry);
INSERT INTO test11(label,geom) values ('label_1',GeomFromEWKT('SRID=4326;POINT(0 0)'));
INSERT INTO test11(label,geom) values ('label_2',GeomFromEWKT('SRID=4326;POINT(-2 2)'));
INSERT INTO test11(label,geom) values ('label_3',GeomFromEWKT('SRID=4326;MULTIPOINT(2 1,1 2)'));
INSERT INTO test11(label,geom) values ('label_4',GeomFromEWKT('SRID=4326;LINESTRING(0 0,1 1,1 2)'));
INSERT INTO test11(label,geom) values ('label_5',GeomFromEWKT('SRID=4326;MULTILINESTRING((1 0,0 1,3 2),(3 2,5 4))'));
INSERT INTO test11(label,geom) values ('label_6',GeomFromEWKT('SRID=4326;POLYGON((0 0,4 0,4 4,0 4,0 0),(1 1, 2 1, 2 2, 1 2,1 1))'));
INSERT INTO test11(label,geom) values ('label_7',GeomFromEWKT('SRID=4326;MULTIPOLYGON(((1 1,3 1,3 3,1 3,1 1),(1 1,2 1,2 2,1 2,1 1)), ((-1 -1,-1 -2,-2 -2,-2 -1,-1 -1)))'));
INSERT INTO test11(label,geom) values ('label_8',GeomFromEWKT('SRID=4326;GEOMETRYCOLLECTION(POLYGON((1 1, 2 1, 2 2, 1 2,1 1)),POINT(2 3),LINESTRING(2 3,3 4))'));
"""

insert_table_12 = """
CREATE TABLE test12(gid serial PRIMARY KEY, name varchar(40), geom geometry);
INSERT INTO test12(name,geom) values ('Point',GeomFromEWKT('SRID=4326;POINT(0 0)'));
INSERT INTO test12(name,geom) values ('PointZ',GeomFromEWKT('SRID=4326;POINTZ(0 0 0)'));
INSERT INTO test12(name,geom) values ('PointM',GeomFromEWKT('SRID=4326;POINTM(0 0 0)'));
INSERT INTO test12(name,geom) values ('PointZM',GeomFromEWKT('SRID=4326;POINTZM(0 0 0 0)'));
INSERT INTO test12(name,geom) values ('MultiPoint',GeomFromEWKT('SRID=4326;MULTIPOINT(0 0, 1 1)'));
INSERT INTO test12(name,geom) values ('MultiPointZ',GeomFromEWKT('SRID=4326;MULTIPOINTZ(0 0 0, 1 1 1)'));
INSERT INTO test12(name,geom) values ('MultiPointM',GeomFromEWKT('SRID=4326;MULTIPOINTM(0 0 0, 1 1 1)'));
INSERT INTO test12(name,geom) values ('MultiPointZM',GeomFromEWKT('SRID=4326;MULTIPOINTZM(0 0 0 0, 1 1 1 1)'));
INSERT INTO test12(name,geom) values ('LineString',GeomFromEWKT('SRID=4326;LINESTRING(0 0, 1 1)'));
INSERT INTO test12(name,geom) values ('LineStringZ',GeomFromEWKT('SRID=4326;LINESTRINGZ(0 0 0, 1 1 1)'));
INSERT INTO test12(name,geom) values ('LineStringM',GeomFromEWKT('SRID=4326;LINESTRINGM(0 0 0, 1 1 1)'));
INSERT INTO test12(name,geom) values ('LineStringZM',GeomFromEWKT('SRID=4326;LINESTRINGZM(0 0 0 0, 1 1 1 1)'));
INSERT INTO test12(name,geom) values ('Polygon',GeomFromEWKT('SRID=4326;POLYGON((0 0, 1 1, 2 2, 0 0))'));
INSERT INTO test12(name,geom) values ('PolygonZ',GeomFromEWKT('SRID=4326;POLYGONZ((0 0 0, 1 1 1, 2 2 2, 0 0 0))'));
INSERT INTO test12(name,geom) values ('PolygonM',GeomFromEWKT('SRID=4326;POLYGONZ((0 0 0, 1 1 1, 2 2 2, 0 0 0))'));
INSERT INTO test12(name,geom) values ('PolygonZM',GeomFromEWKT('SRID=4326;POLYGONZM((0 0 0 0, 1 1 1 1, 2 2 2 2, 0 0 0 0))'));
INSERT INTO test12(name,geom) values ('MultiLineString',GeomFromEWKT('SRID=4326;MULTILINESTRING((0 0, 1 1),(2 2, 3 3))'));
INSERT INTO test12(name,geom) values ('MultiLineStringZ',GeomFromEWKT('SRID=4326;MULTILINESTRINGZ((0 0 0, 1 1 1),(2 2 2, 3 3 3))'));
INSERT INTO test12(name,geom) values ('MultiLineStringM',GeomFromEWKT('SRID=4326;MULTILINESTRINGM((0 0 0, 1 1 1),(2 2 2, 3 3 3))'));
INSERT INTO test12(name,geom) values ('MultiLineStringZM',GeomFromEWKT('SRID=4326;MULTILINESTRINGZM((0 0 0 0, 1 1 1 1),(2 2 2 2, 3 3 3 3))'));
INSERT INTO test12(name,geom) values ('MultiPolygon',GeomFromEWKT('SRID=4326;MULTIPOLYGON(((0 0, 1 1, 2 2, 0 0)),((0 0, 1 1, 2 2, 0 0)))'));
INSERT INTO test12(name,geom) values ('MultiPolygonZ',GeomFromEWKT('SRID=4326;MULTIPOLYGONZ(((0 0 0, 1 1 1, 2 2 2, 0 0 0)),((0 0 0, 1 1 1, 2 2 2, 0 0 0)))'));
INSERT INTO test12(name,geom) values ('MultiPolygonM',GeomFromEWKT('SRID=4326;MULTIPOLYGONM(((0 0 0, 1 1 1, 2 2 2, 0 0 0)),((0 0 0, 1 1 1, 2 2 2, 0 0 0)))'));
INSERT INTO test12(name,geom) values ('MultiPolygonZM',GeomFromEWKT('SRID=4326;MULTIPOLYGONZM(((0 0 0 0, 1 1 1 1, 2 2 2 2, 0 0 0 0)),((0 0 0 0, 1 1 1 1, 2 2 2 2, 0 0 0 0)))'));
"""


def postgis_setup():
    call('dropdb %s' % MAPNIK_TEST_DBNAME, silent=True)
    call(
        'createdb -T %s %s' %
        (POSTGIS_TEMPLATE_DBNAME,
         MAPNIK_TEST_DBNAME),
        silent=False)
    call('shp2pgsql -s 3857 -g geom -W LATIN1 %s world_merc | psql -q %s' %
         (SHAPEFILE, MAPNIK_TEST_DBNAME), silent=True)
    call(
        '''psql -q %s -c "CREATE TABLE \"empty\" (key serial);SELECT AddGeometryColumn('','empty','geom','-1','GEOMETRY',4);"''' %
        MAPNIK_TEST_DBNAME,
        silent=False)
    call(
        '''psql -q %s -c "%s"''' %
        (MAPNIK_TEST_DBNAME,
         insert_table_1),
        silent=False)
    call(
        '''psql -q %s -c "%s"''' %
        (MAPNIK_TEST_DBNAME,
         insert_table_2),
        silent=False)
    call(
        '''psql -q %s -c "%s"''' %
        (MAPNIK_TEST_DBNAME,
         insert_table_3),
        silent=False)
    call(
        '''psql -q %s -c "%s"''' %
        (MAPNIK_TEST_DBNAME,
         insert_table_4),
        silent=False)
    call(
        '''psql -q %s -c "%s"''' %
        (MAPNIK_TEST_DBNAME,
         insert_table_5),
        silent=False)
    call(
        """psql -q %s -c '%s'""" %
        (MAPNIK_TEST_DBNAME,
         insert_table_5b),
        silent=False)
    call(
        '''psql -q %s -c "%s"''' %
        (MAPNIK_TEST_DBNAME,
         insert_table_6),
        silent=False)
    call(
        '''psql -q %s -c "%s"''' %
        (MAPNIK_TEST_DBNAME,
         insert_table_7),
        silent=False)
    call(
        '''psql -q %s -c "%s"''' %
        (MAPNIK_TEST_DBNAME,
         insert_table_8),
        silent=False)
    call(
        '''psql -q %s -c "%s"''' %
        (MAPNIK_TEST_DBNAME,
         insert_table_9),
        silent=False)
    call(
        '''psql -q %s -c "%s"''' %
        (MAPNIK_TEST_DBNAME,
         insert_table_10),
        silent=False)
    call(
        '''psql -q %s -c "%s"''' %
        (MAPNIK_TEST_DBNAME,
         insert_table_11),
        silent=False)
    call(
        '''psql -q %s -c "%s"''' %
        (MAPNIK_TEST_DBNAME,
         insert_table_12),
        silent=False)


def postgis_takedown():
    pass
    # fails as the db is in use: https://github.com/mapnik/mapnik/issues/960
    #call('dropdb %s' % MAPNIK_TEST_DBNAME)

if 'postgis' in mapnik.DatasourceCache.plugin_names() \
        and createdb_and_dropdb_on_path() \
        and psql_can_connect() \
        and shp2pgsql_on_path():

    # initialize test database
    postgis_setup()

    def test_feature():
        ds = mapnik.PostGIS(dbname=MAPNIK_TEST_DBNAME, table='world_merc')
        fs = ds.featureset()
        feature = fs.next()
        assert feature['gid'] ==  1
        assert feature['fips'] ==  u'AC'
        assert feature['iso2'] ==  u'AG'
        assert feature['iso3'] ==  u'ATG'
        assert feature['un'] ==  28
        assert feature['name'] ==  u'Antigua and Barbuda'
        assert feature['area'] ==  44
        assert feature['pop2005'] ==  83039
        assert feature['region'] ==  19
        assert feature['subregion'] ==  29
        assert feature['lon'] ==  -61.783
        assert feature['lat'] ==  17.078
        meta = ds.describe()
        assert meta['srid'] ==  3857
        assert meta.get('key_field') ==  None
        assert meta['encoding'] ==  u'UTF8'
        assert meta['geometry_type'] ==  mapnik.DataGeometryType.Polygon

    def test_subquery():
        ds = mapnik.PostGIS(
            dbname=MAPNIK_TEST_DBNAME,
            table='(select * from world_merc) as w')
        fs = ds.featureset()
        feature = fs.next()
        assert feature['gid'] ==  1
        assert feature['fips'] ==  u'AC'
        assert feature['iso2'] ==  u'AG'
        assert feature['iso3'] ==  u'ATG'
        assert feature['un'] ==  28
        assert feature['name'] ==  u'Antigua and Barbuda'
        assert feature['area'] ==  44
        assert feature['pop2005'] ==  83039
        assert feature['region'] ==  19
        assert feature['subregion'] ==  29
        assert feature['lon'] ==  -61.783
        assert feature['lat'] ==  17.078
        meta = ds.describe()
        assert meta['srid'] ==  3857
        assert meta.get('key_field') ==  None
        assert meta['encoding'] ==  u'UTF8'
        assert meta['geometry_type'] ==  mapnik.DataGeometryType.Polygon

        ds = mapnik.PostGIS(
            dbname=MAPNIK_TEST_DBNAME,
            table='(select gid,geom,fips as _fips from world_merc) as w')
        fs = ds.featureset()
        feature = fs.next()
        assert feature['gid'] ==  1
        assert feature['_fips'] ==  u'AC'
        assert len(feature) ==  2
        meta = ds.describe()
        assert meta['srid'] ==  3857
        assert meta.get('key_field') ==  None
        assert meta['encoding'] ==  u'UTF8'
        assert meta['geometry_type'] ==  mapnik.DataGeometryType.Polygon

    def test_bad_connection():
        try:
            ds = mapnik.PostGIS(dbname=MAPNIK_TEST_DBNAME,
                                table='test',
                                max_size=20,
                                geometry_field='geom',
                                user="rolethatdoesnotexist")
        except Exception as e:
            assert 'role "rolethatdoesnotexist" does not exist' in str(e) or \
                'authentication failed for user "rolethatdoesnotexist"' in str(e)

    def test_empty_db():
        ds = mapnik.PostGIS(dbname=MAPNIK_TEST_DBNAME, table='empty')
        fs = ds.features(mapnik.Query(mapnik.Box2d(-180,-90,180,90)))
        feature = None
        try:
            feature = fs.next()
        except StopIteration:
            pass
        assert feature ==  None
        meta = ds.describe()
        assert meta['srid'] ==  -1
        assert meta.get('key_field') ==  None
        assert meta['encoding'] ==  u'UTF8'
        assert meta['geometry_type'] ==  None

    def test_manual_srid():
        ds = mapnik.PostGIS(dbname=MAPNIK_TEST_DBNAME, srid=99, table='empty')
        fs = ds.features(mapnik.Query(mapnik.Box2d(-180,-90,180,90)))
        feature = None
        try:
            feature = fs.next()
        except StopIteration:
            pass
        assert feature ==  None
        meta = ds.describe()
        assert meta['srid'] ==  99
        assert meta.get('key_field') ==  None
        assert meta['encoding'] ==  u'UTF8'
        assert meta['geometry_type'] ==  None

    def test_geometry_detection():
        ds = mapnik.PostGIS(dbname=MAPNIK_TEST_DBNAME, table='test',
                            geometry_field='geom')
        meta = ds.describe()
        assert meta['srid'] ==  4326
        assert meta.get('key_field') ==  None
        assert meta['geometry_type'] ==  mapnik.DataGeometryType.Collection

        # will fail with postgis 2.0 because it automatically adds a geometry_columns entry
        # ds = mapnik.PostGIS(dbname=MAPNIK_TEST_DBNAME,table='test',
        #                   geometry_field='geom',
        #                    row_limit=1)
        # assert ds.describe()['geometry_type'] == mapnik.DataGeometryType.Point


    def test_that_nonexistant_query_field_throws(**kwargs):
        ds = mapnik.PostGIS(dbname=MAPNIK_TEST_DBNAME, table='empty')
        assert len(ds.fields()) ==  1
        assert ds.fields() ==  ['key']
        assert ds.field_types() ==  ['int']
        query = mapnik.Query(ds.envelope())

        for fld in ds.fields():
            query.add_property_name(fld)
            # also add an invalid one, triggering throw
            query.add_property_name('bogus')
        with pytest.raises(RuntimeError):
            ds.features(query)

    def test_auto_detection_of_unique_feature_id_32_bit():
        ds = mapnik.PostGIS(dbname=MAPNIK_TEST_DBNAME, table='test2',
                            geometry_field='geom',
                            autodetect_key_field=True)
        fs = ds.featureset()
        f = fs.next()
        assert len(ds.fields()) == len(f.attributes)
        assert f['manual_id'] ==  0
        assert fs.next()['manual_id'] ==  1
        assert fs.next()['manual_id'] ==  1000
        assert fs.next()['manual_id'] ==  -1000
        assert fs.next()['manual_id'] ==  2147483647
        assert fs.next()['manual_id'] ==  -2147483648

        fs = ds.featureset()
        assert fs.next().id() ==  0
        assert fs.next().id() ==  1
        assert fs.next().id() ==  1000
        assert fs.next().id() ==  -1000
        assert fs.next().id() ==  2147483647
        assert fs.next().id() ==  -2147483648
        meta = ds.describe()
        assert meta['srid'] ==  4326
        assert meta.get('key_field') ==  u'manual_id'
        assert meta['geometry_type'] ==  mapnik.DataGeometryType.Point

    def test_auto_detection_of_unique_feature_id_32_bit_no_attribute():
        ds = mapnik.PostGIS(dbname=MAPNIK_TEST_DBNAME, table='test2',
                            geometry_field='geom',
                            autodetect_key_field=True,
                            key_field_as_attribute=False)
        fs = ds.featureset()
        f = fs.next()
        assert len(ds.fields()) == len(f.attributes)
        assert len(ds.fields()) == 0
        assert len(f.attributes) == 0
        assert f.id() ==  0
        assert fs.next().id() ==  1
        assert fs.next().id() ==  1000
        assert fs.next().id() ==  -1000
        assert fs.next().id() ==  2147483647
        assert fs.next().id() ==  -2147483648
        meta = ds.describe()
        assert meta['srid'] ==  4326
        assert meta.get('key_field') ==  u'manual_id'
        assert meta['geometry_type'] ==  mapnik.DataGeometryType.Point

    def test_auto_detection_will_fail_since_no_primary_key():
        ds = mapnik.PostGIS(dbname=MAPNIK_TEST_DBNAME, table='test3',
                            geometry_field='geom',
                            autodetect_key_field=False)
        fs = ds.featureset()
        feat = fs.next()
        assert feat['manual_id'] ==  0
        assert feat['non_id'] == 9223372036854775807
        assert fs.next()['manual_id'] ==  1
        assert fs.next()['manual_id'] ==  1000
        assert fs.next()['manual_id'] ==  -1000
        assert fs.next()['manual_id'] ==  2147483647
        assert fs.next()['manual_id'] ==  -2147483648

        # since no valid primary key will be detected the fallback
        # is auto-incrementing counter
        fs = ds.featureset()
        assert fs.next().id() ==  1
        assert fs.next().id() ==  2
        assert fs.next().id() ==  3
        assert fs.next().id() ==  4
        assert fs.next().id() ==  5
        assert fs.next().id() ==  6

        meta = ds.describe()
        assert meta['srid'] ==  4326
        assert meta.get('key_field') ==  None
        assert meta['geometry_type'] ==  mapnik.DataGeometryType.Point


    def test_auto_detection_will_fail_and_should_throw():
        with pytest.raises(RuntimeError):
            ds = mapnik.PostGIS(dbname=MAPNIK_TEST_DBNAME, table='test3',
                                geometry_field='geom',
                                autodetect_key_field=True)
            ds.featureset()

    def test_auto_detection_of_unique_feature_id_64_bit():
        ds = mapnik.PostGIS(dbname=MAPNIK_TEST_DBNAME, table='test4',
                            geometry_field='geom',
                            autodetect_key_field=True)
        fs = ds.featureset()
        f = fs.next()
        assert len(ds.fields()) == len(f.attributes)
        assert f['manual_id'] ==  0
        assert fs.next()['manual_id'] ==  1
        assert fs.next()['manual_id'] ==  1000
        assert fs.next()['manual_id'] ==  -1000
        assert fs.next()['manual_id'] ==  2147483647
        assert fs.next()['manual_id'] ==  -2147483648

        fs = ds.featureset()
        assert fs.next().id() ==  0
        assert fs.next().id() ==  1
        assert fs.next().id() ==  1000
        assert fs.next().id() ==  -1000
        assert fs.next().id() ==  2147483647
        assert fs.next().id() ==  -2147483648

        meta = ds.describe()
        assert meta['srid'] ==  4326
        assert meta.get('key_field') ==  u'manual_id'
        assert meta['geometry_type'] ==  mapnik.DataGeometryType.Point

    def test_disabled_auto_detection_and_subquery():
        ds = mapnik.PostGIS(dbname=MAPNIK_TEST_DBNAME, table='''(select geom, 'a'::varchar as name from test2) as t''',
                            geometry_field='geom',
                            autodetect_key_field=False)
        fs = ds.featureset()
        feat = fs.next()
        assert feat.id() ==  1
        assert feat['name'] ==  'a'
        feat = fs.next()
        assert feat.id() ==  2
        assert feat['name'] ==  'a'
        feat = fs.next()
        assert feat.id() ==  3
        assert feat['name'] ==  'a'
        feat = fs.next()
        assert feat.id() ==  4
        assert feat['name'] ==  'a'
        feat = fs.next()
        assert feat.id() ==  5
        assert feat['name'] ==  'a'
        feat = fs.next()
        assert feat.id() ==  6
        assert feat['name'] ==  'a'

        meta = ds.describe()
        assert meta['srid'] ==  4326
        assert meta.get('key_field') ==  None
        assert meta['geometry_type'] ==  mapnik.DataGeometryType.Point

    def test_auto_detection_and_subquery_including_key():
        ds = mapnik.PostGIS(dbname=MAPNIK_TEST_DBNAME, table='''(select geom, manual_id from test2) as t''',
                            geometry_field='geom',
                            autodetect_key_field=True)
        fs = ds.featureset()
        f = fs.next()
        assert len(ds.fields()) == len(f.attributes)
        assert f['manual_id'] ==  0
        assert fs.next()['manual_id'] ==  1
        assert fs.next()['manual_id'] ==  1000
        assert fs.next()['manual_id'] ==  -1000
        assert fs.next()['manual_id'] ==  2147483647
        assert fs.next()['manual_id'] ==  -2147483648

        fs = ds.featureset()
        assert fs.next().id() ==  0
        assert fs.next().id() ==  1
        assert fs.next().id() ==  1000
        assert fs.next().id() ==  -1000
        assert fs.next().id() ==  2147483647
        assert fs.next().id() ==  -2147483648

        meta = ds.describe()
        assert meta['srid'] ==  4326
        assert meta.get('key_field') ==  u'manual_id'
        assert meta['geometry_type'] ==  mapnik.DataGeometryType.Point


    def test_auto_detection_of_invalid_numeric_primary_key():
        with pytest.raises(RuntimeError):
            mapnik.PostGIS(dbname=MAPNIK_TEST_DBNAME, table='''(select geom, manual_id::numeric from test2) as t''',
                           geometry_field='geom',
                           autodetect_key_field=True)


    def test_auto_detection_of_invalid_multiple_keys():
        with pytest.raises(RuntimeError):
            mapnik.PostGIS(dbname=MAPNIK_TEST_DBNAME, table='''test6''',
                           geometry_field='geom',
                           autodetect_key_field=True)


    def test_auto_detection_of_invalid_multiple_keys_subquery():
        with pytest.raises(RuntimeError):
            mapnik.PostGIS(dbname=MAPNIK_TEST_DBNAME, table='''(select first_id,second_id,geom from test6) as t''',
                           geometry_field='geom',
                           autodetect_key_field=True)

    def test_manually_specified_feature_id_field():
        ds = mapnik.PostGIS(dbname=MAPNIK_TEST_DBNAME, table='test4',
                            geometry_field='geom',
                            key_field='manual_id',
                            autodetect_key_field=True)
        fs = ds.featureset()
        f = fs.next()
        assert len(ds.fields()) == len(f.attributes)
        assert f['manual_id'] ==  0
        assert fs.next()['manual_id'] ==  1
        assert fs.next()['manual_id'] ==  1000
        assert fs.next()['manual_id'] ==  -1000
        assert fs.next()['manual_id'] ==  2147483647
        assert fs.next()['manual_id'] ==  -2147483648

        fs = ds.featureset()
        assert fs.next().id() ==  0
        assert fs.next().id() ==  1
        assert fs.next().id() ==  1000
        assert fs.next().id() ==  -1000
        assert fs.next().id() ==  2147483647
        assert fs.next().id() ==  -2147483648

        meta = ds.describe()
        assert meta['srid'] ==  4326
        assert meta.get('key_field') ==  u'manual_id'
        assert meta['geometry_type'] ==  mapnik.DataGeometryType.Point

    def test_numeric_type_feature_id_field():
        ds = mapnik.PostGIS(dbname=MAPNIK_TEST_DBNAME, table='test5',
                            geometry_field='geom',
                            autodetect_key_field=False)
        fs = ds.featureset()
        assert fs.next()['manual_id'] ==  -1
        assert fs.next()['manual_id'] ==  1

        fs = ds.featureset()
        assert fs.next().id() ==  1
        assert fs.next().id() ==  2

        meta = ds.describe()
        assert meta['srid'] ==  4326
        assert meta.get('key_field') ==  None
        assert meta['geometry_type'] ==  mapnik.DataGeometryType.Point

    def test_querying_table_with_mixed_case():
        ds = mapnik.PostGIS(dbname=MAPNIK_TEST_DBNAME, table='"tableWithMixedCase"',
                            geometry_field='geom',
                            autodetect_key_field=True)
        fs = ds.featureset()
        for id in range(1, 5):
            assert fs.next().id() ==  id

        meta = ds.describe()
        assert meta['srid'] ==  -1
        assert meta.get('key_field') ==  u'gid'
        assert meta['geometry_type'] ==  mapnik.DataGeometryType.Point

    def test_querying_subquery_with_mixed_case():
        ds = mapnik.PostGIS(dbname=MAPNIK_TEST_DBNAME, table='(SeLeCt * FrOm "tableWithMixedCase") as MixedCaseQuery',
                            geometry_field='geom',
                            autodetect_key_field=True)
        fs = ds.featureset()
        for id in range(1, 5):
            assert fs.next().id() ==  id

        meta = ds.describe()
        assert meta['srid'] ==  -1
        assert meta.get('key_field') ==  u'gid'
        assert meta['geometry_type'] ==  mapnik.DataGeometryType.Point

    def test_bbox_token_in_subquery1():
        ds = mapnik.PostGIS(dbname=MAPNIK_TEST_DBNAME, table='''
           (SeLeCt * FrOm "tableWithMixedCase" where geom && !bbox! ) as MixedCaseQuery''',
                            geometry_field='geom',
                            autodetect_key_field=True)
        fs = ds.featureset()
        for id in range(1, 5):
            assert fs.next().id() ==  id

        meta = ds.describe()
        assert meta['srid'] ==  -1
        assert meta.get('key_field') ==  u'gid'
        assert meta['geometry_type'] ==  mapnik.DataGeometryType.Point

    def test_bbox_token_in_subquery2():
        ds = mapnik.PostGIS(dbname=MAPNIK_TEST_DBNAME, table='''
           (SeLeCt * FrOm "tableWithMixedCase" where ST_Intersects(geom,!bbox!) ) as MixedCaseQuery''',
                            geometry_field='geom',
                            autodetect_key_field=True)
        fs = ds.featureset()
        for id in range(1, 5):
            assert fs.next().id() ==  id

        meta = ds.describe()
        assert meta['srid'] ==  -1
        assert meta.get('key_field') ==  u'gid'
        assert meta['geometry_type'] ==  mapnik.DataGeometryType.Point

    def test_empty_geom():
        ds = mapnik.PostGIS(dbname=MAPNIK_TEST_DBNAME, table='test7',
                            geometry_field='geom')
        fs = ds.featureset()
        assert fs.next()['gid'] ==  1

        meta = ds.describe()
        assert meta['srid'] ==  4326
        assert meta.get('key_field') ==  None
        assert meta['geometry_type'] ==  mapnik.DataGeometryType.Collection

    def create_ds():
        ds = mapnik.PostGIS(dbname=MAPNIK_TEST_DBNAME,
                            table='test',
                            max_size=20,
                            geometry_field='geom')
        fs = list(ds.all_features())
        assert len(fs) ==  8

        meta = ds.describe()
        assert meta['srid'] ==  4326
        assert meta.get('key_field') ==  None
        assert meta['geometry_type'] ==  mapnik.DataGeometryType.Collection

    def test_threaded_create(NUM_THREADS=100):
        # run one to start before thread loop
        # to ensure that a throw stops the test
        # from running all threads
        create_ds()
        runs = 0
        for i in range(NUM_THREADS):
            t = threading.Thread(target=create_ds)
            t.start()
            t.join()
            runs += 1
        assert runs ==  NUM_THREADS

    def create_ds_and_error():
        try:
            ds = mapnik.PostGIS(dbname=MAPNIK_TEST_DBNAME,
                                table='asdfasdfasdfasdfasdf',
                                max_size=20)
            ds.all_features()
        except Exception as e:
            assert 'in executeQuery' in str(e)

    def test_threaded_create2(NUM_THREADS=10):
        for i in range(NUM_THREADS):
            t = threading.Thread(target=create_ds_and_error)
            t.start()
            t.join()

    def test_that_64bit_int_fields_work():
        ds = mapnik.PostGIS(dbname=MAPNIK_TEST_DBNAME,
                            table='test8',
                            geometry_field='geom')
        assert len(ds.fields()) ==  2
        assert ds.fields(), ['gid' ==  'int_field']
        assert ds.field_types(), ['int' ==  'int']
        fs = ds.featureset()
        feat = fs.next()
        assert feat.id() ==  1
        assert feat['gid'] ==  1
        assert feat['int_field'] ==  2147483648
        feat = fs.next()
        assert feat.id() ==  2
        assert feat['gid'] ==  2
        assert feat['int_field'] ==  922337203685477580

        meta = ds.describe()
        assert meta['srid'] ==  -1
        assert meta.get('key_field') ==  None
        assert meta['geometry_type'] ==  mapnik.DataGeometryType.Point

    def test_persist_connection_off():
        # NOTE: max_size should be equal or greater than
        #       the pool size. There's currently no API to
        #       check nor set that size, but the current
        #       default is 20, so we use that value. See
        #       http://github.com/mapnik/mapnik/issues/863
        max_size = 20
        for i in range(0, max_size + 1):
            ds = mapnik.PostGIS(dbname=MAPNIK_TEST_DBNAME,
                                max_size=1,  # unused
                                persist_connection=False,
                                table='(select ST_MakePoint(0,0) as g, pg_backend_pid() as p, 1 as v) as w',
                                geometry_field='g')
            fs = ds.featureset()
            assert fs.next()['v'] ==  1

            meta = ds.describe()
            assert meta['srid'] ==  -1
            assert meta['geometry_type'] ==  mapnik.DataGeometryType.Point

    def test_null_comparision():
        ds = mapnik.PostGIS(dbname=MAPNIK_TEST_DBNAME, table='test9',
                            geometry_field='geom')
        fs = ds.featureset()
        feat = fs.next()

        meta = ds.describe()
        assert meta['srid'] ==  -1
        assert meta.get('key_field') ==  None
        assert meta['geometry_type'] ==  mapnik.DataGeometryType.Point

        assert feat['gid'] ==  1
        assert feat['name'] ==  'name'
        assert mapnik.Expression("[name] = 'name'").evaluate(feat)
        assert not mapnik.Expression("[name] = ''").evaluate(feat)
        assert not mapnik.Expression("[name] = null").evaluate(feat)
        assert not mapnik.Expression("[name] = true").evaluate(feat)
        assert not mapnik.Expression("[name] = false").evaluate(feat)
        assert not mapnik.Expression("[name] != 'name'").evaluate(feat)
        assert mapnik.Expression("[name] != ''").evaluate(feat)
        assert mapnik.Expression("[name] != null").evaluate(feat)
        assert mapnik.Expression("[name] != true").evaluate(feat)
        assert mapnik.Expression("[name] != false").evaluate(feat)

        feat = fs.next()
        assert feat['gid'] ==  2
        assert feat['name'] ==  ''
        assert mapnik.Expression("[name] = 'name'").evaluate(feat) ==  False
        assert mapnik.Expression("[name] = ''").evaluate(feat) ==  True
        assert mapnik.Expression("[name] = null").evaluate(feat) ==  False
        assert mapnik.Expression("[name] = true").evaluate(feat) ==  False
        assert mapnik.Expression("[name] = false").evaluate(feat) ==  False
        assert mapnik.Expression("[name] != 'name'").evaluate(feat) ==  True
        assert mapnik.Expression("[name] != ''").evaluate(feat) ==  False
        assert mapnik.Expression("[name] != null").evaluate(feat) ==  True
        assert mapnik.Expression("[name] != true").evaluate(feat) ==  True
        assert mapnik.Expression("[name] != false").evaluate(feat) ==  True

        feat = fs.next()
        assert feat['gid'] ==  3
        assert feat['name'] ==  None  # null
        assert mapnik.Expression("[name] = 'name'").evaluate(feat) ==  False
        assert mapnik.Expression("[name] = ''").evaluate(feat) ==  False
        assert mapnik.Expression("[name] = null").evaluate(feat) ==  True
        assert mapnik.Expression("[name] = true").evaluate(feat) ==  False
        assert mapnik.Expression("[name] = false").evaluate(feat) ==  False
        assert mapnik.Expression("[name] != 'name'").evaluate(feat) ==  True
        # https://github.com/mapnik/mapnik/issues/1859
        assert mapnik.Expression("[name] != ''").evaluate(feat) ==  False
        assert mapnik.Expression("[name] != null").evaluate(feat) ==  False
        assert mapnik.Expression("[name] != true").evaluate(feat) ==  True
        assert mapnik.Expression("[name] != false").evaluate(feat) ==  True

    def test_null_comparision2():
        ds = mapnik.PostGIS(dbname=MAPNIK_TEST_DBNAME, table='test10',
                            geometry_field='geom')
        fs = ds.featureset()
        feat = fs.next()

        meta = ds.describe()
        assert meta['srid'] ==  -1
        assert meta.get('key_field') ==  None
        assert meta['geometry_type'] ==  mapnik.DataGeometryType.Point

        assert feat['gid'] ==  1
        assert feat['bool_field']
        assert not mapnik.Expression("[bool_field] = 'name'").evaluate(feat)
        assert not mapnik.Expression("[bool_field] = ''").evaluate(feat)
        assert not mapnik.Expression("[bool_field] = null").evaluate(feat)
        assert mapnik.Expression("[bool_field] = true").evaluate(feat)
        assert not mapnik.Expression("[bool_field] = false").evaluate(feat)
        assert mapnik.Expression("[bool_field] != 'name'").evaluate(feat)
        assert mapnik.Expression("[bool_field] != ''").evaluate(feat)  # in 2.1.x used to be False
        assert mapnik.Expression("[bool_field] != null").evaluate(feat)  # in 2.1.x used to be False
        assert not mapnik.Expression("[bool_field] != true").evaluate(feat)
        assert mapnik.Expression("[bool_field] != false").evaluate(feat)

        feat = fs.next()
        assert feat['gid'] ==  2
        assert not feat['bool_field']
        assert not mapnik.Expression("[bool_field] = 'name'").evaluate(feat)
        assert not mapnik.Expression("[bool_field] = ''").evaluate(feat)
        assert not mapnik.Expression("[bool_field] = null").evaluate(feat)
        assert not mapnik.Expression("[bool_field] = true").evaluate(feat)
        assert mapnik.Expression("[bool_field] = false").evaluate(feat)
        assert mapnik.Expression("[bool_field] != 'name'").evaluate(feat)
        assert mapnik.Expression("[bool_field] != ''").evaluate(feat)
        assert mapnik.Expression("[bool_field] != null").evaluate(feat) # in 2.1.x used to be False
        assert mapnik.Expression("[bool_field] != true").evaluate(feat)
        assert not mapnik.Expression("[bool_field] != false").evaluate(feat)

        feat = fs.next()
        assert feat['gid'] ==  3
        assert feat['bool_field'] ==  None  # null
        assert not mapnik.Expression("[bool_field] = 'name'").evaluate(feat)
        assert not mapnik.Expression("[bool_field] = ''").evaluate(feat)
        assert mapnik.Expression("[bool_field] = null").evaluate(feat)
        assert not mapnik.Expression("[bool_field] = true").evaluate(feat)
        assert not mapnik.Expression("[bool_field] = false").evaluate(feat)
        assert mapnik.Expression("[bool_field] != 'name'").evaluate(feat) # in 2.1.x used to be False
        # https://github.com/mapnik/mapnik/issues/1859
        assert not mapnik.Expression("[bool_field] != ''").evaluate(feat)
        assert not mapnik.Expression("[bool_field] != null").evaluate(feat)
        assert mapnik.Expression("[bool_field] != true").evaluate(feat)  # in 2.1.x used to be False
        assert mapnik.Expression("[bool_field] != false").evaluate(feat) # in 2.1.x used to be False

    # https://github.com/mapnik/mapnik/issues/1816
    def test_exception_message_reporting():
        try:
            mapnik.PostGIS(dbname=MAPNIK_TEST_DBNAME, table='doesnotexist')
        except Exception as e:
            assert str(e) != 'unidentifiable C++ exception'

    def test_null_id_field():
        opts = {'type': 'postgis',
                'dbname': MAPNIK_TEST_DBNAME,
                'geometry_field': 'geom',
                'table': "(select null::bigint as osm_id, GeomFromEWKT('SRID=4326;POINT(0 0)') as geom) as tmp"}
        ds = mapnik.Datasource(**opts)
        fs = ds.featureset()
        feat = fs.next()
        assert feat.id() ==  int(1)
        assert feat['osm_id'] ==  None

        meta = ds.describe()
        assert meta['srid'] ==  4326
        assert meta.get('key_field') ==  None
        assert meta['geometry_type'] ==  mapnik.DataGeometryType.Point


    def test_null_key_field():
        opts = {'type': 'postgis',
                "key_field": 'osm_id',
                'dbname': MAPNIK_TEST_DBNAME,
                'geometry_field': 'geom',
                'table': "(select null::bigint as osm_id, GeomFromEWKT('SRID=4326;POINT(0 0)') as geom) as tmp"}
        ds = mapnik.Datasource(**opts)
        fs = ds.featureset()
        with pytest.raises(StopIteration):
            # should throw since key_field is null: StopIteration: No more
            # features.
            fs.next()

    def test_psql_error_should_not_break_connection_pool():
        # Bad request, will trigger an error when returning result
        ds_bad = mapnik.PostGIS(dbname=MAPNIK_TEST_DBNAME, table="""(SELECT geom as geom,label::int from test11) as failure_table""",
                                max_async_connection=5, geometry_field='geom', srid=4326)

        # Good request
        ds_good = mapnik.PostGIS(dbname=MAPNIK_TEST_DBNAME, table="test",
                                 max_async_connection=5, geometry_field='geom', srid=4326)

        # This will/should trigger a PSQL error
        failed = False
        try:
            fs = ds_bad.featureset()
            count = sum(1 for f in fs)
        except RuntimeError as e:
            assert 'invalid input syntax for type integer' in str(e)
            failed = True

        assert failed ==  True

        # Should be ok
        fs = ds_good.featureset()
        count = sum(1 for f in fs)
        assert count ==  8

    def test_psql_error_should_give_back_connections_opened_for_lower_layers_to_the_pool():
        map1 = mapnik.Map(600, 300)
        s = mapnik.Style()
        r = mapnik.Rule()
        r.symbols.append(mapnik.PolygonSymbolizer())
        s.rules.append(r)
        map1.append_style('style', s)

        # This layer will fail after a while
        buggy_s = mapnik.Style()
        buggy_r = mapnik.Rule()
        buggy_r.symbols.append(mapnik.PolygonSymbolizer())
        buggy_r.filter = mapnik.Expression("[fips] = 'FR'")
        buggy_s.rules.append(buggy_r)
        map1.append_style('style for buggy layer', buggy_s)
        buggy_layer = mapnik.Layer('this layer is buggy at runtime')
        # We ensure the query wille be long enough
        buggy_layer.datasource = mapnik.PostGIS(dbname=MAPNIK_TEST_DBNAME, table='(SELECT geom as geom, pg_sleep(0.1), fips::int from world_merc) as failure_tabl',
                                                max_async_connection=2, max_size=2, asynchronous_request=True, geometry_field='geom')
        buggy_layer.styles.append('style for buggy layer')

        # The query for this layer will be sent, then the previous layer will
        # raise an exception before results are read
        forced_canceled_layer = mapnik.Layer(
            'this layer will be canceled when an exception stops map rendering')
        forced_canceled_layer.datasource = mapnik.PostGIS(dbname=MAPNIK_TEST_DBNAME, table='world_merc',
                                                          max_async_connection=2, max_size=2, asynchronous_request=True, geometry_field='geom')
        forced_canceled_layer.styles.append('style')

        map1.layers.append(buggy_layer)
        map1.layers.append(forced_canceled_layer)
        map1.zoom_all()
        map2 = mapnik.Map(600, 300)
        map2.background = mapnik.Color('steelblue')
        s = mapnik.Style()
        r = mapnik.Rule()
        r.symbols.append(mapnik.LineSymbolizer())
        r.symbols.append(mapnik.LineSymbolizer())
        s.rules.append(r)
        map2.append_style('style', s)
        layer1 = mapnik.Layer('layer1')
        layer1.datasource = mapnik.PostGIS(dbname=MAPNIK_TEST_DBNAME, table='world_merc',
                                           max_async_connection=2, max_size=2, asynchronous_request=True, geometry_field='geom')
        layer1.styles.append('style')
        map2.layers.append(layer1)
        map2.zoom_all()

        # We expect this to trigger a PSQL error
        try:
            mapnik.render_to_file(
                map1, '/tmp/mapnik-postgis-test-map1.png', 'png')
            # Test must fail if error was not raised just above
            assert False ==  True
        except RuntimeError as e:
            assert 'invalid input syntax for type integer' in str(e)
            pass
        # This used to raise an exception before correction of issue 2042
        mapnik.render_to_file(map2, '/tmp/mapnik-postgis-test-map2.png', 'png')

    def test_handling_of_zm_dimensions():
        ds = mapnik.PostGIS(dbname=MAPNIK_TEST_DBNAME,
                            table='(select gid,ST_CoordDim(geom) as dim,name,geom from test12) as tmp',
                            geometry_field='geom')
        assert len(ds.fields()) ==  3
        assert ds.fields(), ['gid', 'dim' ==  'name']
        assert ds.field_types(), ['int', 'int' ==  'str']
        fs = ds.featureset()

        meta = ds.describe()
        assert meta['srid'] ==  4326
        assert meta.get('key_field') ==  None
        # Note: this is incorrect because we only check first couple geoms
        assert meta['geometry_type'] ==  mapnik.DataGeometryType.Point

        # Point (2d)
        feat = fs.next()
        assert feat.id() ==  1
        assert feat['gid'] ==  1
        assert feat['dim'] ==  2
        assert feat['name'] ==  'Point'
        assert feat.geometry.to_wkt() ==  'POINT(0 0)'

        # PointZ
        feat = fs.next()
        assert feat.id() ==  2
        assert feat['gid'] ==  2
        assert feat['dim'] ==  3
        assert feat['name'] ==  'PointZ'
        assert feat.geometry.to_wkt() ==  'POINT(0 0)'

        # PointM
        feat = fs.next()
        assert feat.id() ==  3
        assert feat['gid'] ==  3
        assert feat['dim'] ==  3
        assert feat['name'] ==  'PointM'
        assert feat.geometry.to_wkt() ==  'POINT(0 0)'

        # PointZM
        feat = fs.next()
        assert feat.id() ==  4
        assert feat['gid'] ==  4
        assert feat['dim'] ==  4
        assert feat['name'] ==  'PointZM'

        assert feat.geometry.to_wkt() ==  'POINT(0 0)'
        # MultiPoint
        feat = fs.next()
        assert feat.id() ==  5
        assert feat['gid'] ==  5
        assert feat['dim'] ==  2
        assert feat['name'] ==  'MultiPoint'
        assert feat.geometry.to_wkt() == 'MULTIPOINT(0 0,1 1)'

        # MultiPointZ
        feat = fs.next()
        assert feat.id() ==  6
        assert feat['gid'] ==  6
        assert feat['dim'] ==  3
        assert feat['name'] ==  'MultiPointZ'
        assert feat.geometry.to_wkt() == 'MULTIPOINT(0 0,1 1)'

        # MultiPointM
        feat = fs.next()
        assert feat.id() ==  7
        assert feat['gid'] ==  7
        assert feat['dim'] ==  3
        assert feat['name'] ==  'MultiPointM'
        assert feat.geometry.to_wkt() == 'MULTIPOINT(0 0,1 1)'

        # MultiPointZM
        feat = fs.next()
        assert feat.id() ==  8
        assert feat['gid'] ==  8
        assert feat['dim'] ==  4
        assert feat['name'] ==  'MultiPointZM'
        assert feat.geometry.to_wkt() == 'MULTIPOINT(0 0,1 1)'

        # LineString
        feat = fs.next()
        assert feat.id() ==  9
        assert feat['gid'] ==  9
        assert feat['dim'] ==  2
        assert feat['name'] ==  'LineString'
        assert feat.geometry.to_wkt() == 'LINESTRING(0 0,1 1)'

        # LineStringZ
        feat = fs.next()
        assert feat.id() ==  10
        assert feat['gid'] ==  10
        assert feat['dim'] ==  3
        assert feat['name'] ==  'LineStringZ'
        assert feat.geometry.to_wkt() == 'LINESTRING(0 0,1 1)'

        # LineStringM
        feat = fs.next()
        assert feat.id() ==  11
        assert feat['gid'] ==  11
        assert feat['dim'] ==  3
        assert feat['name'] ==  'LineStringM'
        assert feat.geometry.to_wkt() == 'LINESTRING(0 0,1 1)'

        # LineStringZM
        feat = fs.next()
        assert feat.id() ==  12
        assert feat['gid'] ==  12
        assert feat['dim'] ==  4
        assert feat['name'] ==  'LineStringZM'
        assert feat.geometry.to_wkt() == 'LINESTRING(0 0,1 1)'

        # Polygon
        feat = fs.next()
        assert feat.id() ==  13
        assert feat['gid'] ==  13
        assert feat['name'] ==  'Polygon'
        assert feat.geometry.to_wkt() == 'POLYGON((0 0,1 1,2 2,0 0))'

        # PolygonZ
        feat = fs.next()
        assert feat.id() ==  14
        assert feat['gid'] ==  14
        assert feat['name'] ==  'PolygonZ'
        assert feat.geometry.to_wkt() == 'POLYGON((0 0,1 1,2 2,0 0))'

        # PolygonM
        feat = fs.next()
        assert feat.id() ==  15
        assert feat['gid'] ==  15
        assert feat['name'] ==  'PolygonM'
        assert feat.geometry.to_wkt() == 'POLYGON((0 0,1 1,2 2,0 0))'

        # PolygonZM
        feat = fs.next()
        assert feat.id() ==  16
        assert feat['gid'] ==  16
        assert feat['name'] ==  'PolygonZM'
        assert feat.geometry.to_wkt() == 'POLYGON((0 0,1 1,2 2,0 0))'

        # MultiLineString
        feat = fs.next()
        assert feat.id() ==  17
        assert feat['gid'] ==  17
        assert feat['name'] ==  'MultiLineString'
        assert feat.geometry.to_wkt() == 'MULTILINESTRING((0 0,1 1),(2 2,3 3))'

        # MultiLineStringZ
        feat = fs.next()
        assert feat.id() ==  18
        assert feat['gid'] ==  18
        assert feat['name'] ==  'MultiLineStringZ'
        assert feat.geometry.to_wkt() == 'MULTILINESTRING((0 0,1 1),(2 2,3 3))'

        # MultiLineStringM
        feat = fs.next()
        assert feat.id() ==  19
        assert feat['gid'] ==  19
        assert feat['name'] ==  'MultiLineStringM'
        assert feat.geometry.to_wkt() == 'MULTILINESTRING((0 0,1 1),(2 2,3 3))'

        # MultiLineStringZM
        feat = fs.next()
        assert feat.id() ==  20
        assert feat['gid'] ==  20
        assert feat['name'] ==  'MultiLineStringZM'
        assert feat.geometry.to_wkt() == 'MULTILINESTRING((0 0,1 1),(2 2,3 3))'

        # MultiPolygon
        feat = fs.next()
        assert feat.id() ==  21
        assert feat['gid'] ==  21
        assert feat['name'] ==  'MultiPolygon'
        assert feat.geometry.to_wkt() == 'MULTIPOLYGON(((0 0,1 1,2 2,0 0)),((0 0,1 1,2 2,0 0)))'

        # MultiPolygonZ
        feat = fs.next()
        assert feat.id() ==  22
        assert feat['gid'] ==  22
        assert feat['name'] ==  'MultiPolygonZ'
        assert feat.geometry.to_wkt() == 'MULTIPOLYGON(((0 0,1 1,2 2,0 0)),((0 0,1 1,2 2,0 0)))'

        # MultiPolygonM
        feat = fs.next()
        assert feat.id() ==  23
        assert feat['gid'] ==  23
        assert feat['name'] ==  'MultiPolygonM'
        assert feat.geometry.to_wkt() == 'MULTIPOLYGON(((0 0,1 1,2 2,0 0)),((0 0,1 1,2 2,0 0)))'

        # MultiPolygonZM
        feat = fs.next()
        assert feat.id() ==  24
        assert feat['gid'] ==  24
        assert feat['name'] ==  'MultiPolygonZM'
        assert feat.geometry.to_wkt() == 'MULTIPOLYGON(((0 0,1 1,2 2,0 0)),((0 0,1 1,2 2,0 0)))'

    def test_handling_of_discarded_key_field():
        ds = mapnik.PostGIS(dbname=MAPNIK_TEST_DBNAME,
                            table='(select * from test12) as tmp',
                            key_field='gid',
                            key_field_as_attribute=False)
        fs = ds.featureset()
        feat = fs.next()
        assert feat['name'] == 'Point'

    def test_variable_in_subquery1():
        ds = mapnik.PostGIS(dbname=MAPNIK_TEST_DBNAME, table='''
           (select * from test where !@zoom! = 30 ) as tmp''',
                            geometry_field='geom', srid=4326,
                            autodetect_key_field=True)
        fs = ds.featureset(variables={'zoom': 30})
        for id in range(1, 5):
            assert fs.next().id() ==  id

        meta = ds.describe()
        assert meta['srid'] ==  4326
        assert meta.get('key_field') ==  "gid"
        assert meta['geometry_type'] ==  None

    # currently needs manual `geometry_table` passed
    # to avoid misparse of `geometry_table`
    # in the future ideally this would not need manual  `geometry_table`
    # https://github.com/mapnik/mapnik/issues/2718
    # currently `bogus` would be picked automatically for geometry_table
    def test_broken_parsing_of_comments():
        ds = mapnik.PostGIS(dbname=MAPNIK_TEST_DBNAME, table='''
             (select * FROM test) AS data
             -- select this from bogus''',
                            geometry_table='test')
        fs = ds.featureset()
        for id in range(1, 5):
            assert fs.next().id() ==  id

        meta = ds.describe()
        assert meta['srid'] ==  4326
        assert meta['geometry_type'] ==  mapnik.DataGeometryType.Collection

    # same
    # to avoid misparse of `geometry_table`
    # in the future ideally this would not need manual  `geometry_table`
    # https://github.com/mapnik/mapnik/issues/2718
    # currently nothing would be picked automatically for geometry_table
    def test_broken_parsing_of_comments():
        ds = mapnik.PostGIS(dbname=MAPNIK_TEST_DBNAME, table='''
             (select * FROM test) AS data
             -- select this from bogus.''',
                            geometry_table='test')
        fs = ds.featureset()
        for id in range(1, 5):
            assert fs.next().id() ==  id

        meta = ds.describe()
        assert meta['srid'] ==  4326
        assert meta['geometry_type'] ==  mapnik.DataGeometryType.Collection

    atexit.register(postgis_takedown)
