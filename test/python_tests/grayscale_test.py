import mapnik

def test_grayscale_conversion():
    im = mapnik.Image(2, 2)
    im.fill(mapnik.Color('white'))
    im.set_grayscale_to_alpha()
    pixel = im.get_pixel(0, 0)
    assert (pixel >> 24) & 0xff == 255
