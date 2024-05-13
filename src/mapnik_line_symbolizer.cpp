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
#include <pybind11/operators.h>
#include <pybind11/stl.h>
#include <pybind11/stl_bind.h>

#define PYBIND11_DETAILED_ERROR_MESSAGES

namespace py = pybind11;

namespace {

std::string get_stroke_dasharray(mapnik::symbolizer_base & sym)
{
    auto dash = mapnik::get<mapnik::dash_array>(sym, mapnik::keys::stroke_dasharray);

    std::ostringstream os;
    for (std::size_t i = 0; i < dash.size(); ++i)
    {
        os << dash[i].first << "," << dash[i].second;
        if (i + 1 < dash.size())
            os << ",";
    }
    return os.str();
}

void set_stroke_dasharray(mapnik::symbolizer_base & sym, std::string str)
{
    mapnik::dash_array dash;
    if (mapnik::util::parse_dasharray(str, dash))
    {
        mapnik::put(sym, mapnik::keys::stroke_dasharray, dash);
    }
    else
    {
        throw std::runtime_error("Can't parse dasharray");
    }
}

}


void export_line_symbolizer(py::module const& m)
{
    using namespace python_mapnik;
    using mapnik::line_symbolizer;

    py::enum_<mapnik::line_rasterizer_enum>(m, "line_rasterizer")
        .value("FULL",mapnik::line_rasterizer_enum::RASTERIZER_FULL)
        .value("FAST",mapnik::line_rasterizer_enum::RASTERIZER_FAST)
        ;

    py::enum_<mapnik::line_cap_enum>(m, "stroke_linecap")
        .value("BUTT_CAP",mapnik::line_cap_enum::BUTT_CAP)
        .value("SQUARE_CAP",mapnik::line_cap_enum::SQUARE_CAP)
        .value("ROUND_CAP",mapnik::line_cap_enum::ROUND_CAP)
        ;

    py::enum_<mapnik::line_join_enum>(m, "stroke_linejoin")
        .value("MITER_JOIN",mapnik::line_join_enum::MITER_JOIN)
        .value("MITER_REVERT_JOIN",mapnik::line_join_enum::MITER_REVERT_JOIN)
        .value("ROUND_JOIN",mapnik::line_join_enum::ROUND_JOIN)
        .value("BEVEL_JOIN",mapnik::line_join_enum::BEVEL_JOIN)
        ;

    py::class_<line_symbolizer, symbolizer_base>(m, "LineSymbolizer")
        .def(py::init<>(), "Default LineSymbolizer - 1px solid black")
        .def("__hash__",hash_impl_2<line_symbolizer>)
        .def_property("stroke",
                      &get_property<line_symbolizer, mapnik::keys::stroke>,
                      &set_color_property<line_symbolizer, mapnik::keys::stroke>,
                      "Stroke color")
        .def_property("stroke_width",
                      &get_property<line_symbolizer,mapnik::keys::stroke_width>,
                      &set_double_property<line_symbolizer, mapnik::keys::stroke_width>,
                      "Stroke width")
        .def_property("stroke_opacity",
                      &get_property<line_symbolizer,mapnik::keys::stroke_opacity>,
                      &set_double_property<line_symbolizer, mapnik::keys::stroke_opacity>,
                      "Stroke opacity")
        .def_property("stroke_gamma",
                      &get_property<line_symbolizer,mapnik::keys::stroke_gamma>,
                      &set_double_property<line_symbolizer,mapnik::keys::stroke_gamma>,
                      "Stroke gamma")
        .def_property("stroke_gamma_method",
                      &get<mapnik::gamma_method_enum, mapnik::keys::stroke_gamma_method>,
                      &set_enum_property<line_symbolizer, mapnik::gamma_method_enum, mapnik::keys::stroke_gamma_method>,
                      "Stroke gamma method")
        .def_property("line_rasterizer",
                      &get<mapnik::line_rasterizer_enum, mapnik::keys::line_rasterizer>,
                      &set_enum_property<line_symbolizer, mapnik::line_rasterizer_enum, mapnik::keys::line_rasterizer>,
                      "Line rasterizer")
        .def_property("stroke_linecap",
                      &get<mapnik::line_cap_enum, mapnik::keys::stroke_linecap>,
                      &set_enum_property<line_symbolizer, mapnik::line_cap_enum, mapnik::keys::stroke_linecap>,
                      "Stroke linecap")
        .def_property("stroke_linejoin",
                      &get<mapnik::line_join_enum, mapnik::keys::stroke_linejoin>,
                      &set_enum_property<line_symbolizer, mapnik::line_join_enum, mapnik::keys::stroke_linejoin>,
                      "Stroke linejoin")
        .def_property("stroke_dasharray",
                      &get_stroke_dasharray,
                      &set_stroke_dasharray,
                      "Stroke dasharray")
        .def_property("stroke_dashoffset",
                      &get_property<line_symbolizer, mapnik::keys::stroke_dashoffset>,
                      &set_double_property<line_symbolizer,mapnik::keys::stroke_dashoffset>,
                      "Stroke dashoffset")
        .def_property("stroke_miterlimit",
                      &get_property<line_symbolizer, mapnik::keys::stroke_miterlimit>,
                      &set_double_property<line_symbolizer, mapnik::keys::stroke_miterlimit>,
                      "Stroke miterlimit")

        ;
}
