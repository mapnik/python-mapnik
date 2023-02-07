import mapnik

try:
    import itertools.izip as zip
except ImportError:
    pass


# TODO - fix truncation in shapefile...
polys = ["POLYGON ((30 10, 10 20, 20 40, 40 40, 30 10))",
         "POLYGON ((35 10, 10 20, 15 40, 45 45, 35 10),(20 30, 35 35, 30 20, 20 30))",
         "MULTIPOLYGON (((30 20, 10 40, 45 40, 30 20)),((15 5, 40 10, 10 20, 5 10, 15 5)))"
         "MULTIPOLYGON (((40 40, 20 45, 45 30, 40 40)),((20 35, 45 20, 30 5, 10 10, 10 30, 20 35),(30 20, 20 25, 20 15, 30 20)))"
         ]

plugins = mapnik.DatasourceCache.plugin_names()
if 'shape' in plugins and 'ogr' in plugins:

    def ensure_geometries_are_interpreted_equivalently(filename):
        ds1 = mapnik.Ogr(file=filename, layer_by_index=0)
        ds2 = mapnik.Shapefile(file=filename)
        fs1 = ds1.featureset()
        fs2 = ds2.featureset()
        count = 0
        for feat1, feat2 in zip(fs1, fs2):
            count += 1
            assert feat1.attributes == feat2.attributes
            assert feat1.to_geojson() == feat2.to_geojson()
            assert feat1.geometry.to_wkt() == feat2.geometry.to_wkt()
            assert feat1.geometry.to_wkb(mapnik.wkbByteOrder.NDR) == feat2.geometry.to_wkb(mapnik.wkbByteOrder.NDR)
            assert feat1.geometry.to_wkb(mapnik.wkbByteOrder.XDR) == feat2.geometry.to_wkb(mapnik.wkbByteOrder.XDR)

    def test_simple_polys():
        ensure_geometries_are_interpreted_equivalently(
            './test/data/shp/wkt_poly.shp')
