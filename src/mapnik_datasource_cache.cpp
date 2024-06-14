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
#include <mapnik/value/types.hpp>
#include <mapnik/params.hpp>
#include <mapnik/datasource.hpp>
#include <mapnik/datasource_cache.hpp>
#include "create_datasource.hpp"
//pybind11
#include <pybind11/pybind11.h>
#include <pybind11/stl.h>

namespace py = pybind11;

namespace  {

bool register_datasources(std::string const& plugins_dir, bool recursive = false)
{
    return mapnik::datasource_cache::instance().register_datasources(plugins_dir, recursive);
}

std::string plugin_directories()
{
    return mapnik::datasource_cache::instance().plugin_directories();
}

std::vector<std::string> plugin_names()
{
    return  mapnik::datasource_cache::instance().plugin_names();
}

} // namespace


void export_datasource_cache(py::module const& m)
{
    py::class_<mapnik::datasource_cache, std::unique_ptr<mapnik::datasource_cache, py::nodelete>>(m, "DatasourceCache")
        .def_static("create",&create_datasource)
        .def_static("register_datasources",&register_datasources)
        .def_static("plugin_names",&plugin_names)
        .def_static("plugin_directories",&plugin_directories)
        ;
}
