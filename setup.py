#! /usr/bin/env python3

from pybind11.setup_helpers import Pybind11Extension, build_ext
from setuptools import setup, find_namespace_packages
import sys
import subprocess
import os

def check_output(args):
     output = subprocess.check_output(args).decode()
     return output.rstrip('\n')

linkflags = []
bin_path = os.path.join(check_output(['pkg-config', '--variable=prefix', 'libmapnik']),'bin')
lib_path = check_output(['pkg-config', '--variable=libdir', 'libmapnik'])
linkflags.extend(check_output(['pkg-config', '--libs', 'libmapnik']).split(' '))

# Remove symlinks
if os.path.islink('packaging/mapnik/bin') :
     os.unlink('packaging/mapnik/bin')
if os.path.islink('packaging/mapnik/lib') :
     os.unlink('packaging/mapnik/lib')
# Dynamically make the mapnik/paths.py file
f_paths = open('packaging/mapnik/paths.py', 'w')
f_paths.write('import os\n')
f_paths.write('\n')

if os.environ.get('SYSTEM_MAPNIK'):
     input_plugin_path = check_output(['pkg-config', '--variable=plugins_dir', 'libmapnik'])
     font_path = check_output(['pkg-config', '--variable=fonts_dir', 'libmapnik'])
     f_paths.write("mapniklibpath = '{path}'\n".format(path=lib_path))
     f_paths.write("inputpluginspath = '{path}'\n".format(path=input_plugin_path))
     f_paths.write("fontscollectionpath = '{path}'\n".format(path=font_path))
else:
     if not os.path.exists('packaging/mapnik/bin'):
          os.symlink(bin_path, 'packaging/mapnik/bin')
     if not os.path.exists('packaging/mapnik/lib') :
          os.symlink(lib_path, 'packaging/mapnik/lib')
     else:
          names = (name for name in os.listdir(lib_path) if os.path.isfile(os.path.join(lib_path, name)))
          for name in names:
               if not os.path.exists(os.path.join('packaging/mapnik/lib', name)):
                    os.symlink(os.path.join(lib_path, name), os.path.join('packaging/mapnik/lib', name))
          input_plugin_path = check_output([mapnik_config, '--input-plugins'])
          if not os.path.exists('packaging/mapnik/lib/mapnik/input'):
               os.symlink(input_plugin_path, 'packaging/mapnik/lib/mapnik/input')
     f_paths.write("mapniklibpath = os.path.join(os.path.dirname(__file__), 'lib')\n")
     f_paths.write("inputpluginspath = os.path.join(os.path.dirname(__file__), 'lib/mapnik/input')\n")
     f_paths.write("fontscollectionpath = os.path.join(os.path.dirname(__file__), 'lib/mapnik/fonts')\n")

f_paths.write("__all__ = [mapniklibpath,inputpluginspath,fontscollectionpath]\n")
f_paths.close()

extra_comp_args = check_output(['pkg-config', '--cflags', 'libmapnik']).split(' ')
extra_comp_args = list(filter(lambda arg: arg != "-fvisibility=hidden", extra_comp_args))

if sys.platform == 'darwin':
     pass
else:
     linkflags.append('-lrt')
     linkflags.append('-Wl,-z,origin')
     linkflags.append('-Wl,-rpath=$ORIGIN/lib')

extra_comp_args = list(filter(lambda arg: arg != "", extra_comp_args))
linkflags = list(filter(lambda arg: arg != "", linkflags))

ext_modules = [
     Pybind11Extension(
          "mapnik._mapnik",
          [
               "src/mapnik_python.cpp",
               "src/mapnik_layer.cpp",
               "src/mapnik_query.cpp",
               "src/mapnik_map.cpp",
               "src/mapnik_color.cpp",
               "src/mapnik_composite_modes.cpp",
               "src/mapnik_coord.cpp",
               "src/mapnik_envelope.cpp",
               "src/mapnik_expression.cpp",
               "src/mapnik_datasource.cpp",
               "src/mapnik_datasource_cache.cpp",
               "src/mapnik_gamma_method.cpp",
               "src/mapnik_geometry.cpp",
               "src/mapnik_feature.cpp",
               "src/mapnik_featureset.cpp",
               "src/mapnik_font_engine.cpp",
               "src/mapnik_fontset.cpp",
               "src/mapnik_grid.cpp",
               "src/mapnik_grid_view.cpp",
               "src/mapnik_image.cpp",
               "src/mapnik_image_view.cpp",
               "src/mapnik_projection.cpp",
               "src/mapnik_proj_transform.cpp",
               "src/mapnik_rule.cpp",
               "src/mapnik_symbolizer.cpp",
               "src/mapnik_debug_symbolizer.cpp",
               "src/mapnik_markers_symbolizer.cpp",
               "src/mapnik_polygon_symbolizer.cpp",
               "src/mapnik_polygon_pattern_symbolizer.cpp",
               "src/mapnik_line_symbolizer.cpp",
               "src/mapnik_line_pattern_symbolizer.cpp",
               "src/mapnik_point_symbolizer.cpp",
               "src/mapnik_raster_symbolizer.cpp",
               "src/mapnik_scaling_method.cpp",
               "src/mapnik_style.cpp",
               "src/mapnik_logger.cpp",
               "src/mapnik_placement_finder.cpp",
               "src/mapnik_text_symbolizer.cpp",
               "src/mapnik_palette.cpp",
               "src/mapnik_parameters.cpp",
               "src/python_grid_utils.cpp",
               "src/mapnik_raster_colorizer.cpp",
               "src/mapnik_label_collision_detector.cpp",
               "src/mapnik_dot_symbolizer.cpp",
               "src/mapnik_building_symbolizer.cpp",
               "src/mapnik_shield_symbolizer.cpp",
               "src/mapnik_group_symbolizer.cpp"
          ],
          extra_compile_args=extra_comp_args,
          extra_link_args=linkflags,
     )
]

if os.environ.get("CC", False) == False:
    os.environ["CC"] = 'c++'
if os.environ.get("CXX", False) == False:
    os.environ["CXX"] = 'c++'

setup(
     name="mapnik",
     include_package_data=True,
     packages=find_namespace_packages(where="packaging"),
     package_dir={"": "packaging"},
     package_data={
          "mapnik.include": ["*.hpp"],
          "mapnik.bin": ["*"],
          "mapnik.lib": ["libmapnik*"],
          "mapnik.lib.mapnik.fonts":["*"],
          "mapnik.lib.mapnik.input":["*.input"]
     },
     exclude_package_data={
          "mapnik.bin": ["mapnik-config"],
          "mapnik.lib": ["*.a"]
     },
     ext_modules=ext_modules,
     cmdclass={"build_ext": build_ext},
)
