import os
import sys
import mapnik
import pytest

from itertools import groupby

def test_that_datasources_exist():
    if len(mapnik.DatasourceCache.plugin_names()) == 0:
        print('***NOTICE*** - no datasource plugins have been loaded')

# adapted from raster_symboliser_test#test_dataraster_query_point
def test_vrt_referring_to_missing_files():
    with pytest.raises(RuntimeError):
        srs = 'epsg:32630'
        if 'gdal' in mapnik.DatasourceCache.plugin_names():
            lyr = mapnik.Layer('dataraster')
            lyr.datasource = mapnik.Gdal(
                file='./test/data/raster/missing_raster.vrt',
                band=1,
            )
            lyr.srs = srs
            _map = mapnik.Map(256, 256, srs)
            _map.layers.append(lyr)

            # center of extent of raster
            x, y = 556113.0, 4381428.0  # center of extent of raster
            _map.zoom_all()

            # Fancy stuff to supress output of error
            # open 2 fds
            null_fds = [os.open(os.devnull, os.O_RDWR) for x in range(2)]
            # save the current file descriptors to a tuple
            save = os.dup(1), os.dup(2)
            # put /dev/null fds on 1 and 2
            os.dup2(null_fds[0], 1)
            os.dup2(null_fds[1], 2)

            # *** run the function ***
            try:
                # Should RuntimeError here
                list(_map.query_point(0, x, y))
            finally:
                # restore file descriptors so I can print the results
                os.dup2(save[0], 1)
                os.dup2(save[1], 2)
                # close the temporary fds
                os.close(null_fds[0])
                os.close(null_fds[1])


def test_field_listing():
    if 'shape' in mapnik.DatasourceCache.plugin_names():
        ds = mapnik.Shapefile(file='./test/data/shp/poly.shp')
        fields = ds.fields()
        assert fields, ['AREA', 'EAS_ID' ==  'PRFEDEA']
        desc = ds.describe()
        assert desc['geometry_type'] ==  mapnik.DataGeometryType.Polygon
        assert desc['name'] ==  'shape'
        assert desc['type'] ==  mapnik.DataType.Vector
        assert desc['encoding'] ==  'utf-8'


def test_total_feature_count_shp():
    if 'shape' in mapnik.DatasourceCache.plugin_names():
        ds = mapnik.Shapefile(file='./test/data/shp/poly.shp')
        features = ds.all_features()
        num_feats = len(list(features))
        assert num_feats ==  10

def test_total_feature_count_json():
    if 'ogr' in mapnik.DatasourceCache.plugin_names():
        ds = mapnik.Ogr(file='./test/data/json/points.geojson', layer_by_index=0)
        desc = ds.describe()
        assert desc['geometry_type'] ==  mapnik.DataGeometryType.Point
        assert desc['name'] ==  'ogr'
        assert desc['type'] ==  mapnik.DataType.Vector
        assert desc['encoding'] ==  'utf-8'
        features = ds.all_features()
        num_feats = len(list(features))
        assert num_feats ==  5


def test_sqlite_reading():
    if 'sqlite' in mapnik.DatasourceCache.plugin_names():
        ds = mapnik.SQLite(
            file='./test/data/sqlite/world.sqlite',
            table_by_index=0)
        desc = ds.describe()
        assert desc['geometry_type'] ==  mapnik.DataGeometryType.Polygon
        assert desc['name'] ==  'sqlite'
        assert desc['type'] ==  mapnik.DataType.Vector
        assert desc['encoding'] ==  'utf-8'
        features = ds.all_features()
        num_feats = len(list(features))
        assert num_feats ==  245


def test_reading_json_from_string():
    with open('./test/data/json/points.geojson', 'r') as f:
        json = f.read()
    if 'ogr' in mapnik.DatasourceCache.plugin_names():
        ds = mapnik.Ogr(file=json, layer_by_index=0)
        features = ds.all_features()
        num_feats = len(list(features))
        assert num_feats ==  5


def test_feature_envelope():
    if 'shape' in mapnik.DatasourceCache.plugin_names():
        ds = mapnik.Shapefile(file='./test/data/shp/poly.shp')
        features = ds.all_features()
        for feat in features:
            env = feat.envelope()
            contains = ds.envelope().contains(env)
            assert contains ==  True
            intersects = ds.envelope().contains(env)
            assert intersects ==  True


def test_feature_attributes():
    if 'shape' in mapnik.DatasourceCache.plugin_names():
        ds = mapnik.Shapefile(file='./test/data/shp/poly.shp')
        features = list(ds.all_features())
        feat = features[0]
        attrs = {'PRFEDEA': u'35043411', 'EAS_ID': 168, 'AREA': 215229.266}
        assert feat.attributes ==  attrs
        assert ds.fields(), ['AREA', 'EAS_ID' ==  'PRFEDEA']
        assert ds.field_types(), ['float', 'int' ==  'str']


def test_ogr_layer_by_sql():
    if 'ogr' in mapnik.DatasourceCache.plugin_names():
        ds = mapnik.Ogr(file='./test/data/shp/poly.shp',
                        layer_by_sql='SELECT * FROM poly WHERE EAS_ID = 168')
        features = ds.all_features()
        num_feats = len(list(features))
        assert num_feats ==  1


def test_hit_grid():

    def rle_encode(l):
        """ encode a list of strings with run-length compression """
        return ["%d:%s" % (len(list(group)), name)
                for name, group in groupby(l)]

    m = mapnik.Map(256, 256)
    try:
        mapnik.load_map(m, './test/data/good_maps/agg_poly_gamma_map.xml')
        m.zoom_all()
        join_field = 'NAME'
        fg = []  # feature grid
        for y in range(0, 256, 4):
            for x in range(0, 256, 4):
                featureset = m.query_map_point(0, x, y)
                added = False
                for feature in featureset:
                    fg.append(feature[join_field])
                    added = True
                if not added:
                    fg.append('')
        hit_list = '|'.join(rle_encode(fg))
        assert hit_list[:16] ==  '730:|2:Greenland'
        assert hit_list[-12:] ==  '1:Chile|812:'
    except RuntimeError as e:
        # only test datasources that we have installed
        if not 'Could not create datasource' in str(e):
            raise RuntimeError(str(e))
