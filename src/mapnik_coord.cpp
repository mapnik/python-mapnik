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
#include <mapnik/coord.hpp>
//pybind11
#include <pybind11/pybind11.h>
#include <pybind11/operators.h>

namespace py = pybind11;
using mapnik::coord;

void export_coord(py::module const& m)
{
    py::class_<coord<double,2> >(m, "Coord")
        .def(py::init<double, double>(),
             // class docstring is in mapnik/__init__.py, class _Coord
             "Constructs a new object with the given coordinates.\n",
             py::arg("x"), py::arg("y"))
        .def_readwrite("x", &coord<double,2>::x,
                       "Gets or sets the x/lon coordinate of the point.\n")
        .def_readwrite("y", &coord<double,2>::y,
                       "Gets or sets the y/lat coordinate of the point.\n")
        .def(py::self == py::self) // __eq__
        .def(py::self + py::self)  //__add__
        .def(py::self + float())
        .def(float() + py::self)
        .def(py::self - py::self)  //__sub__
        .def(py::self - float())
        .def(py::self * float())   //__mult__
        .def(float() * py::self)
        .def(py::self / float())   // __div__
        .def(py::pickle(
                 [](coord<double,2> & c) {
                     return py::make_tuple(c.x, c.y);
                 },
                 [](py::tuple t) {
                     if (t.size() != 2)
                         throw std::runtime_error("Invalid state");
                     coord<double,2> c{t[0].cast<double>(),t[1].cast<double>()};
                     return c;
                 }))
        ;
}
