import os
import mapnik
import pytest

from .utilities import READ_FLAGS, get_unique_colors, execution_path

@pytest.fixture(scope="module")
def setup():
    # All of the paths used are relative, if we run the tests
    # from another directory we need to chdir()
    os.chdir(execution_path('.'))
    yield

def test_type(setup):
    im = mapnik.Image(256, 256)
    assert im.get_type() ==  mapnik.ImageType.rgba8
    im = mapnik.Image(256, 256, mapnik.ImageType.gray8)
    assert im.get_type() ==  mapnik.ImageType.gray8


def test_image_premultiply():
    im = mapnik.Image(256, 256)
    assert im.premultiplied() ==  False
    # Premultiply should return true that it worked
    assert im.premultiply() ==  True
    assert im.premultiplied() ==  True
    # Premultipling again should return false as nothing should happen
    assert im.premultiply() ==  False
    assert im.premultiplied() ==  True
    # Demultiply should return true that it worked
    assert im.demultiply() ==  True
    assert im.premultiplied() ==  False
    # Demultiply again should not work and return false as it did nothing
    assert im.demultiply() ==  False
    assert im.premultiplied() ==  False


def test_image_premultiply_values():
    im = mapnik.Image(256, 256)
    im.fill(mapnik.Color(16, 33, 255, 128))
    im.premultiply()
    c = im.get_pixel_color(0, 0)
    assert c.r ==  8
    assert c.g ==  17
    assert c.b ==  128
    assert c.a ==  128
    im.demultiply()
    # Do to the nature of this operation the result will not be exactly the
    # same
    c = im.get_pixel_color(0, 0)
    assert c.r ==  15
    assert c.g ==  33
    assert c.b ==  255
    assert c.a ==  128


def test_apply_opacity():
    im = mapnik.Image(4, 4)
    im.fill(mapnik.Color(128, 128, 128, 128))
    im.apply_opacity(0.75)
    c = im.get_pixel_color(0, 0)
    assert c.r ==  128
    assert c.g ==  128
    assert c.b ==  128
    assert c.a ==  96


def test_background():
    im = mapnik.Image(256, 256)
    assert im.premultiplied() ==  False
    im.fill(mapnik.Color(32, 64, 125, 128))
    assert im.premultiplied() ==  False
    c = im.get_pixel_color(0, 0)
    assert c.get_premultiplied() ==  False
    assert c.r ==  32
    assert c.g ==  64
    assert c.b ==  125
    assert c.a ==  128
    # Now again with a premultiplied alpha
    im.fill(mapnik.Color(32, 64, 125, 128, True))
    assert im.premultiplied() ==  True
    c = im.get_pixel_color(0, 0)
    assert c.get_premultiplied() ==  True
    assert c.r ==  32
    assert c.g ==  64
    assert c.b ==  125
    assert c.a ==  128


def test_set_and_get_pixel():
    # Create an image that is not premultiplied
    im = mapnik.Image(256, 256)
    c0 = mapnik.Color(16, 33, 255, 128)
    c0_pre = mapnik.Color(16, 33, 255, 128, True)
    im.set_pixel(0, 0, c0)
    im.set_pixel(1, 1, c0_pre)
    # No differences for non premultiplied pixels
    c1_int = mapnik.Color(im.get_pixel(0, 0))
    assert c0.r ==  c1_int.r
    assert c0.g ==  c1_int.g
    assert c0.b ==  c1_int.b
    assert c0.a ==  c1_int.a
    c1 = im.get_pixel_color(0, 0)
    assert c0.r ==  c1.r
    assert c0.g ==  c1.g
    assert c0.b ==  c1.b
    assert c0.a ==  c1.a
    # The premultiplied Color should be demultiplied before being applied.
    c0_pre.demultiply()
    c1_int = mapnik.Color(im.get_pixel(1, 1))
    assert c0_pre.r ==  c1_int.r
    assert c0_pre.g ==  c1_int.g
    assert c0_pre.b ==  c1_int.b
    assert c0_pre.a ==  c1_int.a
    c1 = im.get_pixel_color(1, 1)
    assert c0_pre.r ==  c1.r
    assert c0_pre.g ==  c1.g
    assert c0_pre.b ==  c1.b
    assert c0_pre.a ==  c1.a

    # Now create a new image that is premultiplied
    im = mapnik.Image(256, 256, mapnik.ImageType.rgba8, True, True)
    c0 = mapnik.Color(16, 33, 255, 128)
    c0_pre = mapnik.Color(16, 33, 255, 128, True)
    im.set_pixel(0, 0, c0)
    im.set_pixel(1, 1, c0_pre)
    # It should have put pixels that are the same as premultiplied so
    # premultiply c0
    c0.premultiply()
    c1_int = mapnik.Color(im.get_pixel(0, 0))
    assert c0.r ==  c1_int.r
    assert c0.g ==  c1_int.g
    assert c0.b ==  c1_int.b
    assert c0.a ==  c1_int.a
    c1 = im.get_pixel_color(0, 0)
    assert c0.r ==  c1.r
    assert c0.g ==  c1.g
    assert c0.b ==  c1.b
    assert c0.a ==  c1.a
    # The premultiplied Color should be the same though
    c1_int = mapnik.Color(im.get_pixel(1, 1))
    assert c0_pre.r ==  c1_int.r
    assert c0_pre.g ==  c1_int.g
    assert c0_pre.b ==  c1_int.b
    assert c0_pre.a ==  c1_int.a
    c1 = im.get_pixel_color(1, 1)
    assert c0_pre.r ==  c1.r
    assert c0_pre.g ==  c1.g
    assert c0_pre.b ==  c1.b
    assert c0_pre.a ==  c1.a


def test_pixel_gray8():
    im = mapnik.Image(4, 4, mapnik.ImageType.gray8)
    val_list = range(20)
    for v in val_list:
        im.set_pixel(0, 0, v)
        assert im.get_pixel(0, 0) ==  v
        im.set_pixel(0, 0, -v)
        assert im.get_pixel(0, 0) ==  0


def test_pixel_gray8s():
    im = mapnik.Image(4, 4, mapnik.ImageType.gray8s)
    val_list = range(20)
    for v in val_list:
        im.set_pixel(0, 0, v)
        assert im.get_pixel(0, 0) ==  v
        im.set_pixel(0, 0, -v)
        assert im.get_pixel(0, 0) ==  -v


def test_pixel_gray16():
    im = mapnik.Image(4, 4, mapnik.ImageType.gray16)
    val_list = range(20)
    for v in val_list:
        im.set_pixel(0, 0, v)
        assert im.get_pixel(0, 0) ==  v
        im.set_pixel(0, 0, -v)
        assert im.get_pixel(0, 0) ==  0


def test_pixel_gray16s():
    im = mapnik.Image(4, 4, mapnik.ImageType.gray16s)
    val_list = range(20)
    for v in val_list:
        im.set_pixel(0, 0, v)
        assert im.get_pixel(0, 0) ==  v
        im.set_pixel(0, 0, -v)
        assert im.get_pixel(0, 0) ==  -v


def test_pixel_gray32():
    im = mapnik.Image(4, 4, mapnik.ImageType.gray32)
    val_list = range(20)
    for v in val_list:
        im.set_pixel(0, 0, v)
        assert im.get_pixel(0, 0) ==  v
        im.set_pixel(0, 0, -v)
        assert im.get_pixel(0, 0) ==  0


def test_pixel_gray32s():
    im = mapnik.Image(4, 4, mapnik.ImageType.gray32s)
    val_list = range(20)
    for v in val_list:
        im.set_pixel(0, 0, v)
        assert im.get_pixel(0, 0) ==  v
        im.set_pixel(0, 0, -v)
        assert im.get_pixel(0, 0) ==  -v


def test_pixel_gray64():
    im = mapnik.Image(4, 4, mapnik.ImageType.gray64)
    val_list = range(20)
    for v in val_list:
        im.set_pixel(0, 0, v)
        assert im.get_pixel(0, 0) ==  v
        im.set_pixel(0, 0, -v)
        assert im.get_pixel(0, 0) ==  0


def test_pixel_gray64s():
    im = mapnik.Image(4, 4, mapnik.ImageType.gray64s)
    val_list = range(20)
    for v in val_list:
        im.set_pixel(0, 0, v)
        assert im.get_pixel(0, 0) ==  v
        im.set_pixel(0, 0, -v)
        assert im.get_pixel(0, 0) ==  -v


def test_pixel_floats():
    im = mapnik.Image(4, 4, mapnik.ImageType.gray32f)
    val_list = [0.9, 0.99, 0.999, 0.9999, 0.99999, 1, 1.0001, 1.001, 1.01, 1.1]
    for v in val_list:
        im.set_pixel(0, 0, v)
        assert im.get_pixel(0, 0) == pytest.approx(v)
        im.set_pixel(0, 0, -v)
        assert im.get_pixel(0, 0) == pytest.approx(-v)


def test_pixel_doubles():
    im = mapnik.Image(4, 4, mapnik.ImageType.gray64f)
    val_list = [0.9, 0.99, 0.999, 0.9999, 0.99999, 1, 1.0001, 1.001, 1.01, 1.1]
    for v in val_list:
        im.set_pixel(0, 0, v)
        assert im.get_pixel(0, 0) == pytest.approx(v)
        im.set_pixel(0, 0, -v)
        assert im.get_pixel(0, 0) == pytest.approx(-v)


def test_pixel_overflow():
    im = mapnik.Image(4, 4, mapnik.ImageType.gray8)
    im.set_pixel(0, 0, 256)
    assert im.get_pixel(0, 0) ==  255


def test_pixel_underflow():
    im = mapnik.Image(4, 4, mapnik.ImageType.gray8)
    im.set_pixel(0, 0, -1)
    assert im.get_pixel(0, 0) ==  0
    im = mapnik.Image(4, 4, mapnik.ImageType.gray16)
    im.set_pixel(0, 0, -1)
    assert im.get_pixel(0, 0) ==  0


def test_set_pixel_out_of_range_1():
    with pytest.raises(IndexError):
        im = mapnik.Image(4, 4)
        c = mapnik.Color('blue')
        im.set_pixel(5, 5, c)


def test_set_pixel_out_of_range_2():
    with pytest.raises(IndexError):
        im = mapnik.Image(4, 4)
        c = mapnik.Color('blue')
        im.set_pixel(-1, 1, c)


def test_get_pixel_out_of_range_1():
    with pytest.raises(IndexError):
        im = mapnik.Image(4, 4)
        c = im.get_pixel(5, 5)


def test_get_pixel_out_of_range_2():
    with pytest.raises(IndexError):
        im = mapnik.Image(4, 4)
        c = im.get_pixel(-1, 1)


def test_get_pixel_color_out_of_range_1():
    with pytest.raises(IndexError):
        im = mapnik.Image(4, 4)
        c = im.get_pixel_color(5, 5)


def test_get_pixel_color_out_of_range_2():
    with pytest.raises(IndexError):
        im = mapnik.Image(4, 4)
        c = im.get_pixel_color(-1, 1)


def test_set_color_to_alpha():
    im = mapnik.Image(256, 256)
    im.fill(mapnik.Color('rgba(12,12,12,255)'))
    assert get_unique_colors(im), ['rgba(12,12,12 == 255)']
    im.set_color_to_alpha(mapnik.Color('rgba(12,12,12,0)'))
    assert get_unique_colors(im), ['rgba(0,0,0 == 0)']


def test_negative_image_dimensions():
    with pytest.raises(RuntimeError):
        # TODO - this may have regressed in
        # https://github.com/mapnik/mapnik/commit/4f3521ac24b61fc8ae8fd344a16dc3a5fdf15af7
        im = mapnik.Image(-40, 40)
        # should not get here
        assert im.width() ==  0
        assert im.height() ==  0


def test_jpeg_round_trip():
    filepath = '/tmp/mapnik-jpeg-io.jpeg'
    im = mapnik.Image(255, 267)
    im.fill(mapnik.Color('rgba(1,2,3,.5)'))
    im.save(filepath, 'jpeg')
    im2 = mapnik.Image.open(filepath)
    with open(filepath, READ_FLAGS) as f:
        im3 = mapnik.Image.from_string(f.read())
    assert im.width() ==  im2.width()
    assert im.height() ==  im2.height()
    assert im.width() ==  im3.width()
    assert im.height() ==  im3.height()
    assert len(im.to_string()) ==  len(im2.to_string())
    assert len(im.to_string('jpeg')) ==  len(im2.to_string('jpeg'))
    assert len(im.to_string()) ==  len(im3.to_string())
    assert len(im.to_string('jpeg')) ==  len(im3.to_string('jpeg'))


def test_png_round_trip():
    filepath = '/tmp/mapnik-png-io.png'
    im = mapnik.Image(255, 267)
    im.fill(mapnik.Color('rgba(1,2,3,.5)'))
    im.save(filepath, 'png')
    im2 = mapnik.Image.open(filepath)
    with open(filepath, READ_FLAGS) as f:
        im3 = mapnik.Image.from_string(f.read())
    assert im.width() ==  im2.width()
    assert im.height() ==  im2.height()
    assert im.width() ==  im3.width()
    assert im.height() ==  im3.height()
    assert len(im.to_string()) ==  len(im2.to_string())
    assert len(im.to_string('png')) ==  len(im2.to_string('png'))
    assert len(im.to_string('png8')) ==  len(im2.to_string('png8'))
    assert len(im.to_string()) ==  len(im3.to_string())
    assert len(im.to_string('png')) ==  len(im3.to_string('png'))
    assert len(im.to_string('png8')) ==  len(im3.to_string('png8'))


def test_image_open_from_string():
    filepath = '../data/images/dummy.png'
    im1 = mapnik.Image.open(filepath)
    with open(filepath, READ_FLAGS) as f:
        im2 = mapnik.Image.from_string(f.read())
    assert im1.width() ==  im2.width()
    length = len(im1.to_string())
    assert length ==  len(im2.to_string())
    assert len(mapnik.Image.from_string(im1.to_string('png')).to_string()) ==  length
    assert len(mapnik.Image.from_string(im1.to_string('jpeg')).to_string()) ==  length
    assert len(mapnik.Image.from_memoryview(memoryview(im1.to_string('png'))).to_string()) ==  length
    assert len(mapnik.Image.from_memoryview(memoryview(im1.to_string('jpeg'))).to_string()) ==  length

    # TODO - https://github.com/mapnik/mapnik/issues/1831
    assert len(mapnik.Image.from_string(im1.to_string('tiff')).to_string()) ==  length
    assert len(mapnik.Image.from_memoryview(memoryview(im1.to_string('tiff'))).to_string()) ==  length
