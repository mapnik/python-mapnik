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
#include <mapnik/coord.hpp>
#include <mapnik/geometry/box2d.hpp>
#include <mapnik/projection.hpp>
//pybind11
#include <pybind11/pybind11.h>
#include <pybind11/stl.h>

using mapnik::projection;

namespace py = pybind11;

namespace {

mapnik::coord2d forward_pt(mapnik::coord2d const& pt,
                           mapnik::projection const& prj)
{
    double x = pt.x;
    double y = pt.y;
    prj.forward(x,y);
    return mapnik::coord2d(x,y);
}

mapnik::coord2d inverse_pt(mapnik::coord2d const& pt,
                           mapnik::projection const& prj)
{
    double x = pt.x;
    double y = pt.y;
    prj.inverse(x,y);
    return mapnik::coord2d(x,y);
}

mapnik::box2d<double> forward_env(mapnik::box2d<double> const & box,
                                  mapnik::projection const& prj)
{
    double minx = box.minx();
    double miny = box.miny();
    double maxx = box.maxx();
    double maxy = box.maxy();
    prj.forward(minx,miny);
    prj.forward(maxx,maxy);
    return mapnik::box2d<double>(minx,miny,maxx,maxy);
}

mapnik::box2d<double> inverse_env(mapnik::box2d<double> const & box,
                                  mapnik::projection const& prj)
{
    double minx = box.minx();
    double miny = box.miny();
    double maxx = box.maxx();
    double maxy = box.maxy();
    prj.inverse(minx,miny);
    prj.inverse(maxx,maxy);
    return mapnik::box2d<double>(minx,miny,maxx,maxy);
}

}

void export_projection (py::module& m)
{
    py::class_<projection>(m, "Projection", "Represents a map projection.")
        .def(py::init<std::string const&>(),
             "Constructs a new projection from its PROJ string representation.\n"
             "\n"
             "The constructor will throw a RuntimeError in case the projection\n"
             "cannot be initialized.\n",
             py::arg("proj_string")
            )
        .def(py::pickle(
                 [] (projection const& p) { // __getstate__
                     return py::make_tuple(p.params());
                 },
                 [] (py::tuple t) { // __setstate__
                     if (t.size() != 1)
                         throw std::runtime_error("Invalid state!");
                     projection p(t[0].cast<std::string>());
                     return p;
                 }))
        .def("params",  &projection::params,
             "Returns the PROJ string for this projection.\n")
        .def("definition",&projection::definition,
             "Return projection definition\n")
        .def("description", &projection::description,
             "Returns projection description")
        .def_property_readonly("geographic", &projection::is_geographic,
                               "This property is True if the projection is a geographic projection\n"
                               "(i.e. it uses lon/lat coordinates)\n")
        .def_property_readonly("area_of_use", &projection::area_of_use,
                               "This property returns projection area of use in lonlat WGS84\n")
        ;

    m.def("forward_", &forward_pt);
    m.def("inverse_", &inverse_pt);
    m.def("forward_", &forward_env);
    m.def("inverse_", &inverse_env);

}
