import os

mapnik_data_dir = os.path.dirname(os.path.realpath(__file__))

env = {}
icu_path = os.path.join(mapnik_data_dir, 'share', 'icu')
if os.path.isdir(icu_path):
    env['ICU_DATA'] = icu_path
gdal_path = os.path.join(mapnik_data_dir, 'share', 'gdal')
if os.path.isdir(gdal_path):
    env['GDAL_DATA'] = gdal_path
proj_path = os.path.join(mapnik_data_dir, 'share', 'proj')
if os.path.isdir(proj_path):
    env['PROJ_LIB'] = proj_path
