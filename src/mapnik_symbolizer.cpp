/*****************************************************************************
 *
 * This file is part of Mapnik (c++ mapping toolkit)
 *
 * Copyright (C) 2015 Artem Pavlenko
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
#include "boost_std_shared_shim.hpp"

#pragma GCC diagnostic push
#include <mapnik/warning_ignore.hpp>
#include <boost/python.hpp>
#include <boost/python/suite/indexing/vector_indexing_suite.hpp>
#pragma GCC diagnostic pop

// mapnik
#include <mapnik/symbolizer.hpp>
#include <mapnik/symbolizer_hash.hpp>
#include <mapnik/symbolizer_utils.hpp>
#include <mapnik/symbolizer_keys.hpp>
#include <mapnik/image_util.hpp>
#include <mapnik/parse_path.hpp>
#include <mapnik/path_expression.hpp>
#include "mapnik_enumeration.hpp"
#include "mapnik_svg.hpp"
#include <mapnik/expression_node.hpp>
#include <mapnik/value/error.hpp>
#include <mapnik/marker_cache.hpp> // for known_svg_prefix_
#include <mapnik/group/group_layout.hpp>
#include <mapnik/group/group_rule.hpp>
#include <mapnik/group/group_symbolizer_properties.hpp>
#include <mapnik/util/variant.hpp>

using mapnik::symbolizer;
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
using mapnik::color;
using mapnik::path_processor_type;
using mapnik::path_expression_ptr;
using mapnik::guess_type;
using mapnik::expression_ptr;
using mapnik::parse_path;


namespace {

struct value_to_target
{
    value_to_target(mapnik::symbolizer_base & sym, std::string const& name)
        : sym_(sym), name_(name) {}

    void operator() (mapnik::value_integer const& val)
    {
        auto key = mapnik::get_key(name_);
        switch (std::get<2>(get_meta(key)))
        {
        case mapnik::property_types::target_bool:
            put(sym_, key, static_cast<mapnik::value_bool>(val));
            break;
        case mapnik::property_types::target_double:
            put(sym_, key, static_cast<mapnik::value_double>(val));
            break;
        case mapnik::property_types::target_pattern_alignment:
        case mapnik::property_types::target_comp_op:
        case mapnik::property_types::target_line_rasterizer:
        case mapnik::property_types::target_scaling_method:
        case mapnik::property_types::target_line_cap:
        case mapnik::property_types::target_line_join:
        case mapnik::property_types::target_smooth_algorithm:
        case mapnik::property_types::target_simplify_algorithm:
        case mapnik::property_types::target_halo_rasterizer:
        case mapnik::property_types::target_markers_placement:
        case mapnik::property_types::target_markers_multipolicy:
        case mapnik::property_types::target_halo_comp_op:
        case mapnik::property_types::target_text_transform:
        case mapnik::property_types::target_horizontal_alignment:
        case mapnik::property_types::target_justify_alignment:
        case mapnik::property_types::target_vertical_alignment:
        case mapnik::property_types::target_upright:
        case mapnik::property_types::target_direction:
        case mapnik::property_types::target_line_pattern:
        {
            put(sym_, key, mapnik::enumeration_wrapper(val));
            break;
        }
        default:
            put(sym_, key, val);
            break;
        }
    }

    void operator() (mapnik::value_double const& val)
    {
        auto key = mapnik::get_key(name_);
        switch (std::get<2>(get_meta(key)))
        {
        case mapnik::property_types::target_bool:
            put(sym_, key, static_cast<mapnik::value_bool>(val));
            break;
        case mapnik::property_types::target_integer:
            put(sym_, key, static_cast<mapnik::value_integer>(val));
            break;
        default:
            put(sym_, key, val);
            break;
        }
    }

    template <typename T>
    void operator() (T const& val)
    {
        put(sym_, mapnik::get_key(name_), val);
    }
private:
    mapnik::symbolizer_base & sym_;
    std::string const& name_;

};

using namespace boost::python;
void __setitem__(mapnik::symbolizer_base & sym, std::string const& name, mapnik::symbolizer_base::value_type const& val)
{
    mapnik::util::apply_visitor(value_to_target(sym, name), val);
}

std::shared_ptr<mapnik::symbolizer_base::value_type> numeric_wrapper(const object& arg)
{
    std::shared_ptr<mapnik::symbolizer_base::value_type> result;
    if (PyBool_Check(arg.ptr()))
    {
        mapnik::value_bool val = extract<mapnik::value_bool>(arg);
        result.reset(new mapnik::symbolizer_base::value_type(val));
    }
    else if (PyFloat_Check(arg.ptr()))
    {
        mapnik::value_double val = extract<mapnik::value_double>(arg);
        result.reset(new mapnik::symbolizer_base::value_type(val));
    }
    else
    {
        mapnik::value_integer val = extract<mapnik::value_integer>(arg);
        result.reset(new mapnik::symbolizer_base::value_type(val));
    }
    return result;
}

struct extract_python_object
{
    using result_type = boost::python::object;

    template <typename T>
    auto operator() (T const& val) const -> result_type
    {
        return result_type(val); // wrap into python object
    }
};

boost::python::object __getitem__(mapnik::symbolizer_base const& sym, std::string const& name)
{
    using const_iterator = symbolizer_base::cont_type::const_iterator;
    mapnik::keys key = mapnik::get_key(name);
    const_iterator itr = sym.properties.find(key);
    if (itr != sym.properties.end())
    {
        return mapnik::util::apply_visitor(extract_python_object(), itr->second);
    }
    //mapnik::property_meta_type const& meta = mapnik::get_meta(key);
    //return mapnik::util::apply_visitor(extract_python_object(), std::get<1>(meta));
    return boost::python::object();
}

boost::python::object symbolizer_keys(mapnik::symbolizer_base const& sym)
{
    boost::python::list keys;
    for (auto const& kv : sym.properties)
    {
        std::string name = std::get<0>(mapnik::get_meta(kv.first));
        keys.append(name);
    }
    return keys;
}
/*
std::string __str__(mapnik::symbolizer const& sym)
{
    return mapnik::util::apply_visitor(mapnik::symbolizer_to_json(), sym);
}
*/

std::string get_symbolizer_type(symbolizer const& sym)
{
    return mapnik::symbolizer_name(sym); // FIXME - do we need this ?
}

std::size_t hash_impl(symbolizer const& sym)
{
    return mapnik::util::apply_visitor(mapnik::symbolizer_hash_visitor(), sym);
}

template <typename T>
std::size_t hash_impl_2(T const& sym)
{
    return mapnik::symbolizer_hash::value<T>(sym);
}

struct extract_underlying_type_visitor
{
    template <typename T>
    boost::python::object operator() (T const& sym) const
    {
        return boost::python::object(sym);
    }
};

boost::python::object extract_underlying_type(symbolizer const& sym)
{
    return mapnik::util::apply_visitor(extract_underlying_type_visitor(), sym);
}

}

void export_symbolizer()
{
    using namespace boost::python;

    //implicitly_convertible<mapnik::value_bool, mapnik::symbolizer_base::value_type>();
    implicitly_convertible<mapnik::value_integer, mapnik::symbolizer_base::value_type>();
    implicitly_convertible<mapnik::value_double, mapnik::symbolizer_base::value_type>();
    implicitly_convertible<std::string, mapnik::symbolizer_base::value_type>();
    implicitly_convertible<mapnik::color, mapnik::symbolizer_base::value_type>();
    implicitly_convertible<mapnik::expression_ptr, mapnik::symbolizer_base::value_type>();
    implicitly_convertible<mapnik::path_expression_ptr, mapnik::symbolizer_base::value_type>();
    implicitly_convertible<mapnik::enumeration_wrapper, mapnik::symbolizer_base::value_type>();
    implicitly_convertible<std::shared_ptr<mapnik::group_symbolizer_properties>, mapnik::symbolizer_base::value_type>();

    enum_<mapnik::keys>("keys")
        .value("gamma", mapnik::keys::gamma)
        .value("gamma_method",mapnik::keys::gamma_method)
        ;

    class_<symbolizer>("Symbolizer",no_init)
        .def("type",get_symbolizer_type)
        .def("__hash__",hash_impl)
        .def("extract", extract_underlying_type)
        ;

    class_<symbolizer_base::value_type>("NumericWrapper")
        .def("__init__", make_constructor(numeric_wrapper))
        ;

    class_<symbolizer_base>("SymbolizerBase",no_init)
        .def("__setitem__",&__setitem__)
        .def("__setattr__",&__setitem__)
        .def("__getitem__",&__getitem__)
        .def("__getattr__",&__getitem__)
        .def("keys", &symbolizer_keys)
        //.def("__str__", &__str__)
        .def(self == self) // __eq__
        ;
}

void export_text_symbolizer()
{
    using namespace boost::python;
    mapnik::enumeration_<mapnik::label_placement_e>("label_placement")
        .value("LINE_PLACEMENT", mapnik::label_placement_enum::LINE_PLACEMENT)
        .value("POINT_PLACEMENT", mapnik::label_placement_enum::POINT_PLACEMENT)
        .value("VERTEX_PLACEMENT", mapnik::label_placement_enum::VERTEX_PLACEMENT)
        .value("INTERIOR_PLACEMENT", mapnik::label_placement_enum::INTERIOR_PLACEMENT);

    mapnik::enumeration_<mapnik::vertical_alignment_e>("vertical_alignment")
        .value("TOP", mapnik::vertical_alignment_enum::V_TOP)
        .value("MIDDLE", mapnik::vertical_alignment_enum::V_MIDDLE)
        .value("BOTTOM", mapnik::vertical_alignment_enum::V_BOTTOM)
        .value("AUTO", mapnik::vertical_alignment_enum::V_AUTO);

    mapnik::enumeration_<mapnik::horizontal_alignment_e>("horizontal_alignment")
        .value("LEFT", mapnik::horizontal_alignment_enum::H_LEFT)
        .value("MIDDLE", mapnik::horizontal_alignment_enum::H_MIDDLE)
        .value("RIGHT", mapnik::horizontal_alignment_enum::H_RIGHT)
        .value("AUTO", mapnik::horizontal_alignment_enum::H_AUTO);

    mapnik::enumeration_<mapnik::justify_alignment_e>("justify_alignment")
        .value("LEFT", mapnik::justify_alignment_enum::J_LEFT)
        .value("MIDDLE", mapnik::justify_alignment_enum::J_MIDDLE)
        .value("RIGHT", mapnik::justify_alignment_enum::J_RIGHT)
        .value("AUTO", mapnik::justify_alignment_enum::J_AUTO);

    mapnik::enumeration_<mapnik::text_transform_e>("text_transform")
        .value("NONE", mapnik::text_transform_enum::NONE)
        .value("UPPERCASE", mapnik::text_transform_enum::UPPERCASE)
        .value("LOWERCASE", mapnik::text_transform_enum::LOWERCASE)
        .value("CAPITALIZE", mapnik::text_transform_enum::CAPITALIZE);

    mapnik::enumeration_<mapnik::halo_rasterizer_e>("halo_rasterizer")
        .value("FULL", mapnik::halo_rasterizer_enum::HALO_RASTERIZER_FULL)
        .value("FAST", mapnik::halo_rasterizer_enum::HALO_RASTERIZER_FAST);

    class_< text_symbolizer, bases<symbolizer_base> >("TextSymbolizer",
                                                      init<>("Default ctor"))
        .def("__hash__",hash_impl_2<text_symbolizer>)
        ;

}

void export_shield_symbolizer()
{
    using namespace boost::python;
    class_< shield_symbolizer, bases<text_symbolizer> >("ShieldSymbolizer",
                                                        init<>("Default ctor"))
        .def("__hash__",hash_impl_2<shield_symbolizer>)
        ;

}

void export_polygon_symbolizer()
{
    using namespace boost::python;

    class_<polygon_symbolizer, bases<symbolizer_base> >("PolygonSymbolizer",
                                                        init<>("Default ctor"))
        .def("__hash__",hash_impl_2<polygon_symbolizer>)
        ;

}

void export_polygon_pattern_symbolizer()
{
    using namespace boost::python;

    mapnik::enumeration_<mapnik::pattern_alignment_e>("pattern_alignment")
        .value("LOCAL",mapnik::pattern_alignment_enum::LOCAL_ALIGNMENT)
        .value("GLOBAL",mapnik::pattern_alignment_enum::GLOBAL_ALIGNMENT)
        ;

    class_<polygon_pattern_symbolizer>("PolygonPatternSymbolizer",
                                       init<>("Default ctor"))
        .def("__hash__",hash_impl_2<polygon_pattern_symbolizer>)
        ;
}

void export_raster_symbolizer()
{
    using namespace boost::python;

    class_<raster_symbolizer, bases<symbolizer_base> >("RasterSymbolizer",
                              init<>("Default ctor"))
        ;
}

void export_point_symbolizer()
{
    using namespace boost::python;

    mapnik::enumeration_<mapnik::point_placement_e>("point_placement")
        .value("CENTROID",mapnik::point_placement_enum::CENTROID_POINT_PLACEMENT)
        .value("INTERIOR",mapnik::point_placement_enum::INTERIOR_POINT_PLACEMENT)
        ;

    class_<point_symbolizer, bases<symbolizer_base> >("PointSymbolizer",
                             init<>("Default Point Symbolizer - 4x4 black square"))
        .def("__hash__",hash_impl_2<point_symbolizer>)
        ;
}

void export_markers_symbolizer()
{
    using namespace boost::python;

    mapnik::enumeration_<mapnik::marker_placement_e>("marker_placement")
        .value("POINT_PLACEMENT",mapnik::marker_placement_enum::MARKER_POINT_PLACEMENT)
        .value("INTERIOR_PLACEMENT",mapnik::marker_placement_enum::MARKER_INTERIOR_PLACEMENT)
        .value("LINE_PLACEMENT",mapnik::marker_placement_enum::MARKER_LINE_PLACEMENT)
        ;

    mapnik::enumeration_<mapnik::marker_multi_policy_e>("marker_multi_policy")
        .value("EACH",mapnik::marker_multi_policy_enum::MARKER_EACH_MULTI)
        .value("WHOLE",mapnik::marker_multi_policy_enum::MARKER_WHOLE_MULTI)
        .value("LARGEST",mapnik::marker_multi_policy_enum::MARKER_LARGEST_MULTI)
        ;

    class_<markers_symbolizer, bases<symbolizer_base> >("MarkersSymbolizer",
                               init<>("Default Markers Symbolizer - circle"))
        .def("__hash__",hash_impl_2<markers_symbolizer>)
        ;
}


void export_line_symbolizer()
{
    using namespace boost::python;

    mapnik::enumeration_<mapnik::line_rasterizer_e>("line_rasterizer")
        .value("FULL",mapnik::line_rasterizer_enum::RASTERIZER_FULL)
        .value("FAST",mapnik::line_rasterizer_enum::RASTERIZER_FAST)
        ;

    mapnik::enumeration_<mapnik::line_cap_e>("stroke_linecap",
                             "The possible values for a line cap used when drawing\n"
                             "with a stroke.\n")
        .value("BUTT_CAP",mapnik::line_cap_enum::BUTT_CAP)
        .value("SQUARE_CAP",mapnik::line_cap_enum::SQUARE_CAP)
        .value("ROUND_CAP",mapnik::line_cap_enum::ROUND_CAP)
        ;

    mapnik::enumeration_<mapnik::line_join_e>("stroke_linejoin",
                                      "The possible values for the line joining mode\n"
                                      "when drawing with a stroke.\n")
        .value("MITER_JOIN",mapnik::line_join_enum::MITER_JOIN)
        .value("MITER_REVERT_JOIN",mapnik::line_join_enum::MITER_REVERT_JOIN)
        .value("ROUND_JOIN",mapnik::line_join_enum::ROUND_JOIN)
        .value("BEVEL_JOIN",mapnik::line_join_enum::BEVEL_JOIN)
        ;


    class_<line_symbolizer, bases<symbolizer_base> >("LineSymbolizer",
                            init<>("Default LineSymbolizer - 1px solid black"))
        .def("__hash__",hash_impl_2<line_symbolizer>)
        ;
}

void export_line_pattern_symbolizer()
{
    using namespace boost::python;

    class_<line_pattern_symbolizer, bases<symbolizer_base> >("LinePatternSymbolizer",
                                    init<> ("Default LinePatternSymbolizer"))
        .def("__hash__",hash_impl_2<line_pattern_symbolizer>)
        ;
}

void export_debug_symbolizer()
{
    using namespace boost::python;

    mapnik::enumeration_<mapnik::debug_symbolizer_mode_e>("debug_symbolizer_mode")
        .value("COLLISION",mapnik::debug_symbolizer_mode_enum::DEBUG_SYM_MODE_COLLISION)
        .value("VERTEX",mapnik::debug_symbolizer_mode_enum::DEBUG_SYM_MODE_VERTEX)
        ;

    class_<debug_symbolizer, bases<symbolizer_base> >("DebugSymbolizer",
                             init<>("Default debug Symbolizer"))
        .def("__hash__",hash_impl_2<debug_symbolizer>)
        ;
}

void export_building_symbolizer()
{
    using namespace boost::python;

    class_<building_symbolizer, bases<symbolizer_base> >("BuildingSymbolizer",
                               init<>("Default BuildingSymbolizer"))
        .def("__hash__",hash_impl_2<building_symbolizer>)
        ;

}

namespace {

void group_symbolizer_properties_set_layout_simple(mapnik::group_symbolizer_properties &p,
                                                   mapnik::simple_row_layout &s)
{
    p.set_layout(s);
}

void group_symbolizer_properties_set_layout_pair(mapnik::group_symbolizer_properties &p,
                                                 mapnik::pair_layout &s)
{
    p.set_layout(s);
}

std::shared_ptr<mapnik::group_rule> group_rule_construct1(mapnik::expression_ptr p)
{
    return std::make_shared<mapnik::group_rule>(p, mapnik::expression_ptr());
}

} // anonymous namespace

void export_group_symbolizer()
{
    using namespace boost::python;
    using mapnik::group_rule;
    using mapnik::simple_row_layout;
    using mapnik::pair_layout;
    using mapnik::group_symbolizer_properties;

    class_<group_rule, std::shared_ptr<group_rule> >("GroupRule",
                                                     init<expression_ptr, expression_ptr>())
        .def("__init__", boost::python::make_constructor(group_rule_construct1))
        .def("append", &group_rule::append)
        .def("set_filter", &group_rule::set_filter)
        .def("set_repeat_key", &group_rule::set_repeat_key)
        ;

    class_<simple_row_layout>("SimpleRowLayout")
        .def("item_margin", &simple_row_layout::get_item_margin)
        .def("set_item_margin", &simple_row_layout::set_item_margin)
        ;

    class_<pair_layout>("PairLayout")
        .def("item_margin", &simple_row_layout::get_item_margin)
        .def("set_item_margin", &simple_row_layout::set_item_margin)
        .def("max_difference", &pair_layout::get_max_difference)
        .def("set_max_difference", &pair_layout::set_max_difference)
        ;

    class_<group_symbolizer_properties, std::shared_ptr<group_symbolizer_properties> >("GroupSymbolizerProperties")
        .def("add_rule", &group_symbolizer_properties::add_rule)
        .def("set_layout", &group_symbolizer_properties_set_layout_simple)
        .def("set_layout", &group_symbolizer_properties_set_layout_pair)
        ;

    class_<group_symbolizer, bases<symbolizer_base> >("GroupSymbolizer",
                                                      init<>("Default GroupSymbolizer"))
        .def("__hash__",hash_impl_2<group_symbolizer>)
        ;

}
