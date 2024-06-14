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
#include <mapnik/symbolizer_enumerations.hpp>
#include <mapnik/text/placements/dummy.hpp>
#include "mapnik_symbolizer.hpp"

//pybind11
#include <pybind11/pybind11.h>
#include <pybind11/operators.h>
#include <pybind11/stl.h>
#include <pybind11/stl_bind.h>

namespace py = pybind11;

namespace {

//text symbolizer
mapnik::text_placements_ptr get_placement_finder(mapnik::text_symbolizer const& sym)
{
    return mapnik::get<mapnik::text_placements_ptr>(sym, mapnik::keys::text_placements_);
}

void set_placement_finder(mapnik::text_symbolizer & sym, std::shared_ptr<mapnik::text_placements_dummy> const& finder)
{
    mapnik::put<mapnik::text_placements_ptr>(sym, mapnik::keys::text_placements_, finder);
}

}

void export_text_symbolizer(py::module const& m)
{
    using namespace python_mapnik;
    using mapnik::text_symbolizer;

//     using namespace boost::python;
//     mapnik::enumeration_<mapnik::label_placement_e>("label_placement")
//         .value("LINE_PLACEMENT", mapnik::label_placement_enum::LINE_PLACEMENT)
//         .value("POINT_PLACEMENT", mapnik::label_placement_enum::POINT_PLACEMENT)
//         .value("VERTEX_PLACEMENT", mapnik::label_placement_enum::VERTEX_PLACEMENT)
//         .value("INTERIOR_PLACEMENT", mapnik::label_placement_enum::INTERIOR_PLACEMENT);

//     mapnik::enumeration_<mapnik::vertical_alignment_e>("vertical_alignment")
//         .value("TOP", mapnik::vertical_alignment_enum::V_TOP)
//         .value("MIDDLE", mapnik::vertical_alignment_enum::V_MIDDLE)
//         .value("BOTTOM", mapnik::vertical_alignment_enum::V_BOTTOM)
//         .value("AUTO", mapnik::vertical_alignment_enum::V_AUTO);

//     mapnik::enumeration_<mapnik::horizontal_alignment_e>("horizontal_alignment")
//         .value("LEFT", mapnik::horizontal_alignment_enum::H_LEFT)
//         .value("MIDDLE", mapnik::horizontal_alignment_enum::H_MIDDLE)
//         .value("RIGHT", mapnik::horizontal_alignment_enum::H_RIGHT)
//         .value("AUTO", mapnik::horizontal_alignment_enum::H_AUTO);

//     mapnik::enumeration_<mapnik::justify_alignment_e>("justify_alignment")
//         .value("LEFT", mapnik::justify_alignment_enum::J_LEFT)
//         .value("MIDDLE", mapnik::justify_alignment_enum::J_MIDDLE)
//         .value("RIGHT", mapnik::justify_alignment_enum::J_RIGHT)
//         .value("AUTO", mapnik::justify_alignment_enum::J_AUTO);

//     mapnik::enumeration_<mapnik::text_transform_e>("text_transform")
//         .value("NONE", mapnik::text_transform_enum::NONE)
//         .value("UPPERCASE", mapnik::text_transform_enum::UPPERCASE)
//         .value("LOWERCASE", mapnik::text_transform_enum::LOWERCASE)
//         .value("CAPITALIZE", mapnik::text_transform_enum::CAPITALIZE);

//     mapnik::enumeration_<mapnik::halo_rasterizer_e>("halo_rasterizer")
//         .value("FULL", mapnik::halo_rasterizer_enum::HALO_RASTERIZER_FULL)
//         .value("FAST", mapnik::halo_rasterizer_enum::HALO_RASTERIZER_FAST);

    py::class_<text_symbolizer, symbolizer_base>(m, "TextSymbolizer")
        .def(py::init<>(), "Default ctor")
        .def("__hash__",hash_impl_2<text_symbolizer>)
        .def_property("placement_finder", &get_placement_finder, &set_placement_finder, "Placement finder")
        ;

}
