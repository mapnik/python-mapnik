import os
import hashlib
import mapnik
import pytest
from .utilities import READ_FLAGS, execution_path

@pytest.fixture(scope="module")
def setup():
    # All of the paths used are relative, if we run the tests
    # from another directory we need to chdir()
    os.chdir(execution_path('.'))
    yield

def hashstr(var):
    return hashlib.md5(var).hexdigest()

def test_tiff_round_trip_scanline(setup):
    filepath = '/tmp/mapnik-tiff-io-scanline.tiff'
    im = mapnik.Image(255, 267)
    im.fill(mapnik.Color('rgba(12,255,128,.5)'))
    org_str = hashstr(im.to_string())
    im.save(filepath, 'tiff:method=scanline')
    im2 = mapnik.Image.open(filepath)
    with open(filepath, READ_FLAGS) as f:
        im3 = mapnik.Image.from_string(f.read())
    assert im.width() ==  im2.width()
    assert im.height() ==  im2.height()
    assert im.width() ==  im3.width()
    assert im.height() ==  im3.height()
    assert hashstr(im.to_string()) ==  org_str
    # This won't be the same the first time around because the im is not
    # premultiplied and im2 is
    assert not hashstr(im.to_string()) == hashstr(im2.to_string())
    assert not hashstr(im.to_string('tiff:method=scanline')) == hashstr(im2.to_string('tiff:method=scanline'))
    # Now premultiply
    im.premultiply()
    assert hashstr(im.to_string()) ==  hashstr(im2.to_string())
    assert hashstr(im.to_string('tiff:method=scanline')) == hashstr(im2.to_string('tiff:method=scanline'))
    assert hashstr(im2.to_string()) ==  hashstr(im3.to_string())
    assert hashstr(im2.to_string('tiff:method=scanline')) == hashstr(im3.to_string('tiff:method=scanline'))


def test_tiff_round_trip_stripped():
    filepath = '/tmp/mapnik-tiff-io-stripped.tiff'
    im = mapnik.Image(255, 267)
    im.fill(mapnik.Color('rgba(12,255,128,.5)'))
    org_str = hashstr(im.to_string())
    im.save(filepath, 'tiff:method=stripped')
    im2 = mapnik.Image.open(filepath)
    im2.save('/tmp/mapnik-tiff-io-stripped2.tiff', 'tiff:method=stripped')
    with open(filepath, READ_FLAGS) as f:
        im3 = mapnik.Image.from_string(f.read())
    assert im.width() ==  im2.width()
    assert im.height() ==  im2.height()
    assert im.width() ==  im3.width()
    assert im.height() ==  im3.height()
    # Because one will end up with UNASSOC alpha tag which internally the TIFF reader will premultiply, the first to string will not be the same due to the
    # difference in tags.
    assert not hashstr(im.to_string()) ==  hashstr(im2.to_string())
    assert not hashstr(im.to_string('tiff:method=stripped')) ==  hashstr(im2.to_string('tiff:method=stripped'))
    # Now if we premultiply they will be exactly the same
    im.premultiply()
    assert hashstr(im.to_string()) ==  hashstr(im2.to_string())
    assert hashstr(im.to_string('tiff:method=stripped')) == hashstr(im2.to_string('tiff:method=stripped'))
    assert hashstr(im2.to_string()) ==  hashstr(im3.to_string())
    # Both of these started out premultiplied, so this round trip should be
    # exactly the same!
    assert hashstr(im2.to_string('tiff:method=stripped')) == hashstr(im3.to_string('tiff:method=stripped'))


def test_tiff_round_trip_rows_stripped():
    filepath = '/tmp/mapnik-tiff-io-rows_stripped.tiff'
    filepath2 = '/tmp/mapnik-tiff-io-rows_stripped2.tiff'
    im = mapnik.Image(255, 267)
    im.fill(mapnik.Color('rgba(12,255,128,.5)'))
    c = im.get_pixel_color(0, 0)
    assert c.r ==  12
    assert c.g ==  255
    assert c.b ==  128
    assert c.a ==  128
    assert c.get_premultiplied() ==  False
    im.save(filepath, 'tiff:method=stripped:rows_per_strip=8')
    im2 = mapnik.Image.open(filepath)
    c2 = im2.get_pixel_color(0, 0)
    assert c2.r ==  6
    assert c2.g ==  128
    assert c2.b ==  64
    assert c2.a ==  128
    assert c2.get_premultiplied() ==  True
    im2.save(filepath2, 'tiff:method=stripped:rows_per_strip=8')
    with open(filepath, READ_FLAGS) as f:
        im3 = mapnik.Image.from_string(f.read())
    assert im.width() ==  im2.width()
    assert im.height() ==  im2.height()
    assert im.width() ==  im3.width()
    assert im.height() ==  im3.height()
    # Because one will end up with UNASSOC alpha tag which internally the TIFF reader will premultiply, the first to string will not be the same due to the
    # difference in tags.
    assert not hashstr(im.to_string()) ==  hashstr(im2.to_string())
    assert not hashstr(im.to_string('tiff:method=stripped:rows_per_strip=8')) ==  hashstr(
        im2.to_string('tiff:method=stripped:rows_per_strip=8'))
    # Now premultiply the first image and they will be the same!
    im.premultiply()
    assert hashstr(im.to_string('tiff:method=stripped:rows_per_strip=8')) == hashstr(im2.to_string('tiff:method=stripped:rows_per_strip=8'))
    assert hashstr(im2.to_string()) ==  hashstr(im3.to_string())
    # Both of these started out premultiplied, so this round trip should be
    # exactly the same!
    assert hashstr(im2.to_string('tiff:method=stripped:rows_per_strip=8')) == hashstr(im3.to_string('tiff:method=stripped:rows_per_strip=8'))


def test_tiff_round_trip_buffered_tiled():
    filepath = '/tmp/mapnik-tiff-io-buffered-tiled.tiff'
    filepath2 = '/tmp/mapnik-tiff-io-buffered-tiled2.tiff'
    filepath3 = '/tmp/mapnik-tiff-io-buffered-tiled3.tiff'
    im = mapnik.Image(255, 267)
    im.fill(mapnik.Color('rgba(33,255,128,.5)'))
    c = im.get_pixel_color(0, 0)
    assert c.r ==  33
    assert c.g ==  255
    assert c.b ==  128
    assert c.a ==  128
    assert not c.get_premultiplied()
    im.save(filepath, 'tiff:method=tiled:tile_width=32:tile_height=32')
    im2 = mapnik.Image.open(filepath)
    c2 = im2.get_pixel_color(0, 0)
    assert c2.r ==  17
    assert c2.g ==  128
    assert c2.b ==  64
    assert c2.a ==  128
    assert c2.get_premultiplied()
    with open(filepath, READ_FLAGS) as f:
        im3 = mapnik.Image.from_string(f.read())
    im2.save(filepath2, 'tiff:method=tiled:tile_width=32:tile_height=32')
    im3.save(filepath3, 'tiff:method=tiled:tile_width=32:tile_height=32')
    assert im.width() ==  im2.width()
    assert im.height() ==  im2.height()
    assert im.width() ==  im3.width()
    assert im.height() ==  im3.height()
    # Because one will end up with UNASSOC alpha tag which internally the TIFF reader will premultiply, the first to string will not be the same due to the
    # difference in tags.
    assert not hashstr(im.to_string()) == hashstr(im2.to_string())
    assert not hashstr(im.to_string('tiff:method=tiled:tile_width=32:tile_height=32')) ==  hashstr(
        im2.to_string('tiff:method=tiled:tile_width=32:tile_height=32'))
    # Now premultiply the first image and they should be the same
    im.premultiply()
    assert hashstr(im.to_string()) ==  hashstr(im2.to_string())
    assert hashstr(im.to_string('tiff:method=tiled:tile_width=32:tile_height=32')) == hashstr(im2.to_string('tiff:method=tiled:tile_width=32:tile_height=32'))
    assert hashstr(im2.to_string()) ==  hashstr(im3.to_string())
    # Both of these started out premultiplied, so this round trip should be
    # exactly the same!
    assert hashstr(im2.to_string('tiff:method=tiled:tile_width=32:tile_height=32')) == hashstr(im3.to_string('tiff:method=tiled:tile_width=32:tile_height=32'))


def test_tiff_round_trip_tiled():
    filepath = '/tmp/mapnik-tiff-io-tiled.tiff'
    im = mapnik.Image(256, 256)
    im.fill(mapnik.Color('rgba(1,255,128,.5)'))
    im.save(filepath, 'tiff:method=tiled')
    im2 = mapnik.Image.open(filepath)
    with open(filepath, READ_FLAGS) as f:
        im3 = mapnik.Image.from_string(f.read())
    assert im.width() ==  im2.width()
    assert im.height() ==  im2.height()
    assert im.width() ==  im3.width()
    assert im.height() ==  im3.height()
    # Because one will end up with UNASSOC alpha tag which internally the TIFF reader will premultiply, the first to string will not be the same due to the
    # difference in tags.
    assert not hashstr(im.to_string()) == hashstr(im2.to_string())
    assert not hashstr(im.to_string('tiff:method=tiled')) ==  hashstr(im2.to_string('tiff:method=tiled'))
    # Now premultiply the first image and they will be exactly the same.
    im.premultiply()
    assert hashstr(im.to_string()) ==  hashstr(im2.to_string())
    assert hashstr(im.to_string('tiff:method=tiled')) == hashstr(im2.to_string('tiff:method=tiled'))
    assert hashstr(im2.to_string()) ==  hashstr(im3.to_string())
    # Both of these started out premultiplied, so this round trip should be
    # exactly the same!
    assert hashstr(im2.to_string('tiff:method=tiled')) == hashstr(im3.to_string('tiff:method=tiled'))


def test_tiff_rgb8_compare():
    filepath1 = '../data/tiff/ndvi_256x256_rgb8_striped.tif'
    filepath2 = '/tmp/mapnik-tiff-rgb8.tiff'
    im = mapnik.Image.open(filepath1)
    im.save(filepath2, 'tiff')
    im2 = mapnik.Image.open(filepath2)
    assert im.width() ==  im2.width()
    assert im.height() ==  im2.height()
    assert hashstr(im.to_string()) ==  hashstr(im2.to_string())
    assert hashstr(im.to_string('tiff')) ==  hashstr(im2.to_string('tiff'))
    # should not be a blank image
    assert hashstr(im.to_string("tiff")) != hashstr(mapnik.Image(im.width(), im.height(), mapnik.ImageType.rgba8).to_string("tiff"))


def test_tiff_rgba8_compare_scanline():
    filepath1 = '../data/tiff/ndvi_256x256_rgba8_striped.tif'
    filepath2 = '/tmp/mapnik-tiff-rgba8-scanline.tiff'
    im = mapnik.Image.open(filepath1)
    im.save(filepath2, 'tiff:method=scanline')
    im2 = mapnik.Image.open(filepath2)
    assert im.width() ==  im2.width()
    assert im.height() ==  im2.height()
    assert hashstr(im.to_string()) ==  hashstr(im2.to_string())
    assert hashstr(im.to_string('tiff:method=scanline')) == hashstr(im2.to_string('tiff:method=scanline'))
    # should not be a blank image
    assert hashstr(im.to_string("tiff")) != hashstr(mapnik.Image(im.width(), im.height(), mapnik.ImageType.rgba8).to_string("tiff"))


def test_tiff_rgba8_compare_stripped():
    filepath1 = '../data/tiff/ndvi_256x256_rgba8_striped.tif'
    filepath2 = '/tmp/mapnik-tiff-rgba8-stripped.tiff'
    im = mapnik.Image.open(filepath1)
    im.save(filepath2, 'tiff:method=stripped')
    im2 = mapnik.Image.open(filepath2)
    assert im.width() ==  im2.width()
    assert im.height() ==  im2.height()
    assert hashstr(im.to_string()) ==  hashstr(im2.to_string())
    assert hashstr(im.to_string('tiff:method=stripped')) == hashstr(im2.to_string('tiff:method=stripped'))
    # should not be a blank image
    assert hashstr(im.to_string("tiff")) != hashstr(mapnik.Image(im.width(), im.height(), mapnik.ImageType.rgba8).to_string("tiff"))


def test_tiff_rgba8_compare_tiled():
    filepath1 = '../data/tiff/ndvi_256x256_rgba8_striped.tif'
    filepath2 = '/tmp/mapnik-tiff-rgba8-tiled.tiff'
    im = mapnik.Image.open(filepath1)
    im.save(filepath2, 'tiff:method=tiled')
    im2 = mapnik.Image.open(filepath2)
    assert im.width() ==  im2.width()
    assert im.height() ==  im2.height()
    assert hashstr(im.to_string()) ==  hashstr(im2.to_string())
    assert hashstr(im.to_string('tiff:method=tiled')) == hashstr(im2.to_string('tiff:method=tiled'))
    # should not be a blank image
    assert hashstr(im.to_string("tiff")) != hashstr(mapnik.Image(im.width(), im.height(), mapnik.ImageType.rgba8).to_string("tiff"))


def test_tiff_gray8_compare_scanline():
    filepath1 = '../data/tiff/ndvi_256x256_gray8_striped.tif'
    filepath2 = '/tmp/mapnik-tiff-gray8-scanline.tiff'
    im = mapnik.Image.open(filepath1)
    im.save(filepath2, 'tiff:method=scanline')
    im2 = mapnik.Image.open(filepath2)
    assert im.width() ==  im2.width()
    assert im.height() ==  im2.height()
    assert hashstr(im.to_string()) ==  hashstr(im2.to_string())
    assert hashstr(im.to_string('tiff:method=scanline')) == hashstr(im2.to_string('tiff:method=scanline'))
    # should not be a blank image
    assert hashstr(im.to_string("tiff")) != hashstr(mapnik.Image(im.width(), im.height(), mapnik.ImageType.gray8).to_string("tiff"))

def test_tiff_gray8_compare_stripped():
    filepath1 = '../data/tiff/ndvi_256x256_gray8_striped.tif'
    filepath2 = '/tmp/mapnik-tiff-gray8-stripped.tiff'
    im = mapnik.Image.open(filepath1)
    im.save(filepath2, 'tiff:method=stripped')
    im2 = mapnik.Image.open(filepath2)
    assert im.width() ==  im2.width()
    assert im.height() ==  im2.height()
    assert hashstr(im.to_string()) ==  hashstr(im2.to_string())
    assert hashstr(im.to_string('tiff:method=stripped')) == hashstr(im2.to_string('tiff:method=stripped'))
    # should not be a blank image
    assert hashstr(im.to_string("tiff")) != hashstr(mapnik.Image(im.width(), im.height(), mapnik.ImageType.gray8).to_string("tiff"))


def test_tiff_gray8_compare_tiled():
    filepath1 = '../data/tiff/ndvi_256x256_gray8_striped.tif'
    filepath2 = '/tmp/mapnik-tiff-gray8-tiled.tiff'
    im = mapnik.Image.open(filepath1)
    im.save(filepath2, 'tiff:method=tiled')
    im2 = mapnik.Image.open(filepath2)
    assert im.width() ==  im2.width()
    assert im.height() ==  im2.height()
    assert hashstr(im.to_string()) ==  hashstr(im2.to_string())
    assert hashstr(im.to_string('tiff:method=tiled')) == hashstr(im2.to_string('tiff:method=tiled'))
    # should not be a blank image
    assert hashstr(im.to_string("tiff")) != hashstr(mapnik.Image(im.width(), im.height(), mapnik.ImageType.gray8).to_string("tiff"))


def test_tiff_gray16_compare_scanline():
    filepath1 = '../data/tiff/ndvi_256x256_gray16_striped.tif'
    filepath2 = '/tmp/mapnik-tiff-gray16-scanline.tiff'
    im = mapnik.Image.open(filepath1)
    im.save(filepath2, 'tiff:method=scanline')
    im2 = mapnik.Image.open(filepath2)
    assert im.width() ==  im2.width()
    assert im.height() ==  im2.height()
    assert hashstr(im.to_string()) ==  hashstr(im2.to_string())
    assert hashstr(im.to_string('tiff:method=scanline')) == hashstr(im2.to_string('tiff:method=scanline'))
    # should not be a blank image
    assert hashstr(im.to_string("tiff")) != hashstr(mapnik.Image(im.width(), im.height(), mapnik.ImageType.gray16).to_string("tiff"))

def test_tiff_gray16_compare_stripped():
    filepath1 = '../data/tiff/ndvi_256x256_gray16_striped.tif'
    filepath2 = '/tmp/mapnik-tiff-gray16-stripped.tiff'
    im = mapnik.Image.open(filepath1)
    im.save(filepath2, 'tiff:method=stripped')
    im2 = mapnik.Image.open(filepath2)
    assert im.width() ==  im2.width()
    assert im.height() ==  im2.height()
    assert hashstr(im.to_string()) ==  hashstr(im2.to_string())
    assert hashstr(im.to_string('tiff:method=stripped')) == hashstr(im2.to_string('tiff:method=stripped'))
    # should not be a blank image
    assert hashstr(im.to_string("tiff")) != hashstr(mapnik.Image(im.width(), im.height(), mapnik.ImageType.gray16).to_string("tiff"))


def test_tiff_gray16_compare_tiled():
    filepath1 = '../data/tiff/ndvi_256x256_gray16_striped.tif'
    filepath2 = '/tmp/mapnik-tiff-gray16-tiled.tiff'
    im = mapnik.Image.open(filepath1)
    im.save(filepath2, 'tiff:method=tiled')
    im2 = mapnik.Image.open(filepath2)
    assert im.width() ==  im2.width()
    assert im.height() ==  im2.height()
    assert hashstr(im.to_string()) ==  hashstr(im2.to_string())
    assert hashstr(im.to_string('tiff:method=tiled')) == hashstr(im2.to_string('tiff:method=tiled'))
    # should not be a blank image
    assert hashstr(im.to_string("tiff")) != hashstr(mapnik.Image(im.width(), im.height(), mapnik.ImageType.gray16).to_string("tiff"))


def test_tiff_gray32f_compare_scanline():
    filepath1 = '../data/tiff/ndvi_256x256_gray32f_striped.tif'
    filepath2 = '/tmp/mapnik-tiff-gray32f-scanline.tiff'
    im = mapnik.Image.open(filepath1)
    im.save(filepath2, 'tiff:method=scanline')
    im2 = mapnik.Image.open(filepath2)
    assert im.width() ==  im2.width()
    assert im.height() ==  im2.height()
    assert hashstr(im.to_string()) ==  hashstr(im2.to_string())
    assert hashstr(im.to_string('tiff:method=scanline')) == hashstr(im2.to_string('tiff:method=scanline'))
    # should not be a blank image
    assert hashstr(im.to_string("tiff")) != hashstr(mapnik.Image(im.width(), im.height(), mapnik.ImageType.gray32f).to_string("tiff"))


def test_tiff_gray32f_compare_stripped():
    filepath1 = '../data/tiff/ndvi_256x256_gray32f_striped.tif'
    filepath2 = '/tmp/mapnik-tiff-gray32f-stripped.tiff'
    im = mapnik.Image.open(filepath1)
    im.save(filepath2, 'tiff:method=stripped')
    im2 = mapnik.Image.open(filepath2)
    assert im.width() ==  im2.width()
    assert im.height() ==  im2.height()
    assert hashstr(im.to_string()) ==  hashstr(im2.to_string())
    assert hashstr(im.to_string('tiff:method=stripped')) == hashstr(im2.to_string('tiff:method=stripped'))
    # should not be a blank image
    assert hashstr(im.to_string("tiff")) != hashstr(mapnik.Image(im.width(), im.height(), mapnik.ImageType.gray32f).to_string("tiff"))


def test_tiff_gray32f_compare_tiled():
    filepath1 = '../data/tiff/ndvi_256x256_gray32f_striped.tif'
    filepath2 = '/tmp/mapnik-tiff-gray32f-tiled.tiff'
    im = mapnik.Image.open(filepath1)
    im.save(filepath2, 'tiff:method=tiled')
    im2 = mapnik.Image.open(filepath2)
    assert im.width() ==  im2.width()
    assert im.height() ==  im2.height()
    assert hashstr(im.to_string()) ==  hashstr(im2.to_string())
    assert hashstr(im.to_string('tiff:method=tiled')) == hashstr(im2.to_string('tiff:method=tiled'))
    # should not be a blank image
    assert hashstr(im.to_string("tiff")) != hashstr(mapnik.Image(im.width(), im.height(), mapnik.ImageType.gray32f).to_string("tiff"))
