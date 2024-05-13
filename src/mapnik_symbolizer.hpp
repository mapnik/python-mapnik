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

#ifndef MAPNIK_SYMBOLIZER_INCLUDED
#define MAPNIK_SYMBOLIZER_INCLUDED

#include <mapnik/color.hpp>
#include <mapnik/symbolizer.hpp>
#include <mapnik/symbolizer_hash.hpp>
#include <mapnik/symbolizer_utils.hpp>
#include <mapnik/symbolizer_keys.hpp>
#include <mapnik/symbolizer_enumerations.hpp>

#include <pybind11/pybind11.h>
#include <pybind11/operators.h>
#include <pybind11/stl.h>
#include <pybind11/stl_bind.h>

//#define PYBIND11_DETAILED_ERROR_MESSAGES


PYBIND11_MAKE_OPAQUE(mapnik::symbolizer);

namespace py = pybind11;

namespace python_mapnik {

using mapnik::symbolizer;
using mapnik::symbolizer_base;

// struct value_to_target
// {
//     value_to_target(mapnik::symbolizer_base & sym, std::string const& name)
//         : sym_(sym), name_(name) {}

//     void operator() (mapnik::value_integer const& val)
//     {
//         auto key = mapnik::get_key(name_);
//         switch (std::get<2>(get_meta(key)))
//         {
//         case mapnik::property_types::target_bool:
//             put(sym_, key, static_cast<mapnik::value_bool>(val));
//             break;
//         case mapnik::property_types::target_double:
//             put(sym_, key, static_cast<mapnik::value_double>(val));
//             break;
//         case mapnik::property_types::target_pattern_alignment:
//         case mapnik::property_types::target_comp_op:
//         case mapnik::property_types::target_line_rasterizer:
//         case mapnik::property_types::target_scaling_method:
//         case mapnik::property_types::target_line_cap:
//         case mapnik::property_types::target_line_join:
//         case mapnik::property_types::target_smooth_algorithm:
//         case mapnik::property_types::target_simplify_algorithm:
//         case mapnik::property_types::target_halo_rasterizer:
//         case mapnik::property_types::target_markers_placement:
//         case mapnik::property_types::target_markers_multipolicy:
//         case mapnik::property_types::target_halo_comp_op:
//         case mapnik::property_types::target_text_transform:
//         case mapnik::property_types::target_horizontal_alignment:
//         case mapnik::property_types::target_justify_alignment:
//         case mapnik::property_types::target_vertical_alignment:
//         case mapnik::property_types::target_upright:
//         case mapnik::property_types::target_direction:
//         case mapnik::property_types::target_line_pattern:
//         {
//             put(sym_, key, mapnik::enumeration_wrapper(val));
//             break;
//         }
//         default:
//             put(sym_, key, val);
//             break;
//         }
//     }

//     void operator() (mapnik::value_double const& val)
//     {
//         auto key = mapnik::get_key(name_);
//         switch (std::get<2>(get_meta(key)))
//         {
//         case mapnik::property_types::target_bool:
//             put(sym_, key, static_cast<mapnik::value_bool>(val));
//             break;
//         case mapnik::property_types::target_integer:
//             put(sym_, key, static_cast<mapnik::value_integer>(val));
//             break;
//         default:
//             put(sym_, key, val);
//             break;
//         }
//     }

//     template <typename T>
//     void operator() (T const& val)
//     {
//         put(sym_, mapnik::get_key(name_), val);
//     }
// private:
//     mapnik::symbolizer_base & sym_;
//     std::string const& name_;

// };

//using namespace boost::python;
//void __setitem__(mapnik::symbolizer_base & sym, std::string const& name, mapnik::symbolizer_base::value_type const& val)
//{
//    mapnik::util::apply_visitor(value_to_target(sym, name), val);
//}

// std::shared_ptr<mapnik::symbolizer_base::value_type> numeric_wrapper(const py::object& arg)
// {
//     std::shared_ptr<mapnik::symbolizer_base::value_type> result;
    // if (PyBool_Check(arg.ptr()))
    // {
    //     mapnik::value_bool val = extract<mapnik::value_bool>(arg);
    //     result.reset(new mapnik::symbolizer_base::value_type(val));
    // }
    // else if (PyFloat_Check(arg.ptr()))
    // {
    //     mapnik::value_double val = extract<mapnik::value_double>(arg);
    //     result.reset(new mapnik::symbolizer_base::value_type(val));
    // }
    // else
    // {
    //     mapnik::value_integer val = extract<mapnik::value_integer>(arg);
    //     result.reset(new mapnik::symbolizer_base::value_type(val));
    // }
//     return result;
// }

struct extract_python_object
{
    using result_type = py::object;

    auto operator() (mapnik::value_bool val) const -> result_type
    {
        return py::bool_(val);
    }

    auto operator() (mapnik::value_double val) const -> result_type
    {
        return py::float_(val);
    }
    auto operator() (mapnik::value_integer val) const -> result_type
    {
        return py::int_(val);
    }

    auto operator() (mapnik::color const& col) const -> result_type
    {
        return py::cast(col);
    }

    auto operator() (mapnik::expression_ptr const& expr) const -> result_type
    {
        return py::cast(expr);
    }

    template <typename T>
    auto operator() (T const& val) const -> result_type
    {
        std::cerr << typeid(val).name() << std::endl;
        //return py::cast(val);
        return py::none();//result_type(val); // wrap into python object
    }
};

template <typename Symbolizer, mapnik::keys Key>
py::object get_property(Symbolizer const& sym)
{
    using const_iterator = symbolizer_base::cont_type::const_iterator;
    const_iterator itr = sym.properties.find(Key);
    if (itr != sym.properties.end())
    {
        return mapnik::util::apply_visitor(extract_python_object(), itr->second);
    }
    return py::none();
}

template <typename Symbolizer, auto Key>
void set_color_property(Symbolizer & sym, py::object const& obj)
{
    if (py::isinstance<mapnik::color>(obj))
    {
        mapnik::put(sym, Key, obj.cast<mapnik::color>());
    }
    else if (py::isinstance<mapnik::expr_node>(obj))
    {
        auto expr = obj.cast<mapnik::expression_ptr>();
        mapnik::put(sym, Key, expr);
    }
    else if (py::isinstance<py::str>(obj))
    {
        mapnik::put(sym, Key, mapnik::color(obj.cast<std::string>()));
    }
    else throw pybind11::value_error();
}

template <typename Symbolizer, auto Key>
void set_boolean_property(Symbolizer & sym, py::object const& obj)
{

    if (py::isinstance<py::bool_>(obj))
    {
        mapnik::put(sym, Key, obj.cast<mapnik::value_bool>());
    }
    else if (py::isinstance<mapnik::expr_node>(obj))
    {
        auto expr = obj.cast<mapnik::expression_ptr>();
        mapnik::put(sym, Key, expr);
    }
    else throw pybind11::value_error();
}

template <typename Symbolizer, auto Key>
void set_double_property(Symbolizer & sym, py::object const& obj)
{

    if (py::isinstance<py::int_>(obj) || py::isinstance<py::float_>(obj))
    {
        mapnik::put(sym, Key, obj.cast<mapnik::value_double>());
    }
    else if (py::isinstance<mapnik::expr_node>(obj))
    {
        auto expr = obj.cast<mapnik::expression_ptr>();
        mapnik::put(sym, Key, expr);
    }
    else throw pybind11::value_error();
}

template <typename Symbolizer, typename Enum, auto Key>
void set_enum_property(Symbolizer & sym, py::object const& obj)
{
    if (py::isinstance<Enum>(obj))
    {
        mapnik::put(sym, Key, obj.cast<Enum>());
    }
    else if (py::isinstance<mapnik::expr_node>(obj))
    {
        auto expr = obj.cast<mapnik::expression_ptr>();
        mapnik::put(sym, Key, expr);
    }
    else throw pybind11::value_error();
}

namespace {
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
        mapnik::keys key = mapnik::get_key(name_);
        const_iterator itr = sym.properties.find(key);
        if (itr != sym.properties.end())
        {
            return mapnik::util::apply_visitor(extract_python_object(), itr->second);
        }
        return py::none();
    }
    std::string const& name_;
};

}

inline py::object symbolizer_keys(mapnik::symbolizer const& sym)
{
    py::list keys;
    mapnik::util::apply_visitor(symbolizer_keys_visitor(keys), sym);
    return keys;
}

inline py::object getitem_impl(mapnik::symbolizer const& sym, std::string const& name)
{
    return  mapnik::util::apply_visitor(symbolizer_getitem_visitor(name), sym);
}

inline py::object symbolizer_base_keys(mapnik::symbolizer_base const& sym)
{
    py::list keys;
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

inline std::string get_symbolizer_type(symbolizer const& sym)
{
    return mapnik::symbolizer_name(sym); // FIXME - do we need this ?
}

inline std::size_t hash_impl(symbolizer const& sym)
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
    py::object operator() (T const& sym) const
    {
        return py::none();//py::object(sym);
    }
};

inline py::object extract_underlying_type(symbolizer const& sym)
{
    return mapnik::util::apply_visitor(extract_underlying_type_visitor(), sym);
}

// text symbolizer
// mapnik::text_placements_ptr get_placement_finder(text_symbolizer const& sym)
// {
//     return mapnik::get<mapnik::text_placements_ptr>(sym, mapnik::keys::text_placements_);
// }

// void set_placement_finder(text_symbolizer & sym, std::shared_ptr<text_placements_dummy> const& finder)
// {
//     mapnik::put<mapnik::text_placements_ptr>(sym, mapnik::keys::text_placements_, finder);
// }

template <typename Value, auto Key>
auto get(symbolizer_base const& sym) -> Value
{
    return mapnik::get<Value>(sym, Key);
}

template <typename Value, auto Key>
void set(symbolizer_base & sym, Value const& val)
{
    mapnik::put<Value>(sym, Key, val);
}

inline std::string get_transform(symbolizer_base const& sym)
{
    auto expr = mapnik::get<mapnik::transform_type>(sym, mapnik::keys::geometry_transform);
    if (expr)
        return mapnik::transform_processor_type::to_string(*expr);
    return "";
}

inline void set_transform(symbolizer_base & sym, std::string const& str)
{
    mapnik::put(sym, mapnik::keys::geometry_transform, mapnik::parse_transform(str));
}

} // namespace python_mapnik

#endif //MAPNIK_SYMBOLIZER_INCLUDED
