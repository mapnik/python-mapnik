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
#include <mapnik/version.hpp>
#include <mapnik/map.hpp>
#include <mapnik/load_map.hpp>
#include <mapnik/save_map.hpp>
#include <mapnik/datasource.hpp>
#include <mapnik/layer.hpp>
#include <mapnik/agg_renderer.hpp>
#include <mapnik/image_any.hpp>
#include <mapnik/value.hpp>
#include <mapnik/value/error.hpp>
#include <mapnik/label_collision_detector.hpp>
#include "mapnik_value_converter.hpp"
#include "python_to_value.hpp"

#if defined(GRID_RENDERER)
#include "python_grid_utils.hpp"
#endif
#if defined(SHAPE_MEMORY_MAPPED_FILE)
#include <mapnik/mapped_memory_cache.hpp>
#endif
#if defined(SVG_RENDERER)
#include <mapnik/svg/output/svg_renderer.hpp>
#endif
#if defined(HAVE_CAIRO)
#include <mapnik/cairo_io.hpp>
#include <mapnik/cairo/cairo_renderer.hpp>
#include <cairo.h>
#endif

//stl
#include <stdexcept>
#include <fstream>

//pybind11
#include <pybind11/pybind11.h>

namespace py = pybind11;

namespace {
void clear_cache()
{
    mapnik::marker_cache::instance().clear();
#if defined(SHAPE_MEMORY_MAPPED_FILE)
    mapnik::mapped_memory_cache::instance().clear();
#endif
}

struct agg_renderer_visitor_1
{
    agg_renderer_visitor_1(mapnik::Map const& m, double scale_factor, unsigned offset_x, unsigned offset_y)
        : m_(m), scale_factor_(scale_factor), offset_x_(offset_x), offset_y_(offset_y) {}

    template <typename T>
    void operator() (T & pixmap)
    {
        throw std::runtime_error("This image type is not currently supported for rendering.");
    }

  private:
    mapnik::Map const& m_;
    double scale_factor_;
    unsigned offset_x_;
    unsigned offset_y_;
};

template <>
void agg_renderer_visitor_1::operator()<mapnik::image_rgba8> (mapnik::image_rgba8 & pixmap)
{
    mapnik::agg_renderer<mapnik::image_rgba8> ren(m_,pixmap,scale_factor_,offset_x_, offset_y_);
    ren.apply();
}

struct agg_renderer_visitor_2
{
    agg_renderer_visitor_2(mapnik::Map const &m, std::shared_ptr<mapnik::label_collision_detector4> detector,
                 double scale_factor, unsigned offset_x, unsigned offset_y)
        : m_(m), detector_(detector), scale_factor_(scale_factor), offset_x_(offset_x), offset_y_(offset_y) {}

    template <typename T>
    void operator() (T & pixmap)
    {
        throw std::runtime_error("This image type is not currently supported for rendering.");
    }

  private:
    mapnik::Map const& m_;
    std::shared_ptr<mapnik::label_collision_detector4> detector_;
    double scale_factor_;
    unsigned offset_x_;
    unsigned offset_y_;
};

template <>
void agg_renderer_visitor_2::operator()<mapnik::image_rgba8> (mapnik::image_rgba8 & pixmap)
{
    mapnik::agg_renderer<mapnik::image_rgba8> ren(m_,pixmap,detector_, scale_factor_,offset_x_, offset_y_);
    ren.apply();
}

struct agg_renderer_visitor_3
{
    agg_renderer_visitor_3(mapnik::Map const& m, mapnik::request const& req, mapnik::attributes const& vars,
                 double scale_factor, unsigned offset_x, unsigned offset_y)
        : m_(m), req_(req), vars_(vars), scale_factor_(scale_factor), offset_x_(offset_x), offset_y_(offset_y) {}

    template <typename T>
    void operator() (T & pixmap)
    {
        throw std::runtime_error("This image type is not currently supported for rendering.");
    }

  private:
    mapnik::Map const& m_;
    mapnik::request const& req_;
    mapnik::attributes const& vars_;
    double scale_factor_;
    unsigned offset_x_;
    unsigned offset_y_;

};

template <>
void agg_renderer_visitor_3::operator()<mapnik::image_rgba8> (mapnik::image_rgba8 & pixmap)
{
    mapnik::agg_renderer<mapnik::image_rgba8> ren(m_,req_, vars_, pixmap, scale_factor_, offset_x_, offset_y_);
    ren.apply();
}

struct agg_renderer_visitor_4
{
    agg_renderer_visitor_4(mapnik::Map const& m, double scale_factor, unsigned offset_x, unsigned offset_y,
                 mapnik::layer const& layer, std::set<std::string>& names)
        : m_(m), scale_factor_(scale_factor), offset_x_(offset_x), offset_y_(offset_y),
          layer_(layer), names_(names) {}

    template <typename T>
    void operator() (T & pixmap)
    {
        throw std::runtime_error("This image type is not currently supported for rendering.");
    }

  private:
    mapnik::Map const& m_;
    double scale_factor_;
    unsigned offset_x_;
    unsigned offset_y_;
    mapnik::layer const& layer_;
    std::set<std::string> & names_;
};

template <>
void agg_renderer_visitor_4::operator()<mapnik::image_rgba8> (mapnik::image_rgba8 & pixmap)
{
    mapnik::agg_renderer<mapnik::image_rgba8> ren(m_,pixmap,scale_factor_,offset_x_, offset_y_);
    ren.apply(layer_, names_);
}


void render(mapnik::Map const& map,
            mapnik::image_any& image,
            double scale_factor = 1.0,
            unsigned offset_x = 0u,
            unsigned offset_y = 0u)
{
    py::gil_scoped_release release;
    mapnik::util::apply_visitor(agg_renderer_visitor_1(map, scale_factor, offset_x, offset_y), image);
}

void render_with_vars(mapnik::Map const& map,
            mapnik::image_any& image,
            py::dict const& d,
            double scale_factor = 1.0,
            unsigned offset_x = 0u,
            unsigned offset_y = 0u)
{
    mapnik::attributes vars = mapnik::dict2attr(d);
    mapnik::request req(map.width(),map.height(),map.get_current_extent());
    req.set_buffer_size(map.buffer_size());
    py::gil_scoped_release release;
    mapnik::util::apply_visitor(agg_renderer_visitor_3(map, req, vars, scale_factor, offset_x, offset_y), image);
}

void render_with_detector(
    mapnik::Map const& map,
    mapnik::image_any &image,
    std::shared_ptr<mapnik::label_collision_detector4> detector,
    double scale_factor = 1.0,
    unsigned offset_x = 0u,
    unsigned offset_y = 0u)
{
    py::gil_scoped_release release;
    mapnik::util::apply_visitor(agg_renderer_visitor_2(map, detector, scale_factor, offset_x, offset_y), image);
}

void render_layer2(mapnik::Map const& map,
                   mapnik::image_any& image,
                   unsigned layer_idx,
                   double scale_factor,
                   unsigned offset_x,
                   unsigned offset_y)
{
    std::vector<mapnik::layer> const& layers = map.layers();
    std::size_t layer_num = layers.size();
    if (layer_idx >= layer_num) {
        std::ostringstream s;
        s << "Zero-based layer index '" << layer_idx << "' not valid, only '"
          << layer_num << "' layers are in map\n";
        throw std::runtime_error(s.str());
    }

    py::gil_scoped_release release;
    mapnik::layer const& layer = layers[layer_idx];
    std::set<std::string> names;
    mapnik::util::apply_visitor(agg_renderer_visitor_4(map, scale_factor, offset_x, offset_y, layer, names), image);
}

#if defined(HAVE_CAIRO) && defined(HAVE_PYCAIRO)

void render3(mapnik::Map const& map,
             PycairoSurface* py_surface,
             double scale_factor = 1.0,
             unsigned offset_x = 0,
             unsigned offset_y = 0)
{
    py::gil_scoped_release release;
    mapnik::cairo_surface_ptr surface(cairo_surface_reference(py_surface->surface), mapnik::cairo_surface_closer());
    mapnik::cairo_renderer<mapnik::cairo_ptr> ren(map,mapnik::create_context(surface),scale_factor,offset_x,offset_y);
    ren.apply();
}

void render4(mapnik::Map const& map, PycairoSurface* py_surface)
{
    py::gil_scoped_release release;
    mapnik::cairo_surface_ptr surface(cairo_surface_reference(py_surface->surface), mapnik::cairo_surface_closer());
    mapnik::cairo_renderer<mapnik::cairo_ptr> ren(map,mapnik::create_context(surface));
    ren.apply();
}

void render5(mapnik::Map const& map,
             PycairoContext* py_context,
             double scale_factor = 1.0,
             unsigned offset_x = 0,
             unsigned offset_y = 0)
{
    py::gil_scoped_release release;
    mapnik::cairo_ptr context(cairo_reference(py_context->ctx), mapnik::cairo_closer());
    mapnik::cairo_renderer<mapnik::cairo_ptr> ren(map,context,scale_factor,offset_x, offset_y);
    ren.apply();
}

void render6(mapnik::Map const& map, PycairoContext* py_context)
{
    py::gil_scoped_release release;
    mapnik::cairo_ptr context(cairo_reference(py_context->ctx), mapnik::cairo_closer());
    mapnik::cairo_renderer<mapnik::cairo_ptr> ren(map,context);
    ren.apply();
}
void render_with_detector2(
    mapnik::Map const& map,
    PycairoContext* py_context,
    std::shared_ptr<mapnik::label_collision_detector4> detector)
{
    py::gil_scoped_release release;
    mapnik::cairo_ptr context(cairo_reference(py_context->ctx), mapnik::cairo_closer());
    mapnik::cairo_renderer<mapnik::cairo_ptr> ren(map,context,detector);
    ren.apply();
}

void render_with_detector3(
    mapnik::Map const& map,
    PycairoContext* py_context,
    std::shared_ptr<mapnik::label_collision_detector4> detector,
    double scale_factor = 1.0,
    unsigned offset_x = 0u,
    unsigned offset_y = 0u)
{
    py::gil_scoped_release release;
    mapnik::cairo_ptr context(cairo_reference(py_context->ctx), mapnik::cairo_closer());
    mapnik::cairo_renderer<mapnik::cairo_ptr> ren(map,context,detector,scale_factor,offset_x,offset_y);
    ren.apply();
}

void render_with_detector4(
    mapnik::Map const& map,
    PycairoSurface* py_surface,
    std::shared_ptr<mapnik::label_collision_detector4> detector)
{
    py::gil_scoped_release release;
    mapnik::cairo_surface_ptr surface(cairo_surface_reference(py_surface->surface), mapnik::cairo_surface_closer());
    mapnik::cairo_renderer<mapnik::cairo_ptr> ren(map, mapnik::create_context(surface), detector);
    ren.apply();
}

void render_with_detector5(
    mapnik::Map const& map,
    PycairoSurface* py_surface,
    std::shared_ptr<mapnik::label_collision_detector4> detector,
    double scale_factor = 1.0,
    unsigned offset_x = 0u,
    unsigned offset_y = 0u)
{
    py::gil_scoped_release release;
    mapnik::cairo_surface_ptr surface(cairo_surface_reference(py_surface->surface), mapnik::cairo_surface_closer());
    mapnik::cairo_renderer<mapnik::cairo_ptr> ren(map, mapnik::create_context(surface), detector, scale_factor, offset_x, offset_y);
    ren.apply();
}

#endif


void render_tile_to_file(mapnik::Map const& map,
                         unsigned offset_x, unsigned offset_y,
                         unsigned width, unsigned height,
                         std::string const& file,
                         std::string const& format)
{
    mapnik::image_any image(width,height);
    render(map,image,1.0,offset_x, offset_y);
    mapnik::save_to_file(image,file,format);
}

void render_to_file1(mapnik::Map const& map,
                     std::string const& filename,
                     std::string const& format)
{
    if (format == "svg-ng")
    {
#if defined(SVG_RENDERER)
        std::ofstream file (filename.c_str(), std::ios::out|std::ios::trunc|std::ios::binary);
        if (!file)
        {
            throw mapnik::image_writer_exception("could not open file for writing: " + filename);
        }
        using iter_type = std::ostream_iterator<char>;
        iter_type output_stream_iterator(file);
        mapnik::svg_renderer<iter_type> ren(map,output_stream_iterator);
        ren.apply();
#else
        throw mapnik::image_writer_exception("SVG backend not available, cannot write to format: " + format);
#endif
    }
    else if (format == "pdf" || format == "svg" || format =="ps" || format == "ARGB32" || format == "RGB24")
    {
#if defined(HAVE_CAIRO)
        mapnik::save_to_cairo_file(map,filename,format,1.0);
#else
        throw mapnik::image_writer_exception("Cairo backend not available, cannot write to format: " + format);
#endif
    }
    else
    {
        mapnik::image_any image(map.width(),map.height());
        render(map,image,1.0,0,0);
        mapnik::save_to_file(image,filename,format);
    }
}

void render_to_file2(mapnik::Map const& map,std::string const& filename)
{
    std::string format = mapnik::guess_type(filename);
    if (format == "pdf" || format == "svg" || format =="ps")
    {
#if defined(HAVE_CAIRO)
        mapnik::save_to_cairo_file(map,filename,format,1.0);
#else
        throw mapnik::image_writer_exception("Cairo backend not available, cannot write to format: " + format);
#endif
    }
    else
    {
        mapnik::image_any image(map.width(),map.height());
        render(map,image,1.0,0,0);
        mapnik::save_to_file(image,filename);
    }
}

void render_to_file3(mapnik::Map const& map,
                     std::string const& filename,
                     std::string const& format,
                     double scale_factor = 1.0)
{
    if (format == "svg-ng")
    {
#if defined(SVG_RENDERER)
        std::ofstream file (filename.c_str(), std::ios::out|std::ios::trunc|std::ios::binary);
        if (!file)
        {
            throw mapnik::image_writer_exception("could not open file for writing: " + filename);
        }
        using iter_type = std::ostream_iterator<char>;
        iter_type output_stream_iterator(file);
        mapnik::svg_renderer<iter_type> ren(map,output_stream_iterator,scale_factor);
        ren.apply();
#else
        throw mapnik::image_writer_exception("SVG backend not available, cannot write to format: " + format);
#endif
    }
    else if (format == "pdf" || format == "svg" || format =="ps" || format == "ARGB32" || format == "RGB24")
    {
#if defined(HAVE_CAIRO)
        mapnik::save_to_cairo_file(map,filename,format,scale_factor);
#else
        throw mapnik::image_writer_exception("Cairo backend not available, cannot write to format: " + format);
#endif
    }
    else
    {
        mapnik::image_any image(map.width(),map.height());
        render(map,image,scale_factor,0,0);
        mapnik::save_to_file(image,filename,format);
    }
}

// indicator for pycairo support in the python bindings
bool has_pycairo()
{
#if defined(HAVE_CAIRO) && defined(HAVE_PYCAIRO)
#if PY_MAJOR_VERSION >= 3
    Pycairo_CAPI = (Pycairo_CAPI_t*) PyCapsule_Import(const_cast<char *>("cairo.CAPI"), 0);
#else
    Pycairo_CAPI = (Pycairo_CAPI_t*) PyCObject_Import(const_cast<char *>("cairo"), const_cast<char *>("CAPI"));
#endif
    if (Pycairo_CAPI == nullptr){
        /*
          Case where pycairo support has been compiled into
          mapnik but at runtime the cairo python module
          is unable to be imported and therefore Pycairo surfaces
          and contexts cannot be passed to mapnik.render()
        */
        return false;
    }
    return true;
#else
    return false;
#endif
}


unsigned mapnik_version()
{
    return MAPNIK_VERSION;
}

std::string mapnik_version_string()
{
    return MAPNIK_VERSION_STRING;
}

bool has_proj()
{
#if defined(MAPNIK_USE_PROJ)
    return true;
#else
    return false;
#endif
}

bool has_svg_renderer()
{
#if defined(SVG_RENDERER)
    return true;
#else
    return false;
#endif
}

bool has_grid_renderer()
{
#if defined(GRID_RENDERER)
    return true;
#else
    return false;
#endif
}

constexpr bool has_jpeg()
{
#if defined(HAVE_JPEG)
    return true;
#else
    return false;
#endif
}

constexpr bool has_png()
{
#if defined(HAVE_PNG)
    return true;
#else
    return false;
#endif
}

bool has_tiff()
{
#if defined(HAVE_TIFF)
    return true;
#else
    return false;
#endif
}

bool has_webp()
{
#if defined(HAVE_WEBP)
    return true;
#else
     return false;
 #endif
}

// indicator for cairo rendering support inside libmapnik
bool has_cairo()
{
#if defined(HAVE_CAIRO)
    return true;
#else
    return false;
#endif
}

} // namespace


void export_color(py::module const&);
void export_composite_modes(py::module const&);
void export_coord(py::module const&);
void export_envelope(py::module const&);
void export_gamma_method(py::module const&);
void export_geometry(py::module const&);
void export_feature(py::module const&);
void export_featureset(py::module const&);
void export_font_engine(py::module const&);
void export_fontset(py::module const&);
void export_expression(py::module const&);
void export_datasource(py::module&); // non-const because of m.def(..)
void export_datasource_cache(py::module const&);
#if defined(GRID_RENDERER)
void export_grid(py::module const&);
void export_grid_view(py::module const&);
#endif
void export_image(py::module const&);
void export_image_view(py::module const&);
void export_layer(py::module const&);
void export_map(py::module const&);
void export_projection(py::module&); // non-const because of m.def(..)
void export_proj_transform(py::module const&);
void export_query(py::module const&);
void export_rule(py::module const&);
void export_symbolizer(py::module const&);
void export_polygon_symbolizer(py::module const&);
void export_line_symbolizer(py::module const&);
void export_point_symbolizer(py::module const&);
void export_style(py::module const&);
void export_logger(py::module const&);
void export_placement_finder(py::module const&);
void export_text_symbolizer(py::module const&);
void export_debug_symbolizer(py::module const&);
void export_markers_symbolizer(py::module const&);
void export_polygon_pattern_symbolizer(py::module const&);
void export_line_pattern_symbolizer(py::module const&);
void export_raster_symbolizer(py::module const&);
void export_palette(py::module const&);
void export_parameters(py::module const&);
void export_raster_colorizer(py::module const&);
void export_scaling_method(py::module const&);
void export_label_collision_detector(py::module const& m);
void export_dot_symbolizer(py::module const&);
void export_shield_symbolizer(py::module const&);
void export_group_symbolizer(py::module const&);
void export_building_symbolizer(py::module const&);

using mapnik::load_map;
using mapnik::load_map_string;
using mapnik::save_map;
using mapnik::save_map_to_string;


PYBIND11_MODULE(_mapnik, m) {
    export_color(m);
    export_composite_modes(m);
    export_coord(m);
    export_envelope(m);
    export_geometry(m);
    export_gamma_method(m);
    export_feature(m);
    export_featureset(m);
    export_font_engine(m);
    export_fontset(m);
    export_expression(m);
    export_datasource(m);
    export_datasource_cache(m);
#if defined(GRID_RENDERER)
    export_grid(m);
    export_grid_view(m);
#endif
    export_image(m);
    export_image_view(m);
    export_layer(m);
    export_map(m);
    export_projection(m);
    export_proj_transform(m);
    export_query(m);
    export_rule(m);
    export_symbolizer(m);
    export_polygon_symbolizer(m);
    export_line_symbolizer(m);
    export_point_symbolizer(m);
    export_style(m);
    export_logger(m);
    export_placement_finder(m);
    export_text_symbolizer(m);
    export_palette(m);
    export_parameters(m);
    export_debug_symbolizer(m);
    export_markers_symbolizer(m);
    export_polygon_pattern_symbolizer(m);
    export_line_pattern_symbolizer(m);
    export_raster_symbolizer(m);
    export_raster_colorizer(m);
    export_scaling_method(m);
    export_label_collision_detector(m);
    export_dot_symbolizer(m);
    export_shield_symbolizer(m);
    export_group_symbolizer(m);
    export_building_symbolizer(m);
    // exceptions
    py::register_exception<mapnik::value_error>(m, "PyExc_MapnikValueError", PyExc_ValueError);
    //
    m.def("version", &mapnik_version,"Get the Mapnik version number");
    m.def("version_string", &mapnik_version_string,"Get the Mapnik version string");
    m.def("has_proj", &has_proj, "Get proj status");
    m.def("has_jpeg", &has_jpeg, "Get jpeg read/write support status");
    m.def("has_png", &has_png, "Get png read/write support status");
    m.def("has_tiff", &has_tiff, "Get tiff read/write support status");
    m.def("has_webp", &has_webp, "Get webp read/write support status");
    m.def("has_svg_renderer", &has_svg_renderer, "Get svg_renderer status");
    m.def("has_grid_renderer", &has_grid_renderer, "Get grid_renderer status");
    m.def("has_cairo", &has_cairo, "Get cairo library status");

    m.def("load_map", &load_map,
          py::arg("Map"),
          py::arg("filename"),
          py::arg("strict")=false,
          py::arg("base_path") = "" );

    m.def("load_map_from_string", &load_map_string,
          py::arg("Map"),
          py::arg("str"),
          py::arg("strict")=false,
          py::arg("base_path") = "" );

    // render
    m.def("render", &render,
          py::arg("Map"),
          py::arg("image"),
          py::arg("scale_factor") = 1.0,
          py::arg("offset_x") = 0,
          py::arg("offset_y") = 0);

    m.def("render_with_vars", &render_with_vars,
          py::arg("Map"),
          py::arg("image"),
          py::arg("vars"),
          py::arg("scale_factor") = 1.0,
          py::arg("offset_x") = 0,
          py::arg("offset_y") = 0);

    m.def("render_with_detector", &render_with_detector,
          py::arg("Map"),
          py::arg("image"),
          py::arg("detector"),
          py::arg("scale_factor") = 1.0,
          py::arg("offset_x") = 0,
          py::arg("offset_y") = 0);

#if defined(HAVE_CAIRO) && defined(HAVE_PYCAIRO)
    m.def("render",&render3,
        "\n"
        "Render Map to Cairo Surface using offsets\n"
        "\n"
        "Usage:\n"
        ">>> from mapnik import Map, render, load_map\n"
        ">>> from cairo import SVGSurface\n"
        ">>> m = Map(256,256)\n"
        ">>> load_map(m,'mapfile.xml')\n"
        ">>> surface = SVGSurface('image.svg', m.width, m.height)\n"
        ">>> render(m,surface,1,1)\n"
        "\n"
        );

    m.def("render",&render4,
        "\n"
        "Render Map to Cairo Surface\n"
        "\n"
        "Usage:\n"
        ">>> from mapnik import Map, render, load_map\n"
        ">>> from cairo import SVGSurface\n"
        ">>> m = Map(256,256)\n"
        ">>> load_map(m,'mapfile.xml')\n"
        ">>> surface = SVGSurface('image.svg', m.width, m.height)\n"
        ">>> render(m,surface)\n"
        "\n"
        );

    m.def("render",&render5,
        "\n"
        "Render Map to Cairo Context using offsets\n"
        "\n"
        "Usage:\n"
        ">>> from mapnik import Map, render, load_map\n"
        ">>> from cairo import SVGSurface, Context\n"
        ">>> surface = SVGSurface('image.svg', m.width, m.height)\n"
        ">>> ctx = Context(surface)\n"
        ">>> load_map(m,'mapfile.xml')\n"
        ">>> render(m,context,1,1)\n"
        "\n"
        );

    m.def("render",&render6,
        "\n"
        "Render Map to Cairo Context\n"
        "\n"
        "Usage:\n"
        ">>> from mapnik import Map, render, load_map\n"
        ">>> from cairo import SVGSurface, Context\n"
        ">>> surface = SVGSurface('image.svg', m.width, m.height)\n"
        ">>> ctx = Context(surface)\n"
        ">>> load_map(m,'mapfile.xml')\n"
        ">>> render(m,context)\n"
        "\n"
        );

    m.def("render_with_detector", &render_with_detector2,
        "\n"
        "Render Map to Cairo Context using a pre-constructed detector.\n"
        "\n"
        "Usage:\n"
        ">>> from mapnik import Map, LabelCollisionDetector, render_with_detector, load_map\n"
        ">>> from cairo import SVGSurface, Context\n"
        ">>> surface = SVGSurface('image.svg', m.width, m.height)\n"
        ">>> ctx = Context(surface)\n"
        ">>> m = Map(256,256)\n"
        ">>> load_map(m,'mapfile.xml')\n"
        ">>> detector = LabelCollisionDetector(m)\n"
        ">>> render_with_detector(m, ctx, detector)\n"
        );

    m.def("render_with_detector", &render_with_detector3,
        "\n"
        "Render Map to Cairo Context using a pre-constructed detector, scale and offsets.\n"
        "\n"
        "Usage:\n"
        ">>> from mapnik import Map, LabelCollisionDetector, render_with_detector, load_map\n"
        ">>> from cairo import SVGSurface, Context\n"
        ">>> surface = SVGSurface('image.svg', m.width, m.height)\n"
        ">>> ctx = Context(surface)\n"
        ">>> m = Map(256,256)\n"
        ">>> load_map(m,'mapfile.xml')\n"
        ">>> detector = LabelCollisionDetector(m)\n"
        ">>> render_with_detector(m, ctx, detector, 1, 1, 1)\n"
        );

    m.def("render_with_detector", &render_with_detector4,
        "\n"
        "Render Map to Cairo Surface using a pre-constructed detector.\n"
        "\n"
        "Usage:\n"
        ">>> from mapnik import Map, LabelCollisionDetector, render_with_detector, load_map\n"
        ">>> from cairo import SVGSurface, Context\n"
        ">>> surface = SVGSurface('image.svg', m.width, m.height)\n"
        ">>> m = Map(256,256)\n"
        ">>> load_map(m,'mapfile.xml')\n"
        ">>> detector = LabelCollisionDetector(m)\n"
        ">>> render_with_detector(m, surface, detector)\n"
        );

    m.def("render_with_detector", &render_with_detector5,
        "\n"
        "Render Map to Cairo Surface using a pre-constructed detector, scale and offsets.\n"
        "\n"
        "Usage:\n"
        ">>> from mapnik import Map, LabelCollisionDetector, render_with_detector, load_map\n"
        ">>> from cairo import SVGSurface, Context\n"
        ">>> surface = SVGSurface('image.svg', m.width, m.height)\n"
        ">>> m = Map(256,256)\n"
        ">>> load_map(m,'mapfile.xml')\n"
        ">>> detector = LabelCollisionDetector(m)\n"
        ">>> render_with_detector(m, surface, detector, 1, 1, 1)\n"
        );
#endif

    m.def("render_layer", &render_layer2,
          py::arg("map"),
          py::arg("image"),
          py::arg("layer"),
          py::arg("scale_factor")=1.0,
          py::arg("offset_x")=0,
          py::arg("offset_y")=0
        );

#if defined(GRID_RENDERER)
    m.def("render_layer", &mapnik::render_layer_for_grid,
        py::arg("map"),
        py::arg("grid"),
        py::arg("layer"),
        py::arg("fields") = py::list(),
        py::arg("scale_factor")=1.0,
        py::arg("offset_x")=0,
        py::arg("offset_y")=0);
#endif

    // save
    m.def("save_map", &save_map,
          py::arg("Map"),
          py::arg("filename"),
          py::arg("explicit_defaults") = false);

    m.def("save_map_to_string", &save_map_to_string,
          py::arg("Map"),
          py::arg("explicit_defaults") = false);

    m.def("clear_cache", &clear_cache,
          "\n"
          "Clear all global caches of markers and mapped memory regions.\n"
          "\n"
          "Usage:\n"
          ">>> from mapnik import clear_cache\n"
          ">>> clear_cache()\n");


    m.def("render_to_file",&render_to_file1,
          "\n"
          "Render Map to file using explicit image type.\n"
          "\n"
          "Usage:\n"
          ">>> from mapnik import Map, render_to_file, load_map\n"
          ">>> m = Map(256,256)\n"
          ">>> load_map(m,'mapfile.xml')\n"
          ">>> render_to_file(m,'image32bit.png','png')\n"
          "\n"
          "8 bit (paletted) PNG can be requested with 'png256':\n"
          ">>> render_to_file(m,'8bit_image.png','png256')\n"
          "\n"
          "JPEG quality can be controlled by adding a suffix to\n"
          "'jpeg' between 0 and 100 (default is 85):\n"
          ">>> render_to_file(m,'top_quality.jpeg','jpeg100')\n"
          ">>> render_to_file(m,'medium_quality.jpeg','jpeg50')\n");

    m.def("render_to_file",&render_to_file2,
          "\n"
          "Render Map to file (type taken from file extension)\n"
          "\n"
          "Usage:\n"
          ">>> from mapnik import Map, render_to_file, load_map\n"
          ">>> m = Map(256,256)\n"
          ">>> render_to_file(m,'image.jpeg')\n"
          "\n");

    m.def("render_to_file",&render_to_file3,
          "\n"
          "Render Map to file using explicit image type and scale factor.\n"
          "\n"
          "Usage:\n"
          ">>> from mapnik import Map, render_to_file, load_map\n"
          ">>> m = Map(256,256)\n"
          ">>> scale_factor = 4\n"
          ">>> render_to_file(m,'image.jpeg',scale_factor)\n"
          "\n");

    m.def("has_pycairo", &has_pycairo, "Get pycairo module status");
}
