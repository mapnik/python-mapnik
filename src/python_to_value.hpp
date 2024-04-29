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
#ifndef MAPNIK_PYTHON_BINDING_PYTHON_TO_VALUE
#define MAPNIK_PYTHON_BINDING_PYTHON_TO_VALUE

// mapnik
#include <mapnik/value.hpp>
#include <mapnik/unicode.hpp>
#include <mapnik/attribute.hpp>

//pybind11
#include <pybind11/pybind11.h>
//#include <pybind11/stl.h>

namespace py = pybind11;

namespace mapnik {

    static mapnik::attributes dict2attr(py::dict const& d)
    {
        mapnik::attributes vars;
        mapnik::transcoder tr_("utf8");
        for (auto item : d)
        {
            std::string key = std::string(py::str(item.first));
            py::handle handle = item.second;
            if (py::isinstance<py::str>(handle))
            {
                vars[key] = tr_.transcode(handle.cast<std::string>().c_str());
            }
            else if (py::isinstance<py::bool_>(handle))
            {
                vars[key] = handle.cast<bool>();
            }
            else if (py::isinstance<py::float_>(handle))
            {
                vars[key] = handle.cast<double>();
            }
            else if (py::isinstance<py::int_>(handle))
            {
                  vars[key] = handle.cast<long long>();
            }
            else
            {
                vars[key] = tr_.transcode(py::str(handle).cast<std::string>().c_str());
            }
        }
        return vars;
    }
}

#endif // MAPNIK_PYTHON_BINDING_PYTHON_TO_VALUE
