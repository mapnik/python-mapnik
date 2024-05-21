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
#include <mapnik/debug.hpp>
#include <mapnik/util/singleton.hpp>

//pybind11
#include <pybind11/pybind11.h>
#include <pybind11/stl.h>

namespace py = pybind11;

void export_logger(py::module const& m)
{
    using mapnik::logger;
    using mapnik::singleton;
    using mapnik::CreateStatic;


    py::enum_<mapnik::logger::severity_type>(m, "severity_type")
        .value("Debug", logger::debug)
        .value("Warn", logger::warn)
        .value("Error", logger::error)
        .value("None", logger::none)
        ;

    py::class_<logger, std::unique_ptr<logger, py::nodelete>>(m, "logger")
        .def_static("get_severity", &logger::get_severity)
        .def_static("set_severity", &logger::set_severity)
        .def_static("get_object_severity", &logger::get_object_severity)
        .def_static("set_object_severity", &logger::set_object_severity)
        .def_static("clear_object_severity", &logger::clear_object_severity)
        .def_static("get_format", &logger::get_format)
        .def_static("set_format", &logger::set_format)
        .def_static("str", &logger::str)
        .def_static("use_file", &logger::use_file)
        .def_static("use_console", &logger::use_console)
        ;
}
