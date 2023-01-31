import mapnik

def test_introspect_symbolizers():
    # create a symbolizer
    p = mapnik.PointSymbolizer()
    p.file = "./test/data/images/dummy.png"
    p.allow_overlap = True
    p.opacity = 0.5

    assert p.allow_overlap ==  True
    assert p.opacity ==  0.5
    assert p.filename ==  './test/data/images/dummy.png'

    # make sure the defaults
    # are what we think they are
    assert p.allow_overlap ==  True
    assert p.opacity ==  0.5
    assert p.filename ==  './test/data/images/dummy.png'

    # contruct objects to hold it
    r = mapnik.Rule()
    r.symbols.append(p)
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
    syms = r2.symbols
    assert len(syms) ==  1

    # TODO here, we can do...
    sym = syms[0]
    p2 = sym.extract()
    assert isinstance(p2, mapnik.PointSymbolizer)

    assert p2.allow_overlap ==  True
    assert p2.opacity ==  0.5
    assert p2.filename ==  './test/data/images/dummy.png'
