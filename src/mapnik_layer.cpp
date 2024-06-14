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
#include <mapnik/layer.hpp>
#include <mapnik/datasource.hpp>
#include <mapnik/datasource_cache.hpp>
//pybind11
#include <pybind11/pybind11.h>
#include <pybind11/operators.h>
#include <pybind11/stl.h>
#include <pybind11/stl_bind.h>

namespace py = pybind11;

using mapnik::layer;
using mapnik::parameters;
using mapnik::datasource_cache;

PYBIND11_MAKE_OPAQUE(std::vector<std::string>);

std::vector<std::string> & (mapnik::layer::*set_styles_)() = &mapnik::layer::styles;
std::vector<std::string> const& (mapnik::layer::*get_styles_)() const = &mapnik::layer::styles;

void export_layer(py::module const& m)
{
    py::bind_vector<std::vector<std::string>>(m, "StyleNames", py::module_local());

    py::class_<layer>(m, "Layer", "A Mapnik map layer.")
        .def(py::init<std::string const&, std::string const&>(),
             "Create a Layer with a named string and, optionally, an srs string.\n"
             "\n"
             "The srs can be either a Proj epsg code ('epsg:<code>') or\n"
             "of a Proj literal ('+proj=<literal>').\n"
             "If no srs is specified it will default to 'epsg:4326'\n"
             "\n"
             "Usage:\n"
             ">>> from mapnik import Layer\n"
             ">>> lyr = Layer('My Layer','epsg:4326')\n"
             ">>> lyr\n"
             "<mapnik._mapnik.Layer object at 0x6a270>\n",
             py::arg("name"), py::arg("srs") = mapnik::MAPNIK_GEOGRAPHIC_PROJ
            )

        .def("envelope",&layer::envelope,
             "Return the geographic envelope/bounding box."
             "\n"
             "Determined based on the layer datasource.\n"
             "\n"
             "Usage:\n"
             ">>> from mapnik import Layer\n"
             ">>> lyr = Layer('My Layer','epsg:4326')\n"
             ">>> lyr.envelope()\n"
             "box2d(-1.0,-1.0,0.0,0.0) # default until a datasource is loaded\n"
            )

        .def("visible", &layer::visible,
             "Return True if this layer's data is active and visible at a given scale_denom.\n"
             "\n"
             "Otherwise returns False.\n"
             "Accepts a scale value as an integer or float input.\n"
             "Will return False if:\n"
             "\tscale_denom >= minimum_scale_denominator - 1e-6\n"
             "\tor:\n"
             "\tscale_denom < maximum_scale_denominator + 1e-6\n"
             "\n"
             "Usage:\n"
             ">>> from mapnik import Layer\n"
             ">>> lyr = Layer('My Layer','epsg:4326')\n"
             ">>> lyr.visible(1.0/1000000)\n"
             "True\n"
             ">>> lyr.active = False\n"
             ">>> lyr.visible(1.0/1000000)\n"
             "False\n"
            )

        .def_property("active",
                      &layer::active,
                      &layer::set_active,
                      "Get/Set whether this layer is active and will be rendered (same as status property).\n"
                      "\n"
                      "Usage:\n"
                      ">>> from mapnik import Layer\n"
                      ">>> lyr = Layer('My Layer','epsg:4326')\n"
                      ">>> lyr.active\n"
                      "True # Active by default\n"
                      ">>> lyr.active = False # set False to disable layer rendering\n"
                      ">>> lyr.active\n"
                      "False\n"
            )

        .def_property("status",
                      &layer::active,
                      &layer::set_active,
                      "Get/Set whether this layer is active and will be rendered.\n"
                      "\n"
                      "Usage:\n"
                      ">>> from mapnik import Layer\n"
                      ">>> lyr = Layer('My Layer','epsg:4326')\n"
                      ">>> lyr.status\n"
                      "True # Active by default\n"
                      ">>> lyr.status = False # set False to disable layer rendering\n"
                      ">>> lyr.status\n"
                      "False\n"
            )

        .def_property("clear_label_cache",
                      &layer::clear_label_cache,
                      &layer::set_clear_label_cache,
                      "Get/Set whether to clear the label collision detector cache for this layer during rendering\n"
                      "\n"
                      "Usage:\n"
                      ">>> lyr.clear_label_cache\n"
                      "False # False by default, meaning label positions from other layers will impact placement \n"
                      ">>> lyr.clear_label_cache = True # set to True to clear the label collision detector cache\n"
            )

        .def_property("cache_features",
                      &layer::cache_features,
                      &layer::set_cache_features,
                      "Get/Set whether features should be cached during rendering if used between multiple styles\n"
                      "\n"
                      "Usage:\n"
                      ">>> lyr.cache_features\n"
                      "False # False by default\n"
                      ">>> lyr.cache_features = True # set to True to enable feature caching\n"
            )

        .def_property("datasource",
                      &layer::datasource,
                      &layer::set_datasource,
                      "The datasource attached to this layer.\n"
                      "\n"
                      "Usage:\n"
                      ">>> from mapnik import Layer, Datasource\n"
                      ">>> lyr = Layer('My Layer','epsg:4326')\n"
                      ">>> lyr.datasource = Datasource(type='shape',file='world_borders')\n"
                      ">>> lyr.datasource\n"
                      "<mapnik.Datasource object at 0x65470>\n"
            )

        .def_property("buffer_size",
                      &layer::buffer_size,
                      &layer::set_buffer_size,
                      "Get/Set the size of buffer around layer in pixels.\n"
                      "\n"
                      "Usage:\n"
                      ">>> print(l.buffer_size)\n"
                      "None # None by default\n"
                      ">>> l.buffer_size = 2\n"
                      ">>> l.buffer_size\n"
                      "2\n"
            )

        .def_property("maximum_extent",
                      &layer::maximum_extent,
                      &layer::set_maximum_extent,
                      "The maximum extent of the map.\n"
                      "\n"
                      "Usage:\n"
                      ">>> m.maximum_extent = Box2d(-180,-90,180,90)\n"
            )

        .def_property("maximum_scale_denominator",
                      &layer::maximum_scale_denominator,
                      &layer::set_maximum_scale_denominator,
                      "Get/Set the maximum scale denominator of the layer.\n"
                      "\n"
                      "Usage:\n"
                      ">>> from mapnik import Layer\n"
                      ">>> lyr = Layer('My Layer','epsg:4326')\n"
                      ">>> lyr.maximum_scale_denominator\n"
                      "1.7976931348623157e+308 # default is the numerical maximum\n"
                      ">>> lyr.maximum_scale_denominator = 1.0/1000000\n"
                      ">>> lyr.maximum_scale_denominator\n"
                      "9.9999999999999995e-07\n"
            )

        .def_property("minimum_scale_denominator",
                      &layer::minimum_scale_denominator,
                      &layer::set_minimum_scale_denominator,
                      "Get/Set the minimum scale denominator of the layer.\n"
                      "\n"
                      "Usage:\n"
                      ">>> from mapnik import Layer\n"
                      ">>> lyr = Layer('My Layer','epsg:4326')\n"
                      ">>> lyr.minimum_scale_denominator # default is 0\n"
                      "0.0\n"
                      ">>> lyr.minimum_scale_denominator = 1.0/1000000\n"
                      ">>> lyr.minimum_scale_denominator\n"
                      "9.9999999999999995e-07\n"
            )

        .def_property("name",
                      &layer::name,
                      &layer::set_name,
                      "Get/Set the name of the layer.\n"
                      "\n"
                      "Usage:\n"
                      ">>> from mapnik import Layer\n"
                      ">>> lyr = Layer('My Layer','epsg:4326')\n"
                      ">>> lyr.name\n"
                      "'My Layer'\n"
                      ">>> lyr.name = 'New Name'\n"
                      ">>> lyr.name\n"
                      "'New Name'\n"
            )

        .def_property("queryable",
                      &layer::queryable,
                      &layer::set_queryable,
                      "Get/Set whether this layer is queryable.\n"
                      "\n"
                      "Usage:\n"
                      ">>> from mapnik import layer\n"
                      ">>> lyr = layer('My layer','epsg:4326')\n"
                      ">>> lyr.queryable\n"
                      "False # Not queryable by default\n"
                      ">>> lyr.queryable = True\n"
                      ">>> lyr.queryable\n"
                      "True\n"
            )

        .def_property("srs",
                      &layer::srs,
                      &layer::set_srs,
                      "Get/Set the SRS of the layer.\n"
                      "\n"
                      "Usage:\n"
                      ">>> from mapnik import layer\n"
                      ">>> lyr = layer('My layer','epsg:4326')\n"
                      ">>> lyr.srs\n"
                      "'epsg:4326' # The default srs if not initialized with custom srs\n"
                      ">>> # set to google mercator with Proj literal\n"
                      "... \n"
                      ">>> lyr.srs = 'epsg:3857'\n"
            )

        .def_property("group_by",
                      &layer::group_by,
                      &layer::set_group_by,
                      "Get/Set the optional layer group name.\n"
                      "\n"
                      "More details at https://github.com/mapnik/mapnik/wiki/Grouped-rendering:\n"
            )

        .def_property("styles",
                      get_styles_,
                      set_styles_,
                      "The styles list attached to this layer.\n"
                      "\n"
                      "Usage:\n"
                      ">>> from mapnik import layer\n"
                      ">>> lyr = layer('My layer','epsg:4326')\n"
                      ">>> lyr.styles\n"
                      "<mapnik._mapnik.Names object at 0x6d3e8>\n"
                      ">>> len(lyr.styles)\n"
                      "0\n # no styles until you append them\n"
                      "lyr.styles.append('My Style') # mapnik uses named styles for flexibility\n"
                      ">>> len(lyr.styles)\n"
                      "1\n"
                      ">>> lyr.styles[0]\n"
                      "'My Style'\n"
            )
        // comparison
        .def(py::self == py::self)
        ;
}
