import os
mapnik_data_dir = os.path.dirname(os.path.realpath(__file__))
env = {
    'ICU_DATA': os.path.join(mapnik_data_dir, 'icu'),
    'GDAL_DATA': os.path.join(mapnik_data_dir, 'gdal'),
    'PROJ_LIB': os.path.join(mapnik_data_dir, 'proj')
}

