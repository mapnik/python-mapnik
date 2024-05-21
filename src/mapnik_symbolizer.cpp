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
#include <mapnik/transform/parse_transform.hpp>
#include <mapnik/transform/transform_processor.hpp>

#include "mapnik_enumeration.hpp"
#include "mapnik_symbolizer.hpp"

//pybind11
#include <pybind11/pybind11.h>
#include <pybind11/operators.h>
#include <pybind11/stl.h>
#include <pybind11/stl_bind.h>

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
using mapnik::building_symbolizer;
using mapnik::markers_symbolizer;
using mapnik::debug_symbolizer;
using mapnik::group_symbolizer;
using mapnik::symbolizer_base;

using namespace python_mapnik;

namespace {

struct extract_underlying_type_visitor
{
    template <typename T>
    py::object operator() (T const& sym) const
    {
        return py::cast(sym);
    }
};

inline py::object extract_underlying_type(symbolizer const& sym)
{
    return mapnik::util::apply_visitor(extract_underlying_type_visitor(), sym);
}

std::string __str__(mapnik::symbolizer const& sym)
{
    return mapnik::util::apply_visitor(mapnik::symbolizer_to_json(), sym);
}

std::string symbolizer_type_name(symbolizer const& sym)
{
    return mapnik::symbolizer_name(sym);
}

struct symbolizer_keys_visitor
{
    symbolizer_keys_visitor(py::list & keys)
        : keys_(keys) {}

    template <typename Symbolizer>
    void operator() (Symbolizer const& sym) const
    {
        for (auto const& kv : sym.properties)
        {
            std::string name = std::get<0>(mapnik::get_meta(kv.first));
            keys_.append(name);
        }
    }
    py::list & keys_;
};

struct symbolizer_getitem_visitor
{
    using const_iterator = symbolizer_base::cont_type::const_iterator;
    symbolizer_getitem_visitor(std::string const& name)
        : name_(name) {}

    template <typename Symbolizer>
    py::object operator() (Symbolizer const& sym) const
    {
        for (auto const& kv : sym.properties)
        {
            std::string name = std::get<0>(mapnik::get_meta(kv.first));
            if (name == name_)
            {
                return mapnik::util::apply_visitor(extract_python_object<>(kv.first), std::get<1>(kv));
            }
        }
        throw pybind11::key_error("Invalid property name");
    }
    std::string const& name_;
};

py::object symbolizer_keys(mapnik::symbolizer const& sym)
{
    py::list keys;
    mapnik::util::apply_visitor(symbolizer_keys_visitor(keys), sym);
    return keys;
}

py::object getitem_impl(mapnik::symbolizer const& sym, std::string const& name)
{
    return  mapnik::util::apply_visitor(symbolizer_getitem_visitor(name), sym);
}

py::object symbolizer_base_keys(mapnik::symbolizer_base const& sym)
{
    py::list keys;
    for (auto const& kv : sym.properties)
    {
        std::string name = std::get<0>(mapnik::get_meta(kv.first));
        keys.append(name);
    }
    return keys;
}

} // namespace

void export_symbolizer(py::module const& m)
{
    py::implicitly_convertible<std::string, mapnik::color>();

    py::class_<symbolizer>(m, "Symbolizer")
        .def(py::init<dot_symbolizer>())
        .def(py::init<polygon_symbolizer>())
        .def(py::init<polygon_pattern_symbolizer>())
        .def(py::init<point_symbolizer>())
        .def(py::init<line_symbolizer>())
        .def(py::init<line_pattern_symbolizer>())
        .def(py::init<text_symbolizer>())
        .def("type_name", symbolizer_type_name)
        .def("__hash__", hash_impl)
        .def("__getitem__",&getitem_impl)
        .def("__getattr__",&getitem_impl)
        .def("keys", &symbolizer_keys)
        .def("extract", &extract_underlying_type)
        .def("__str__", &__str__)
        .def("__repr__", &__str__)
        .def("to_json", &__str__)
        ;

    py::class_<symbolizer_base>(m, "SymbolizerBase")
        //.def("__getitem__",&__getitem__)
        //.def("__getattr__",&__getitem__)
        .def("keys", &symbolizer_base_keys)
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
