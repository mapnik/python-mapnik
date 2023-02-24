import sys
import mapnik

def test_parameter_null():
    p = mapnik.Parameter('key', None)
    assert p[0] ==  'key'
    assert p[1] ==  None


def test_parameter_string():
    p = mapnik.Parameter('key', 'value')
    assert p[0] ==  'key'
    assert p[1] ==  'value'


def test_parameter_unicode():
    p = mapnik.Parameter('key', u'value')
    assert p[0] ==  'key'
    assert p[1] ==  u'value'


def test_parameter_integer():
    p = mapnik.Parameter('int', sys.maxsize)
    assert p[0] ==  'int'
    assert p[1] ==  sys.maxsize


def test_parameter_double():
    p = mapnik.Parameter('double', float(sys.maxsize))
    assert p[0] ==  'double'
    assert p[1] ==  float(sys.maxsize)


def test_parameter_boolean():
    p = mapnik.Parameter('boolean', True)
    assert p[0] ==  'boolean'
    assert p[1] ==  True
    assert bool(p[1]) ==  True


def test_parameters():
    params = mapnik.Parameters()
    p = mapnik.Parameter('float', 1.0777)
    assert p[0] ==  'float'
    assert p[1] ==  1.0777

    params.append(p)

    assert params[0][0] ==  'float'
    assert params[0][1] ==  1.0777

    assert params.get('float') ==  1.0777
