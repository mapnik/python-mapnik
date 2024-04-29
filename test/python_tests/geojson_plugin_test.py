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

if 'geojson' in mapnik.DatasourceCache.plugin_names():

    def test_geojson_init(setup):
        ds = mapnik.Datasource(
            type='geojson',
            file='../data/json/escaped.geojson')
        e = ds.envelope()
        assert e.minx == pytest.approx(-81.705583, abs=1e-7)
        assert e.miny == pytest.approx(41.480573, abs=1e-6)
        assert e.maxx == pytest.approx(-81.705583, abs=1e-5)
        assert e.maxy == pytest.approx(41.480573, abs=1e-3)

    def test_geojson_properties():
        ds = mapnik.Datasource(
            type='geojson',
            file='../data/json/escaped.geojson')
        f = list(ds.features_at_point(ds.envelope().center()))[0]
        assert len(ds.fields()) ==  11
        desc = ds.describe()
        assert desc['geometry_type'] ==  mapnik.DataGeometryType.Point

        assert f['name'] ==  u'Test'
        assert f['int'] ==  1
        assert f['description'] ==  u'Test: \u005C'
        assert f['spaces'] ==  u'this has spaces'
        assert f['double'] ==  1.1
        assert f['boolean'] ==  True
        assert f['NOM_FR'] ==  u'Qu\xe9bec'
        assert f['NOM_FR'] ==  u'Québec'

        ds = mapnik.Datasource(
            type='geojson',
            file='../data/json/escaped.geojson')
        f = list(iter(ds))[0]
        assert len(ds.fields()) ==  11

        desc = ds.describe()
        assert desc['geometry_type'] ==  mapnik.DataGeometryType.Point

        assert f['name'] ==  u'Test'
        assert f['int'] ==  1
        assert f['description'] ==  u'Test: \u005C'
        assert f['spaces'] ==  u'this has spaces'
        assert f['double'] ==  1.1
        assert f['boolean'] ==  True
        assert f['NOM_FR'] ==  u'Qu\xe9bec'
        assert f['NOM_FR'] ==  u'Québec'

    def test_large_geojson_properties():
        ds = mapnik.Datasource(
            type='geojson',
            file='../data/json/escaped.geojson',
            cache_features=False)
        f = list(ds.features_at_point(ds.envelope().center()))[0]
        assert len(ds.fields()) ==  11
        desc = ds.describe()
        assert desc['geometry_type'] ==  mapnik.DataGeometryType.Point

        assert f['name'] ==  u'Test'
        assert f['int'] ==  1
        assert f['description'] ==  u'Test: \u005C'
        assert f['spaces'] ==  u'this has spaces'
        assert f['double'] ==  1.1
        assert f['boolean'] ==  True
        assert f['NOM_FR'] ==  u'Qu\xe9bec'
        assert f['NOM_FR'] ==  u'Québec'

        ds = mapnik.Datasource(
            type='geojson',
            file='../data/json/escaped.geojson')
        f = list(iter(ds))[0]
        assert len(ds.fields()) ==  11

        desc = ds.describe()
        assert desc['geometry_type'] ==  mapnik.DataGeometryType.Point

        assert f['name'] ==  u'Test'
        assert f['int'] ==  1
        assert f['description'] ==  u'Test: \u005C'
        assert f['spaces'] ==  u'this has spaces'
        assert f['double'] ==  1.1
        assert f['boolean'] ==  True
        assert f['NOM_FR'] ==  u'Qu\xe9bec'
        assert f['NOM_FR'] ==  u'Québec'

    def test_geojson_from_in_memory_string():
        # will silently fail since it is a geometry and needs to be a featurecollection.
        #ds = mapnik.Datasource(type='geojson',inline='{"type":"LineString","coordinates":[[0,0],[10,10]]}')
        # works since it is a featurecollection
        ds = mapnik.Datasource(
            type='geojson',
            inline='{ "type":"FeatureCollection", "features": [ { "type":"Feature", "properties":{"name":"test"}, "geometry": { "type":"LineString","coordinates":[[0,0],[10,10]] } } ]}')
        assert len(ds.fields()) ==  1
        f = list(iter(ds))[0]
        desc = ds.describe()
        assert desc['geometry_type'] ==  mapnik.DataGeometryType.LineString
        assert f['name'] ==  u'test'

#    @raises(RuntimeError)
    def test_that_nonexistant_query_field_throws(**kwargs):
        ds = mapnik.Datasource(
            type='geojson',
            file='../data/json/escaped.geojson')
        assert len(ds.fields()) ==  11
        # TODO - this sorting is messed up
        #assert ds.fields(),['name', 'int', 'double', 'description', 'boolean' ==  'NOM_FR']
        #assert ds.field_types(),['str', 'int', 'float', 'str', 'bool' ==  'str']
# TODO - should geojson plugin throw like others?
#        query = mapnik.Query(ds.envelope())
#        for fld in ds.fields():
#            query.add_property_name(fld)
#        # also add an invalid one, triggering throw
#        query.add_property_name('bogus')
#        fs = ds.features(query)

    def test_parsing_feature_collection_with_top_level_properties():
        ds = mapnik.Datasource(
            type='geojson',
            file='../data/json/feature_collection_level_properties.json')
        f = list(iter(ds))[0]

        desc = ds.describe()
        assert desc['geometry_type'] ==  mapnik.DataGeometryType.Point
        assert f['feat_name'] ==  u'feat_value'
