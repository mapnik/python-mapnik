#! /usr/bin/env python3

from pybind11.setup_helpers import Pybind11Extension, build_ext
from setuptools import setup, find_packages
import sys
import subprocess
import os

mapnik_config = 'mapnik-config'

def check_output(args):
     output = subprocess.check_output(args).decode()
     return output.rstrip('\n')

linkflags = []
lib_path = os.path.join(check_output([mapnik_config, '--prefix']),'lib')
linkflags.extend(check_output([mapnik_config, '--libs']).split(' '))
linkflags.extend(check_output([mapnik_config, '--ldflags']).split(' '))
linkflags.extend(check_output([mapnik_config, '--dep-libs']).split(' '))
linkflags.extend([
    '-lmapnik-wkt',
    '-lmapnik-json',
])

# Dynamically make the mapnik/paths.py file
f_paths = open('packaging/mapnik/paths.py', 'w')
f_paths.write('import os\n')
f_paths.write('\n')

input_plugin_path = check_output([mapnik_config, '--input-plugins'])
font_path = check_output([mapnik_config, '--fonts'])

if os.environ.get('LIB_DIR_NAME'):
    mapnik_lib_path = lib_path + os.environ.get('LIB_DIR_NAME')
else:
    mapnik_lib_path = lib_path + "/mapnik"
    f_paths.write("mapniklibpath = '{path}'\n".format(path=mapnik_lib_path))
    f_paths.write(
        "inputpluginspath = '{path}'\n".format(path=input_plugin_path))
    f_paths.write(
        "fontscollectionpath = '{path}'\n".format(path=font_path))
    f_paths.write(
        "__all__ = [mapniklibpath,inputpluginspath,fontscollectionpath]\n")
    f_paths.close()

extra_comp_args = check_output([mapnik_config, '--cflags']).split(' ')
extra_comp_args = list(filter(lambda arg: arg != "-fvisibility=hidden", extra_comp_args))

if sys.platform == 'darwin':
     pass
else:
     linkflags.append('-lrt')
     linkflags.append('-Wl,-z,origin')
     linkflags.append('-Wl,-rpath=$ORIGIN/lib')


ext_modules = [
     Pybind11Extension(
          "mapnik._mapnik",
          [
               "src/mapnik_python.cpp",
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
               "src/mapnik_image.cpp",
               "src/mapnik_projection.cpp",
               "src/mapnik_proj_transform.cpp",
          ],
          extra_compile_args=extra_comp_args,
          extra_link_args=linkflags,
     )
]

if os.environ.get("CC", False) == False:
    os.environ["CC"] = check_output([mapnik_config, '--cxx'])
if os.environ.get("CXX", False) == False:
    os.environ["CXX"] = check_output([mapnik_config, '--cxx'])

setup(
     name="mapnik",
     version="4.0.0.dev",
     packages=find_packages(where="packaging"),
     package_dir={"": "packaging"},
     package_data={
          'mapnik': ['lib/*.*', 'lib/*/*/*', 'share/*/*'],
     },
     ext_modules=ext_modules,
     #extras_require={"test": "pytest"},
     cmdclass={"build_ext": build_ext},
     #zip_safe=False,
     python_requires=">=3.7",
)
