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
#include <mapnik/color.hpp>
#include <mapnik/palette.hpp>
#include <mapnik/image_util.hpp>
#include <mapnik/image_copy.hpp>
#include <mapnik/image_reader.hpp>
#include <mapnik/image_compositing.hpp>
#include <mapnik/image_view_any.hpp>
// cairo
#if defined(HAVE_CAIRO) && defined(HAVE_PYCAIRO)
#include <mapnik/cairo/cairo_context.hpp>
#include <mapnik/cairo/cairo_image_util.hpp>
#if PY_MAJOR_VERSION >= 3
#define PYCAIRO_NO_IMPORT
#include <py3cairo.h>
#else
#include <pycairo.h>
#endif
#include <cairo.h>
#endif
//stl
#include <type_traits>
//pybind11
#include <pybind11/pybind11.h>
#include <pybind11/operators.h>

using mapnik::image_any;
using mapnik::image_reader;
using mapnik::get_image_reader;
using mapnik::type_from_filename;
using mapnik::save_to_file;

namespace py = pybind11;

namespace {
// output 'raw' pixels
py::object to_string1(image_any const& im)
{
    return py::bytes(reinterpret_cast<const char *>(im.bytes()), im.size());
}

// encode (png,jpeg)
py::object to_string2(image_any const & im, std::string const& format)
{
    std::string s = mapnik::save_to_string(im, format);
    return py::bytes(s.data(), s.length());
}

py::object to_string3(image_any const & im, std::string const& format, mapnik::rgba_palette const& pal)
{
    std::string s = mapnik::save_to_string(im, format, pal);
    return py::bytes(s.data(), s.length());
}


void save_to_file1(mapnik::image_any const& im, std::string const& filename)
{
    save_to_file(im,filename);
}

void save_to_file2(mapnik::image_any const& im, std::string const& filename, std::string const& type)
{
    save_to_file(im,filename,type);
}

void save_to_file3(mapnik::image_any const& im, std::string const& filename, std::string const& type, mapnik::rgba_palette const& pal)
{
    save_to_file(im,filename,type,pal);
}

mapnik::image_view_any get_view(mapnik::image_any const& data,unsigned x,unsigned y, unsigned w,unsigned h)
{
    return mapnik::create_view(data,x,y,w,h);
}

bool is_solid(mapnik::image_any const& im)
{
    return mapnik::is_solid(im);
}

void fill_color(mapnik::image_any & im, mapnik::color const& c)
{
    mapnik::fill(im, c);
}

void fill_int(mapnik::image_any & im, int val)
{
    mapnik::fill(im, val);
}

void fill_double(mapnik::image_any & im, double val)
{
    mapnik::fill(im, val);
}

std::shared_ptr<image_any> copy(mapnik::image_any const& im, mapnik::image_dtype type, double offset, double scaling)
{
    return std::make_shared<image_any>(mapnik::image_copy(im, type, offset, scaling));
}

std::size_t compare(mapnik::image_any const& im1, mapnik::image_any const& im2, double threshold, bool alpha)
{
    return mapnik::compare(im1, im2, threshold, alpha);
}

struct get_pixel_visitor
{
    get_pixel_visitor(unsigned x, unsigned y)
        : x_(x), y_(y) {}

    py::object operator() (mapnik::image_null const&)
    {
        throw std::runtime_error("Can not return a null image from a pixel (shouldn't have reached here)");
    }

    template <typename T>
    py::object operator() (T const& im)
    {
        using pixel_type = typename T::pixel_type;
        using python_type = std::conditional<std::is_integral<pixel_type>::value, py::int_, py::float_>::type;
        return python_type(mapnik::get_pixel<pixel_type>(im, x_, y_));
    }
  private:
    unsigned x_;
    unsigned y_;
};

py::object get_pixel(mapnik::image_any const& im, int x, int y)
{
    if (x < 0 || x >= static_cast<int>(im.width()) ||
        y < 0 || y >= static_cast<int>(im.height()))
    {
        throw std::out_of_range("invalid x,y for image dimensions");
    }
    return mapnik::util::apply_visitor(get_pixel_visitor(x, y), im);
}

mapnik::color get_pixel_color(mapnik::image_any const& im, int x, int y)
{
    if (x < 0 || x >= static_cast<int>(im.width()) ||
        y < 0 || y >= static_cast<int>(im.height()))
    {
        throw std::out_of_range("invalid x,y for image dimensions");
    }
    return mapnik::get_pixel<mapnik::color>(im, x, y);
}

template <typename T>
void set_pixel(mapnik::image_any & im, int x, int y, T c)
{
    if (x < 0 || x >= static_cast<int>(im.width()) ||
        y < 0 || y >= static_cast<int>(im.height()))
    {
        throw std::out_of_range("invalid x,y for image dimensions");
    }
    mapnik::set_pixel(im, x, y, c);
}

mapnik::image_dtype get_type(mapnik::image_any & im)
{
    return im.get_dtype();
}

std::shared_ptr<image_any> open_from_file(std::string const& filename)
{
    boost::optional<std::string> type = type_from_filename(filename);
    if (type)
    {
        std::unique_ptr<image_reader> reader(get_image_reader(filename,*type));
        if (reader.get())
        {
            return std::make_shared<image_any>(reader->read(0,0,reader->width(),reader->height()));
        }
        throw mapnik::image_reader_exception("Failed to load: " + filename);
    }
    throw mapnik::image_reader_exception("Unsupported image format:" + filename);
}

std::shared_ptr<image_any> from_string(std::string const& str)
{
    std::unique_ptr<image_reader> reader(get_image_reader(str.c_str(),str.size()));
    if (reader.get())
    {
        return std::make_shared<image_any>(reader->read(0,0,reader->width(), reader->height()));
    }
    throw mapnik::image_reader_exception("Failed to load image from String" );
}

std::shared_ptr<image_any> from_buffer(py::bytes const& obj)
{
    std::string_view view = std::string_view(obj);
    std::unique_ptr<image_reader> reader
        (get_image_reader(reinterpret_cast<char const*>(view.data()), view.length()));
    if (reader.get())
    {
        return std::make_shared<image_any>(reader->read(0, 0, reader->width(), reader->height()));
    }
    throw mapnik::image_reader_exception("Failed to load image from Buffer" );
}

std::shared_ptr<image_any> from_memoryview(py::memoryview const& memview)
{
    auto buf = py::buffer(memview);
    py::buffer_info info = buf.request();
    std::unique_ptr<image_reader> reader
        (get_image_reader(reinterpret_cast<char const*>(info.ptr), info.size));
    if (reader.get())
    {
        return std::make_shared<image_any>(reader->read(0, 0, reader->width(), reader->height()));
    }
    throw mapnik::image_reader_exception("Failed to load image from Buffer" );
}

void set_grayscale_to_alpha(image_any & im)
{
    mapnik::set_grayscale_to_alpha(im);
}

void set_grayscale_to_alpha_c(image_any & im, mapnik::color const& c)
{
    mapnik::set_grayscale_to_alpha(im, c);
}

void set_color_to_alpha(image_any & im, mapnik::color const& c)
{
    mapnik::set_color_to_alpha(im, c);
}

void apply_opacity(image_any & im, float opacity)
{
    mapnik::apply_opacity(im, opacity);
}

bool premultiplied(image_any &im)
{
    return im.get_premultiplied();
}

bool premultiply(image_any & im)
{
    return mapnik::premultiply_alpha(im);
}

bool demultiply(image_any & im)
{
    return mapnik::demultiply_alpha(im);
}

void clear(image_any & im)
{
    mapnik::fill(im, 0);
}

void composite(image_any & dst, image_any & src, mapnik::composite_mode_e mode, float opacity, int dx, int dy)
{
    bool demultiply_dst = mapnik::premultiply_alpha(dst);
    bool demultiply_src = mapnik::premultiply_alpha(src);
    mapnik::composite(dst,src,mode,opacity,dx,dy);
    if (demultiply_dst)
    {
        mapnik::demultiply_alpha(dst);
    }
    if (demultiply_src)
    {
        mapnik::demultiply_alpha(src);
    }
}

#if defined(HAVE_CAIRO) && defined(HAVE_PYCAIRO)
std::shared_ptr<image_any> from_cairo(PycairoSurface* py_surface)
{
    mapnik::cairo_surface_ptr surface(cairo_surface_reference(py_surface->surface), mapnik::cairo_surface_closer());
    mapnik::image_rgba8 image = mapnik::image_rgba8(cairo_image_surface_get_width(&*surface), cairo_image_surface_get_height(&*surface));
    cairo_image_to_rgba8(image, surface);
    return std::make_shared<image_any>(std::move(image));
}
#endif

} // namespace

void export_image(py::module const& m)
{
    py::enum_<mapnik::image_dtype>(m, "ImageType")
        .value("rgba8", mapnik::image_dtype_rgba8)
        .value("gray8", mapnik::image_dtype_gray8)
        .value("gray8s", mapnik::image_dtype_gray8s)
        .value("gray16", mapnik::image_dtype_gray16)
        .value("gray16s", mapnik::image_dtype_gray16s)
        .value("gray32", mapnik::image_dtype_gray32)
        .value("gray32s", mapnik::image_dtype_gray32s)
        .value("gray32f", mapnik::image_dtype_gray32f)
        .value("gray64", mapnik::image_dtype_gray64)
        .value("gray64s", mapnik::image_dtype_gray64s)
        .value("gray64f", mapnik::image_dtype_gray64f)
        ;

    py::class_<image_any,std::shared_ptr<image_any>>(m, "Image","This class represents a image.")
        .def(py::init<int,int>())
        .def(py::init<int,int,mapnik::image_dtype>())
        .def(py::init<int,int,mapnik::image_dtype,bool>())
        .def(py::init<int,int,mapnik::image_dtype,bool,bool>())
        .def(py::init<int,int,mapnik::image_dtype,bool,bool,bool>())
        .def("width",&image_any::width)
        .def("height",&image_any::height)
        .def("view",&get_view)
        .def("painted",&image_any::painted)
        .def("is_solid",&is_solid)
        .def("fill",&fill_color)
        .def("fill",&fill_int)
        .def("fill",&fill_double)
        .def("set_grayscale_to_alpha",&set_grayscale_to_alpha, "Set the grayscale values to the alpha channel of the Image")
        .def("set_grayscale_to_alpha",&set_grayscale_to_alpha_c, "Set the grayscale values to the alpha channel of the Image")
        .def("set_color_to_alpha",&set_color_to_alpha, "Set a given color to the alpha channel of the Image")
        .def("apply_opacity",&apply_opacity, "Set the opacity of the Image relative to the current alpha of each pixel.")
        .def("composite",&composite,
             py::arg("image"),
             py::arg("mode") = mapnik::src_over,
             py::arg("opacity") = 1.0f,
             py::arg("dx") = 0,
             py::arg("dy") = 0
            )
        .def("compare",&compare,
             py::arg("image"),
             py::arg("threshold")=0.0,
             py::arg("alpha")=true
            )
        .def("copy",&copy,
             py::arg("type"),
             py::arg("offset")=0.0,
             py::arg("scaling")=1.0
            )
        .def_property("offset",
                      &image_any::get_offset,
                      &image_any::set_offset,
                      "Gets or sets the offset component.\n")
        .def_property("scaling",
                      &image_any::get_scaling,
                      &image_any::set_scaling,
                      "Gets or sets the offset component.\n")
        .def("premultiplied",&premultiplied)
        .def("premultiply",&premultiply)
        .def("demultiply",&demultiply)
        .def("set_pixel",&set_pixel<mapnik::color>)
        .def("set_pixel",&set_pixel<double>)
        .def("set_pixel",&set_pixel<int>)
        .def("get_pixel_color",&get_pixel_color,
             py::arg("x"), py::arg("y"))
        .def("get_pixel", &get_pixel)
        .def("get_type",&get_type)
        .def("clear",&clear)
        .def("to_string",&to_string1)
        .def("to_string",&to_string2)
        .def("to_string",&to_string3)
        .def("save", &save_to_file1)
        .def("save", &save_to_file2)
        .def("save", &save_to_file3)
        .def_static("open",open_from_file)
        .def_static("from_buffer",&from_buffer)
        .def_static("from_memoryview",&from_memoryview)
        .def_static("from_string",&from_string)
#if defined(HAVE_CAIRO) && defined(HAVE_PYCAIRO)
        .def_static("from_cairo",&from_cairo)
#endif
        ;

}
