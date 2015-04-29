#! /usr/bin/env python

# monkey-patch for parallel compilation
def parallelCCompile(self, sources, output_dir=None, macros=None, include_dirs=None, debug=0, extra_preargs=None, extra_postargs=None, depends=None):
    # those lines are copied from distutils.ccompiler.CCompiler directly
    macros, objects, extra_postargs, pp_opts, build = self._setup_compile(output_dir, macros, include_dirs, sources, depends, extra_postargs)
    cc_args = self._get_cc_args(pp_opts, debug, extra_preargs)
    # parallel code
    import multiprocessing
    import multiprocessing.pool
    N=multiprocessing.cpu_count() # number of parallel compilations
    def _single_compile(obj):
        try: src, ext = build[obj]
        except KeyError: return
        self._compile(obj, src, ext, cc_args, extra_postargs, pp_opts)
    # convert to list, imap is evaluated on-demand
    list(multiprocessing.pool.ThreadPool(N).imap(_single_compile,objects))
    return objects
import distutils.ccompiler
distutils.ccompiler.CCompiler.compile=parallelCCompile

from setuptools import setup, Extension
import os
import subprocess
import sys

# run bootstrap.sh to get 

if os.environ.get("MASON_BUILD", "false") == "true":
    subprocess.call(['./bootstrap.sh'])
    mapnik_config = 'mason_packages/.link/bin/mapnik-config'
else:
    mapnik_config = 'mapnik-config'

boost_python_lib = os.environ.get("BOOST_PYTHON_LIB", 'boost_python')

try:
    linkflags = subprocess.check_output([mapnik_config, '--libs']).rstrip('\n').split(' ')
    lib_path = linkflags[0][2:]
    linkflags.extend(subprocess.check_output([mapnik_config, '--ldflags']).rstrip('\n').split(' '))
    linkflags.extend(['-Wl','-bind_at_load'])
except:
    linkflags = []

try:
    lib_files = os.listdir(lib_path)
    lib_files = [os.path.join(lib_path, f) for f in lib_files if f.startswith('libmapnik.')]
except:
    lib_files = []

try:
    input_plugin_path = subprocess.check_output([mapnik_config, '--input-plugins']).rstrip('\n')
    input_plugin_files = os.listdir(input_plugin_path)
    input_plugin_files = [os.path.join(input_plugin_path,f) for f in input_plugin_files]
except:
    input_plugin_files = []
try:
    font_path = subprocess.check_output([mapnik_config, '--fonts']).rstrip('\n')
    font_files = os.listdir(font_path)
    font_files = [os.path.join(font_path,f) for f in font_files]
except:
    font_files = []

try:
    if os.environ.get("ICU_DATA", False):
        icu_path = os.environ["ICU_DATA"]
        icu_files = os.listdir(icu_path)
        icu_files = [os.path.join(icu_path,f) for f in icu_files]
    else:
        icu_path = subprocess.check_output([mapnik_config, '--icu-data']).rstrip('\n')
        if icu_path:
            icu_files = os.listdir(icu_path)
            icu_files = [os.path.join(icu_path,f) for f in icu_files]
        else:
            icu_files = []
except:
    icu_files = []

try:
    if os.environ.get("GDAL_DATA", False):
        gdal_path = os.environ["GDAL_DATA"]
        gdal_files = os.listdir(gdal_path)
        gdal_files = [os.path.join(gdal_path,f) for f in gdal_files]
    else:
        gdal_path = subprocess.check_output([mapnik_config, '--gdal-data']).rstrip('\n')
        if gdal_path:
            gdal_files = os.listdir(gdal_path)
            gdal_files = [os.path.join(gdal_path,f) for f in gdal_files]
        else:
            gdal_files = []
except:
    gdal_files = []

try:
    if os.environ.get("PROJ_LIB", False):
        proj_path = os.environ["PROJ_LIB"]
        proj_files = os.listdir(proj_path)
        proj_files = [os.path.join(proj_path,f) for f in gdal_files]
    else:
        proj_path = subprocess.check_output([mapnik_config, '--proj-lib']).rstrip('\n')
        if not proj_path:
            if os.path.isdir('/usr/local/share/proj'):
                proj_path = '/usr/local/share/proj'
            elif os.path.isdir('/usr/share/proj'):
                proj_path = '/usr/share/proj'
        if proj_path:
            proj_files = os.listdir(proj_path)
            proj_files = [os.path.join(proj_path,f) for f in proj_files]
        else:
            proj_files = []
except:
    proj_files = []

try:
    extra_comp_args = subprocess.check_output([mapnik_config, '--cflags']).rstrip('\n').split(' ')

    if sys.platform == 'darwin':
        extra_comp_args.append('-mmacosx-version-min=10.8')
        linkflags.append('-mmacosx-version-min=10.8')
except:
    extra_comp_args = []

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
    data_files = [
        ('mapnik', lib_files),
        ('mapnik/input', input_plugin_files),
        ('mapnik/fonts', font_files),
        ('mapnik/icu', icu_files),
        ('mapnik/gdal', gdal_files),
        ('mapnik/proj', proj_files),
    ],
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
