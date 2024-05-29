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
#include <mapnik/symbolizer.hpp>
#include <mapnik/symbolizer_hash.hpp>
#include <mapnik/symbolizer_utils.hpp>
#include <mapnik/symbolizer_keys.hpp>
#include "mapnik_symbolizer.hpp"
//pybind11
#include <pybind11/pybind11.h>

namespace py = pybind11;

void export_polygon_pattern_symbolizer(py::module const& m)
{
    using namespace python_mapnik;
    using mapnik::polygon_pattern_symbolizer;

    py::class_<polygon_pattern_symbolizer, symbolizer_base>(m, "PolygonPatternSymbolizer")
        .def(py::init<>(), "Default ctor")
        .def("__hash__", hash_impl_2<polygon_pattern_symbolizer>)
         .def_property("file",
                       &get_property<polygon_pattern_symbolizer, mapnik::keys::file>,
                       &set_path_property<polygon_pattern_symbolizer, mapnik::keys::file>,
                       "File path or mapnik.PathExpression")
        ;

}
