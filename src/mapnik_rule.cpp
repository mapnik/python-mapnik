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

#include <mapnik/config.hpp>
// mapnik
#include <mapnik/rule.hpp>
#include <mapnik/expression.hpp>
#include <mapnik/expression_string.hpp>
//pybind11
#include <pybind11/pybind11.h>
#include <pybind11/operators.h>
#include <pybind11/stl.h>
#include <pybind11/stl_bind.h>

namespace py = pybind11;

using mapnik::rule;
using mapnik::expr_node;
using mapnik::expression_ptr;
using mapnik::point_symbolizer;
using mapnik::line_symbolizer;
using mapnik::line_pattern_symbolizer;
using mapnik::polygon_symbolizer;
using mapnik::polygon_pattern_symbolizer;
using mapnik::raster_symbolizer;
using mapnik::shield_symbolizer;
using mapnik::text_symbolizer;
using mapnik::building_symbolizer;
using mapnik::markers_symbolizer;
using mapnik::group_symbolizer;
using mapnik::symbolizer;
using mapnik::to_expression_string;

PYBIND11_MAKE_OPAQUE(std::vector<symbolizer>);

void export_rule(py::module const& m)
{
    py::bind_vector<std::vector<symbolizer>>(m, "Symbolizers", py::module_local());

    py::class_<rule>(m, "Rule")
        .def(py::init<>(), "default constructor")
        .def(py::init<std::string, double, double>(),
             py::arg("name"),
             py::arg("min_scale_denominator")=0,
             py::arg("max_scale_denominator")=std::numeric_limits<double>::infinity())

        .def_property("name",
                      &rule::get_name,
                      &rule::set_name)

        .def_property("filter",
                      &rule::get_filter,
                      &rule::set_filter)

        .def_property("min_scale", &rule::get_min_scale, &rule::set_min_scale)
        .def_property("max_scale", &rule::get_max_scale, &rule::set_max_scale)
        .def("set_else", &rule::set_else)
        .def("has_else", &rule::has_else_filter)
        .def("set_also", &rule::set_also)
        .def("has_also", &rule::has_also_filter)
        .def("active", &rule::active)
        .def_property_readonly("symbolizers", &rule::get_symbolizers)
        ;
}
