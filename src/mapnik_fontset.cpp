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
#include <mapnik/font_set.hpp>
//pybind11
#include <pybind11/pybind11.h>

namespace py = pybind11;

using mapnik::font_set;

void export_fontset (py::module const& m)
{
    py::class_<font_set>(m, "FontSet")
        .def(py::init<std::string const&>(), "default fontset constructor")
        .def_property("name",
                       &font_set::get_name,
                       &font_set::set_name,
                      "Get/Set the name of the FontSet.\n"
            )
        .def("add_face_name", &font_set::add_face_name,
             "Add a face-name to the fontset.\n"
             "\n"
             "Example:\n"
             ">>> fs = Fontset('book-fonts')\n"
             ">>> fs.add_face_name('DejaVu Sans Book')\n",
             py::arg("name"))
        .def_property_readonly("names",
                               &font_set::get_face_names,
                               "List of face names belonging to a FontSet.\n")
        ;
}
