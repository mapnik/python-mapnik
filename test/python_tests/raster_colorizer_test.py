import os
import sys
import pytest
import mapnik

from .utilities import execution_path

@pytest.fixture
def setup():
    # All of the paths used are relative, if we run the tests
    # from another directory we need to chdir()
    os.chdir(execution_path('.'))
    yield

# test discrete colorizer mode
def test_get_color_discrete(setup):
    # setup
    colorizer = mapnik.RasterColorizer()
    colorizer.default_color = mapnik.Color(0, 0, 0, 0)
    colorizer.default_mode = mapnik.COLORIZER_DISCRETE

    colorizer.add_stop(10, mapnik.Color(100, 100, 100, 100))
    colorizer.add_stop(20, mapnik.Color(200, 200, 200, 200))

    # should be default colour
    assert colorizer.get_color(-50) == mapnik.Color(0, 0, 0, 0)
    assert colorizer.get_color(0) ==  mapnik.Color(0, 0, 0, 0)

    # now in stop 1
    assert colorizer.get_color(10) == mapnik.Color(100, 100, 100, 100)
    assert colorizer.get_color(19) == mapnik.Color(100, 100, 100, 100)

    # now in stop 2
    assert colorizer.get_color(20) == mapnik.Color(200, 200, 200, 200)
    assert colorizer.get_color(1000) ==  mapnik.Color(200, 200, 200, 200)

# test exact colorizer mode


def test_get_color_exact():
    # setup
    colorizer = mapnik.RasterColorizer()
    colorizer.default_color = mapnik.Color(0, 0, 0, 0)
    colorizer.default_mode = mapnik.COLORIZER_EXACT

    colorizer.add_stop(10, mapnik.Color(100, 100, 100, 100))
    colorizer.add_stop(20, mapnik.Color(200, 200, 200, 200))

    # should be default colour
    assert colorizer.get_color(-50) == mapnik.Color(0, 0, 0, 0)
    assert colorizer.get_color(11) == mapnik.Color(0, 0, 0, 0)
    assert colorizer.get_color(20.001) == mapnik.Color(0, 0, 0, 0)

    # should be stop 1
    assert colorizer.get_color(10) == mapnik.Color(100, 100, 100, 100)

    # should be stop 2
    assert colorizer.get_color(20) == mapnik.Color(200, 200, 200, 200)

# test linear colorizer mode


def test_get_color_linear():
    # setup
    colorizer = mapnik.RasterColorizer()
    colorizer.default_color = mapnik.Color(0, 0, 0, 0)
    colorizer.default_mode = mapnik.COLORIZER_LINEAR

    colorizer.add_stop(10, mapnik.Color(100, 100, 100, 100))
    colorizer.add_stop(20, mapnik.Color(200, 200, 200, 200))

    # should be default colour
    assert colorizer.get_color(-50) == mapnik.Color(0, 0, 0, 0)
    assert colorizer.get_color(9.9) == mapnik.Color(0, 0, 0, 0)

    # should be stop 1
    assert colorizer.get_color(10) == mapnik.Color(100, 100, 100, 100)

    # should be stop 2
    assert colorizer.get_color(20) == mapnik.Color(200, 200, 200, 200)

    # half way between stops 1 and 2
    assert colorizer.get_color(15) ==  mapnik.Color(150, 150, 150, 150)

    # after stop 2
    assert colorizer.get_color(100) ==  mapnik.Color(200, 200, 200, 200)


def test_stop_label():
    stop = mapnik.ColorizerStop(
        1, mapnik.COLORIZER_LINEAR, mapnik.Color('red'))
    assert not stop.label
    label = u"32º C"
    stop.label = label
    assert stop.label == label, stop.label
