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

//mapnik
#include <mapnik/config.hpp>
#include <mapnik/value.hpp>
#include <mapnik/value/types.hpp>
#include <mapnik/feature.hpp>
#include <mapnik/feature_factory.hpp>
#include <mapnik/feature_kv_iterator.hpp>
#include <mapnik/datasource.hpp>
#include <mapnik/wkb.hpp>
#include <mapnik/json/feature_parser.hpp>
#include <mapnik/util/feature_to_geojson.hpp>

#include "mapnik_value_converter.hpp"
// stl
#include <stdexcept>
//pybind11
#include <pybind11/pybind11.h>
#include <pybind11/stl.h>

namespace py = pybind11;

namespace {

using mapnik::geometry_utils;
using mapnik::context_type;
using mapnik::context_ptr;
using mapnik::feature_kv_iterator;
using mapnik::value;

mapnik::feature_ptr from_geojson_impl(std::string const& json, mapnik::context_ptr const& ctx)
{
    mapnik::feature_ptr feature(mapnik::feature_factory::create(ctx,1));
    if (!mapnik::json::from_geojson(json,*feature))
    {
        throw std::runtime_error("Failed to parse geojson feature");
    }
    return feature;
}

std::string feature_to_geojson(mapnik::feature_impl const& feature)
{
    std::string json;
    if (!mapnik::util::to_geojson(json,feature))
    {
        throw std::runtime_error("Failed to generate GeoJSON");
    }
    return json;
}

mapnik::value __getitem__(mapnik::feature_impl const& feature, std::string const& name)
{
    return feature.get(name);
}

mapnik::value __getitem2__(mapnik::feature_impl const& feature, std::size_t index)
{
    return feature.get(index);
}

void __setitem__(mapnik::feature_impl & feature, std::string const& name, mapnik::value const& val)
{
    feature.put_new(name,val);
}

py::dict attributes(mapnik::feature_impl const& f)
{
    auto attributes = py::dict();
    feature_kv_iterator itr = f.begin();
    feature_kv_iterator end = f.end();

    for ( ;itr!=end; ++itr)
    {
        attributes[std::get<0>(*itr).c_str()] = std::get<1>(*itr);
    }

    return attributes;
}

} // end anonymous namespace

void export_feature(py::module const& m)
{
    py::class_<context_type, context_ptr>(m, "Context")
        .def(py::init<>(), "Default constructor")
        .def("push", &context_type::push)
        ;

    py::class_<mapnik::feature_impl, std::shared_ptr<mapnik::feature_impl>>(m, "Feature")
        .def(py::init<context_ptr,mapnik::value_integer>(), "Default constructor")
        .def("id",&mapnik::feature_impl::id)
        //.def_property("id",&mapnik::feature_impl::id, &mapnik::feature_impl::set_id)
        .def_property("geometry",
                      py::cpp_function((mapnik::geometry::geometry<double>& (mapnik::feature_impl::*)())
                                       &mapnik::feature_impl::get_geometry, py::return_value_policy::reference_internal),
                      py::cpp_function(&mapnik::feature_impl::set_geometry_copy))
        .def("envelope", &mapnik::feature_impl::envelope)
        .def("has_key", &mapnik::feature_impl::has_key)
        .def_property_readonly("attributes", [] (mapnik::feature_impl const& f) { return attributes(f) ;})
        .def("__setitem__", &__setitem__)
        .def("__contains__" ,&__getitem__)
        .def("__getitem__", &__getitem__)
        .def("__getitem__", &__getitem2__)
        .def("__len__", &mapnik::feature_impl::size)
        .def("context", &mapnik::feature_impl::context)
        .def("to_json", &feature_to_geojson)
        .def("to_geojson", &feature_to_geojson)
        .def_property_readonly("__geo_interface__",
                               [] (mapnik::feature_impl const& f) {
                                   py::object json = py::module_::import("json");
                                   py::object loads = json.attr("loads");
                                   return loads(feature_to_geojson(f));})
        .def_static("from_geojson", from_geojson_impl)
        ;
}
