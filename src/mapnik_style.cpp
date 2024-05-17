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
#include <mapnik/value/error.hpp>
#include <mapnik/rule.hpp>
#include <mapnik/feature_type_style.hpp>
#include <mapnik/image_filter_types.hpp> // generate_image_filters
//pybind11
#include <pybind11/pybind11.h>
#include <pybind11/stl.h>
#include <pybind11/stl_bind.h>


namespace py = pybind11;

using mapnik::feature_type_style;
using mapnik::rules;
using mapnik::rule;

PYBIND11_MAKE_OPAQUE(rules);

std::string get_image_filters(feature_type_style & style)
{
    std::string filters_str;
    std::back_insert_iterator<std::string> sink(filters_str);
    generate_image_filters(sink, style.image_filters());
    return filters_str;
}

void set_image_filters(feature_type_style & style, std::string const& filters)
{
    std::vector<mapnik::filter::filter_type> new_filters;
    bool result = parse_image_filters(filters, new_filters);
    if (!result)
    {
        throw mapnik::value_error("failed to parse image-filters: '" + filters + "'");
    }
    style.image_filters() = std::move(new_filters);
}

void export_style(py::module const& m)
{
    py::enum_<mapnik::filter_mode_enum>(m, "filter_mode")
        .value("ALL",mapnik::filter_mode_enum::FILTER_ALL)
        .value("FIRST",mapnik::filter_mode_enum::FILTER_FIRST)
        ;

    py::bind_vector<rules>(m, "Rules", py::module_local());

    py::class_<feature_type_style>(m, "Style")
        .def(py::init<>(), "default style constructor")
        .def_property_readonly("rules",
                               &feature_type_style::get_rules,
                               "Rules assigned to this style.\n")
        .def_property("filter_mode",
                      &feature_type_style::get_filter_mode,
                      &feature_type_style::set_filter_mode,
                      "Set/get the filter mode of the style")
        .def_property("opacity",
                      &feature_type_style::get_opacity,
                      &feature_type_style::set_opacity,
                      "Set/get the opacity of the style")
        .def_property("comp_op",
                      &feature_type_style::comp_op,
                      &feature_type_style::set_comp_op,
                      "Set/get the comp-op (composite operation) of the style")
        .def_property("image_filters_inflate",
                      &feature_type_style::image_filters_inflate,
                      &feature_type_style::image_filters_inflate,
                      "Set/get the image_filters_inflate property of the style")
        .def_property("image_filters",
                      get_image_filters,
                      set_image_filters,
                      "Set/get the comp-op (composite operation) of the style")
        ;

}
