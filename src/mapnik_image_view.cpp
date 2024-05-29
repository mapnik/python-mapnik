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
#include <mapnik/image.hpp>
#include <mapnik/image_view.hpp>
#include <mapnik/image_view_any.hpp>
#include <mapnik/image_util.hpp>
#include <mapnik/palette.hpp>
#include <mapnik/util/variant.hpp>
//stl
#include <sstream>
//pybind11
#include <pybind11/pybind11.h>
#include <pybind11/operators.h>

using mapnik::image_view_any;
using mapnik::save_to_file;

namespace py = pybind11;

// output 'raw' pixels
py::object view_tostring1(image_view_any const& view)
{
    std::ostringstream ss(std::ios::out|std::ios::binary);
    mapnik::view_to_stream(view, ss);
    return py::bytes(ss.str().c_str(), ss.str().size());
}

// encode (png,jpeg)
py::object view_tostring2(image_view_any const & view, std::string const& format)
{
    std::string s = save_to_string(view, format);
    return py::bytes(s.data(), s.length());
}

py::object view_tostring3(image_view_any const & view, std::string const& format, mapnik::rgba_palette const& pal)
{
    std::string s = save_to_string(view, format, pal);
    return py::bytes(s.data(), s.length());
}

bool is_solid(image_view_any const& view)
{
    return mapnik::is_solid(view);
}

void save_view1(image_view_any const& view,
                std::string const& filename)
{
    save_to_file(view,filename);
}

void save_view2(image_view_any const& view,
                std::string const& filename,
                std::string const& type)
{
    save_to_file(view,filename,type);
}

void save_view3(image_view_any const& view,
                std::string const& filename,
                std::string const& type,
                mapnik::rgba_palette const& pal)
{
    save_to_file(view,filename,type,pal);
}


void export_image_view(py::module const& m)
{
    py::class_<image_view_any>(m, "ImageView", "A view into an image.")
        .def("width",&image_view_any::width)
        .def("height",&image_view_any::height)
        .def("is_solid",&is_solid)
        .def("to_string",&view_tostring1)
        .def("to_string",&view_tostring2)
        .def("to_string",&view_tostring3)
        .def("save",&save_view1)
        .def("save",&save_view2)
        .def("save",&save_view3)
        ;
}
