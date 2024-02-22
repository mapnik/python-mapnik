import os
import mapnik
import pytest

from .utilities import execution_path

@pytest.fixture(scope="module")
def setup():
    # All of the paths used are relative, if we run the tests
    # from another directory we need to chdir()
    os.chdir(execution_path('.'))
    yield


def test_loading_fontset_from_map(setup):
    m = mapnik.Map(256, 256)
    mapnik.load_map(m, '../data/good_maps/fontset.xml', True)
    fs = m.find_fontset('book-fonts')
    assert len(fs.names) ==  2
    assert list(fs.names) == ['DejaVu Sans Book', 'DejaVu Sans Oblique']

# def test_loading_fontset_from_python():
#     m = mapnik.Map(256,256)
#     fset = mapnik.FontSet('foo')
#     fset.add_face_name('Comic Sans')
#     fset.add_face_name('Papyrus')
#     assert fset.name == 'foo'
#     fset.name = 'my-set'
#     assert fset.name == 'my-set'
#     m.append_fontset('my-set', fset)
#     sty = mapnik.Style()
#     rule = mapnik.Rule()
#     tsym = mapnik.TextSymbolizer()
#     assert tsym.fontset == None
#     tsym.fontset = fset
#     rule.symbols.append(tsym)
#     sty.rules.append(rule)
#     m.append_style('Style',sty)
#     serialized_map = mapnik.save_map_to_string(m)
#     assert 'fontset-name="my-set"' in serialized_map == True
