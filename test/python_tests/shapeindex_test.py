import fnmatch
import os
import shutil
from subprocess import PIPE, Popen

import mapnik
import pytest

from .utilities import execution_path

@pytest.fixture(scope="module")
def setup():
    # All of the paths used are relative, if we run the tests
    # from another directory we need to chdir()
    os.chdir(execution_path('.'))
    yield
    index = '../data/sqlite/world.sqlite.index'
    if os.path.exists(index):
        os.unlink(index)

def test_shapeindex(setup):
    # first copy shapefiles to tmp directory
    source_dir = '../data/shp/'
    working_dir = '/tmp/mapnik-shp-tmp/'
    if os.path.exists(working_dir):
        shutil.rmtree(working_dir)
    shutil.copytree(source_dir, working_dir)
    matches = []
    for root, dirnames, filenames in os.walk('%s' % source_dir):
        for filename in fnmatch.filter(filenames, '*.shp'):
            matches.append(os.path.join(root, filename))
    for shp in matches:
        source_file = os.path.join(
            source_dir, os.path.relpath(
                shp, source_dir))
        dest_file = os.path.join(working_dir, os.path.relpath(shp, source_dir))
        ds = mapnik.Shapefile(file=source_file)
        count = 0
        fs = iter(ds)
        try:
            while (next(fs)):
                count = count + 1
        except StopIteration:
            pass
        stdin, stderr = Popen(
            'shapeindex %s' %
            dest_file, shell=True, stdout=PIPE, stderr=PIPE).communicate()
        ds2 = mapnik.Shapefile(file=dest_file)
        count2 = 0
        fs = iter(ds)
        try:
            while (next(fs)):
                count2 = count2 + 1
        except StopIteration:
            pass
        assert count == count2
