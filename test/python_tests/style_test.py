import mapnik

def test_style_init():
    s = mapnik.Style()
    assert s.filter_mode ==  mapnik.filter_mode.ALL
    assert len(s.rules) ==  0
    assert s.opacity ==  1
    assert s.comp_op ==  None
    assert s.image_filters ==  ""
    assert not s.image_filters_inflate
