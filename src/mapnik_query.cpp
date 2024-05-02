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
#include <mapnik/query.hpp>
#include <mapnik/geometry/box2d.hpp>
#include "python_to_value.hpp"
#include "mapnik_value_converter.hpp"
//stl
#include <string>
#include <set>
//pybind11
#include <pybind11/pybind11.h>
#include <pybind11/stl.h>

namespace py = pybind11;

void export_query(py::module const& m)
{
    using mapnik::query;
    using mapnik::box2d;

    py::class_<query>(m, "Query", "a spatial query data object")
        .def(py::init<box2d<double>,query::resolution_type const&, double>())
        .def(py::init<box2d<double>>())
        .def_property_readonly("resolution", [] (query const& q) {
            auto resolution = q.resolution();
            return py::make_tuple(std::get<0>(resolution),
                                  std::get<1>(resolution));
        })
        .def_property_readonly("scale_denominator", &query::scale_denominator)
        .def_property_readonly("bbox", &query::get_bbox)
        .def_property_readonly("unbuffered_bbox", &query::get_unbuffered_bbox)
        .def_property_readonly("property_names",[] (query const& q){
            auto names = q.property_names();
            py::list obj;
            for (std::string const& name : names)
            {
                obj.append(name);
            }
            return obj;
        })
        .def("add_property_name", &query::add_property_name)
        .def_property("variables",
                      [] (query const& q) {
                          py::dict d;
                          for (auto kv : q.variables())
                          {
                              d[kv.first.c_str()] = kv.second;
                          }
                          return d;
                      },
                      [] (query& q, py::dict const& d) {
                          mapnik::attributes vars = mapnik::dict2attr(d);
                          q.set_variables(vars);
                      })
        ;
}
