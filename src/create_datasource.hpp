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

#ifndef MAPNIK_CREATE_DATASOURCE_HPP
#define MAPNIK_CREATE_DATASOURCE_HPP

// mapnik
#include <mapnik/config.hpp>
#include <mapnik/datasource.hpp>
//pybind11
#include <pybind11/pybind11.h>
#include <pybind11/operators.h>
#include <pybind11/stl.h>

namespace py = pybind11;

inline std::shared_ptr<mapnik::datasource> create_datasource(py::kwargs const& kwargs)
{
    mapnik::parameters params;
    for (auto param : kwargs)
    {
        std::string key = std::string(py::str(param.first));
        py::handle handle = param.second;
        if (py::isinstance<py::str>(handle))
        {
            params[key] = handle.cast<std::string>();
        }
        else if (py::isinstance<py::bool_>(handle))
        {
            params[key] = handle.cast<mapnik::value_bool>();
        }
        else if (py::isinstance<py::float_>(handle))
        {
            params[key] = handle.cast<mapnik::value_double>();
        }
        else if (py::isinstance<py::int_>(handle))
        {
            params[key] = handle.cast<mapnik::value_integer>();
        }
        else
        {
            params[key] = py::str(handle).cast<std::string>();
        }
    }
    return mapnik::datasource_cache::instance().create(params);
}


#endif //MAPNIK_CREATE_DATASOURCE_HPP
