#! /usr/bin/env python

from distutils import sysconfig
from setuptools import setup, Extension
import os
import subprocess
import sys
import re

cflags = sysconfig.get_config_var('CFLAGS')
sysconfig._config_vars['CFLAGS'] = re.sub(' +', ' ', cflags.replace('-g', '').replace('-Os', ''))
opt = sysconfig.get_config_var('OPT')
sysconfig._config_vars['OPT'] = re.sub(' +', ' ', opt.replace('-g', '').replace('-Os', ''))
ldshared = sysconfig.get_config_var('LDSHARED')
sysconfig._config_vars['LDSHARED'] = re.sub(' +', ' ', ldshared.replace('-g', '').replace('-Os', '').replace('-arch i386', ''))
ldflags = sysconfig.get_config_var('LDFLAGS')
sysconfig._config_vars['LDFLAGS'] = re.sub(' +', ' ', ldflags.replace('-g', '').replace('-Os', '').replace('-arch i386', ''))

if os.environ.get("MASON_BUILD", "false") == "true":
    # run bootstrap.sh to get mason builds
    subprocess.call(['./bootstrap.sh'])
    mapnik_config = 'mason_packages/.link/bin/mapnik-config'
    mason_build = True
else:
    mapnik_config = 'mapnik-config'
    mason_build = False

boost_python_lib = os.environ.get("BOOST_PYTHON_LIB", 'boost_python')

try:
    linkflags = subprocess.check_output([mapnik_config, '--libs']).rstrip('\n').split(' ')
    lib_path = linkflags[0][2:]
    linkflags.extend(subprocess.check_output([mapnik_config, '--ldflags']).rstrip('\n').split(' '))
    linkflags.extend(['-Wl,-bind_at_load'])
except:
    raise Exception("Failed to find proper linking flags from mapnik config");

## Dynamically make the mapnik/paths.py file if it doesn't exist.
if os.path.isfile('mapnik/paths.py'):
    create_paths = False
else:
    create_paths = True
    f_paths = open('mapnik/paths.py', 'w')
    f_paths.write('import os\n')
    f_paths.write('\n')

if mason_build:
    lib_files = os.listdir(lib_path)
    lib_files = [os.path.join(lib_path, f) for f in lib_files if f.startswith('libmapnik.')]
    for f in lib_files:
        try:
            os.symlink(f, os.path.join('mapnik', os.path.basename(f)))
        except OSError:
            pass
    input_plugin_path = subprocess.check_output([mapnik_config, '--input-plugins']).rstrip('\n')
    try:
        os.symlink(input_plugin_path, os.path.join('mapnik', 'input'))
    except OSError:
        pass
    font_path = subprocess.check_output([mapnik_config, '--fonts']).rstrip('\n')
    try:
        os.symlink(input_plugin_path, os.path.join('mapnik', 'fonts'))
    except OSError:
        pass
    if create_paths:
        f_paths.write('mapniklibpath = os.path.dirname(os.path.realpath(__file__))\n')
elif create_paths:
    f_paths.write("mapniklibpath = '"+lib_path+"/mapnik'\n")
    f_paths.write('mapniklibpath = os.path.normpath(mapniklibpath)\n')

if create_paths:
    f_paths.write("inputpluginspath = os.path.join(mapniklibpath,'input')\n")
    f_paths.write("fontscollectionpath = os.path.join(mapniklibpath,'fonts')\n")
    f_paths.write("__all__ = [mapniklibpath,inputpluginspath,fontscollectionpath]\n")
    f_paths.close()


if not mason_build:
    icu_path = subprocess.check_output([mapnik_config, '--icu-data']).rstrip('\n')
else:
    icu_path = 'mason_packages/.link/share/icu/'
if icu_path:
    try:
        os.symlink(icu_path, os.path.join('mapnik', 'icu'))
    except OSError:
        pass

if not mason_build:
    gdal_path = subprocess.check_output([mapnik_config, '--gdal-data']).rstrip('\n')
else:
    gdal_path = 'mason_packages/.link/share/gdal/'
if gdal_path:
    try:
        os.symlink(gdal_path, os.path.join('mapnik', 'gdal'))
    except OSError:
        pass

if not mason_build:
    proj_path = subprocess.check_output([mapnik_config, '--proj-lib']).rstrip('\n')
else:
    proj_path = 'mason_packages/.link/share/proj/'
if proj_path:
    try:
        os.symlink(proj_path, os.path.join('mapnik', 'proj'))
    except OSError:
        pass

extra_comp_args = subprocess.check_output([mapnik_config, '--cflags']).rstrip('\n').split(' ')

if sys.platform == 'darwin':
    extra_comp_args.append('-mmacosx-version-min=10.8')
    linkflags.append('-mmacosx-version-min=10.8')

if not mason_build:
    os.environ["CC"] = subprocess.check_output([mapnik_config, '--cxx']).rstrip('\n')

setup(
    name = "mapnik",
    version = "0.1",
    packages = ['mapnik'],
    author = "Blake Thompson",
    author_email = "flippmoke@gmail.com",
    description = "Python bindings for Mapnik",
    license = "GNU LESSER GENERAL PUBLIC LICENSE",
    keywords = "mapnik mapbox mapping carteography",
    url = "http://mapnik.org/", 
    tests_require = [
        'nose',
    ],
    test_suite = 'nose.collector',
    ext_modules = [
        Extension('mapnik._mapnik', [
                'src/mapnik_color.cpp',
                'src/mapnik_coord.cpp',
                'src/mapnik_datasource.cpp',
                'src/mapnik_datasource_cache.cpp',
                'src/mapnik_envelope.cpp',
                'src/mapnik_expression.cpp',
                'src/mapnik_feature.cpp',
                'src/mapnik_featureset.cpp',
                'src/mapnik_font_engine.cpp',
                'src/mapnik_fontset.cpp',
                'src/mapnik_gamma_method.cpp',
                'src/mapnik_geometry.cpp',
                'src/mapnik_grid.cpp',
                'src/mapnik_grid_view.cpp',
                'src/mapnik_image.cpp',
                'src/mapnik_image_view.cpp',
                'src/mapnik_label_collision_detector.cpp',
                'src/mapnik_layer.cpp',
                'src/mapnik_logger.cpp',
                'src/mapnik_map.cpp',
                'src/mapnik_palette.cpp',
                'src/mapnik_parameters.cpp',
                'src/mapnik_proj_transform.cpp',
                'src/mapnik_projection.cpp',
                'src/mapnik_python.cpp',
                'src/mapnik_query.cpp',
                'src/mapnik_raster_colorizer.cpp',
                'src/mapnik_rule.cpp',
                'src/mapnik_scaling_method.cpp',
                'src/mapnik_style.cpp',
                'src/mapnik_svg_generator_grammar.cpp',
                'src/mapnik_symbolizer.cpp',
                'src/mapnik_text_placement.cpp',
                'src/mapnik_view_transform.cpp',
                'src/python_grid_utils.cpp',
            ],
            language='c++',
            libraries = [
                'mapnik', 
                'mapnik-wkt',
                'mapnik-json',
                'boost_thread',
                'boost_system',
                boost_python_lib,
            ],
            extra_compile_args = extra_comp_args,
            extra_link_args = linkflags,
        )
    ]
)
