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
#ifndef MAPNIK_PYTHON_BINDING_GRID_UTILS_INCLUDED
#define MAPNIK_PYTHON_BINDING_GRID_UTILS_INCLUDED

// mapnik
#include <mapnik/map.hpp>
#include <mapnik/grid/grid.hpp>
// pybind11
#include <pybind11/pybind11.h>

namespace py = pybind11;

namespace mapnik {


template <typename T>
void grid2utf(T const& grid_type,
                     py::list& l,
                     std::vector<typename T::lookup_type>& key_order);


template <typename T>
void grid2utf(T const& grid_type,
                     py::list& l,
                     std::vector<typename T::lookup_type>& key_order,
                     unsigned int resolution);


template <typename T>
void write_features(T const& grid_type,
                           py::dict& feature_data,
                           std::vector<typename T::lookup_type> const& key_order);

template <typename T>
void grid_encode_utf(T const& grid_type,
                            py::dict & json,
                            bool add_features,
                            unsigned int resolution);

template <typename T>
py::dict grid_encode( T const& grid, std::string const& format, bool add_features, unsigned int resolution);

void render_layer_for_grid(const mapnik::Map& map,
                           mapnik::grid& grid,
                           unsigned layer_idx, // TODO - layer by name or index
                           py::list const& fields,
                           double scale_factor,
                           unsigned offset_x,
                           unsigned offset_y);

}

#endif // MAPNIK_PYTHON_BINDING_GRID_UTILS_INCLUDED
