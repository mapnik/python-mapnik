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

#if defined(GRID_RENDERER)
// mapnik
#include <mapnik/config.hpp>
#include <mapnik/grid/grid.hpp>
#include "python_grid_utils.hpp"

//pybind11
#include <pybind11/pybind11.h>

namespace py = pybind11;

// help compiler see template definitions
static py::dict (*encode)( mapnik::grid const&, std::string const& , bool, unsigned int) = mapnik::grid_encode;

bool painted(mapnik::grid const& grid)
{
    return grid.painted();
}

mapnik::grid::value_type get_pixel(mapnik::grid const& grid, int x, int y)
{
    if (x < static_cast<int>(grid.width()) && y < static_cast<int>(grid.height()))
    {
        mapnik::grid::data_type const & data = grid.data();
        return data(x,y);
    }
    throw  py::index_error("invalid x,y for grid dimensions");
}

void export_grid(py::module const& m)
{
    py::class_<mapnik::grid, std::shared_ptr<mapnik::grid>>
        (m, "Grid", "This class represents a feature hitgrid.")
        .def(py::init<int,int,std::string>(),
             "Create a mapnik.Grid object\n",
             py::arg("width"), py::arg("height"), py::arg("key")="__id__")
        .def("painted",&painted)
        .def("width",&mapnik::grid::width)
        .def("height",&mapnik::grid::height)
        .def("view",&mapnik::grid::get_view)
        .def("get_pixel",&get_pixel)
        .def("clear",&mapnik::grid::clear)
        .def("encode", encode,
             "Encode the grid as as optimized json\n",
             py::arg("encoding") = "utf", py::arg("features") = true, py::arg("resolution") = 4)
        .def_property("key",
                      &mapnik::grid::get_key,
                      &mapnik::grid::set_key,
                      "Get/Set key to be used as unique indentifier for features\n"
                      "The value should either be __id__ to refer to the feature.id()\n"
                      "or some globally unique integer or string attribute field\n"
            )
        ;

}

#endif
