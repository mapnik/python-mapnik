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

def test_introspect_symbolizers(setup):
    # create a symbolizer
    p = mapnik.PointSymbolizer()
    p.file = "../data/images/dummy.png"
    p.allow_overlap = True
    p.opacity = 0.5

    assert p.allow_overlap ==  True
    assert p.opacity ==  0.5
    assert str(p.file) == '../data/images/dummy.png'

    # make sure the defaults
    # are what we think they are
    assert p.allow_overlap ==  True
    assert p.opacity ==  0.5
    assert str(p.file) ==  '../data/images/dummy.png'

    # contruct objects to hold it
    r = mapnik.Rule()
    r.symbolizers.append(p)
    s = mapnik.Style()
    s.rules.append(r)
    m = mapnik.Map(0, 0)
    m.append_style('s', s)

    # try to figure out what is
    # in the map and make sure
    # style is there and the same

    s2 = m.find_style('s')
    rules = s2.rules
    assert len(rules) ==  1
    r2 = rules[0]
    syms = r2.symbolizers
    assert len(syms) ==  1

    # TODO here, we can do...
    sym = syms[0]
    p2 = sym.extract()
    assert isinstance(p2, mapnik.PointSymbolizer)

    assert p2.allow_overlap ==  True
    assert p2.opacity ==  0.5
    assert str(p2.file) == '../data/images/dummy.png'
