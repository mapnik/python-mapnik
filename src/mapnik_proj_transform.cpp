/*****************************************************************************
 *
 * This file is part of Mapnik (c++ mapping toolkit)
 *
 * Copyright (C) 2015 Artem Pavlenko
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

#include <mapnik/config.hpp>
#include "boost_std_shared_shim.hpp"

#include <mapnik/warning_ignore.hpp>
#include <boost/python.hpp>
#include <boost/noncopyable.hpp>

// mapnik
#include <mapnik/proj_transform.hpp>
#include <mapnik/projection.hpp>
#include <mapnik/coord.hpp>
#include <mapnik/geometry/box2d.hpp>

// stl
#include <stdexcept>


using mapnik::proj_transform;
using mapnik::projection;

struct proj_transform_pickle_suite : boost::python::pickle_suite
{
    static boost::python::tuple
    getinitargs(const proj_transform& p)
    {
        using namespace boost::python;
        return boost::python::make_tuple(p.definition());
    }
};

namespace  {

mapnik::coord2d forward_transform_c(mapnik::proj_transform& t, mapnik::coord2d const& c)
{
    double x = c.x;
    double y = c.y;
    double z = 0.0;
    if (!t.forward(x,y,z)) {
        std::ostringstream s;
        s << "Failed to forward project " << t.definition();
        throw std::runtime_error(s.str());
    }
    return mapnik::coord2d(x,y);
}

mapnik::coord2d backward_transform_c(mapnik::proj_transform& t, mapnik::coord2d const& c)
{
    double x = c.x;
    double y = c.y;
    double z = 0.0;
    if (!t.backward(x,y,z)) {
        std::ostringstream s;
        s << "Failed to back project " << t.definition();
        throw std::runtime_error(s.str());
    }
    return mapnik::coord2d(x,y);
}

mapnik::box2d<double> forward_transform_env(mapnik::proj_transform& t, mapnik::box2d<double> const & box)
{
    mapnik::box2d<double> new_box = box;
    if (!t.forward(new_box)) {
        std::ostringstream s;
        s << "Failed to forward project " << t.definition();
        throw std::runtime_error(s.str());
    }
    return new_box;
}

mapnik::box2d<double> backward_transform_env(mapnik::proj_transform& t, mapnik::box2d<double> const & box)
{
    mapnik::box2d<double> new_box = box;
    if (!t.backward(new_box)){
        std::ostringstream s;
        s << "Failed to back project " << t.definition();
        throw std::runtime_error(s.str());
    }
    return new_box;
}

mapnik::box2d<double> forward_transform_env_p(mapnik::proj_transform& t, mapnik::box2d<double> const & box, unsigned int points)
{
    mapnik::box2d<double> new_box = box;
    if (!t.forward(new_box,points)) {
        std::ostringstream s;
        s << "Failed to forward project " << t.definition();
        throw std::runtime_error(s.str());
    }
    return new_box;
}

mapnik::box2d<double> backward_transform_env_p(mapnik::proj_transform& t, mapnik::box2d<double> const & box, unsigned int points)
{
    mapnik::box2d<double> new_box = box;
    if (!t.backward(new_box,points)){
        std::ostringstream s;
        s << "Failed to back project " <<  t.definition();
        throw std::runtime_error(s.str());
    }
    return new_box;
}

}

void export_proj_transform ()
{
    using namespace boost::python;

    class_<proj_transform, boost::noncopyable>("ProjTransform", init<projection const&, projection const&>())
        .def_pickle(proj_transform_pickle_suite())
        .def("forward", forward_transform_c)
        .def("backward",backward_transform_c)
        .def("forward", forward_transform_env)
        .def("backward",backward_transform_env)
        .def("forward", forward_transform_env_p)
        .def("backward",backward_transform_env_p)
        .def("definition",&proj_transform::definition)
        ;

}
