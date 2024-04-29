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
#include <mapnik/geometry/box2d.hpp>
#include <mapnik/datasource.hpp>
#include <mapnik/datasource_cache.hpp>
#include <mapnik/feature_layer_desc.hpp>
#include <mapnik/memory_datasource.hpp>
#include "mapnik_value_converter.hpp"
// stl
#include <vector>
//pybind11
#include <pybind11/pybind11.h>
#include <pybind11/operators.h>
#include <pybind11/stl.h>

namespace PYBIND11_NAMESPACE { namespace detail {
    template <typename T>
    struct type_caster<boost::optional<T>> : optional_caster<boost::optional<T>> {};
}}


using mapnik::datasource;
using mapnik::memory_datasource;
using mapnik::layer_descriptor;
using mapnik::attribute_descriptor;
using mapnik::parameters;

namespace py = pybind11;

namespace
{

struct mapnik_param_to_python
{
    static PyObject* convert(mapnik::value_holder const& v)
    {
        return mapnik::util::apply_visitor(value_converter(),v);
    }
};

std::shared_ptr<mapnik::datasource> create_datasource(py::kwargs const& kwargs)
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
            params[key] = handle.cast<bool>();
        }
        else if (py::isinstance<py::float_>(handle))
        {
            params[key] = handle.cast<double>();
        }
        else if (py::isinstance<py::int_>(handle))
        {
            params[key] = handle.cast<long long>();
        }
        else
        {
            params[key] = py::str(handle).cast<std::string>();
        }
    }
    return mapnik::datasource_cache::instance().create(params);
}

py::dict describe(std::shared_ptr<mapnik::datasource> const& ds)
{
    py::dict description;
    mapnik::layer_descriptor ld = ds->get_descriptor();
    description["type"] = ds->type();
    description["name"] = ld.get_name();
    description["geometry_type"] = ds->get_geometry_type();
    description["encoding"] = ld.get_encoding();
    for (auto const& param : ld.get_extra_parameters())
    {
        description[py::str(param.first)] = mapnik_param_to_python::convert(param.second);
    }
    return description;
}

py::list fields(std::shared_ptr<mapnik::datasource> const& ds)
{
    py::list flds;
    if (ds)
    {
        layer_descriptor ld = ds->get_descriptor();
        std::vector<attribute_descriptor> const& desc_ar = ld.get_descriptors();
        std::vector<attribute_descriptor>::const_iterator it = desc_ar.begin();
        std::vector<attribute_descriptor>::const_iterator end = desc_ar.end();
        for (; it != end; ++it)
        {
            flds.append(it->get_name());
        }
    }
    return flds;
}
py::list field_types(std::shared_ptr<mapnik::datasource> const& ds)
{
    py::list fld_types;
    if (ds)
    {
        layer_descriptor ld = ds->get_descriptor();
        std::vector<attribute_descriptor> const& desc_ar = ld.get_descriptors();
        std::vector<attribute_descriptor>::const_iterator it = desc_ar.begin();
        std::vector<attribute_descriptor>::const_iterator end = desc_ar.end();
        for (; it != end; ++it)
        {
            unsigned type = it->get_type();
            if (type == mapnik::Integer)
                fld_types.append(py::str("int"));
            else if (type == mapnik::Float)
                fld_types.append(py::str("float"));
            else if (type == mapnik::Double)
                fld_types.append(py::str("float"));
            else if (type == mapnik::String)
                fld_types.append(py::str("str"));
            else if (type == mapnik::Boolean)
                fld_types.append(py::str("bool"));
            else if (type == mapnik::Geometry)
                fld_types.append(py::str("geometry"));
            else if (type == mapnik::Object)
                fld_types.append(py::str("object"));
            else
                fld_types.append(py::str("unknown"));
        }
    }
    return fld_types;
}

py::dict parameters_impl(std::shared_ptr<mapnik::datasource> const& ds)
{
    auto const params = ds->params();
    py::dict d;
    for (auto kv : params)
    {
        d[py::str(kv.first)] = mapnik_param_to_python::convert(kv.second);
    }
    return d;
}

} // namespace


void export_datasource(py::module& m)
{
    py::enum_<mapnik::datasource::datasource_t>(m, "DataType")
        .value("Vector",mapnik::datasource::Vector)
        .value("Raster",mapnik::datasource::Raster)
        ;

    py::enum_<mapnik::datasource_geometry_t>(m, "DataGeometryType")
        .value("Point",mapnik::datasource_geometry_t::Point)
        .value("LineString",mapnik::datasource_geometry_t::LineString)
        .value("Polygon",mapnik::datasource_geometry_t::Polygon)
        .value("Collection",mapnik::datasource_geometry_t::Collection)
        ;

    py::class_<datasource,std::shared_ptr<datasource>> (m, "Datasource")
        .def(py::init([] (py::kwargs const& kwargs) { return create_datasource(kwargs);}))
        .def("type", &datasource::type)
        .def("geometry_type", &datasource::get_geometry_type)
        .def("describe", &describe)
        .def("envelope", &datasource::envelope)
        .def("features", &datasource::features)
        .def("fields" ,&fields)
        .def("field_types", &field_types)
        .def("features_at_point", &datasource::features_at_point, py::arg("coord"), py::arg("tolerance") = 0)
        .def("parameters", &parameters_impl,
             "The configuration parameters of the data source. "
             "These vary depending on the type of data source.")
        .def(py::self == py::self)
        .def("__iter__",
             [](datasource const& ds) {
                 mapnik::query q(ds.envelope());
                 layer_descriptor ld = ds.get_descriptor();
                 std::vector<attribute_descriptor> const& desc_ar = ld.get_descriptors();
                 for (auto const& desc : desc_ar)
                 {
                     q.add_property_name(desc.get_name());
                 }
                 return ds.features(q);
             },
             py::keep_alive<0, 1>())
        ;

    m.def("CreateDatasource",&create_datasource);

    py::class_<memory_datasource, datasource, std::shared_ptr<memory_datasource>>
        (m, "MemoryDatasource")
        .def(py::init([]() {
            mapnik::parameters p;
            p.insert(std::make_pair("type","memory"));
            return std::make_shared<memory_datasource>(p);}))
        .def("add_feature", &memory_datasource::push,
             "Adds a Feature:\n"
             ">>> ms = MemoryDatasource()\n"
             ">>> feature = Feature(Context(),1)\n"
             ">>> ms.add_feature(f)\n")
        .def("num_features", &memory_datasource::size)
        ;

    py::implicitly_convertible<memory_datasource, datasource>();
}
