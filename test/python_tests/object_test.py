import os
import tempfile
import mapnik
import pytest

from .utilities import execution_path

@pytest.fixture(scope="module")
def setup():
    # All of the paths used are relative, if we run the tests
    # from another directory we need to chdir()
    os.chdir(execution_path('.'))
    yield

def test_debug_symbolizer(setup):
    s = mapnik.DebugSymbolizer()
    s.mode = mapnik.debug_symbolizer_mode.COLLISION
    assert s.mode == mapnik.debug_symbolizer_mode.COLLISION

def test_raster_symbolizer():
    s = mapnik.RasterSymbolizer()
    s.comp_op = mapnik.CompositeOp.src_over
    s.scaling = mapnik.scaling_method.NEAR
    s.opacity = 1.0
    s.mesh_size = 16

    assert s.comp_op == mapnik.CompositeOp.src_over  # note: mode is deprecated
    assert s.scaling == mapnik.scaling_method.NEAR
    assert s.opacity == 1.0
    assert s.colorizer == None
    assert s.mesh_size == 16
    assert s.premultiplied == None
    s.premultiplied = True
    assert s.premultiplied == True

def test_line_pattern():
    s = mapnik.LinePatternSymbolizer()
    s.file = mapnik.PathExpression('../data/images/dummy.png')
    assert str(s.file) ==  '../data/images/dummy.png'

def test_map_init():
    m = mapnik.Map(256, 256)
    assert m.width ==  256
    assert m.height ==  256
    assert m.srs ==  'epsg:4326'
    assert m.base ==  ''
    assert m.maximum_extent ==  None
    assert m.background_image ==  None
    assert m.background_image_comp_op ==  mapnik.CompositeOp.src_over
    assert m.background_image_opacity ==  1.0
    m = mapnik.Map(256, 256, '+proj=latlong')
    assert m.srs ==  '+proj=latlong'

def test_map_style_access():
    m = mapnik.Map(256, 256)
    sty = mapnik.Style()
    m.append_style("style",sty)
    styles = list(m.styles.items())
    assert len(styles) == 1
    assert styles[0][0] == 'style'
    # returns a copy so let's just check it is the right instance
    assert isinstance(styles[0][1],mapnik.Style)

def test_map_maximum_extent_modification():
    m = mapnik.Map(256, 256)
    assert m.maximum_extent ==  None
    m.maximum_extent = mapnik.Box2d()
    assert m.maximum_extent ==  mapnik.Box2d()
    m.maximum_extent = None
    assert m.maximum_extent ==  None

# Map initialization from string
def test_map_init_from_string():
    map_string = '''<Map background-color="steelblue" base="./" srs="epsg:4326">
     <Style name="My Style">
      <Rule>
       <PolygonSymbolizer fill="#f2eff9"/>
       <LineSymbolizer stroke="rgb(50%,50%,50%)" stroke-width="0.1"/>
      </Rule>
     </Style>
     <Layer name="boundaries">
      <StyleName>My Style</StyleName>
       <Datasource>
        <Parameter name="type">shape</Parameter>
        <Parameter name="file">../../demo/data/boundaries</Parameter>
       </Datasource>
      </Layer>
    </Map>'''

    m = mapnik.Map(600, 300)
    assert m.base ==  ''
    try:
        mapnik.load_map_from_string(m, map_string)
        assert m.base ==  './'
        mapnik.load_map_from_string(m, map_string, False, "") # this "" will have no effect
        assert m.base ==  './'

        tmp_dir = tempfile.gettempdir()
        try:
            mapnik.load_map_from_string(m, map_string, False, tmp_dir)
        except RuntimeError:
            pass # runtime error expected because shapefile path should be wrong and datasource will throw
        assert m.base ==  tmp_dir  # tmp_dir will be set despite the exception because load_map mostly worked
        m.remove_all()
        m.base = 'foo'
        mapnik.load_map_from_string(m, map_string, True, ".")
        assert m.base ==  '.'
    except RuntimeError as e:
        # only test datasources that we have installed
        if not 'Could not create datasource' in str(e):
            raise RuntimeError(e)

# # Color initialization
def test_color_init_errors():
    with pytest.raises(Exception): # Boost.Python.ArgumentError
        c = mapnik.Color()

def test_color_init_errors():
    with pytest.raises(RuntimeError):
        c = mapnik.Color('foo') # mapnik config

def test_color_init():
     c = mapnik.Color('blue')
     assert c.a ==  255
     assert c.r ==  0
     assert c.g ==  0
     assert c.b ==  255

     assert c.to_hex_string() ==  '#0000ff'

     c = mapnik.Color('#f2eff9')

     assert c.a ==  255
     assert c.r ==  242
     assert c.g ==  239
     assert c.b ==  249

     assert c.to_hex_string() ==  '#f2eff9'

     c = mapnik.Color('rgb(50%,50%,50%)')

     assert c.a ==  255
     assert c.r ==  128
     assert c.g ==  128
     assert c.b ==  128

     assert c.to_hex_string() ==  '#808080'

     c = mapnik.Color(0, 64, 128)

     assert c.a ==  255
     assert c.r ==  0
     assert c.g ==  64
     assert c.b ==  128

     assert c.to_hex_string() ==  '#004080'

     c = mapnik.Color(0, 64, 128, 192)

     assert c.a ==  192
     assert c.r ==  0
     assert c.g ==  64
     assert c.b ==  128

     assert c.to_hex_string() ==  '#004080c0'

def test_color_equality():

    c1 = mapnik.Color('blue')
    c2 = mapnik.Color(0,0,255)
    c3 = mapnik.Color('black')

    c3.r = 0
    c3.g = 0
    c3.b = 255
    c3.a = 255

    assert c1 ==  c2
    assert c1 ==  c3

    c1 = mapnik.Color(0, 64, 128)
    c2 = mapnik.Color(0, 64, 128)
    c3 = mapnik.Color(0, 0, 0)

    c3.r = 0
    c3.g = 64
    c3.b = 128

    assert c1 ==  c2
    assert c1 ==  c3

    c1 = mapnik.Color(0, 64, 128, 192)
    c2 = mapnik.Color(0, 64, 128, 192)
    c3 = mapnik.Color(0, 0, 0, 255)

    c3.r = 0
    c3.g = 64
    c3.b = 128
    c3.a = 192

    assert c1 ==  c2
    assert c1 ==  c3

    c1 = mapnik.Color('rgb(50%,50%,50%)')
    c2 = mapnik.Color(128, 128, 128, 255)
    c3 = mapnik.Color('#808080')
    c4 = mapnik.Color('gray')

    assert c1 ==  c2
    assert c1 ==  c3
    assert c1 ==  c4

    c1 = mapnik.Color('hsl(0, 100%, 50%)')   # red
    c2 = mapnik.Color('hsl(120, 100%, 50%)') # lime
    c3 = mapnik.Color('hsla(240, 100%, 50%, 0.5)') # semi-transparent solid blue

    assert c1 ==  mapnik.Color('red')
    assert c2 ==  mapnik.Color('lime')
    assert c3, mapnik.Color(0,0,255 == 128)

def test_rule_init():
    min_scale = 5
    max_scale = 10

    r = mapnik.Rule()

    assert r.name ==  ''
    assert r.min_scale ==  0
    assert r.max_scale ==  float('inf')
    assert r.has_else() ==  False
    assert r.has_also() ==  False

    r = mapnik.Rule()

    r.set_else(True)
    assert r.has_else() ==  True
    assert r.has_also() ==  False

    r = mapnik.Rule()

    r.set_also(True)
    assert r.has_else() ==  False
    assert r.has_also() ==  True

    r = mapnik.Rule("Name")

    assert r.name ==  'Name'
    assert r.min_scale ==  0
    assert r.max_scale ==  float('inf')
    assert r.has_else() ==  False
    assert r.has_also() ==  False

    r = mapnik.Rule("Name")

    assert r.name ==  'Name'
    assert r.min_scale ==  0
    assert r.max_scale ==  float('inf')
    assert r.has_else() ==  False
    assert r.has_also() ==  False

    r = mapnik.Rule("Name", min_scale)

    assert r.name ==  'Name'
    assert r.min_scale ==  min_scale
    assert r.max_scale ==  float('inf')
    assert r.has_else() ==  False
    assert r.has_also() ==  False

    r = mapnik.Rule("Name", min_scale, max_scale)

    assert r.name ==  'Name'
    assert r.min_scale ==  min_scale
    assert r.max_scale ==  max_scale
    assert r.has_else() ==  False
    assert r.has_also() ==  False
