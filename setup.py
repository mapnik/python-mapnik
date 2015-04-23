from setuptools import setup, Extension
import os
import subprocess

if os.environ.get("CXX", False):
    os.environ["CC"] = os.environ["CXX"]

linkflags = subprocess.check_output(['mapnik-config', '--libs']).rstrip('\n').split(' ')
linkflags.extend(subprocess.check_output(['mapnik-config', '--ldflags']).rstrip('\n').split(' '))
linkflags.extend(['-Wl','-bind_at_load'])

setup(
    name = "mapnik",
    version = "0.1",
    packages = ['mapnik'],
    ext_modules = [
        Extension('_mapnik', [
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
                'protobuf-lite'
            ],
            extra_compile_args = subprocess.check_output(['mapnik-config', '--cflags']).rstrip('\n').split(' '),
            extra_link_args = linkflags,
        )
    ]
)
