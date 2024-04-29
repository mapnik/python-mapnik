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
#include <mapnik/feature.hpp>
#include <mapnik/datasource.hpp>

//pybind11
#include <pybind11/pybind11.h>
#include <pybind11/operators.h>
#include <pybind11/stl.h>

namespace py = pybind11;

namespace {

inline mapnik::feature_ptr next(mapnik::featureset_ptr const& itr)
{
    mapnik::feature_ptr f = itr->next();
    if (!f) throw py::stop_iteration();
    return f;
}

}

void export_featureset(py::module const& m)
{
    // Featureset implements Python iterator interface
    py::class_<mapnik::Featureset, std::shared_ptr<mapnik::Featureset>>
        (m, "Featureset")
        .def("__iter__", [](mapnik::Featureset& itr) -> mapnik::Featureset& { return itr; })
        .def("__next__", next)
        ;
}
