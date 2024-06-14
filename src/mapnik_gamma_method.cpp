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
#include <mapnik/symbolizer_enumerations.hpp>
//pybind11
#include <pybind11/pybind11.h>

namespace py = pybind11;

void export_gamma_method(py::module const& m)
{
    py::enum_<mapnik::gamma_method_enum>(m, "gamma_method")
        .value("POWER", mapnik::gamma_method_enum::GAMMA_POWER)
        .value("LINEAR",mapnik::gamma_method_enum::GAMMA_LINEAR)
        .value("NONE", mapnik::gamma_method_enum::GAMMA_NONE)
        .value("THRESHOLD", mapnik::gamma_method_enum::GAMMA_THRESHOLD)
        .value("MULTIPLY", mapnik::gamma_method_enum::GAMMA_MULTIPLY)
        ;

}
