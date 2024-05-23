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


def test_arbitrary_parameters_attached_to_map(setup):
    m = mapnik.Map(256, 256)
    mapnik.load_map(m, '../data/good_maps/extra_arbitary_map_parameters.xml')
    assert len(m.parameters) ==  5
    assert m.parameters['key'] ==  'value2'
    assert m.parameters['key3'] ==  'value3'
    assert m.parameters['unicode'] ==  u'iván'
    assert m.parameters['integer'] ==  10
    assert m.parameters['decimal'] ==  .999
    m2 = mapnik.Map(256, 256)
    for k, v in m.parameters.items():
        m2.parameters[k] = v
    assert len(m2.parameters) ==  5
    assert m2.parameters['key'] ==  'value2'
    assert m2.parameters['key3'] ==  'value3'
    assert m2.parameters['unicode'] ==  u'iván'
    assert m2.parameters['integer'] ==  10
    assert m2.parameters['decimal'] ==  .999
    map_string = mapnik.save_map_to_string(m)
    m3 = mapnik.Map(256, 256)
    mapnik.load_map_from_string(m3, map_string)
    assert len(m3.parameters) ==  5
    assert m3.parameters['key'] ==  'value2'
    assert m3.parameters['key3'] ==  'value3'
    assert m3.parameters['unicode'] ==  u'iván'
    assert m3.parameters['integer'] ==  10
    assert m3.parameters['decimal'] ==  .999


def test_serializing_arbitrary_parameters():
    m = mapnik.Map(256, 256)
    m.parameters['width'] =  m.width
    m.parameters['height'] = m.height

    m2 = mapnik.Map(1, 1)
    mapnik.load_map_from_string(m2, mapnik.save_map_to_string(m))
    assert m2.parameters['width'] ==  m.width
    assert m2.parameters['height'] ==  m.height
