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
#include <mapnik/parse_path.hpp>

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
using mapnik::parse_path;
using mapnik::path_processor;

template <typename TargetType>
struct enum_converter
{
    static auto apply(mapnik::enumeration_wrapper const& wrapper, mapnik::keys key) -> py::object
    {
        return py::cast(TargetType(wrapper.value));
    }
};

template <>
struct enum_converter<void>
{
    static auto apply(mapnik::enumeration_wrapper const& wrapper, mapnik::keys key) -> py::object
    {
        auto meta = mapnik::get_meta(key);
        auto const& convert_fun_ptr(std::get<1>(meta));
        if (convert_fun_ptr)
        {
            return py::cast(convert_fun_ptr(wrapper));
        }
        throw pybind11::key_error("Invalid property name");
    }
};

template <typename TargetType = void>
struct extract_python_object
{
    using result_type = py::object;
    mapnik::keys key_;
    extract_python_object(mapnik::keys key)
        : key_(key) {}

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

    auto operator() (mapnik::path_expression_ptr const& expr) const ->result_type
    {
        if (expr) return py::cast(path_processor::to_string(*expr));
        return py::none();
    }

    auto operator() (mapnik::enumeration_wrapper const& wrapper) const ->result_type
    {
        return enum_converter<TargetType>::apply(wrapper, key_);
    }

    auto operator() (mapnik::transform_list_ptr const& expr) const ->result_type
    {
        if (expr) return py::cast(mapnik::transform_processor_type::to_string(*expr));
        return py::none();
    }

    template <typename T>
    auto operator() (T const& val) const -> result_type
    {
        std::cerr << "Can't convert to Python object [" <<  typeid(val).name() << "]" << std::endl;
        return py::none();
    }
};

template <typename Symbolizer, mapnik::keys Key, typename Enum = int>
py::object get_property(Symbolizer const& sym)
{
    using const_iterator = symbolizer_base::cont_type::const_iterator;
    const_iterator itr = sym.properties.find(Key);
    if (itr != sym.properties.end())
    {
        return mapnik::util::apply_visitor(extract_python_object<Enum>(Key), itr->second);
    }
    throw pybind11::key_error("Invalid property name");
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

template <typename Symbolizer, auto Key>
void set_path_property(Symbolizer & sym, py::object const& obj)
{
    if (py::isinstance<py::str>(obj))
    {
        mapnik::put(sym, Key, parse_path(obj.cast<std::string>()));
    }
    else throw pybind11::value_error();
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
