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
#include <mapnik/font_engine_freetype.hpp>
//pybind11
#include <pybind11/pybind11.h>

namespace py = pybind11;

void export_font_engine(py::module const& m)
{
    using mapnik::freetype_engine;

    py::class_<freetype_engine>(m, "FontEngine")
        .def_static("register_font", &freetype_engine::register_font)
        .def_static("register_fonts", &freetype_engine::register_fonts)
        .def_static("face_names", &freetype_engine::face_names)
        ;
}
