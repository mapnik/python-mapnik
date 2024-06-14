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
#include <mapnik/image_compositing.hpp>
//pybind11
#include <pybind11/pybind11.h>

namespace py = pybind11;

void export_composite_modes(py::module const& m)
{
    // NOTE: must match list in include/mapnik/image_compositing.hpp
    py::enum_<mapnik::composite_mode_e>(m, "CompositeOp")
        .value("clear", mapnik::clear)
        .value("src", mapnik::src)
        .value("dst", mapnik::dst)
        .value("src_over", mapnik::src_over)
        .value("dst_over", mapnik::dst_over)
        .value("src_in", mapnik::src_in)
        .value("dst_in", mapnik::dst_in)
        .value("src_out", mapnik::src_out)
        .value("dst_out", mapnik::dst_out)
        .value("src_atop", mapnik::src_atop)
        .value("dst_atop", mapnik::dst_atop)
        .value("xor", mapnik::_xor)
        .value("plus", mapnik::plus)
        .value("minus", mapnik::minus)
        .value("multiply", mapnik::multiply)
        .value("screen", mapnik::screen)
        .value("overlay", mapnik::overlay)
        .value("darken", mapnik::darken)
        .value("lighten", mapnik::lighten)
        .value("color_dodge", mapnik::color_dodge)
        .value("color_burn", mapnik::color_burn)
        .value("hard_light", mapnik::hard_light)
        .value("soft_light", mapnik::soft_light)
        .value("difference", mapnik::difference)
        .value("exclusion", mapnik::exclusion)
        .value("contrast", mapnik::contrast)
        .value("invert", mapnik::invert)
        .value("grain_merge", mapnik::grain_merge)
        .value("grain_extract", mapnik::grain_extract)
        .value("hue", mapnik::hue)
        .value("saturation", mapnik::saturation)
        .value("color", mapnik::_color)
        .value("value", mapnik::_value)
        .value("linear_dodge", mapnik::linear_dodge)
        .value("linear_burn", mapnik::linear_burn)
        .value("divide", mapnik::divide)
        ;
}
