import os
import mapnik

def test_color_init():
    c = mapnik.Color(12, 128, 255)
    assert c.r == 12
    assert c.g == 128
    assert c.b == 255
    assert c.a == 255
    assert not c.get_premultiplied()
    c = mapnik.Color(16, 32, 64, 128)
    assert c.r == 16
    assert c.g == 32
    assert c.b == 64
    assert c.a == 128
    assert not c.get_premultiplied()
    c = mapnik.Color(16, 32, 64, 128, True)
    assert c.r == 16
    assert c.g == 32
    assert c.b == 64
    assert c.a == 128
    assert c.get_premultiplied()
    c = mapnik.Color('rgba(16,32,64,0.5)')
    assert c.r == 16
    assert c.g == 32
    assert c.b == 64
    assert c.a == 128
    assert not c.get_premultiplied()
    c = mapnik.Color('rgba(16,32,64,0.5)', True)
    assert c.r == 16
    assert c.g == 32
    assert c.b == 64
    assert c.a == 128
    assert c.get_premultiplied()
    hex_str = '#10204080'
    c = mapnik.Color(hex_str)
    assert c.r == 16
    assert c.g == 32
    assert c.b == 64
    assert c.a == 128
    assert hex_str == c.to_hex_string()
    assert not c.get_premultiplied()
    c = mapnik.Color(hex_str, True)
    assert c.r == 16
    assert c.g == 32
    assert c.b == 64
    assert c.a == 128
    assert hex_str == c.to_hex_string()
    assert c.get_premultiplied()
    rgba_int = 2151686160
    c = mapnik.Color(rgba_int)
    assert c.r == 16
    assert c.g == 32
    assert c.b == 64
    assert c.a == 128
    assert rgba_int == c.packed()
    assert not c.get_premultiplied()
    c = mapnik.Color(rgba_int, True)
    assert c.r == 16
    assert c.g == 32
    assert c.b == 64
    assert c.a == 128
    assert rgba_int == c.packed()
    assert c.get_premultiplied()


def test_color_properties():
    c = mapnik.Color(16, 32, 64, 128)
    assert c.r == 16
    assert c.g == 32
    assert c.b == 64
    assert c.a == 128
    c.r = 17
    assert c.r == 17
    c.g = 33
    assert c.g == 33
    c.b = 65
    assert c.b == 65
    c.a = 128
    assert c.a == 128


def test_color_premultiply():
    c = mapnik.Color(16, 33, 255, 128)
    assert c.premultiply()
    assert c.r == 8
    assert c.g == 17
    assert c.b == 128
    assert c.a == 128
    # Repeating it again should do nothing
    assert not c.premultiply()
    assert c.r == 8
    assert c.g == 17
    assert c.b == 128
    assert c.a == 128
    c.demultiply()
    c.demultiply()
    # This will not return the same values as before but we expect that
    assert c.r == 15
    assert c.g == 33
    assert c.b == 255
    assert c.a == 128
