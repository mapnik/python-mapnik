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
#include <mapnik/symbolizer.hpp>
#include <mapnik/symbolizer_hash.hpp>
#include <mapnik/symbolizer_utils.hpp>
#include <mapnik/symbolizer_keys.hpp>
#include <mapnik/symbolizer_enumerations.hpp>
#include <mapnik/image_util.hpp>
#include <mapnik/parse_path.hpp>
#include <mapnik/path_expression.hpp>
#include <mapnik/expression_node.hpp>
#include <mapnik/expression_string.hpp>
#include <mapnik/value/error.hpp>
#include <mapnik/marker_cache.hpp> // for known_svg_prefix_
#include <mapnik/group/group_layout.hpp>
#include <mapnik/group/group_rule.hpp>
#include <mapnik/group/group_symbolizer_properties.hpp>
#include <mapnik/util/variant.hpp>
#include <mapnik/text/placements/dummy.hpp>
#include <mapnik/transform/parse_transform.hpp>
#include <mapnik/transform/transform_processor.hpp>

#include "mapnik_enumeration.hpp"
#include "mapnik_symbolizer.hpp"

//#include "python_variant.hpp"
//#include "mapnik_value_converter.hpp"

//pybind11
#include <pybind11/pybind11.h>
#include <pybind11/operators.h>
#include <pybind11/stl.h>
#include <pybind11/stl_bind.h>

//#define PYBIND11_DETAILED_ERROR_MESSAGES

namespace py = pybind11;

using mapnik::symbolizer;
using mapnik::dot_symbolizer;
using mapnik::debug_symbolizer;
using mapnik::point_symbolizer;
using mapnik::line_symbolizer;
using mapnik::line_pattern_symbolizer;
using mapnik::polygon_symbolizer;
using mapnik::polygon_pattern_symbolizer;
using mapnik::raster_symbolizer;
using mapnik::shield_symbolizer;
using mapnik::text_symbolizer;
using mapnik::text_placements_dummy;
using mapnik::building_symbolizer;
using mapnik::markers_symbolizer;
using mapnik::debug_symbolizer;
using mapnik::group_symbolizer;
using mapnik::symbolizer_base;
// using mapnik::color;
// using mapnik::path_processor_type;
// using mapnik::path_expression_ptr;
// using mapnik::guess_type;
// using mapnik::expression_ptr;
// using mapnik::parse_path;

using namespace python_mapnik;

void export_symbolizer(py::module const& m)
{
    py::implicitly_convertible<std::string, mapnik::color>();

    py::enum_<mapnik::keys>(m, "keys")
        .value("gamma", mapnik::keys::gamma)
        .value("gamma_method", mapnik::keys::gamma_method)
        ;

    py::class_<symbolizer>(m, "Symbolizer")
        .def(py::init<dot_symbolizer>())
        .def(py::init<polygon_symbolizer>())
        .def(py::init<polygon_pattern_symbolizer>())
        .def(py::init<point_symbolizer>())
        .def(py::init<line_symbolizer>())
        .def(py::init<line_pattern_symbolizer>())
        .def("type", get_symbolizer_type)
        .def("__hash__", hash_impl)
        .def("__getitem__",&getitem_impl)
        .def("__getattr__",&getitem_impl)
        .def("keys", &symbolizer_keys)
        //.def("extract", extract_underlying_type)
        ;

    // class_<symbolizer_base::value_type>("NumericWrapper")
    //     .def("__init__", make_constructor(numeric_wrapper))
    //     ;

    py::class_<symbolizer_base>(m, "SymbolizerBase")
        //.def("__setitem__",&__setitem__)
        //.def("__setattr__",&__setitem__)
        //.def("__getitem__",&__getitem__)
        //.def("__getattr__",&__getitem__)
        .def("keys", &symbolizer_base_keys)
        //.def("__str__", &__str__)
        .def(py::self == py::self) // __eq__
        .def_property("smooth",
                      &get_property<symbolizer_base, mapnik::keys::smooth>,
                      &set_double_property<symbolizer_base, mapnik::keys::smooth>,
                      "Smoothing value")
        .def_property("simplify_tolerance",
                      &get_property<symbolizer_base, mapnik::keys::simplify_tolerance>,
                      &set_double_property<symbolizer_base, mapnik::keys::simplify_tolerance>,
                      "Simplify tolerance")
        .def_property("clip",
                      &get_property<symbolizer_base, mapnik::keys::clip>,
                      &set_boolean_property<symbolizer_base, mapnik::keys::clip>,
                      "Clip - False/True")
        .def_property("comp_op",
                      &get<mapnik::composite_mode_e, mapnik::keys::comp_op>,
                      &set_enum_property<symbolizer_base, mapnik::composite_mode_e, mapnik::keys::comp_op>,
                      "Composite mode (comp-op)")
        .def_property("geometry_transform",
                      &get_transform,
                      &set_transform,
                      "Geometry transform")
        ;

    py::implicitly_convertible<point_symbolizer,symbolizer>();
    py::implicitly_convertible<line_symbolizer,symbolizer>();
    py::implicitly_convertible<line_pattern_symbolizer,symbolizer>();
    py::implicitly_convertible<polygon_symbolizer,symbolizer>();
    py::implicitly_convertible<building_symbolizer,symbolizer>();
    py::implicitly_convertible<polygon_pattern_symbolizer,symbolizer>();
    py::implicitly_convertible<raster_symbolizer,symbolizer>();
    py::implicitly_convertible<shield_symbolizer,symbolizer>();
    py::implicitly_convertible<text_symbolizer,symbolizer>();
    py::implicitly_convertible<markers_symbolizer,symbolizer>();
    py::implicitly_convertible<group_symbolizer,symbolizer>();
    py::implicitly_convertible<dot_symbolizer,symbolizer>();
    py::implicitly_convertible<debug_symbolizer,symbolizer>();
}

// void export_text_symbolizer()
// {
//     using namespace boost::python;
//     mapnik::enumeration_<mapnik::label_placement_e>("label_placement")
//         .value("LINE_PLACEMENT", mapnik::label_placement_enum::LINE_PLACEMENT)
//         .value("POINT_PLACEMENT", mapnik::label_placement_enum::POINT_PLACEMENT)
//         .value("VERTEX_PLACEMENT", mapnik::label_placement_enum::VERTEX_PLACEMENT)
//         .value("INTERIOR_PLACEMENT", mapnik::label_placement_enum::INTERIOR_PLACEMENT);

//     mapnik::enumeration_<mapnik::vertical_alignment_e>("vertical_alignment")
//         .value("TOP", mapnik::vertical_alignment_enum::V_TOP)
//         .value("MIDDLE", mapnik::vertical_alignment_enum::V_MIDDLE)
//         .value("BOTTOM", mapnik::vertical_alignment_enum::V_BOTTOM)
//         .value("AUTO", mapnik::vertical_alignment_enum::V_AUTO);

//     mapnik::enumeration_<mapnik::horizontal_alignment_e>("horizontal_alignment")
//         .value("LEFT", mapnik::horizontal_alignment_enum::H_LEFT)
//         .value("MIDDLE", mapnik::horizontal_alignment_enum::H_MIDDLE)
//         .value("RIGHT", mapnik::horizontal_alignment_enum::H_RIGHT)
//         .value("AUTO", mapnik::horizontal_alignment_enum::H_AUTO);

//     mapnik::enumeration_<mapnik::justify_alignment_e>("justify_alignment")
//         .value("LEFT", mapnik::justify_alignment_enum::J_LEFT)
//         .value("MIDDLE", mapnik::justify_alignment_enum::J_MIDDLE)
//         .value("RIGHT", mapnik::justify_alignment_enum::J_RIGHT)
//         .value("AUTO", mapnik::justify_alignment_enum::J_AUTO);

//     mapnik::enumeration_<mapnik::text_transform_e>("text_transform")
//         .value("NONE", mapnik::text_transform_enum::NONE)
//         .value("UPPERCASE", mapnik::text_transform_enum::UPPERCASE)
//         .value("LOWERCASE", mapnik::text_transform_enum::LOWERCASE)
//         .value("CAPITALIZE", mapnik::text_transform_enum::CAPITALIZE);

//     mapnik::enumeration_<mapnik::halo_rasterizer_e>("halo_rasterizer")
//         .value("FULL", mapnik::halo_rasterizer_enum::HALO_RASTERIZER_FULL)
//         .value("FAST", mapnik::halo_rasterizer_enum::HALO_RASTERIZER_FAST);

//     class_<text_symbolizer>("TextSymbolizer", init<>("Default ctor"))
//         .def("__hash__",hash_impl_2<text_symbolizer>)
//         .add_property("placement_finder", &get_placement_finder, &set_placement_finder, "Placement finder")
//         ;

// }

// void export_shield_symbolizer()
// {
//     using namespace boost::python;
//     class_< shield_symbolizer, bases<text_symbolizer> >("ShieldSymbolizer",
//                                                         init<>("Default ctor"))
//         .def("__hash__",hash_impl_2<shield_symbolizer>)
//         ;

// }


// void export_polygon_pattern_symbolizer()
// {
//     using namespace boost::python;

//     mapnik::enumeration_<mapnik::pattern_alignment_e>("pattern_alignment")
//         .value("LOCAL",mapnik::pattern_alignment_enum::LOCAL_ALIGNMENT)
//         .value("GLOBAL",mapnik::pattern_alignment_enum::GLOBAL_ALIGNMENT)
//         ;

//     class_<polygon_pattern_symbolizer>("PolygonPatternSymbolizer",
//                                        init<>("Default ctor"))
//         .def("__hash__",hash_impl_2<polygon_pattern_symbolizer>)
//         ;
// }

// void export_raster_symbolizer()
// {
//     using namespace boost::python;

//     class_<raster_symbolizer, bases<symbolizer_base> >("RasterSymbolizer",
//                               init<>("Default ctor"))
//         ;
// }

// void export_point_symbolizer()
// {
//     using namespace boost::python;

//     mapnik::enumeration_<mapnik::point_placement_e>("point_placement")
//         .value("CENTROID",mapnik::point_placement_enum::CENTROID_POINT_PLACEMENT)
//         .value("INTERIOR",mapnik::point_placement_enum::INTERIOR_POINT_PLACEMENT)
//         ;

//     class_<point_symbolizer, bases<symbolizer_base> >("PointSymbolizer",
//                              init<>("Default Point Symbolizer - 4x4 black square"))
//         .def("__hash__",hash_impl_2<point_symbolizer>)
//         ;
// }

// void export_markers_symbolizer()
// {
//     using namespace boost::python;

//     mapnik::enumeration_<mapnik::marker_placement_e>("marker_placement")
//         .value("POINT_PLACEMENT",mapnik::marker_placement_enum::MARKER_POINT_PLACEMENT)
//         .value("INTERIOR_PLACEMENT",mapnik::marker_placement_enum::MARKER_INTERIOR_PLACEMENT)
//         .value("LINE_PLACEMENT",mapnik::marker_placement_enum::MARKER_LINE_PLACEMENT)
//         ;

//     mapnik::enumeration_<mapnik::marker_multi_policy_e>("marker_multi_policy")
//         .value("EACH",mapnik::marker_multi_policy_enum::MARKER_EACH_MULTI)
//         .value("WHOLE",mapnik::marker_multi_policy_enum::MARKER_WHOLE_MULTI)
//         .value("LARGEST",mapnik::marker_multi_policy_enum::MARKER_LARGEST_MULTI)
//         ;

//     class_<markers_symbolizer, bases<symbolizer_base> >("MarkersSymbolizer",
//                                init<>("Default Markers Symbolizer - circle"))
//         .def("__hash__",hash_impl_2<markers_symbolizer>)
//         ;
// }

// namespace {

// std::string get_stroke_dasharray(mapnik::symbolizer_base & sym)
// {
//     auto dash = mapnik::get<mapnik::dash_array>(sym, mapnik::keys::stroke_dasharray);

//     std::ostringstream os;
//     for (std::size_t i = 0; i < dash.size(); ++i)
//     {
//         os << dash[i].first << "," << dash[i].second;
//         if (i + 1 < dash.size())
//             os << ",";
//     }
//     return os.str();
// }

// void set_stroke_dasharray(mapnik::symbolizer_base & sym, std::string str)
// {
//     mapnik::dash_array dash;
//     if (mapnik::util::parse_dasharray(str, dash))
//     {
//         mapnik::put(sym, mapnik::keys::stroke_dasharray, dash);
//     }
//     else
//     {
//         throw std::runtime_error("Can't parse dasharray");
//     }
// }

// }

// void export_line_symbolizer()
// {
//     using namespace boost::python;

//     mapnik::enumeration_<mapnik::line_rasterizer_e>("line_rasterizer")
//         .value("FULL",mapnik::line_rasterizer_enum::RASTERIZER_FULL)
//         .value("FAST",mapnik::line_rasterizer_enum::RASTERIZER_FAST)
//         ;

//     mapnik::enumeration_<mapnik::line_cap_e>("stroke_linecap",
//                              "The possible values for a line cap used when drawing\n"
//                              "with a stroke.\n")
//         .value("BUTT_CAP",mapnik::line_cap_enum::BUTT_CAP)
//         .value("SQUARE_CAP",mapnik::line_cap_enum::SQUARE_CAP)
//         .value("ROUND_CAP",mapnik::line_cap_enum::ROUND_CAP)
//         ;

//     mapnik::enumeration_<mapnik::line_join_e>("stroke_linejoin",
//                                       "The possible values for the line joining mode\n"
//                                       "when drawing with a stroke.\n")
//         .value("MITER_JOIN",mapnik::line_join_enum::MITER_JOIN)
//         .value("MITER_REVERT_JOIN",mapnik::line_join_enum::MITER_REVERT_JOIN)
//         .value("ROUND_JOIN",mapnik::line_join_enum::ROUND_JOIN)
//         .value("BEVEL_JOIN",mapnik::line_join_enum::BEVEL_JOIN)
//         ;

//     class_<line_symbolizer, bases<symbolizer_base> >("LineSymbolizer",
//                             init<>("Default LineSymbolizer - 1px solid black"))
//         .def("__hash__",hash_impl_2<line_symbolizer>)
//         .add_property("stroke",
//                       &get<mapnik::color, mapnik::keys::stroke>,
//                       &set<mapnik::color, mapnik::keys::stroke>, "Stroke color")
//         .add_property("stroke_width",
//                       &get<double, mapnik::keys::stroke_width>,
//                       &set<double, mapnik::keys::stroke_width>, "Stroke width")
//         .add_property("stroke_opacity",
//                       &get<double, mapnik::keys::stroke_opacity>,
//                       &set<double, mapnik::keys::stroke_opacity>, "Stroke opacity")
//         .add_property("stroke_gamma",
//                       &get<double, mapnik::keys::stroke_gamma>,
//                       &set<double, mapnik::keys::stroke_gamma>, "Stroke gamma")
//         .add_property("stroke_gamma_method",
//                       &get<mapnik::gamma_method_enum, mapnik::keys::stroke_gamma_method>,
//                       &set<mapnik::gamma_method_enum, mapnik::keys::stroke_gamma_method>, "Stroke gamma method")
//         .add_property("line_rasterizer",
//                       &get<mapnik::line_rasterizer_enum, mapnik::keys::line_rasterizer>,
//                       &set<mapnik::line_rasterizer_enum, mapnik::keys::line_rasterizer>, "Line rasterizer")
//         .add_property("stroke_linecap",
//                       &get<mapnik::line_cap_enum, mapnik::keys::stroke_linecap>,
//                       &set<mapnik::line_cap_enum, mapnik::keys::stroke_linecap>, "Stroke linecap")
//         .add_property("stroke_linejoin",
//                       &get<mapnik::line_join_enum, mapnik::keys::stroke_linejoin>,
//                       &set<mapnik::line_join_enum, mapnik::keys::stroke_linejoin>, "Stroke linejoin")
//         .add_property("stroke_dasharray",
//                       &get_stroke_dasharray,
//                       &set_stroke_dasharray, "Stroke dasharray")
//         .add_property("stroke_dashoffset",
//                       &get<double, mapnik::keys::stroke_dashoffset>,
//                       &set<double, mapnik::keys::stroke_dashoffset>, "Stroke dashoffset")
//         .add_property("stroke_miterlimit",
//                       &get<double, mapnik::keys::stroke_miterlimit>,
//                       &set<double, mapnik::keys::stroke_miterlimit>, "Stroke miterlimit")

//         ;
// }

// void export_line_pattern_symbolizer()
// {
//     using namespace boost::python;

//     class_<line_pattern_symbolizer, bases<symbolizer_base> >("LinePatternSymbolizer",
//                                     init<> ("Default LinePatternSymbolizer"))
//         .def("__hash__",hash_impl_2<line_pattern_symbolizer>)
//         ;
// }

// void export_debug_symbolizer()
// {
//     using namespace boost::python;

//     mapnik::enumeration_<mapnik::debug_symbolizer_mode_e>("debug_symbolizer_mode")
//         .value("COLLISION",mapnik::debug_symbolizer_mode_enum::DEBUG_SYM_MODE_COLLISION)
//         .value("VERTEX",mapnik::debug_symbolizer_mode_enum::DEBUG_SYM_MODE_VERTEX)
//         ;

//     class_<debug_symbolizer, bases<symbolizer_base> >("DebugSymbolizer",
//                              init<>("Default debug Symbolizer"))
//         .def("__hash__",hash_impl_2<debug_symbolizer>)
//         ;
// }

// void export_building_symbolizer()
// {
//     using namespace boost::python;

//     class_<building_symbolizer, bases<symbolizer_base> >("BuildingSymbolizer",
//                                init<>("Default BuildingSymbolizer"))
//         .def("__hash__",hash_impl_2<building_symbolizer>)
//         ;

// }

// namespace {

// void group_symbolizer_properties_set_layout_simple(mapnik::group_symbolizer_properties &p,
//                                                    mapnik::simple_row_layout &s)
// {
//     p.set_layout(s);
// }

// void group_symbolizer_properties_set_layout_pair(mapnik::group_symbolizer_properties &p,
//                                                  mapnik::pair_layout &s)
// {
//     p.set_layout(s);
// }

// std::shared_ptr<mapnik::group_rule> group_rule_construct1(mapnik::expression_ptr p)
// {
//     return std::make_shared<mapnik::group_rule>(p, mapnik::expression_ptr());
// }

// } // anonymous namespace

// void export_group_symbolizer()
// {
//     using namespace boost::python;
//     using mapnik::group_rule;
//     using mapnik::simple_row_layout;
//     using mapnik::pair_layout;
//     using mapnik::group_symbolizer_properties;

//     class_<group_rule, std::shared_ptr<group_rule> >("GroupRule",
//                                                      init<expression_ptr, expression_ptr>())
//         .def("__init__", boost::python::make_constructor(group_rule_construct1))
//         .def("append", &group_rule::append)
//         .def("set_filter", &group_rule::set_filter)
//         .def("set_repeat_key", &group_rule::set_repeat_key)
//         ;

//     class_<simple_row_layout>("SimpleRowLayout")
//         .def("item_margin", &simple_row_layout::get_item_margin)
//         .def("set_item_margin", &simple_row_layout::set_item_margin)
//         ;

//     class_<pair_layout>("PairLayout")
//         .def("item_margin", &simple_row_layout::get_item_margin)
//         .def("set_item_margin", &simple_row_layout::set_item_margin)
//         .def("max_difference", &pair_layout::get_max_difference)
//         .def("set_max_difference", &pair_layout::set_max_difference)
//         ;

//     class_<group_symbolizer_properties, std::shared_ptr<group_symbolizer_properties> >("GroupSymbolizerProperties")
//         .def("add_rule", &group_symbolizer_properties::add_rule)
//         .def("set_layout", &group_symbolizer_properties_set_layout_simple)
//         .def("set_layout", &group_symbolizer_properties_set_layout_pair)
//         ;

//     class_<group_symbolizer, bases<symbolizer_base> >("GroupSymbolizer",
//                                                       init<>("Default GroupSymbolizer"))
//         .def("__hash__",hash_impl_2<group_symbolizer>)
//         ;

// }
