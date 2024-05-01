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

if 'shape' in mapnik.DatasourceCache.plugin_names():

    # Shapefile initialization
    def test_shapefile_init(setup):
        s = mapnik.Shapefile(file='../data/shp/boundaries')
        e = s.envelope()
        assert e.minx == pytest.approx(-11121.6896651, abs=1e-07)
        assert e.miny == pytest.approx( -724724.216526, abs=1e-6)
        assert e.maxx == pytest.approx( 2463000.67866, abs=1e-5)
        assert e.maxy == pytest.approx( 1649661.267, abs=1e-3)

    # Shapefile properties
    def test_shapefile_properties():
        s = mapnik.Shapefile(file='../data/shp/boundaries', encoding='latin1')
        f = list(s.features_at_point(s.envelope().center()))[0]

        assert f['CGNS_FID'] ==  u'6f733341ba2011d892e2080020a0f4c9'
        assert f['COUNTRY'] ==  u'CAN'
        assert f['F_CODE'] ==  u'FA001'
        assert f['NAME_EN'] ==  u'Quebec'
        # this seems to break if icu data linking is not working
        assert f['NOM_FR'] ==  u'Qu\xe9bec'
        assert f['NOM_FR'] ==  u'Québec'
        assert f['Shape_Area'] ==  1512185733150.0
        assert f['Shape_Leng'] ==  19218883.724300001


    def test_that_nonexistant_query_field_throws(**kwargs):
        ds = mapnik.Shapefile(file='../data/shp/world_merc')
        assert len(ds.fields()) ==  11
        assert ds.fields() == ['FIPS', 'ISO2', 'ISO3', 'UN', 'NAME',
                               'AREA', 'POP2005', 'REGION', 'SUBREGION', 'LON', 'LAT']
        assert ds.field_types() == ['str','str','str','int','str','int','int','int','int','float','float']
        query = mapnik.Query(ds.envelope())
        with pytest.raises(RuntimeError):
            for fld in ds.fields():
                query.add_property_name(fld)
                # also add an invalid one, triggering throw
                query.add_property_name('bogus')
                ds.features(query)

    def test_dbf_logical_field_is_boolean():
        ds = mapnik.Shapefile(file='../data/shp/long_lat')
        assert len(ds.fields()) ==  7
        assert ds.fields() == ['LONG', 'LAT', 'LOGICAL_TR', 'LOGICAL_FA', 'CHARACTER', 'NUMERIC', 'DATE']
        assert ds.field_types() == ['str', 'str', 'bool', 'bool', 'str', 'float', 'str']
        query = mapnik.Query(ds.envelope())
        for fld in ds.fields():
            query.add_property_name(fld)
        feat = list(iter(ds))[0]
        assert feat.id() ==  1
        assert feat['LONG'] ==  '0'
        assert feat['LAT'] ==  '0'
        assert feat['LOGICAL_TR'] ==  True
        assert feat['LOGICAL_FA'] ==  False
        assert feat['CHARACTER'] ==  '254'
        assert feat['NUMERIC'] ==  32
        assert feat['DATE'] ==  '20121202'

    # created by hand in qgis 1.8.0
    def test_shapefile_point2d_from_qgis():
        ds = mapnik.Shapefile(file='../data/shp/points/qgis.shp')
        assert len(ds.fields()) ==  2
        assert ds.fields(), ['id' ==  'name']
        assert ds.field_types(), ['int' ==  'str']
        assert len(list(iter(ds))) ==  3

    # ogr2ogr tests/data/shp/3dpoint/ogr_zfield.shp
    # tests/data/shp/3dpoint/qgis.shp -zfield id
    def test_shapefile_point_z_from_qgis():
        ds = mapnik.Shapefile(file='../data/shp/points/ogr_zfield.shp')
        assert len(ds.fields()) ==  2
        assert ds.fields(), ['id' ==  'name']
        assert ds.field_types(), ['int' ==  'str']
        assert len(list(iter(ds))) ==  3

    def test_shapefile_multipoint_from_qgis():
        ds = mapnik.Shapefile(file='../data/shp/points/qgis_multi.shp')
        assert len(ds.fields()) ==  2
        assert ds.fields(), ['id' ==  'name']
        assert ds.field_types(), ['int' ==  'str']
        assert len(list(iter(ds))) ==  1

    # pointzm from arcinfo
    def test_shapefile_point_zm_from_arcgis():
        ds = mapnik.Shapefile(file='../data/shp/points/poi.shp')
        assert len(ds.fields()) ==  7
        assert ds.fields() == ['interst_id',
                               'state_d',
                               'cnty_name',
                               'latitude',
                               'longitude',
                               'Name',
                               'Website']
        assert ds.field_types() == ['str', 'str', 'str', 'float', 'float', 'str', 'str']
        assert len(list(iter(ds))) ==  17

    # copy of the above with ogr2ogr that makes m record 14 instead of 18
    def test_shapefile_point_zm_from_ogr():
        ds = mapnik.Shapefile(file='../data/shp/points/poi_ogr.shp')
        assert len(ds.fields()) ==  7
        assert ds.fields(),['interst_id',
                            'state_d',
                            'cnty_name',
                            'latitude',
                            'longitude',
                            'Name',
                            'Website']
        assert ds.field_types() == ['str', 'str', 'str', 'float', 'float', 'str', 'str']
        assert len(list(iter(ds))) ==  17
