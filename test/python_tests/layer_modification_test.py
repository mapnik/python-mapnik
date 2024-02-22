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

def test_adding_datasource_to_layer(setup):
    map_string = '''<?xml version="1.0" encoding="utf-8"?>
<Map>

    <Layer name="world_borders">
        <StyleName>world_borders_style</StyleName>
        <StyleName>point_style</StyleName>
        <!-- leave datasource empty -->
        <!--
        <Datasource>
            <Parameter name="file">../data/shp/world_merc.shp</Parameter>
            <Parameter name="type">shape</Parameter>
        </Datasource>
        -->
    </Layer>

</Map>
'''
    m = mapnik.Map(256, 256)

    try:
        mapnik.load_map_from_string(m, map_string)

        # validate it loaded fine
        assert m.layers[0].styles[0] ==  'world_borders_style'
        assert m.layers[0].styles[1] ==  'point_style'
        assert len(m.layers) ==  1

        # also assign a variable reference to that layer
        # below we will test that this variable references
        # the same object that is attached to the map
        lyr = m.layers[0]

        # ensure that there was no datasource for the layer...
        assert m.layers[0].datasource ==  None
        assert lyr.datasource ==  None

        # also note that since the srs was black it defaulted to wgs84
        assert m.layers[0].srs == 'epsg:4326'
        assert lyr.srs ==  'epsg:4326'

        # now add a datasource one...
        ds = mapnik.Shapefile(file='../data/shp/world_merc.shp')
        m.layers[0].datasource = ds

        # now ensure it is attached
        assert m.layers[0].datasource.describe()['name'] ==  "shape"
        assert lyr.datasource.describe()['name'] ==  "shape"

        # and since we have now added a shapefile in spherical mercator, adjust
        # the projection
        lyr.srs = '+proj=merc +lon_0=0 +lat_ts=0 +x_0=0 +y_0=0 +ellps=WGS84 +datum=WGS84 +units=m +no_defs'

        # test that assignment
        assert m.layers[0].srs == '+proj=merc +lon_0=0 +lat_ts=0 +x_0=0 +y_0=0 +ellps=WGS84 +datum=WGS84 +units=m +no_defs'
        assert lyr.srs ==  '+proj=merc +lon_0=0 +lat_ts=0 +x_0=0 +y_0=0 +ellps=WGS84 +datum=WGS84 +units=m +no_defs'
    except RuntimeError as e:
        # only test datasources that we have installed
        if not 'Could not create datasource' in str(e):
            raise RuntimeError(e)
