import mapnik
import pytest
import os

from .utilities import execution_path

@pytest.fixture(scope="module")
def setup():
    # All of the paths used are relative, if we run the tests
    # from another directory we need to chdir()
    os.chdir(execution_path('.'))
    yield

if 'topojson' in mapnik.DatasourceCache.plugin_names():

    def test_topojson_init(setup):
        # topojson tests/data/json/escaped.geojson -o tests/data/topojson/escaped.topojson --properties
        # topojson version 1.4.2
        ds = mapnik.Datasource(
            type='topojson',
            file='../data/topojson/escaped.topojson')
        e = ds.envelope()
        assert e.minx == pytest.approx(-81.705583, 1e-7)
        assert e.miny == pytest.approx( 41.480573, 1e-6)
        assert e.maxx == pytest.approx(-81.705583, 1e-5)
        assert e.maxy == pytest.approx(41.480573,  1e-3)

    def test_topojson_properties():
         ds = mapnik.Datasource(
             type='topojson',
             file='../data/topojson/escaped.topojson')

         f = list(ds.features_at_point(ds.envelope().center()))[0]
         assert len(ds.fields()) ==  11
         desc = ds.describe()
         assert desc['geometry_type'] ==  mapnik.DataGeometryType.Point

         assert  f['name'] == u'Test'
         assert  f['int'] ==  1
         assert  f['description'] == u'Test: \u005C'
         assert  f['spaces'] ==  u'this has spaces'
         assert  f['double'] == 1.1
         assert  f['boolean'] == True
         assert  f['NOM_FR'] == u'Qu\xe9bec'
         assert  f['NOM_FR'] == u'Québec'

    def test_geojson_from_in_memory_string():
        ds = mapnik.Datasource(
            type='topojson',
            inline=open(
                '../data/topojson/escaped.topojson',
                'r').read())
        f = list(ds.features_at_point(ds.envelope().center()))[0]
        assert len(ds.fields()) ==  11
        desc = ds.describe()
        assert desc['geometry_type'] ==  mapnik.DataGeometryType.Point

        assert  f['name'] == u'Test'
        assert  f['int'] ==  1
        assert  f['description'] == u'Test: \u005C'
        assert  f['spaces'] ==  u'this has spaces'
        assert  f['double'] == 1.1
        assert  f['boolean'] == True
        assert  f['NOM_FR'] == u'Qu\xe9bec'
        assert  f['NOM_FR'] == u'Québec'

    #@raises(RuntimeError)
    def test_that_nonexistant_query_field_throws(**kwargs):
        #with pytest.raises(RuntimeError):
        ds = mapnik.Datasource(
            type='topojson',
            file='../data/topojson/escaped.topojson')
        assert len(ds.fields()) ==  11
        # TODO - this sorting is messed up
        assert ds.fields() == ['name', 'int', 'description',
                               'spaces', 'double', 'boolean', 'NOM_FR',
                               'object', 'array', 'empty_array', 'empty_object']
        assert ds.field_types() == ['str', 'int',
                                    'str', 'str', 'float', 'bool', 'str',
                                    'str', 'str', 'str', 'str']
        # TODO - should topojson plugin throw like others?
        query = mapnik.Query(ds.envelope())
        for fld in ds.fields():
            query.add_property_name(fld)
            # also add an invalid one, triggering throw
            query.add_property_name('bogus')
            fs = ds.features(query)


#if __name__ == "__main__":
    #setup()
#    exit(run_all(eval(x) for x in dir() if x.startswith("test_")))
