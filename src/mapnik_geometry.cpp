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

// mapnik
#include <mapnik/geometry.hpp>
#include <mapnik/geometry/geometry_type.hpp>
#include <mapnik/geometry/envelope.hpp>
#include <mapnik/geometry/is_valid.hpp>
#include <mapnik/geometry/is_simple.hpp>
#include <mapnik/geometry/is_empty.hpp>
#include <mapnik/geometry/correct.hpp>
#include <mapnik/geometry/centroid.hpp>
#include <mapnik/wkt/wkt_factory.hpp> // from_wkt
#include <mapnik/json/geometry_parser.hpp> // from_geojson
#include <mapnik/util/geometry_to_geojson.hpp> // to_geojson
#include <mapnik/util/geometry_to_wkb.hpp> // to_wkb
#include <mapnik/util/geometry_to_wkt.hpp> // to_wkt
#include <mapnik/wkb.hpp>
#include "python_variant.hpp"

// stl
#include <stdexcept>

//pybind11
#include <pybind11/pybind11.h>
#include <pybind11/stl.h>
#include <pybind11/native_enum.h>

namespace py = pybind11;

namespace {

std::shared_ptr<mapnik::geometry::geometry<double> > from_wkb_impl(std::string const& wkb)
{
    std::shared_ptr<mapnik::geometry::geometry<double> > geom = std::make_shared<mapnik::geometry::geometry<double> >();
    try
    {
        *geom = mapnik::geometry_utils::from_wkb(wkb.c_str(), wkb.size());
    }
    catch (...)
    {
        throw std::runtime_error("Failed to parse WKB");
    }
    return geom;
}

std::shared_ptr<mapnik::geometry::geometry<double> > from_wkt_impl(std::string const& wkt)
{
    std::shared_ptr<mapnik::geometry::geometry<double> > geom = std::make_shared<mapnik::geometry::geometry<double> >();
    if (!mapnik::from_wkt(wkt, *geom))
        throw std::runtime_error("Failed to parse WKT geometry");
    return geom;
}

std::shared_ptr<mapnik::geometry::geometry<double> > from_geojson_impl(std::string const& json)
{
    std::shared_ptr<mapnik::geometry::geometry<double> > geom = std::make_shared<mapnik::geometry::geometry<double> >();
    if (!mapnik::json::from_geojson(json, *geom))
        throw std::runtime_error("Failed to parse geojson geometry");
    return geom;
}

}

template <typename GeometryType>
py::object to_wkb_impl(GeometryType const& geom, mapnik::wkbByteOrder byte_order)
{
    mapnik::util::wkb_buffer_ptr wkb = mapnik::util::to_wkb(geom, byte_order);
    if (wkb) return py::bytes(wkb->buffer(), wkb->size());
    return py::none();
}

template <typename GeometryType>
std::string to_geojson_impl(GeometryType const& geom)
{
    std::string wkt;
    if (!mapnik::util::to_geojson(wkt, geom))
    {
        throw std::runtime_error("Generate JSON failed");
    }
    return wkt;
}

template <typename GeometryType>
std::string to_wkt_impl(GeometryType const& geom)
{
    std::string wkt;
    if (!mapnik::util::to_wkt(wkt,geom))
    {
        throw std::runtime_error("Generate WKT failed");
    }
    return wkt;
}

mapnik::geometry::geometry_types geometry_type_impl(mapnik::geometry::geometry<double> const& geom)
{
    return mapnik::geometry::geometry_type(geom);
}

template <typename GeometryType>
mapnik::box2d<double> geometry_envelope_impl(GeometryType const& geom)
{
    return mapnik::geometry::envelope(geom);
}

template <typename GeometryType>
bool geometry_is_valid_impl(GeometryType const& geom)
{
    return mapnik::geometry::is_valid(geom);
}

template <typename GeometryType>
bool geometry_is_simple_impl(GeometryType const& geom)
{
    return mapnik::geometry::is_simple(geom);
}

template <typename GeometryType>
bool geometry_is_empty_impl(GeometryType const& geom)
{
    return mapnik::geometry::is_empty(geom);
}

void geometry_correct_impl(mapnik::geometry::geometry<double> & geom)
{
    mapnik::geometry::correct(geom);
}

template <typename T>
void add_coord(T & geom, double x, double y)
{
    geom.emplace_back(x, y);
}

template <typename Dst, typename Src>
void add_impl(Dst & geom, Src const& src)
{
    geom.push_back(src); // copy
}

mapnik::geometry::point<double> geometry_centroid_impl(mapnik::geometry::geometry<double> const& geom)
{
    mapnik::geometry::point<double> pt;
    mapnik::geometry::centroid(geom, pt);
    return pt;
}


void export_geometry(py::module const& m)
{
    using mapnik::geometry::geometry;
    using mapnik::geometry::point;
    using mapnik::geometry::line_string;
    using mapnik::geometry::linear_ring;
    using mapnik::geometry::polygon;
    using mapnik::geometry::multi_point;
    using mapnik::geometry::multi_line_string;
    using mapnik::geometry::multi_polygon;
    using mapnik::geometry::geometry_collection;


    py::native_enum<mapnik::geometry::geometry_types>(m, "GeometryType", "enum.Enum")
        .value("Unknown",mapnik::geometry::geometry_types::Unknown)
        .value("Point",mapnik::geometry::geometry_types::Point)
        .value("LineString",mapnik::geometry::geometry_types::LineString)
        .value("Polygon",mapnik::geometry::geometry_types::Polygon)
        .value("MultiPoint",mapnik::geometry::geometry_types::MultiPoint)
        .value("MultiLineString",mapnik::geometry::geometry_types::MultiLineString)
        .value("MultiPolygon",mapnik::geometry::geometry_types::MultiPolygon)
        .value("GeometryCollection",mapnik::geometry::geometry_types::GeometryCollection)
        .finalize()
        ;

    py::native_enum<mapnik::wkbByteOrder>(m, "wkbByteOrder", "enum.Enum")
        .value("XDR", mapnik::wkbXDR)
        .value("NDR", mapnik::wkbNDR)
        .finalize()
        ;


    py::class_<point<double> >(m, "Point")
        .def(py::init<double, double>(),
             "Constructs a new Point object\n",
             py::arg("x"), py::arg("y"))
        .def_readwrite("x", &point<double>::x, "X coordinate")
        .def_readwrite("y", &point<double>::y, "Y coordinate")
        .def("is_valid", &geometry_is_valid_impl<point<double>>)
        .def("is_simple", &geometry_is_simple_impl<point<double>>)
        .def("to_geojson",&to_geojson_impl<point<double>>)
        .def("to_wkb",&to_wkb_impl<point<double>>)
        .def("to_wkt",&to_wkt_impl<point<double>>)
        .def("envelope",&geometry_envelope_impl<point<double>>)
        ;

    py::class_<multi_point<double>>(m, "MultiPoint")
        .def(py::init<>(),
             "Constructs a new MultiPoint object\n")
        .def("add_point", &add_coord<multi_point<double>>, "Adds coord x,y")
        .def("add_point", &add_impl<multi_point<double>, point<double>>, "Adds mapnik.Point")
        .def("is_valid", &geometry_is_valid_impl<multi_point<double>>)
        .def("is_simple", &geometry_is_simple_impl<multi_point<double>>)
        .def("to_geojson",&to_geojson_impl<multi_point<double>>)
        .def("to_wkb",&to_wkb_impl<multi_point<double>>)
        .def("to_wkt",&to_wkt_impl<multi_point<double>>)
        .def("envelope",&geometry_envelope_impl<multi_point<double>>)
        .def("num_points",[](multi_point<double> const& mp) { return mp.size(); },"Number of points in MultiPoint")
        .def("__len__", [](multi_point<double>const &mp) { return mp.size(); })
        .def("__iter__", [](multi_point<double> const& mp) {
            return py::make_iterator(mp.begin(), mp.end());
        }, py::keep_alive<0, 1>())
        ;

    py::class_<line_string<double> >(m, "LineString")
        .def(py::init<>(), "Constructs a new LineString object\n")
        .def("add_point", &add_coord<line_string<double>>, "Adds coord x,y")
        .def("add_point", &add_impl<line_string<double>, point<double>>, "Adds mapnik.Point")
        .def("is_valid", &geometry_is_valid_impl<line_string<double>>)
        .def("is_simple", &geometry_is_simple_impl<line_string<double>>)
        .def("to_geojson",&to_geojson_impl<line_string<double>>)
        .def("to_wkb",&to_wkb_impl<line_string<double>>)
        .def("to_wkt",&to_wkt_impl<line_string<double>>)
        .def("envelope",&geometry_envelope_impl<line_string<double>>)
        .def("num_points",[](line_string<double> const& l) { return l.size(); },"Number of points in LineString")
        .def("__len__", [](line_string<double>const &l) { return l.size(); })
        .def("__iter__", [](line_string<double> const& l) {
            return py::make_iterator(l.begin(), l.end());
        }, py::keep_alive<0, 1>())
        ;

    py::class_<linear_ring<double> >(m, "LinearRing")
        .def(py::init<>(),  "Constructs a new LinearRtring object\n")
        .def("add_point", &add_coord<linear_ring<double>>, "Adds coord x,y")
        .def("add_point", &add_impl<linear_ring<double>, point<double>>, "Adds mapnik.Point")
        .def("envelope",&geometry_envelope_impl<linear_ring<double>>)
        .def("__len__", [](linear_ring<double>const &r) { return r.size(); })
        .def("__iter__", [](linear_ring<double> const& r) {
            return py::make_iterator(r.begin(), r.end());
        }, py::keep_alive<0, 1>())
        ;

    py::class_<polygon<double> >(m, "Polygon")
        .def(py::init<>(), "Constructs a new Polygon object\n")
        .def("add_ring", &add_impl<polygon<double>, linear_ring<double>>, "Add ring")
        .def("is_valid", &geometry_is_valid_impl<polygon<double>>)
        .def("is_simple", &geometry_is_simple_impl<polygon<double>>)
        .def("to_geojson",&to_geojson_impl<polygon<double>>)
        .def("to_wkb",&to_wkb_impl<polygon<double>>)
        .def("to_wkt",&to_wkt_impl<polygon<double>>)
        .def("envelope",&geometry_envelope_impl<polygon<double>>)
        .def("num_rings", [](polygon<double>const &p) { return p.size(); }, "Number of rings")
        .def("__len__", [](polygon<double>const &p) { return p.size(); })
        .def("__iter__", [](polygon<double> const& p) {
            return py::make_iterator(p.begin(), p.end());
        }, py::keep_alive<0, 1>())
        ;

    py::class_<multi_line_string<double> >(m, "MultiLineString")
        .def(py::init<>(), "Constructs a new MultiLineString object\n")
        .def("add_string", &add_impl<multi_line_string<double>, line_string<double>>, "Add LineString")
        .def("is_valid", &geometry_is_valid_impl<multi_line_string<double>>)
        .def("is_simple", &geometry_is_simple_impl<multi_line_string<double>>)
        .def("to_geojson",&to_geojson_impl<multi_line_string<double>>)
        .def("to_wkb",&to_wkb_impl<multi_line_string<double>>)
        .def("to_wkt",&to_wkt_impl<multi_line_string<double>>)
        .def("envelope",&geometry_envelope_impl<multi_line_string<double>>)
        .def("__len__", [](multi_line_string<double>const& mls) { return mls.size(); })
        .def("__iter__", [](multi_line_string<double> const& mls) {
            return py::make_iterator(mls.begin(), mls.end());
        }, py::keep_alive<0, 1>())
        ;

    py::class_<multi_polygon<double> >(m, "MultiPolygon")
        .def(py::init<>(), "Constructs a new MultiPolygon object\n")
        .def("add_polygon", &add_impl<multi_polygon<double>, polygon<double>>, "Add Polygon")
        .def("is_valid", &geometry_is_valid_impl<multi_polygon<double>>)
        .def("is_simple", &geometry_is_simple_impl<multi_polygon<double>>)
        .def("to_geojson",&to_geojson_impl<multi_polygon<double>>)
        .def("to_wkb",&to_wkb_impl<multi_polygon<double>>)
        .def("to_wkt",&to_wkt_impl<multi_polygon<double>>)
        .def("envelope",&geometry_envelope_impl<multi_polygon<double>>)
        .def("__len__", [](multi_polygon<double>const& mp) { return mp.size(); })
        .def("__iter__", [](multi_polygon<double> const& mp) {
            return py::make_iterator(mp.begin(), mp.end());
        }, py::keep_alive<0, 1>())
        ;

    py::class_<geometry_collection<double> >(m, "GeometryCollection")
        .def(py::init<>(), "Constructs a new GeometryCollection object\n")
        .def("add_geometry", &add_impl<geometry_collection<double>, geometry<double>>, "Add Geometry")
        .def("is_valid", &geometry_is_valid_impl<geometry_collection<double>>)
        .def("is_simple", &geometry_is_simple_impl<geometry_collection<double>>)
        .def("to_geojson",&to_geojson_impl<geometry_collection<double>>)
        .def("to_wkb",&to_wkb_impl<geometry_collection<double>>)
        .def("to_wkt",&to_wkt_impl<geometry_collection<double>>)
        .def("envelope",&geometry_envelope_impl<geometry_collection<double>>)
        .def("__len__", [](geometry_collection<double>const& gc) { return gc.size(); })
        .def("__iter__", [](geometry_collection<double> const& gc) {
            return py::make_iterator(gc.begin(), gc.end());
        }, py::keep_alive<0, 1>())
        ;

    py::class_<geometry<double>, std::shared_ptr<geometry<double>>>(m, "Geometry")
        .def(py::init<point<double>>())
        .def(py::init<line_string<double>>())
        .def(py::init<polygon<double>>())
        .def(py::init<multi_point<double>>())
        .def(py::init<multi_line_string<double>>())
        .def(py::init<multi_polygon<double>>())
        .def(py::init<geometry_collection<double>>())
        .def("envelope",&geometry_envelope_impl<geometry<double>>)
        .def_static("from_geojson", from_geojson_impl)
        .def_static("from_wkt", from_wkt_impl)
        .def_static("from_wkb", from_wkb_impl)
        .def("__str__",&to_wkt_impl<geometry<double>>)
        .def("type",&geometry_type_impl)
        .def("is_valid", &geometry_is_valid_impl<geometry<double>>)
        .def("is_simple", &geometry_is_simple_impl<geometry<double>>)
        .def("is_empty", &geometry_is_empty_impl<geometry<double>>)
        .def("correct", &geometry_correct_impl)
        .def("centroid",&geometry_centroid_impl)
        .def("to_wkb",&to_wkb_impl<geometry<double>>)
        .def("to_wkt",&to_wkt_impl<geometry<double>>)
        .def("to_json",&to_geojson_impl<geometry<double>>)
        .def("to_geojson",&to_geojson_impl<geometry<double>>)
        .def_property_readonly("__geo_interface__", [](geometry<double> const& g) {
            py::object json = py::module_::import("json");
            py::object loads = json.attr("loads");
            return loads(to_geojson_impl<geometry<double>>(g));})
        ;

    py::implicitly_convertible<mapnik::geometry::point<double>, mapnik::geometry::geometry<double>>();
    py::implicitly_convertible<mapnik::geometry::line_string<double>, mapnik::geometry::geometry<double>>();
    py::implicitly_convertible<mapnik::geometry::polygon<double>, mapnik::geometry::geometry<double>>();
    py::implicitly_convertible<mapnik::geometry::multi_point<double>, mapnik::geometry::geometry<double>>();
    py::implicitly_convertible<mapnik::geometry::multi_line_string<double>, mapnik::geometry::geometry<double>>();
    py::implicitly_convertible<mapnik::geometry::multi_polygon<double>, mapnik::geometry::geometry<double>>();
    py::implicitly_convertible<mapnik::geometry::geometry_collection<double>, mapnik::geometry::geometry<double>>();

}
