import mapnik
import pytest

def test_coord_init():
    c = mapnik.Coord(100, 100)
    assert c.x == 100
    assert c.y == 100

def test_coord_multiplication():
     c = mapnik.Coord(100, 100)
     c *= 2
     assert c.x == 200
     assert c.y == 200

def test_envelope_init():
     e = mapnik.Box2d(100, 100, 200, 200)
     assert e.contains(100, 100)
     assert e.contains(100, 200)
     assert e.contains(200, 200)
     assert e.contains(200, 100)
     assert e.contains(e.center())
     assert not e.contains(99.9, 99.9)
     assert not e.contains(99.9, 200.1)
     assert not e.contains(200.1, 200.1)
     assert not e.contains(200.1, 99.9)
     assert e.width() ==  100
     assert e.height() == 100
     assert e.minx ==  100
     assert e.miny == 100
     assert e.maxx == 200
     assert e.maxy == 200
     assert  e[0] == 100
     assert  e[1] == 100
     assert  e[2] == 200
     assert  e[3] == 200
     assert  e[0] == e[-4]
     assert  e[1] == e[-3]
     assert  e[2] == e[-2]
     assert  e[3] == e[-1]
     c = e.center()
     assert  c.x == 150
     assert  c.y == 150


def test_envelope_static_init():
    e = mapnik.Box2d.from_string('100 100 200 200')
    e2 = mapnik.Box2d.from_string('100,100,200,200')
    e3 = mapnik.Box2d.from_string('100 , 100 , 200 , 200')

    assert  e == e2
    assert  e == e3
    assert e.contains(100, 100)
    assert e.contains(100, 200)
    assert e.contains(200, 200)
    assert e.contains(200, 100)

    assert e.contains(e.center())
    assert not e.contains(99.9, 99.9)
    assert not e.contains(99.9, 200.1)
    assert not e.contains(200.1, 200.1)
    assert not e.contains(200.1, 99.9)

    assert  e.width() == 100
    assert  e.height() == 100
    assert  e.minx == 100
    assert  e.miny == 100
    assert  e.maxx == 200
    assert  e.maxy == 200

    assert  e[0] == 100
    assert  e[1] == 100
    assert  e[2] == 200
    assert  e[3] == 200
    assert  e[0] == e[-4]
    assert  e[1] == e[-3]
    assert  e[2] == e[-2]
    assert  e[3] == e[-1]

    c = e.center()
    assert  c.x == 150
    assert  c.y == 150

def test_envelope_multiplication():
     # no width then no impact of multiplication
     a = mapnik.Box2d(100, 100, 100, 100)
     a *= 5
     assert a.minx == 100
     assert a.miny == 100
     assert a.maxx == 100
     assert a.maxy == 100

     a = mapnik.Box2d(100.0, 100.0, 100.0, 100.0)
     a *= 5
     assert  a.minx == 100
     assert  a.miny == 100
     assert  a.maxx == 100
     assert  a.maxy == 100

     a = mapnik.Box2d(100.0, 100.0, 100.001, 100.001)
     a *= 5
     assert a.minx == pytest.approx(99.9979, 1e-3)
     assert a.miny == pytest.approx(99.9979, 1e-3)
     assert a.maxx == pytest.approx(100.0030,1e-3)
     assert a.maxy == pytest.approx(100.0030,1e-3)

     e = mapnik.Box2d(100, 100, 200, 200)
     e *= 2
     assert  e.minx == 50
     assert  e.miny == 50
     assert  e.maxx == 250
     assert  e.maxy == 250

     assert e.contains(50, 50)
     assert e.contains(50, 250)
     assert e.contains(250, 250)
     assert e.contains(250, 50)

     assert not e.contains(49.9, 49.9)
     assert not e.contains(49.9, 250.1)
     assert not e.contains(250.1, 250.1)
     assert not e.contains(250.1, 49.9)

     c = e.center()
     assert  c.x == 150
     assert  c.y == 150

     assert e.contains(c)

     assert  e.width() == 200
     assert  e.height()== 200

     assert  e.minx == 50
     assert  e.miny == 50

     assert  e.maxx == 250
     assert  e.maxy == 250


def test_envelope_clipping():
     e1 = mapnik.Box2d(-180, -90, 180, 90)
     e2 = mapnik.Box2d(-120, 40, -110, 48)
     e1.clip(e2)
     assert  e1 == e2

     # madagascar in merc
     e1 = mapnik.Box2d(4772116.5490, -2744395.0631, 5765186.4203, -1609458.0673)
     e2 = mapnik.Box2d(5124338.3753, -2240522.1727, 5207501.8621, -2130452.8520)
     e1.clip(e2)
     assert  e1 == e2

#     # nz in lon/lat
     e1 = mapnik.Box2d(163.8062, -47.1897, 179.3628, -33.9069)
     e2 = mapnik.Box2d(173.7378, -39.6395, 174.4849, -38.9252)
     e1.clip(e2)
     assert  e1 == e2
