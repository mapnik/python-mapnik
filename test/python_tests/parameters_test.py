import sys
import mapnik

def test_parameter_null():
    p = mapnik.Parameters()
    p['key'] = None
    assert p['key'] is None


def test_parameter_string():
    p = mapnik.Parameters()
    p['key'] = 'value'
    assert p['key'] == 'value'


def test_parameter_unicode():
    p = mapnik.Parameters()
    p['key'] =  u'value'
    assert p['key'] ==  u'value'


def test_parameter_integer():
    p = mapnik.Parameters()
    p['int'] = sys.maxsize
    assert p['int'] ==  sys.maxsize


def test_parameter_double():
    p = mapnik.Parameters()
    p['double'] = float(sys.maxsize)
    assert p['double'] ==  float(sys.maxsize)


def test_parameter_boolean():
    p = mapnik.Parameters()
    p['boolean'] = True
    assert p['boolean'] ==  True
    assert bool(p['boolean']) ==  True


def test_parameters():
    p = mapnik.Parameters()
    p['float'] = 1.0777
    p['int'] = 123456789
    assert p['float'] == 1.0777
    assert p['int'] == 123456789
