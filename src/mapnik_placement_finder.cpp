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


#include <mapnik/config.hpp>
#include <mapnik/symbolizer.hpp>
#include <mapnik/symbolizer_hash.hpp>
#include <mapnik/symbolizer_utils.hpp>
#include <mapnik/symbolizer_keys.hpp>
#include <mapnik/symbolizer_enumerations.hpp>
#include <mapnik/text/placements/dummy.hpp>
#include <mapnik/text/text_properties.hpp>
#include <mapnik/text/formatting/text.hpp>

//pybind11
#include <pybind11/pybind11.h>
//#include <pybind11/operators.h>
//#include <pybind11/stl.h>
//#include <pybind11/stl_bind.h>

namespace py = pybind11;

namespace
{

void set_face_name(mapnik::text_placements_dummy & finder, std::string const& face_name)
{
    finder.defaults.format_defaults.face_name = face_name;
}

std::string get_face_name(mapnik::text_placements_dummy & finder)
{
    return finder.defaults.format_defaults.face_name;
}

void set_text_size(mapnik::text_placements_dummy & finder, double text_size)
{
    finder.defaults.format_defaults.text_size = text_size;
}

mapnik::symbolizer_base::value_type get_text_size(mapnik::text_placements_dummy & finder)
{
    return finder.defaults.format_defaults.text_size;
}

void set_fill(mapnik::text_placements_dummy & finder, mapnik::color const& fill)
{
    finder.defaults.format_defaults.fill = fill;
}

mapnik::symbolizer_base::value_type get_fill(mapnik::text_placements_dummy & finder)
{
    return finder.defaults.format_defaults.fill;
}
void set_halo_fill(mapnik::text_placements_dummy & finder, mapnik::color const& halo_fill )
{
    finder.defaults.format_defaults.halo_fill = halo_fill;
}

mapnik::symbolizer_base::value_type get_halo_fill(mapnik::text_placements_dummy & finder)
{
    return finder.defaults.format_defaults.halo_fill;
}


void set_halo_radius(mapnik::text_placements_dummy & finder, double halo_radius)
{
    finder.defaults.format_defaults.halo_radius = halo_radius;
}

mapnik::symbolizer_base::value_type get_halo_radius(mapnik::text_placements_dummy & finder)
{
    return finder.defaults.format_defaults.halo_radius;
}

void set_format_expr(mapnik::text_placements_dummy & finder, std::string const& expr)
{
    finder.defaults.set_format_tree(
        std::make_shared<mapnik::formatting::text_node>(mapnik::parse_expression(expr)));
}

std::string get_format_expr(mapnik::text_placements_dummy & finder)
{
    return "FIXME";
}

}

void export_placement_finder(py::module const& m)
{
    //using namespace boost::python;
    //implicitly_convertible<mapnik::symbolizer_base::value_type, mapnik::value_double>();
/*
  text_placements_ptr placement_finder = std::make_shared<text_placements_dummy>();
                placement_finder->defaults.format_defaults.face_name = "DejaVu Sans Book";
                placement_finder->defaults.format_defaults.text_size = 10.0;
                placement_finder->defaults.format_defaults.fill = color(0, 0, 0);
                placement_finder->defaults.format_defaults.halo_fill = color(255, 255, 200);
                placement_finder->defaults.format_defaults.halo_radius = 1.0;
                placement_finder->defaults.set_format_tree(
                  std::make_shared<mapnik::formatting::text_node>(parse_expression("[GEONAME]")));
                put<text_placements_ptr>(text_sym, keys::text_placements_, placement_finder);
*/
    py::class_<mapnik::text_placements_dummy, std::shared_ptr<mapnik::text_placements_dummy>>(m, "PlacementFinder")
        .def(py::init<>(), "Default ctor")
        .def_property("face_name", &get_face_name, &set_face_name, "Font face name")
        .def_property("text_size", &get_text_size, &set_text_size, "Size of text")
        .def_property("fill", &get_fill, &set_fill, "Fill")
        .def_property("halo_fill", &get_halo_fill, &set_halo_fill, "Halo fill")
        .def_property("halo_radius", &get_halo_radius, &set_halo_radius, "Halo radius")
        .def_property("format_expression", &get_format_expr, &set_format_expr, "Format expression")
        ;
}
