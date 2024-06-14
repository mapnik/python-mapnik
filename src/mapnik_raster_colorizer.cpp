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
#include <mapnik/raster_colorizer.hpp>
#include <mapnik/symbolizer.hpp>
//pybind11
#include <pybind11/pybind11.h>
#include <pybind11/operators.h>

namespace py = pybind11;

using mapnik::raster_colorizer;
using mapnik::raster_colorizer_ptr;
using mapnik::symbolizer_base;
using mapnik::colorizer_stop;
using mapnik::colorizer_stops;
using mapnik::colorizer_mode_enum;
using mapnik::color;

namespace {
void add_stop(raster_colorizer_ptr & rc, colorizer_stop & stop)
{
    rc->add_stop(stop);
}

void add_stop2(raster_colorizer_ptr & rc, float v)
{
    colorizer_stop stop(v, rc->get_default_mode(), rc->get_default_color());
    rc->add_stop(stop);
}

void add_stop3(raster_colorizer_ptr &rc, float v, color c)
{
    colorizer_stop stop(v, rc->get_default_mode(), c);
    rc->add_stop(stop);
}

void add_stop4(raster_colorizer_ptr &rc, float v, colorizer_mode_enum m)
{
    colorizer_stop stop(v, m, rc->get_default_color());
    rc->add_stop(stop);
}

void add_stop5(raster_colorizer_ptr &rc, float v, colorizer_mode_enum m, color c)
{
    colorizer_stop stop(v, m, c);
    rc->add_stop(stop);
}

mapnik::color get_color(raster_colorizer_ptr const&rc, float value)
{
    unsigned rgba = rc->get_color(value);
    unsigned r = (rgba & 0xff);
    unsigned g = (rgba >> 8 ) & 0xff;
    unsigned b = (rgba >> 16) & 0xff;
    unsigned a = (rgba >> 24) & 0xff;
    return mapnik::color(r,g,b,a);
}

colorizer_stops const& get_stops(raster_colorizer_ptr & rc)
{
    return rc->get_stops();
}

}

void export_raster_colorizer(py::module const& m)
{
    py::class_<raster_colorizer,raster_colorizer_ptr>(m, "RasterColorizer",
                                                      "A Raster Colorizer object.")

        .def(py::init<colorizer_mode_enum, color>(),
             py::arg("default_mode"), py::arg("default_color"))
        .def(py::init<>())
        .def_property("default_color",
                      &raster_colorizer::get_default_color,
                      &raster_colorizer::set_default_color,
                      "The default color for stops added without a color (mapnik.Color).\n")
        .def_property("default_mode",
                      &raster_colorizer::get_default_mode_enum,
                      &raster_colorizer::set_default_mode_enum,
                      "The default mode (mapnik.ColorizerMode).\n"
                      "\n"
                      "If a stop is added without a mode, then it will inherit this default mode\n")
        .def_property_readonly("stops",
                      get_stops,
                      "The list of stops this RasterColorizer contains\n")
        .def_property("epsilon",
                      &raster_colorizer::get_epsilon,
                      &raster_colorizer::set_epsilon,
                      "Comparison epsilon value for exact mode\n"
                      "\n"
                      "When comparing values in exact mode, values need only be within epsilon to match.\n")

        .def("add_stop", add_stop,
             "Add a colorizer stop to the raster colorizer.\n"
             "\n"
             "Usage:\n"
             ">>> colorizer = mapnik.RasterColorizer()\n"
             ">>> color = mapnik.Color(\"#0044cc\")\n"
             ">>> stop = mapnik.ColorizerStop(3, mapnik.COLORIZER_INHERIT, color)\n"
             ">>> colorizer.add_stop(stop)\n",
             py::arg("ColorizerStop")
            )
        .def("add_stop", add_stop2,

             "Add a colorizer stop to the raster colorizer, using the default mode and color.\n"
             "\n"
             "Usage:\n"
             ">>> default_color = mapnik.Color(\"#0044cc\")\n"
             ">>> colorizer = mapnik.RasterColorizer(mapnik.COLORIZER_LINEAR, default_color)\n"
             ">>> colorizer.add_stop(100)\n",
             py::arg("value")
            )
        .def("add_stop", add_stop3,
             "Add a colorizer stop to the raster colorizer, using the default mode.\n"
             "\n"
             "Usage:\n"
             ">>> default_color = mapnik.Color(\"#0044cc\")\n"
             ">>> colorizer = mapnik.RasterColorizer(mapnik.COLORIZER_LINEAR, default_color)\n"
             ">>> colorizer.add_stop(100, mapnik.Color(\"#123456\"))\n",
             py::arg("value"), py::arg("color")
            )
        .def("add_stop", add_stop4,
             "Add a colorizer stop to the raster colorizer, using the default color.\n"
             "\n"
             "Usage:\n"
             ">>> default_color = mapnik.Color(\"#0044cc\")\n"
             ">>> colorizer = mapnik.RasterColorizer(mapnik.COLORIZER_LINEAR, default_color)\n"
             ">>> colorizer.add_stop(100, mapnik.COLORIZER_EXACT)\n",
             py::arg("value"), py::arg("ColorizerMode")
            )
        .def("add_stop", add_stop5,
             "Add a colorizer stop to the raster colorizer.\n"
             "\n"
             "Usage:\n"
             ">>> default_color = mapnik.Color(\"#0044cc\")\n"
             ">>> colorizer = mapnik.RasterColorizer(mapnik.COLORIZER_LINEAR, default_color)\n"
             ">>> colorizer.add_stop(100, mapnik.COLORIZER_DISCRETE, mapnik.Color(\"#112233\"))\n",
             py::arg("value"), py::arg("ColorizerMode"), py::arg("color")
            )
        .def("get_color", get_color,
             "Get the color assigned to a certain value in raster data.\n"
             "\n"
             "Usage:\n"
             ">>> colorizer = mapnik.RasterColorizer()\n"
             ">>> color = mapnik.Color(\"#0044cc\")\n"
             ">>> colorizer.add_stop(0, mapnik.COLORIZER_DISCRETE, mapnik.Color(\"#000000\"))\n"
             ">>> colorizer.add_stop(100, mapnik.COLORIZER_DISCRETE, mapnik.Color(\"#0E0A06\"))\n"
             ">>> colorizer.get_color(50)\n"
             "Color('#070503')\n"
            )
        ;



    py::class_<colorizer_stops>(m, "ColorizerStops",
                            "A RasterColorizer's collection of ordered color stops.\n"
                            "This class is not meant to be instantiated from python. However, "
                            "it can be accessed at a RasterColorizer's \"stops\" attribute for "
                            "introspection purposes")
        .def("__iter__", [] (colorizer_stops const& stops) {
            return py::make_iterator(stops.begin(), stops.end());
        })
        ;

    py::enum_<colorizer_mode_enum>(m, "ColorizerMode")
        .value("COLORIZER_INHERIT", colorizer_mode_enum::COLORIZER_INHERIT)
        .value("COLORIZER_LINEAR", colorizer_mode_enum::COLORIZER_LINEAR)
        .value("COLORIZER_DISCRETE", colorizer_mode_enum::COLORIZER_DISCRETE)
        .value("COLORIZER_EXACT", colorizer_mode_enum::COLORIZER_EXACT)
        .export_values()
        ;


    py::class_<colorizer_stop>(m, "ColorizerStop",
                               "A Colorizer Stop object.\n"
                               "Create with a value, ColorizerMode, and Color\n"
                               "\n"
                               "Usage:"
                               ">>> color = mapnik.Color(\"#fff000\")\n"
                               ">>> stop= mapnik.ColorizerStop(42.42, mapnik.COLORIZER_LINEAR, color)\n")
        .def(py::init<float, colorizer_mode_enum, color const&>())
        .def_property("color",
                      &colorizer_stop::get_color,
                      &colorizer_stop::set_color,
                      "The stop color (mapnik.Color).\n")
        .def_property("value",
                      &colorizer_stop::get_value,
                      &colorizer_stop::set_value,
                      "The stop value.\n")
        .def_property("label",
                      &colorizer_stop::get_label,
                      &colorizer_stop::set_label,
                      "The stop label.\n")
        .def_property("mode",
                      &colorizer_stop::get_mode_enum,
                      &colorizer_stop::set_mode_enum,
                      "The stop mode (mapnik.ColorizerMode).\n"
                      "\n"
                      "If this is COLORIZER_INHERIT then it will inherit the default mode\n"
                      " from the RasterColorizer it is added to.\n")
        .def(py::self == py::self)
        .def("__str__", &colorizer_stop::to_string)
        ;
}
