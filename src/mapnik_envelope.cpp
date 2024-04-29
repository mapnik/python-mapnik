/*****************************************************************************
 *
 * This file is part of Mapnik (c++ mapping toolkit)
 *
 * Copyright (C) 2024 Artem Pavlenko
 *
 * This library is free software; you can redistribute it and/or
 * modify it under the terms of the GNU Lesser General Public
 * License as published by the Free Software Foundation; either
 * version 2.1 of the License, or (at your option) any later version.
 *
 * This library is distributed in the hope that it will be useful,
 * but WITHOUT ANY WARRANTY; without even the implied warranty of
 * MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the GNU
 * Lesser General Public License for more details.
 *
 * You should have received a copy of the GNU Lesser General Public
 * License along with this library; if not, write to the Free Software
 * Foundation, Inc., 51 Franklin St, Fifth Floor, Boston, MA  02110-1301  USA
 *
 *****************************************************************************/

// mapnik
#include <mapnik/config.hpp>
#include <mapnik/geometry/box2d.hpp>
#include <mapnik/value/error.hpp>
//stl
#include <sstream>
//pybind11
#include <pybind11/pybind11.h>
#include <pybind11/operators.h>

namespace py = pybind11;

using mapnik::coord;
using mapnik::box2d;

box2d<double> from_string(std::string const& s)
{
    box2d<double> bbox;
    bool success = bbox.from_string(s);
    if (success)
    {
        return bbox;
    }
    else
    {
        std::stringstream ss;
        ss << "Could not parse bbox from string: '" << s << "'";
        throw mapnik::value_error(ss.str());
    }
}

//define overloads here
void (box2d<double>::*width_p1)(double) = &box2d<double>::width;
double (box2d<double>::*width_p2)() const = &box2d<double>::width;

void (box2d<double>::*height_p1)(double) = &box2d<double>::height;
double (box2d<double>::*height_p2)() const = &box2d<double>::height;

void (box2d<double>::*expand_to_include_p1)(double,double) = &box2d<double>::expand_to_include;
void (box2d<double>::*expand_to_include_p2)(coord<double,2> const& ) = &box2d<double>::expand_to_include;
void (box2d<double>::*expand_to_include_p3)(box2d<double> const& ) = &box2d<double>::expand_to_include;

bool (box2d<double>::*contains_p1)(double,double) const = &box2d<double>::contains;
bool (box2d<double>::*contains_p2)(coord<double,2> const&) const = &box2d<double>::contains;
bool (box2d<double>::*contains_p3)(box2d<double> const&) const = &box2d<double>::contains;

//intersects
bool (box2d<double>::*intersects_p1)(double,double) const = &box2d<double>::intersects;
bool (box2d<double>::*intersects_p2)(coord<double,2> const&) const = &box2d<double>::intersects;
bool (box2d<double>::*intersects_p3)(box2d<double> const&) const = &box2d<double>::intersects;

// intersect
box2d<double> (box2d<double>::*intersect)(box2d<double> const&) const = &box2d<double>::intersect;

// re_center
void (box2d<double>::*re_center_p1)(double,double) = &box2d<double>::re_center;
void (box2d<double>::*re_center_p2)(coord<double,2> const& ) = &box2d<double>::re_center;

// clip
void (box2d<double>::*clip)(box2d<double> const&) = &box2d<double>::clip;

// pad
void (box2d<double>::*pad)(double) = &box2d<double>::pad;

// to string


void export_envelope(py::module const& m)
{
    py::class_<box2d<double> >(m, "Box2d")
        // class docstring is in mapnik/__init__.py, class _Coord
        .def(py::init<double,double,double,double>(),
             "Constructs a new envelope from the coordinates\n"
             "of its lower left and upper right corner points.\n",
             py::arg("minx"),py::arg("miny"),py::arg("maxx"),py::arg("maxy"))

        .def(py::init<>(), "Equivalent to Box2d(INVALID).\n")

        .def(py::init<coord<double,2> const&, coord<double,2> const&>(),
             "Equivalent to Box2d(ll.x, ll.y, ur.x, ur.y).\n",
             py::arg("ll"),py::arg("ur"))

        .def_static("from_string",from_string)
        .def_property("minx", &box2d<double>::minx, &box2d<double>::set_minx,
                      "X coordinate for the lower left corner")
        .def_property("miny", &box2d<double>::miny, &box2d<double>::set_miny,
                      "Y coordinate for the lower left corner")
        .def_property("maxx", &box2d<double>::maxx, &box2d<double>::set_maxx,
                      "X coordinate for the upper right corner")
        .def_property("maxy", &box2d<double>::maxy, &box2d<double>::set_maxy,
                      "Y coordinate for the upper right corner")
        .def("center", &box2d<double>::center,
             "Returns the coordinates of the center of the bounding box.\n"
             "\n"
             "Example:\n"
             ">>> e = Box2d(0, 0, 100, 100)\n"
             ">>> e.center()\n"
             "Coord(50, 50)\n")
        .def("center", re_center_p1,
             "Moves the envelope so that the given coordinates become its new center.\n"
             "The width and the height are preserved.\n"
             "\n "
             "Example:\n"
             ">>> e = Box2d(0, 0, 100, 100)\n"
             ">>> e.center(60, 60)\n"
             ">>> e.center()\n"
             "Coord(60.0,60.0)\n"
             ">>> (e.width(), e.height())\n"
             "(100.0, 100.0)\n"
             ">>> e\n"
             "Box2d(10.0, 10.0, 110.0, 110.0)\n",
             py::arg("x"), py::arg("y"))
        .def("center", re_center_p2,
             "Moves the envelope so that the given coordinates become its new center.\n"
             "The width and the height are preserved.\n"
             "\n "
             "Example:\n"
             ">>> e = Box2d(0, 0, 100, 100)\n"
             ">>> e.center(Coord60, 60)\n"
             ">>> e.center()\n"
             "Coord(60.0,60.0)\n"
             ">>> (e.width(), e.height())\n"
             "(100.0, 100.0)\n"
             ">>> e\n"
             "Box2d(10.0, 10.0, 110.0, 110.0)\n",
             py::arg("Coord"))
        .def("clip", clip,
             "Clip the envelope based on the bounds of another envelope.\n"
             "\n "
             "Example:\n"
             ">>> e = Box2d(0, 0, 100, 100)\n"
             ">>> c = Box2d(-50, -50, 50, 50)\n"
             ">>> e.clip(c)\n"
             ">>> e\n"
             "Box2d(0.0,0.0,50.0,50.0\n",
             py::arg("other"))
        .def("pad", pad,
             "Pad the envelope based on a padding value.\n"
             "\n "
             "Example:\n"
             ">>> e = Box2d(0, 0, 100, 100)\n"
             ">>> e.pad(10)\n"
             ">>> e\n"
             "Box2d(-10.0,-10.0,110.0,110.0\n",
             py::arg("padding"))
        .def("width", width_p1,
             "Sets the width to new_width of the envelope preserving its center.\n"
             "\n "
             "Example:\n"
             ">>> e = Box2d(0, 0, 100, 100)\n"
             ">>> e.width(120)\n"
             ">>> e.center()\n"
             "Coord(50.0,50.0)\n"
             ">>> e\n"
             "Box2d(-10.0, 0.0, 110.0, 100.0)\n",
             py::arg("new_width"))
        .def("width", width_p2,
             "Returns the width of this envelope.\n")
        .def("height", height_p1,
             "Sets the height to new_height of the envelope preserving its center.\n"
             "\n "
             "Example:\n"
             ">>> e = Box2d(0, 0, 100, 100)\n"
             ">>> e.height(120)\n"
             ">>> e.center()\n"
             "Coord(50.0,50.0)\n"
             ">>> e\n"
             "Box2d(0.0, -10.0, 100.0, 110.0)\n",
             py::arg("new_height"))
        .def("height", height_p2,
             "Returns the height of this envelope.\n")
        .def("expand_to_include",expand_to_include_p1,
             "Expands this envelope to include the point given by x and y.\n"
             "\n"
             "Example:\n",
             ">>> e = Box2d(0, 0, 100, 100)\n"
             ">>> e.expand_to_include(110, 110)\n"
             ">>> e\n"
             "Box2d(0.0, 00.0, 110.0, 110.0)\n",
             py::arg("x"),py::arg("y"))

        .def("expand_to_include",expand_to_include_p2,
             "Equivalent to expand_to_include(p.x, p.y)\n",
             py::arg("p"))

        .def("expand_to_include",expand_to_include_p3,
             "Equivalent to:\n"
             "  expand_to_include(other.minx, other.miny)\n"
             "  expand_to_include(other.maxx, other.maxy)\n",
             py::arg("other"))
        .def("contains",contains_p1,
             "Returns True iff this envelope contains the point\n"
             "given by x and y.\n",
             py::arg("x"),py::arg("y"))
        .def("contains",contains_p2,
             "Equivalent to contains(p.x, p.y)\n",
             py::arg("p"))
        .def("contains",contains_p3,
             "Equivalent to:\n"
             "  contains(other.minx, other.miny) and contains(other.maxx, other.maxy)\n",
             py::arg("other"))
        .def("intersects",intersects_p1,
             "Returns True iff this envelope intersects the point\n"
             "given by x and y.\n"
             "\n"
             "Note: For points, intersection is equivalent\n"
             "to containment, i.e. the following holds:\n"
             "   e.contains(x, y) == e.intersects(x, y)\n",
             py::arg("x"),py::arg("y"))
        .def("intersects",intersects_p2,
             "Equivalent to contains(p.x, p.y)\n",
             py::arg("p"))
        .def("intersects",intersects_p3,
             "Returns True iff this envelope intersects the other envelope,\n"
             "This relationship is symmetric."
             "\n"
             "Example:\n"
             ">>> e1 = Box2d(0, 0, 100, 100)\n"
             ">>> e2 = Box2d(50, 50, 150, 150)\n"
             ">>> e1.intersects(e2)\n"
             "True\n"
             ">>> e1.contains(e2)\n"
             "False\n",
             py::arg("other"))
        .def("intersect",intersect,
             "Returns the overlap of this envelope and the other envelope\n"
             "as a new envelope.\n"
             "\n"
             "Example:\n"
             ">>> e1 = Box2d(0, 0, 100, 100)\n"
             ">>> e2 = Box2d(50, 50, 150, 150)\n"
             ">>> e1.intersect(e2)\n"
             "Box2d(50.0, 50.0, 100.0, 100.0)\n",
             py::arg("other"))
        .def(py::self == py::self) // __eq__
        .def(py::self != py::self) // __neq__
        .def(py::self + py::self)  // __add__
        .def(py::self * float())   // __mult__
        .def(float() * py::self)
        .def(py::self / float())   // __div__
        .def("__getitem__",&box2d<double>::operator[])
        .def("valid",&box2d<double>::valid)
        .def(py::pickle(
                 [](box2d<double> const& box) {
                     return py::make_tuple(box.minx(), box.miny(), box.maxx(), box.maxy());
                 },
                 [](py::tuple t) {
                     if (t.size() != 4)
                         throw std::runtime_error("Invalid state");
                     box2d<double> box{t[0].cast<double>(),
                                       t[1].cast<double>(),
                                       t[2].cast<double>(),
                                       t[3].cast<double>()};
                     return box;
                 }))
        .def("__repr__",
             [](box2d<double> const& box) {
                 return box.to_string();
             })
        ;

}
