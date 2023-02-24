import os
from glob import glob
import mapnik

plugin_mapping = {
    '.csv': ['csv'],
    '.json': ['geojson', 'ogr'],
    '.tif': ['gdal'],
    #'.tif' : ['gdal','raster'],
    '.kml': ['ogr'],
    '.gpx': ['ogr'],
    '.vrt': ['gdal']
}


def test_opening_data():
    # https://github.com/mapbox/mapnik-test-data
    # cd tests/data
    # git clone --depth 1 https://github.com/mapbox/mapnik-test-data
    if os.path.exists('../data/mapnik-test-data/'):
        files = glob('../data/mapnik-test-data/data/*/*.*')
        for filepath in files:
            ext = os.path.splitext(filepath)[1]
            if plugin_mapping.get(ext):
                # print 'testing opening %s' % filepath
                if 'topo' in filepath:
                    kwargs = {'type': 'ogr', 'file': filepath}
                    kwargs['layer_by_index'] = 0
                    try:
                        mapnik.Datasource(**kwargs)
                    except Exception as e:
                        print('could not open, %s: %s' % (kwargs, e))
                else:
                    for plugin in plugin_mapping[ext]:
                        kwargs = {'type': plugin, 'file': filepath}
                        if plugin == 'ogr':
                            kwargs['layer_by_index'] = 0
                        try:
                            mapnik.Datasource(**kwargs)
                        except Exception as e:
                            print('could not open, %s: %s' % (kwargs, e))
            # else:
            #    print 'skipping opening %s' % filepath
