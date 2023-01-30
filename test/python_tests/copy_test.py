import mapnik

def test_image_16_8_simple():
    im = mapnik.Image(2, 2, mapnik.ImageType.gray16)
    im.set_pixel(0, 0, 256)
    im.set_pixel(0, 1, 999)
    im.set_pixel(1, 0, 5)
    im.set_pixel(1, 1, 2)
    im2 = im.copy(mapnik.ImageType.gray8)
    assert im2.get_pixel(0, 0) ==  255
    assert im2.get_pixel(0, 1) ==  255
    assert im2.get_pixel(1, 0) ==  5
    assert im2.get_pixel(1, 1) ==  2
    # Cast back!
    im = im2.copy(mapnik.ImageType.gray16)
    assert im.get_pixel(0, 0) ==  255
    assert im.get_pixel(0, 1) ==  255
    assert im.get_pixel(1, 0) ==  5
    assert im.get_pixel(1, 1) ==  2


def test_image_32f_8_simple():
    im = mapnik.Image(2, 2, mapnik.ImageType.gray32f)
    im.set_pixel(0, 0, 120.1234)
    im.set_pixel(0, 1, -23.4)
    im.set_pixel(1, 0, 120.6)
    im.set_pixel(1, 1, 360.2)
    im2 = im.copy(mapnik.ImageType.gray8)
    assert im2.get_pixel(0, 0) ==  120
    assert im2.get_pixel(0, 1) ==  0
    assert im2.get_pixel(1, 0) ==  120  # Notice this is truncated!
    assert im2.get_pixel(1, 1) ==  255


def test_image_offset_and_scale():
    im = mapnik.Image(2, 2, mapnik.ImageType.gray16)
    assert im.offset ==  0.0
    assert im.scaling ==  1.0
    im.offset = 1.0
    im.scaling = 2.0
    assert im.offset ==  1.0
    assert im.scaling ==  2.0


def test_image_16_8_scale_and_offset():
    im = mapnik.Image(2, 2, mapnik.ImageType.gray16)
    im.set_pixel(0, 0, 256)
    im.set_pixel(0, 1, 258)
    im.set_pixel(1, 0, 99999)
    im.set_pixel(1, 1, 615)
    offset = 255
    scaling = 3
    im2 = im.copy(mapnik.ImageType.gray8, offset, scaling)
    assert im2.get_pixel(0, 0) ==  0
    assert im2.get_pixel(0, 1) ==  1
    assert im2.get_pixel(1, 0) ==  255
    assert im2.get_pixel(1, 1) ==  120
    # pixels will be a little off due to offsets in reverting!
    im3 = im2.copy(mapnik.ImageType.gray16)
    assert im3.get_pixel(0, 0) ==  255  # Rounding error with ints
    assert im3.get_pixel(0, 1) ==  258  # same
    # The other one was way out of range for our scale/offset
    assert im3.get_pixel(1, 0) ==  1020
    assert im3.get_pixel(1, 1) ==  615  # same


def test_image_16_32f_scale_and_offset():
    im = mapnik.Image(2, 2, mapnik.ImageType.gray16)
    im.set_pixel(0, 0, 256)
    im.set_pixel(0, 1, 258)
    im.set_pixel(1, 0, 0)
    im.set_pixel(1, 1, 615)
    offset = 255
    scaling = 3.2
    im2 = im.copy(mapnik.ImageType.gray32f, offset, scaling)
    assert im2.get_pixel(0, 0) ==  0.3125
    assert im2.get_pixel(0, 1) ==  0.9375
    assert im2.get_pixel(1, 0) ==  -79.6875
    assert im2.get_pixel(1, 1) ==  112.5
    im3 = im2.copy(mapnik.ImageType.gray16)
    assert im3.get_pixel(0, 0) ==  256
    assert im3.get_pixel(0, 1) ==  258
    assert im3.get_pixel(1, 0) ==  0
    assert im3.get_pixel(1, 1) ==  615
