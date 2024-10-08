import atexit
import os
import re
import sys
import time
from binascii import hexlify
from subprocess import PIPE, Popen
import mapnik
import pytest
from .utilities import execution_path, side_by_side_image

MAPNIK_TEST_DBNAME = 'mapnik-tmp-pgraster-test-db'
POSTGIS_TEMPLATE_DBNAME = 'template_postgis'
DEBUG_OUTPUT = False


def log(msg):
    if DEBUG_OUTPUT:
        print(msg)

@pytest.fixture(scope="module")
def setup():
    # All of the paths used are relative, if we run the tests
    # from another directory we need to chdir()
    os.chdir(execution_path('.'))

def call(cmd, silent=False):
    stdin, stderr = Popen(cmd, shell=True, stdout=PIPE,
                          stderr=PIPE).communicate()
    stdin = stdin.decode()
    stderr = stderr.decode()
    if not stderr:
        return stdin.strip()
    elif not silent and 'error' in stderr.lower() \
            or 'not found' in stderr.lower() \
            or 'could not connect' in stderr.lower() \
            or 'bad connection' in stderr.lower() \
            or 'not recognized as an internal' in stderr.lower():
        raise RuntimeError(stderr.strip())


def psql_can_connect():
    """Test ability to connect to a postgis template db with no options.

    Basically, to run these tests your user must have full read
    access over unix sockets without supplying a password. This
    keeps these tests simple and focused on postgis not on postgres
    auth issues.
    """
    try:
        call('psql %s -c "select postgis_version()"' % POSTGIS_TEMPLATE_DBNAME)
        return True
    except RuntimeError:
        print('Notice: skipping pgraster tests (connection)')
        return False


def psql_run(cmd):
    cmd = 'psql --set ON_ERROR_STOP=1 %s -c "%s"' % \
        (MAPNIK_TEST_DBNAME, cmd.replace('"', '\\"'))
    log('DEBUG: running ' + cmd)
    call(cmd)


def raster2pgsql_on_path():
    """Test for presence of raster2pgsql on the user path.

    We require this program to load test data into a temporarily database.
    """
    try:
        call('raster2pgsql')
        return True
    except RuntimeError:
        print('Notice: skipping pgraster tests (raster2pgsql)')
        return False


def createdb_and_dropdb_on_path():
    """Test for presence of dropdb/createdb on user path.

    We require these programs to setup and teardown the testing db.
    """
    try:
        call('createdb --help')
        call('dropdb --help')
        return True
    except RuntimeError:
        print('Notice: skipping pgraster tests (createdb/dropdb)')
        return False


def postgis_setup():
    call('dropdb %s' % MAPNIK_TEST_DBNAME, silent=True)
    call(
        'createdb -T %s %s' %
        (POSTGIS_TEMPLATE_DBNAME,
         MAPNIK_TEST_DBNAME),
        silent=False)


def postgis_takedown():
    pass
    # fails as the db is in use: https://github.com/mapnik/mapnik/issues/960
    #call('dropdb %s' % MAPNIK_TEST_DBNAME)


def import_raster(filename, tabname, tilesize, constraint, overview):
    log('tile: ' + tilesize + ' constraints: ' + str(constraint)
        + ' overviews: ' + overview)
    cmd = 'raster2pgsql -Y -I -q'
    if constraint:
        cmd += ' -C'
    if tilesize:
        cmd += ' -t ' + tilesize
    if overview:
        cmd += ' -l ' + overview
    cmd += ' %s %s | psql --set ON_ERROR_STOP=1 -q %s' % (
        os.path.abspath(os.path.normpath(filename)), tabname, MAPNIK_TEST_DBNAME)
    log('Import call: ' + cmd)
    call(cmd)


def drop_imported(tabname, overview):
    psql_run('DROP TABLE IF EXISTS "' + tabname + '";')
    if overview:
        for of in overview.split(','):
            psql_run('DROP TABLE IF EXISTS "o_' + of + '_' + tabname + '";')


def compare_images(expected, im):
    cur_dir = os.path.dirname(os.path.realpath(__file__))
    expected = os.path.join(
        os.path.dirname(expected),
        os.path.basename(expected).replace(
            ':',
            '_'))
    expected = os.path.join(cur_dir, expected)
    if not os.path.exists(expected) or os.environ.get('UPDATE'):
        print('generating expected image %s' % expected)
        im.save(expected, 'png32')
    expected_im = mapnik.Image.open(expected)
    diff = expected.replace('.png', '-diff.png')
    if len(im.to_string("png32")) != len(expected_im.to_string("png32")):
        compared = side_by_side_image(expected_im, im)
        compared.save(diff)
        assert False, 'images do not match, check diff at %s' % diff
    else:
        if os.path.exists(diff):
            os.unlink(diff)
    return True

if 'pgraster' in mapnik.DatasourceCache.plugin_names() \
        and createdb_and_dropdb_on_path() \
        and psql_can_connect() \
        and raster2pgsql_on_path():

        # initialize test database
    postgis_setup()

    # [old]dataraster.tif, 2283x1913 int16 single-band
    # dataraster-small.tif, 457x383 int16 single-band
    def _test_dataraster_16bsi_rendering(lbl, overview, rescale, clip):
        if rescale:
            lbl += ' Sc'
        if clip:
            lbl += ' Cl'
        ds = mapnik.PgRaster(dbname=MAPNIK_TEST_DBNAME, table='"dataRaster"',
                             band=1, use_overviews=1 if overview else 0,
                             prescale_rasters=rescale, clip_rasters=clip)
        fs = iter(ds)
        feature = next(fs)
        assert feature['rid'] ==  1
        lyr = mapnik.Layer('dataraster_16bsi')
        lyr.datasource = ds
        expenv = mapnik.Box2d(-14637, 3903178, 1126863, 4859678)
        env = lyr.envelope()
        # As the input size is a prime number both horizontally
        # and vertically, we expect the extent of the overview
        # tables to be a pixel wider than the original, whereas
        # the pixel size in geographical units depends on the
        # overview factor. So we start with the original pixel size
        # as base scale and multiply by the overview factor.
        # NOTE: the overview table extent only grows north and east
        pixsize = 500  # see gdalinfo dataraster.tif
        pixsize = 2497  # see gdalinfo dataraster-small.tif
        tol = pixsize * max(overview.split(',')) if overview else 0
        assert env.minx == expenv.minx
        assert env.miny == pytest.approx(expenv.miny,1.0e-7)
        assert env.maxx == pytest.approx(expenv.maxx,1.0e-7)
        assert env.maxy == expenv.maxy
        mm = mapnik.Map(256, 256)
        style = mapnik.Style()
        col = mapnik.RasterColorizer()
        col.default_mode = mapnik.COLORIZER_DISCRETE
        col.add_stop(0, mapnik.Color(0x40, 0x40, 0x40, 255))
        col.add_stop(10, mapnik.Color(0x80, 0x80, 0x80, 255))
        col.add_stop(20, mapnik.Color(0xa0, 0xa0, 0xa0, 255))
        sym = mapnik.RasterSymbolizer()
        sym.colorizer = col
        rule = mapnik.Rule()
        rule.symbolizers.append(sym)
        style.rules.append(rule)
        mm.append_style('foo', style)
        lyr.styles.append('foo')
        mm.layers.append(lyr)
        mm.zoom_to_box(expenv)
        im = mapnik.Image(mm.width, mm.height)
        t0 = time.time()  # we want wall time to include IO waits
        mapnik.render(mm, im)
        lap = time.time() - t0
        log('T ' + str(lap) + ' -- ' + lbl + ' E:full')
        # no data
        assert im.view(1, 1, 1, 1).to_string() ==  b'\x00\x00\x00\x00'
        assert im.view(255, 255, 1, 1).to_string() == b'\x00\x00\x00\x00'
        assert im.view(195, 116, 1, 1).to_string() == b'\x00\x00\x00\x00'
        # A0A0A0
        assert im.view(100, 120, 1, 1).to_string() == b'\xa0\xa0\xa0\xff'
        assert im.view(75, 80, 1, 1).to_string() == b'\xa0\xa0\xa0\xff'
        # 808080
        assert im.view(74, 170, 1, 1).to_string() == b'\x80\x80\x80\xff'
        assert im.view(30, 50, 1, 1).to_string() == b'\x80\x80\x80\xff'
        # 404040
        assert im.view(190, 70, 1, 1).to_string() == b'\x40\x40\x40\xff'
        assert im.view(140, 170, 1, 1).to_string() == b'\x40\x40\x40\xff'

        # Now zoom over a portion of the env (1/10)
        newenv = mapnik.Box2d(273663, 4024478, 330738, 4072303)
        mm.zoom_to_box(newenv)
        t0 = time.time()  # we want wall time to include IO waits
        mapnik.render(mm, im)
        lap = time.time() - t0
        log('T ' + str(lap) + ' -- ' + lbl + ' E:1/10')
        # nodata
        assert hexlify(im.view(255, 255, 1, 1).to_string()) == b'00000000'
        assert hexlify(im.view(200, 254, 1, 1).to_string()) == b'00000000'
        # A0A0A0
        assert hexlify(im.view(90, 232, 1, 1).to_string()) == b'a0a0a0ff'
        assert hexlify(im.view(96, 245, 1, 1).to_string()) == b'a0a0a0ff'
        # 808080
        assert hexlify(im.view(1, 1, 1, 1).to_string()) == b'808080ff'
        assert hexlify(im.view(128, 128, 1, 1).to_string()) == b'808080ff'
        # 404040
        assert hexlify(im.view(255, 0, 1, 1).to_string()) == b'404040ff'

    def _test_dataraster_16bsi(lbl, tilesize, constraint, overview):
        import_raster(
            os.path.join(os.path.dirname(os.path.realpath(__file__)),'../../test/data/raster/dataraster-small.tif'),
            'dataRaster',
            tilesize,
            constraint,
            overview)
        if constraint:
            lbl += ' C'
        if tilesize:
            lbl += ' T:' + tilesize
        if overview:
            lbl += ' O:' + overview
        for prescale in [0, 1]:
            for clip in [0, 1]:
                _test_dataraster_16bsi_rendering(lbl, overview, prescale, clip)
        drop_imported('dataRaster', overview)

    def test_dataraster_16bsi():
        # for tilesize in ['','256x256']:
        for tilesize in ['256x256']:
            for constraint in [0, 1]:
                # for overview in ['','4','2,16']:
                for overview in ['', '2']:
                    _test_dataraster_16bsi(
                        'data_16bsi', tilesize, constraint, overview)

    # # river.tiff, RGBA 8BUI
    def _test_rgba_8bui_rendering(lbl, overview, rescale, clip):
        if rescale:
            lbl += ' Sc'
        if clip:
            lbl += ' Cl'
        ds = mapnik.PgRaster(dbname=MAPNIK_TEST_DBNAME, table='(select * from "River" order by rid) foo',
                             use_overviews=1 if overview else 0,
                             prescale_rasters=rescale, clip_rasters=clip)
        fs = iter(ds)
        feature = next(fs)
        assert feature['rid'] == 1
        lyr = mapnik.Layer('rgba_8bui')
        lyr.datasource = ds
        expenv = mapnik.Box2d(0, -210, 256, 0)
        env = lyr.envelope()
        # As the input size is a prime number both horizontally
        # and vertically, we expect the extent of the overview
        # tables to be a pixel wider than the original, whereas
        # the pixel size in geographical units depends on the
        # overview factor. So we start with the original pixel size
        # as base scale and multiply by the overview factor.
        # NOTE: the overview table extent only grows north and east
        pixsize = 1  # see gdalinfo river.tif
        tol = pixsize * max(overview.split(',')) if overview else 0
        assert env.minx == expenv.minx
        assert env.miny == expenv.miny
        assert env.maxx == expenv.maxx
        assert env.maxy == expenv.maxy
        mm = mapnik.Map(256, 256)
        style = mapnik.Style()
        sym = mapnik.RasterSymbolizer()
        rule = mapnik.Rule()
        rule.symbolizers.append(sym)
        style.rules.append(rule)
        mm.append_style('foo', style)
        lyr.styles.append('foo')
        mm.layers.append(lyr)
        mm.zoom_to_box(expenv)
        im = mapnik.Image(mm.width, mm.height)
        t0 = time.time()  # we want wall time to include IO waits
        mapnik.render(mm, im)
        lap = time.time() - t0
        log('T ' + str(lap) + ' -- ' + lbl + ' E:full')
        expected = './images/support/pgraster/%s-%s-%s-%s-box1.png' % (
            lyr.name, lbl, overview, clip)
        compare_images(expected, im)
        # no data
        assert hexlify(im.view(3, 3, 1, 1).to_string()) == b'00000000'
        assert hexlify(im.view(250, 250, 1, 1).to_string()) == b'00000000'
        # full opaque river color
        assert hexlify(im.view(175, 118, 1, 1).to_string()) == b'b9d8f8ff'
        # half-transparent pixel
        pxstr = hexlify(im.view(122, 138, 1, 1).to_string()).decode()
        apat = ".*(..)$"
        match = re.match(apat, pxstr)
        assert match, 'pixel ' + pxstr + ' does not match pattern ' + apat
        alpha = match.group(1)
        assert alpha != 'ff' and alpha != '00', \
            'unexpected full transparent/opaque pixel: ' + alpha

        # Now zoom over a portion of the env (1/10)
        newenv = mapnik.Box2d(166, -105, 191, -77)
        mm.zoom_to_box(newenv)
        t0 = time.time()  # we want wall time to include IO waits
        im = mapnik.Image(mm.width, mm.height)
        mapnik.render(mm, im)
        lap = time.time() - t0
        log('T ' + str(lap) + ' -- ' + lbl + ' E:1/10')
        expected = './images/support/pgraster/%s-%s-%s-%s-box2.png' % (
            lyr.name, lbl, overview, clip)
        compare_images(expected, im)
        # no data
        assert hexlify(im.view(255, 255, 1, 1).to_string()) == b'00000000'
        assert hexlify(im.view(200, 40, 1, 1).to_string()) == b'00000000'
        # full opaque river color
        assert hexlify(im.view(100, 168, 1, 1).to_string()) == b'b9d8f8ff'
        # half-transparent pixel
        pxstr = hexlify(im.view(122, 138, 1, 1).to_string()).decode()
        apat = ".*(..)$"
        match = re.match(apat, pxstr)
        assert match, 'pixel ' + pxstr + ' does not match pattern ' + apat
        alpha = match.group(1)
        assert alpha != 'ff' and alpha != '00', \
            'unexpected full transparent/opaque pixel: ' + alpha

    def _test_rgba_8bui(lbl, tilesize, constraint, overview):
        import_raster(
            os.path.join(os.path.dirname(os.path.realpath(__file__)),'../../test/data/raster/river.tiff'),
            'River',
            tilesize,
            constraint,
            overview)
        if constraint:
            lbl += ' C'
        if tilesize:
            lbl += ' T:' + tilesize
        if overview:
            lbl += ' O:' + overview
        for prescale in [0, 1]:
            for clip in [0, 1]:
                _test_rgba_8bui_rendering(lbl, overview, prescale, clip)
        drop_imported('River', overview)

    def test_rgba_8bui():
        for tilesize in ['', '16x16']:
            for constraint in [0, 1]:
                for overview in ['2']:
                    _test_rgba_8bui(
                        'rgba_8bui', tilesize, constraint, overview)

    # # nodata-edge.tif, RGB 8BUI
    def _test_rgb_8bui_rendering(lbl, tnam, overview, rescale, clip):
        if rescale:
            lbl += ' Sc'
        if clip:
            lbl += ' Cl'
        ds = mapnik.PgRaster(dbname=MAPNIK_TEST_DBNAME, table=f'(select * from "{tnam}" order by rid) foo',
                             use_overviews=1 if overview else 0,
                             prescale_rasters=rescale, clip_rasters=clip)
        fs = iter(ds)
        feature = next(fs)
        assert feature['rid'] == 1
        lyr = mapnik.Layer('rgba_8bui')
        lyr.datasource = ds
        expenv = mapnik.Box2d(-12329035.765216826, 4508650.398543958,
                              -12328653.027947055, 4508957.346255356)
        env = lyr.envelope()
        # As the input size is a prime number both horizontally
        # and vertically, we expect the extent of the overview
        # tables to be a pixel wider than the original, whereas
        # the pixel size in geographical units depends on the
        # overview factor. So we start with the original pixel size
        # as base scale and multiply by the overview factor.
        # NOTE: the overview table extent only grows north and east
        pixsize = 2  # see gdalinfo nodata-edge.tif
        tol = pixsize * max(overview.split(',')) if overview else 0
        assert env.minx == expenv.minx
        assert env.miny == expenv.miny
        assert env.maxx == expenv.maxx
        assert env.maxy == expenv.maxy
        mm = mapnik.Map(256, 256)
        style = mapnik.Style()
        sym = mapnik.RasterSymbolizer()
        rule = mapnik.Rule()
        rule.symbolizers.append(sym)
        style.rules.append(rule)
        mm.append_style('foo', style)
        lyr.styles.append('foo')
        mm.layers.append(lyr)
        mm.zoom_to_box(expenv)
        im = mapnik.Image(mm.width, mm.height)
        t0 = time.time()  # we want wall time to include IO waits
        mapnik.render(mm, im)
        lap = time.time() - t0
        log('T ' + str(lap) + ' -- ' + lbl + ' E:full')
        expected = './images/support/pgraster/%s-%s-%s-%s-%s-box1.png' % (
            lyr.name, tnam, lbl, overview, clip)
        compare_images(expected, im)
        # no data
        assert hexlify(im.view(3, 16, 1, 1).to_string()) == b'00000000'
        assert hexlify(im.view(128, 16, 1, 1).to_string()) == b'00000000'
        assert hexlify(im.view(250, 16, 1, 1).to_string()) == b'00000000'
        assert hexlify(im.view(3, 240, 1, 1).to_string()) == b'00000000'
        assert hexlify(im.view(128, 240, 1, 1).to_string()) == b'00000000'
        assert hexlify(im.view(250, 240, 1, 1).to_string()) == b'00000000'
        # dark brown
        assert hexlify(im.view(174, 39, 1, 1).to_string()) == b'c3a698ff'
        # dark gray
        assert hexlify(im.view(195, 132, 1, 1).to_string()) == b'575f62ff'
        # Now zoom over a portion of the env (1/10)
        newenv = mapnik.Box2d(-12329035.7652168, 4508926.651484220,
                              -12328997.49148983, 4508957.34625536)
        mm.zoom_to_box(newenv)
        t0 = time.time()  # we want wall time to include IO waits
        im = mapnik.Image(mm.width, mm.height)
        mapnik.render(mm, im)
        lap = time.time() - t0
        log('T ' + str(lap) + ' -- ' + lbl + ' E:1/10')
        expected = 'images/support/pgraster/%s-%s-%s-%s-%s-box2.png' % (
            lyr.name, tnam, lbl, overview, clip)
        compare_images(expected, im)
        # no data
        assert hexlify(im.view(3, 16, 1, 1).to_string()) == b'00000000'
        assert hexlify(im.view(128, 16, 1, 1).to_string()) == b'00000000'
        assert hexlify(im.view(250, 16, 1, 1).to_string()) == b'00000000'
        # black
        assert hexlify(im.view(3, 42, 1, 1).to_string()) == b'000000ff'
        assert hexlify(im.view(3, 134, 1, 1).to_string()) == b'000000ff'
        assert hexlify(im.view(3, 244, 1, 1).to_string()) == b'000000ff'
        # gray
        assert hexlify(im.view(135, 157, 1, 1).to_string()) == b'4e555bff'
        # brown
        assert hexlify(im.view(195, 223, 1, 1).to_string()) == b'f2cdbaff'

    def _test_rgb_8bui(lbl, tilesize, constraint, overview):
        tnam = 'nodataedge'
        import_raster(
            os.path.join(os.path.dirname(os.path.realpath(__file__)),'../../test/data/raster/nodata-edge.tif'),
            tnam,
            tilesize,
            constraint,
            overview)
        if constraint:
            lbl += ' C'
        if tilesize:
            lbl += ' T:' + tilesize
        if overview:
            lbl += ' O:' + overview
        for prescale in [0, 1]:
            for clip in [0, 1]:
                _test_rgb_8bui_rendering(lbl, tnam, overview, prescale, clip)
        drop_imported(tnam, overview)

    def test_rgb_8bui():
        for tilesize in ['64x64']:
            for constraint in [1]:
                for overview in ['']:
                    _test_rgb_8bui('rgb_8bui', tilesize, constraint, overview)

    def _test_grayscale_subquery(lbl, pixtype, value):
        #
        #      3   8   13
        #    +---+---+---+
        #  3 | v | v | v |  NOTE: writes different color
        #    +---+---+---+        in 13,8 and 8,13
        #  8 | v | v | a |
        #    +---+---+---+
        # 13 | v | b | v |
        #    +---+---+---+
        #
        val_a = int(value / 3)
        val_b = val_a * 2
        sql = "(select 3 as i, " \
              " ST_SetValues(" \
              "  ST_SetValues(" \
              "   ST_AsRaster(" \
              "    ST_MakeEnvelope(0,0,14,14), " \
              "    1.0, -1.0, '%s', %s" \
              "   ), " \
              "   11, 6, 4, 5, %s::float8" \
              "  )," \
              "  6, 11, 5, 4, %s::float8" \
              " ) as \"R\"" \
              ") as foo" % (pixtype, value, val_a, val_b)
        rescale = 0
        clip = 0
        if rescale:
            lbl += ' Sc'
        if clip:
            lbl += ' Cl'
        ds = mapnik.PgRaster(dbname=MAPNIK_TEST_DBNAME, table=sql,
                             raster_field='"R"', use_overviews=1,
                             prescale_rasters=rescale, clip_rasters=clip)
        fs = iter(ds)
        feature = next(fs)
        assert feature['i'] == 3
        lyr = mapnik.Layer('grayscale_subquery')
        lyr.datasource = ds
        expenv = mapnik.Box2d(0, 0, 14, 14)
        env = lyr.envelope()
        assert env.minx == expenv.minx
        assert env.miny == expenv.miny
        assert env.maxx == expenv.maxx
        assert env.maxy == expenv.maxy
        mm = mapnik.Map(15, 15)
        style = mapnik.Style()
        sym = mapnik.RasterSymbolizer()
        rule = mapnik.Rule()
        rule.symbolizers.append(sym)
        style.rules.append(rule)
        mm.append_style('foo', style)
        lyr.styles.append('foo')
        mm.layers.append(lyr)
        mm.zoom_to_box(expenv)
        im = mapnik.Image(mm.width, mm.height)
        t0 = time.time()  # we want wall time to include IO waits
        mapnik.render(mm, im)
        lap = time.time() - t0
        log('T ' + str(lap) + ' -- ' + lbl + ' E:full')
        expected = 'images/support/pgraster/%s-%s-%s-%s.png' % (
            lyr.name, lbl, pixtype, value)
        compare_images(expected, im)
        h = format(value, '02x')
        hex_v = h + h + h + 'ff'
        hex_v = hex_v.encode()
        h = format(val_a, '02x')
        hex_a = h + h + h + 'ff'
        hex_a = hex_a.encode()
        h = format(val_b, '02x')
        hex_b = h + h + h + 'ff'
        hex_b = hex_b.encode()
        assert hexlify(im.view(3, 3, 1, 1).to_string()) == hex_v
        assert hexlify(im.view(8, 3, 1, 1).to_string()) == hex_v
        assert hexlify(im.view(13, 3, 1, 1).to_string()) == hex_v
        assert hexlify(im.view(3, 8, 1, 1).to_string()) == hex_v
        assert hexlify(im.view(8, 8, 1, 1).to_string()) == hex_v
        assert hexlify(im.view(13, 8, 1, 1).to_string()) == hex_a
        assert hexlify(im.view(3, 13, 1, 1).to_string()) == hex_v
        assert hexlify(im.view(8, 13, 1, 1).to_string()) == hex_b
        assert hexlify(im.view(13, 13, 1, 1).to_string()) == hex_v

    def test_grayscale_2bui_subquery():
        _test_grayscale_subquery('grayscale_2bui_subquery', '2BUI', 3)

    def test_grayscale_4bui_subquery():
        _test_grayscale_subquery('grayscale_4bui_subquery', '4BUI', 15)

    def test_grayscale_8bui_subquery():
        _test_grayscale_subquery('grayscale_8bui_subquery', '8BUI', 63)

    def test_grayscale_8bsi_subquery():
        # NOTE: we're using a positive integer because Mapnik
        #       does not support negative data values anyway
        _test_grayscale_subquery('grayscale_8bsi_subquery', '8BSI', 69)

    def test_grayscale_16bui_subquery():
        _test_grayscale_subquery('grayscale_16bui_subquery', '16BUI', 126)

    def test_grayscale_16bsi_subquery():
        # NOTE: we're using a positive integer because Mapnik
        #       does not support negative data values anyway
        _test_grayscale_subquery('grayscale_16bsi_subquery', '16BSI', 144)

    def test_grayscale_32bui_subquery():
        _test_grayscale_subquery('grayscale_32bui_subquery', '32BUI', 255)

    def test_grayscale_32bsi_subquery():
        # NOTE: we're using a positive integer because Mapnik
        #       does not support negative data values anyway
        _test_grayscale_subquery('grayscale_32bsi_subquery', '32BSI', 129)

    def _test_data_subquery(lbl, pixtype, value):
        #
        #      3   8   13
        #    +---+---+---+
        #  3 | v | v | v |  NOTE: writes different values
        #    +---+---+---+        in 13,8 and 8,13
        #  8 | v | v | a |
        #    +---+---+---+
        # 13 | v | b | v |
        #    +---+---+---+
        #
        val_a = value / 3
        val_b = val_a * 2
        sql = "(select 3 as i, " \
              " ST_SetValues(" \
              "  ST_SetValues(" \
              "   ST_AsRaster(" \
              "    ST_MakeEnvelope(0,0,14,14), " \
              "    1.0, -1.0, '%s', %s" \
              "   ), " \
              "   11, 6, 5, 5, %s::float8" \
              "  )," \
              "  6, 11, 5, 5, %s::float8" \
              " ) as \"R\"" \
              ") as foo" % (pixtype, value, val_a, val_b)
        overview = ''
        rescale = 0
        clip = 0
        if rescale:
            lbl += ' Sc'
        if clip:
            lbl += ' Cl'
        ds = mapnik.PgRaster(dbname=MAPNIK_TEST_DBNAME, table=sql,
                             raster_field='R', use_overviews=0 if overview else 0,
                             band=1, prescale_rasters=rescale, clip_rasters=clip)
        fs = iter(ds)
        feature = next(fs)
        assert feature['i'] == 3
        lyr = mapnik.Layer('data_subquery')
        lyr.datasource = ds
        expenv = mapnik.Box2d(0, 0, 14, 14)
        env = lyr.envelope()
        assert env.minx == expenv.minx#, places=0)
        assert env.miny == expenv.miny#, places=0)
        assert env.maxx == expenv.maxx#, places=0)
        assert env.maxy == expenv.maxy#, places=0)
        mm = mapnik.Map(15, 15)
        style = mapnik.Style()
        col = mapnik.RasterColorizer()
        col.default_mode = mapnik.COLORIZER_DISCRETE
        col.add_stop(val_a, mapnik.Color(0xff, 0x00, 0x00, 255))
        col.add_stop(val_b, mapnik.Color(0x00, 0xff, 0x00, 255))
        col.add_stop(value, mapnik.Color(0x00, 0x00, 0xff, 255))
        sym = mapnik.RasterSymbolizer()
        sym.colorizer = col
        rule = mapnik.Rule()
        rule.symbolizers.append(sym)
        style.rules.append(rule)
        mm.append_style('foo', style)
        lyr.styles.append('foo')
        mm.layers.append(lyr)
        mm.zoom_to_box(expenv)
        im = mapnik.Image(mm.width, mm.height)
        t0 = time.time()  # we want wall time to include IO waits
        mapnik.render(mm, im)
        lap = time.time() - t0
        log('T ' + str(lap) + ' -- ' + lbl + ' E:full')
        expected = 'images/support/pgraster/%s-%s-%s-%s.png' % (
            lyr.name, lbl, pixtype, value)
        compare_images(expected, im)

    def test_data_2bui_subquery():
        _test_data_subquery('data_2bui_subquery', '2BUI', 3)

    def test_data_4bui_subquery():
        _test_data_subquery('data_4bui_subquery', '4BUI', 15)

    def test_data_8bui_subquery():
        _test_data_subquery('data_8bui_subquery', '8BUI', 63)

    def test_data_8bsi_subquery():
        # NOTE: we're using a positive integer because Mapnik
        #       does not support negative data values anyway
        _test_data_subquery('data_8bsi_subquery', '8BSI', 69)

    def test_data_16bui_subquery():
        _test_data_subquery('data_16bui_subquery', '16BUI', 126)

    def test_data_16bsi_subquery():
        # NOTE: we're using a positive integer because Mapnik
        #       does not support negative data values anyway
        _test_data_subquery('data_16bsi_subquery', '16BSI', 135)

    def test_data_32bui_subquery():
        _test_data_subquery('data_32bui_subquery', '32BUI', 255)

    def test_data_32bsi_subquery():
        # NOTE: we're using a positive integer because Mapnik
        #       does not support negative data values anyway
        _test_data_subquery('data_32bsi_subquery', '32BSI', 264)

    def test_data_32bf_subquery():
        _test_data_subquery('data_32bf_subquery', '32BF', 450)

    def test_data_64bf_subquery():
        _test_data_subquery('data_64bf_subquery', '64BF', 3072)

    def _test_rgba_subquery(lbl, pixtype, r, g, b, a, g1, b1):
        #
        #      3   8   13
        #    +---+---+---+
        #  3 | v | v | h |  NOTE: writes different alpha
        #    +---+---+---+        in 13,8 and 8,13
        #  8 | v | v | a |
        #    +---+---+---+
        # 13 | v | b | v |
        #    +---+---+---+
        #
        sql = "(select 3 as i, " \
              " ST_SetValues(" \
              "  ST_SetValues(" \
              "   ST_AddBand(" \
              "    ST_AddBand(" \
              "     ST_AddBand(" \
              "      ST_AsRaster(" \
              "       ST_MakeEnvelope(0,0,14,14), " \
              "       1.0, -1.0, '%s', %s" \
              "      )," \
              "      '%s', %d::float" \
              "     ), " \
              "     '%s', %d::float" \
              "    ), " \
              "    '%s', %d::float" \
              "   ), " \
              "   2, 11, 6, 4, 5, %s::float8" \
              "  )," \
              "  3, 6, 11, 5, 4, %s::float8" \
              " ) as r" \
              ") as foo" % (
                  pixtype,
                  r,
                  pixtype,
                  g,
                  pixtype,
                  b,
                  pixtype,
                  a,
                  g1,
                  b1)
        overview = ''
        rescale = 0
        clip = 0
        if rescale:
            lbl += ' Sc'
        if clip:
            lbl += ' Cl'
        ds = mapnik.PgRaster(dbname=MAPNIK_TEST_DBNAME, table=sql,
                             raster_field='r', use_overviews=0 if overview else 0,
                             prescale_rasters=rescale, clip_rasters=clip)
        fs = iter(ds)
        feature = next(fs)
        assert feature['i'] == 3
        lyr = mapnik.Layer('rgba_subquery')
        lyr.datasource = ds
        expenv = mapnik.Box2d(0, 0, 14, 14)
        env = lyr.envelope()
        assert env.minx == expenv.minx#, places=0)
        assert env.miny == expenv.miny#, places=0)
        assert env.maxx == expenv.maxx#, places=0)
        assert env.maxy == expenv.maxy#, places=0)
        mm = mapnik.Map(15, 15)
        style = mapnik.Style()
        sym = mapnik.RasterSymbolizer()
        rule = mapnik.Rule()
        rule.symbolizers.append(sym)
        style.rules.append(rule)
        mm.append_style('foo', style)
        lyr.styles.append('foo')
        mm.layers.append(lyr)
        mm.zoom_to_box(expenv)
        im = mapnik.Image(mm.width, mm.height)
        t0 = time.time()  # we want wall time to include IO waits
        mapnik.render(mm, im)
        lap = time.time() - t0
        log('T ' + str(lap) + ' -- ' + lbl + ' E:full')
        expected = 'images/support/pgraster/%s-%s-%s-%s-%s-%s-%s-%s-%s.png' % (
            lyr.name, lbl, pixtype, r, g, b, a, g1, b1)
        compare_images(expected, im)
        hex_v = format(r << 24 | g << 16 | b  << 8 | a, '08x').encode()
        hex_a = format(r << 24 | g1<< 16 | b  << 8 | a, '08x').encode()
        hex_b = format(r << 24 | g << 16 | b1 << 8 | a, '08x').encode()
        assert hexlify(im.view(3, 3, 1, 1).to_string()) ==  hex_v
        assert hexlify(im.view(8, 3, 1, 1).to_string()) == hex_v
        assert hexlify(im.view(13, 3, 1, 1).to_string()) == hex_v
        assert hexlify(im.view(3, 8, 1, 1).to_string()) == hex_v
        assert hexlify(im.view(8, 8, 1, 1).to_string()) == hex_v
        assert hexlify(im.view(13, 8, 1, 1).to_string()) == hex_a
        assert hexlify(im.view(3, 13, 1, 1).to_string()) == hex_v
        assert hexlify(im.view(8, 13, 1, 1).to_string()) == hex_b
        assert hexlify(im.view(13, 13, 1, 1).to_string()) == hex_v

    def test_rgba_8bui_subquery():
        _test_rgba_subquery(
            'rgba_8bui_subquery',
            '8BUI',
            255,
            0,
            0,
            255,
            255,
            255)

    #def test_rgba_16bui_subquery():
    #   _test_rgba_subquery('rgba_16bui_subquery', '16BUI', 65535, 0, 0, 65535, 65535, 65535)

    #def test_rgba_32bui_subquery():
    #   _test_rgba_subquery('rgba_32bui_subquery', '32BUI')

    atexit.register(postgis_takedown)

def enabled(tname):
    enabled = len(sys.argv) < 2 or tname in sys.argv
    if not enabled:
        print("Skipping " + tname + " as not explicitly enabled")
    return enabled
