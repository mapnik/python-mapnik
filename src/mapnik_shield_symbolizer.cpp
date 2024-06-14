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

void export_shield_symbolizer(py::module const& m)
{
    using namespace python_mapnik;
    using mapnik::shield_symbolizer;

    py::class_<shield_symbolizer, symbolizer_base>(m, "ShieldSymbolizer")
        .def(py::init<>(), "Default ctor")
        .def("__hash__", hash_impl_2<shield_symbolizer>)
        .def_property("file",
                      &get_property<shield_symbolizer, mapnik::keys::file>,
                      &set_path_property<shield_symbolizer, mapnik::keys::file>,
                      "Shield image file path or mapnik.PathExpression")
        .def_property("shield_dx",
                      &get_property<shield_symbolizer, mapnik::keys::shield_dx>,
                      &set_double_property<shield_symbolizer, mapnik::keys::shield_dx>,
                      "shield_dx displacement")
        .def_property("shield_dy",
                      &get_property<shield_symbolizer, mapnik::keys::shield_dy>,
                      &set_double_property<shield_symbolizer, mapnik::keys::shield_dy>,
                      "shield_dy displacement")
        .def_property("image_transform",
                      &get_transform<mapnik::keys::image_transform>,
                      &set_transform<mapnik::keys::image_transform>,
                      "Shield image transform")
        .def_property("unlock_image",
                      &get_property<shield_symbolizer, mapnik::keys::unlock_image>,
                      &set_boolean_property<shield_symbolizer, mapnik::keys::unlock_image>,
                      "Unlock shield image")
        .def_property("offset",
                      &get_property<shield_symbolizer, mapnik::keys::offset>,
                      &set_double_property<shield_symbolizer, mapnik::keys::offset>,
                      "Shield offset")
        ;

}
