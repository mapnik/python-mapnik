#! /usr/bin/env python

import os
import re
import shutil
import subprocess
import sys
from distutils import sysconfig

from setuptools import Extension, setup

PYTHON3 = sys.version_info[0] == 3


# Utils
def check_output(args):
    output = subprocess.check_output(args)
    if PYTHON3:
        # check_output returns bytes in PYTHON3.
        output = output.decode()
    return output.rstrip('\n')


cflags = sysconfig.get_config_var('CFLAGS')
sysconfig._config_vars['CFLAGS'] = re.sub(
    ' +', ' ', cflags.replace('-g', '').replace('-Os', '').replace('-arch i386', ''))
opt = sysconfig.get_config_var('OPT')
sysconfig._config_vars['OPT'] = re.sub(
    ' +', ' ', opt.replace('-g', '').replace('-Os', ''))
ldshared = sysconfig.get_config_var('LDSHARED')
sysconfig._config_vars['LDSHARED'] = re.sub(
    ' +', ' ', ldshared.replace('-g', '').replace('-Os', '').replace('-arch i386', ''))
ldflags = sysconfig.get_config_var('LDFLAGS')
sysconfig._config_vars['LDFLAGS'] = re.sub(
    ' +', ' ', ldflags.replace('-g', '').replace('-Os', '').replace('-arch i386', ''))
pycflags = sysconfig.get_config_var('PY_CFLAGS')
sysconfig._config_vars['PY_CFLAGS'] = re.sub(
    ' +', ' ', pycflags.replace('-g', '').replace('-Os', '').replace('-arch i386', ''))
sysconfig._config_vars['CFLAGSFORSHARED'] = ''
os.environ['ARCHFLAGS'] = ''

if os.environ.get("MASON_BUILD", "false") == "true":
    # run bootstrap.sh to get mason builds
    subprocess.call(['./bootstrap.sh'])
    mapnik_config = 'mason_packages/.link/bin/mapnik-config'
    mason_build = True
else:
    mapnik_config = 'mapnik-config'
    mason_build = False

boost_python_lib = os.environ.get("BOOST_PYTHON_LIB", 'boost_python-mt')
boost_system_lib = os.environ.get("BOOST_SYSTEM_LIB", 'boost_system-mt')
boost_thread_lib = os.environ.get("BOOST_THREAD_LIB", 'boost_thread-mt')

try:
    linkflags = check_output([mapnik_config, '--libs']).split(' ')
    lib_path = linkflags[0][2:]
    linkflags.extend(check_output([mapnik_config, '--ldflags']).split(' '))
except:
    raise Exception("Failed to find proper linking flags from mapnik config")

# Dynamically make the mapnik/paths.py file if it doesn't exist.
if os.path.isfile('mapnik/paths.py'):
    create_paths = False
else:
    create_paths = True
    f_paths = open('mapnik/paths.py', 'w')
    f_paths.write('import os\n')
    f_paths.write('\n')

if mason_build:
    try:
        if sys.platform == 'darwin':
            base_f = 'libmapnik.dylib'
        else:
            base_f = 'libmapnik.so.3.0'
        f = os.path.join(lib_path, base_f)
        shutil.copyfile(f, os.path.join('mapnik', base_f))
    except shutil.Error:
        pass
    input_plugin_path = check_output([mapnik_config, '--input-plugins'])
    input_plugin_files = os.listdir(input_plugin_path)
    input_plugin_files = [os.path.join(
        input_plugin_path, f) for f in input_plugin_files]
    if not os.path.exists(os.path.join('mapnik', 'plugins', 'input')):
        os.makedirs(os.path.join('mapnik', 'plugins', 'input'))
    for f in input_plugin_files:
        try:
            shutil.copyfile(f, os.path.join(
                'mapnik', 'plugins', 'input', os.path.basename(f)))
        except shutil.Error:
            pass
    font_path = check_output([mapnik_config, '--fonts'])
    font_files = os.listdir(font_path)
    font_files = [os.path.join(font_path, f) for f in font_files]
    if not os.path.exists(os.path.join('mapnik', 'plugins', 'fonts')):
        os.makedirs(os.path.join('mapnik', 'plugins', 'fonts'))
    for f in font_files:
        try:
            shutil.copyfile(f, os.path.join(
                'mapnik', 'plugins', 'fonts', os.path.basename(f)))
        except shutil.Error:
            pass
    if create_paths:
        f_paths.write(
            'mapniklibpath = os.path.join(os.path.dirname(os.path.realpath(__file__)), "plugins")\n')
elif create_paths:
    f_paths.write("mapniklibpath = '" + lib_path + "/mapnik'\n")
    f_paths.write('mapniklibpath = os.path.normpath(mapniklibpath)\n')

if create_paths:
    f_paths.write("inputpluginspath = os.path.join(mapniklibpath,'input')\n")
    f_paths.write(
        "fontscollectionpath = os.path.join(mapniklibpath,'fonts')\n")
    f_paths.write(
        "__all__ = [mapniklibpath,inputpluginspath,fontscollectionpath]\n")
    f_paths.close()


if not mason_build:
    icu_path = check_output([mapnik_config, '--icu-data'])
else:
    icu_path = 'mason_packages/.link/share/icu/'
if icu_path:
    icu_files = os.listdir(icu_path)
    icu_files = [os.path.join(icu_path, f) for f in icu_files]
    if not os.path.exists(os.path.join('mapnik', 'plugins', 'icu')):
        os.makedirs(os.path.join('mapnik', 'plugins', 'icu'))
    for f in icu_files:
        try:
            shutil.copyfile(f, os.path.join(
                'mapnik', 'plugins', 'icu', os.path.basename(f)))
        except shutil.Error:
            pass

if not mason_build:
    gdal_path = check_output([mapnik_config, '--gdal-data'])
else:
    gdal_path = 'mason_packages/.link/share/gdal/'
    if os.path.exists('mason_packages/.link/share/gdal/gdal/'):
        gdal_path = 'mason_packages/.link/share/gdal/gdal/'
if gdal_path:
    gdal_files = os.listdir(gdal_path)
    gdal_files = [os.path.join(gdal_path, f) for f in gdal_files]
    if not os.path.exists(os.path.join('mapnik', 'plugins', 'gdal')):
        os.makedirs(os.path.join('mapnik', 'plugins', 'gdal'))
    for f in gdal_files:
        try:
            shutil.copyfile(f, os.path.join(
                'mapnik', 'plugins', 'gdal', os.path.basename(f)))
        except shutil.Error:
            pass

if not mason_build:
    proj_path = check_output([mapnik_config, '--proj-lib'])
else:
    proj_path = 'mason_packages/.link/share/proj/'
    if os.path.exists('mason_packages/.link/share/proj/proj/'):
        proj_path = 'mason_packages/.link/share/proj/proj/'
if proj_path:
    proj_files = os.listdir(proj_path)
    proj_files = [os.path.join(proj_path, f) for f in proj_files]
    if not os.path.exists(os.path.join('mapnik', 'plugins', 'proj')):
        os.makedirs(os.path.join('mapnik', 'plugins', 'proj'))
    for f in proj_files:
        try:
            shutil.copyfile(f, os.path.join(
                'mapnik', 'plugins', 'proj', os.path.basename(f)))
        except shutil.Error:
            pass

extra_comp_args = check_output([mapnik_config, '--cflags']).split(' ')

if sys.platform == 'darwin':
    extra_comp_args.append('-mmacosx-version-min=10.8')
    # silence warning coming from boost python macros which
    # would is hard to silence via pragma
    extra_comp_args.append('-Wno-parentheses-equality')
    linkflags.append('-mmacosx-version-min=10.8')
else:
    linkflags.append('-lrt')
    linkflags.append('-Wl,-z,origin')
    linkflags.append('-Wl,-rpath=$ORIGIN')

if os.environ.get("CC", False) == False:
    os.environ["CC"] = check_output([mapnik_config, '--cxx'])
if os.environ.get("CXX", False) == False:
    os.environ["CXX"] = check_output([mapnik_config, '--cxx'])

setup(
    name="mapnik",
    version="0.1",
    packages=['mapnik'],
    author="Blake Thompson",
    author_email="flippmoke@gmail.com",
    description="Python bindings for Mapnik",
    license="GNU LESSER GENERAL PUBLIC LICENSE",
    keywords="mapnik mapbox mapping carteography",
    url="http://mapnik.org/",
    tests_require=[
        'nose',
    ],
    package_data={
        'mapnik': ['libmapnik.*', 'plugins/*/*'],
    },
    test_suite='nose.collector',
    ext_modules=[
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
            libraries=[
                'mapnik',
                'mapnik-wkt',
                'mapnik-json',
                boost_python_lib,
                boost_thread_lib,
                boost_system_lib
        ],
            extra_compile_args=extra_comp_args,
            extra_link_args=linkflags,
        )
    ]
)
