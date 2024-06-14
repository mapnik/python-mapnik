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

void export_point_symbolizer(py::module const& m)
{
    using namespace python_mapnik;
    using mapnik::point_symbolizer;

    py::enum_<mapnik::point_placement_enum>(m, "point_placement")
        .value("CENTROID",mapnik::point_placement_enum::CENTROID_POINT_PLACEMENT)
        .value("INTERIOR",mapnik::point_placement_enum::INTERIOR_POINT_PLACEMENT)
        ;

    py::class_<point_symbolizer, symbolizer_base>(m, "PointSymbolizer")
        .def(py::init<>(), "Default Point Symbolizer - 4x4 black square")
        .def("__hash__",hash_impl_2<point_symbolizer>)

        .def_property("file",
                      &get_property<point_symbolizer, mapnik::keys::file>,
                      &set_path_property<point_symbolizer, mapnik::keys::file>,
                      "File path or mapnik.PathExpression")

        .def_property("opacity",
                      &get_property<point_symbolizer, mapnik::keys::opacity>,
                      &set_double_property<point_symbolizer, mapnik::keys::opacity>,
                      "Opacity - [0..1]")

        .def_property("allow_overlap",
                      &get_property<point_symbolizer, mapnik::keys::allow_overlap>,
                      &set_boolean_property<point_symbolizer, mapnik::keys::allow_overlap>,
                      "Allow overlapping - True/False")

        .def_property("ignore_placement",
                      &get_property<point_symbolizer, mapnik::keys::ignore_placement>,
                      &set_boolean_property<point_symbolizer, mapnik::keys::ignore_placement>,
                      "Ignore placement - True/False")

        .def_property("placement",
                      &get_property<point_symbolizer, mapnik::keys::point_placement_type, mapnik::point_placement_enum>,
                      &set_enum_property<point_symbolizer, mapnik::point_placement_enum, mapnik::keys::point_placement_type>,
                      "Point placement type CENTROID/INTERIOR")

        ;
}
