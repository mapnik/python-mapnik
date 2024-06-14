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
#include <string>
#include <mapnik/grid/grid_view.hpp>
#include <mapnik/grid/grid.hpp>
#include "python_grid_utils.hpp"

// help compiler see template definitions
static py::dict (*encode)( mapnik::grid_view const&, std::string const& , bool, unsigned int) = mapnik::grid_encode;

void export_grid_view(py::module const& m)
{
    py::class_<mapnik::grid_view, std::shared_ptr<mapnik::grid_view>>
        (m, "GridView", "This class represents a feature hitgrid subset.")
        .def("width",&mapnik::grid_view::width)
        .def("height",&mapnik::grid_view::height)
        .def("encode",encode,
             "Encode the grid as as optimized json\n",
             py::arg("encoding")="utf",py::arg("add_features")=true,py::arg("resolution")=4)
        ;
}

#endif
