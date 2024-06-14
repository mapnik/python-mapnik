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

//mapnik
#include <mapnik/config.hpp>
#include <mapnik/color.hpp>
//pybind11
#include <pybind11/pybind11.h>
#include <pybind11/operators.h>

namespace py = pybind11;
using mapnik::color;

void export_color (py::module const& m)
{
    py::class_<color>(m, "Color")
        .def(py::init<std::uint8_t,std::uint8_t,std::uint8_t,std::uint8_t>(),
             "Creates a new color from its RGB components\n"
             "and an alpha value.\n"
             "All values between 0 and 255.\n",
             py::arg("r"), py::arg("g"), py::arg("b"), py::arg("a"))
        .def(py::init<std::uint8_t,std::uint8_t,std::uint8_t,std::uint8_t,bool>(),
             "Creates a new color from its RGB components\n"
             "and an alpha value.\n"
             "All values between 0 and 255.\n",
             py::arg("r"), py::arg("g"), py::arg("b"), py::arg("a"), py::arg("premultiplied"))
        .def(py::init<std::uint8_t,std::uint8_t,std::uint8_t>(),
             "Creates a new color from its RGB components.\n"
             "All values between 0 and 255.\n",
             py::arg("r"), py::arg("g"), py::arg("b"))
        .def(py::init<std::uint32_t>(),
             "Creates a new color from an unsigned integer.\n"
             "All values between 0 and 2^32-1\n",
             py::arg("val"))
        .def(py::init<uint32_t, bool>(),
             "Creates a new color from an unsigned integer.\n"
             "All values between 0 and 2^32-1\n",
             py::arg("val"), py::arg("premultiplied"))

        .def(py::init<std::string>(),
             "Creates a new color from its CSS string representation.\n"
             "The string may be a CSS color name (e.g. 'blue')\n"
             "or a hex color string (e.g. '#0000ff').\n",
             py::arg("color_string"))

        .def(py::init<std::string, bool>(),
             "Creates a new color from its CSS string representation.\n"
             "The string may be a CSS color name (e.g. 'blue')\n"
             "or a hex color string (e.g. '#0000ff').\n",
             py::arg("color_string"), py::arg("premultiplied"))

        .def_property("r",
                      &color::red,
                      &color::set_red,
                      "Gets or sets the red component.\n"
                      "The value is between 0 and 255.\n")
        .def_property("g",
                      &color::green,
                      &color::set_green,
                      "Gets or sets the green component.\n"
                      "The value is between 0 and 255.\n")
        .def_property("b",
                      &color::blue,
                      &color::set_blue,
                      "Gets or sets the blue component.\n"
                      "The value is between 0 and 255.\n")
        .def_property("a",
                      &color::alpha,
                      &color::set_alpha,
                      "Gets or sets the alpha component.\n"
                      "The value is between 0 and 255.\n")
        .def(py::self == py::self)
        .def(py::self != py::self)
        .def("__str__",&color::to_string)
        .def("__repr__",&color::to_string)
        .def("set_premultiplied",&color::set_premultiplied)
        .def("get_premultiplied",&color::get_premultiplied)
        .def("premultiply",&color::premultiply)
        .def("demultiply",&color::demultiply)
        .def("packed",&color::rgba)
        .def("to_hex_string",&color::to_hex_string,
             "Returns the hexadecimal representation of this color.\n"
             "\n"
             "Example:\n"
             ">>> c = Color('blue')\n"
             ">>> c.to_hex_string()\n"
             "'#0000ff'\n")
        .def(py::pickle(
                 [](color & c) {
                     return py::make_tuple(c.red(), c.green(), c.blue(), c.alpha());
                 },
                 [](py::tuple t) {
                     if (t.size() != 4)
                         throw std::runtime_error("Invalid state");
                     color c{t[0].cast<std::uint8_t>(),
                             t[1].cast<std::uint8_t>(),
                             t[2].cast<std::uint8_t>(),
                             t[3].cast<std::uint8_t>()};
                     return c;
                 }))
        ;
}
