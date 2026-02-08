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

#ifndef MAPNIK_PYTHON_BINDING_VALUE_CONVERTER_INCLUDED
#define MAPNIK_PYTHON_BINDING_VALUE_CONVERTER_INCLUDED

// mapnik
#include <mapnik/value.hpp>
#include <mapnik/params.hpp>
#include <mapnik/unicode.hpp>
//pybind11
#include <pybind11/pybind11.h>

namespace {

struct value_converter
{
    PyObject * operator() (mapnik::value_integer val) const
    {
        return ::PyLong_FromLongLong(val);
    }

    PyObject * operator() (mapnik::value_double val) const
    {
        return ::PyFloat_FromDouble(val);
    }

    PyObject * operator() (mapnik::value_bool val) const
    {
        return ::PyBool_FromLong(val);
    }

    PyObject * operator() (std::string const& s) const
    {
        return ::PyUnicode_DecodeUTF8(s.c_str(), static_cast<ssize_t>(s.length()),0);
    }

    PyObject * operator() (mapnik::value_unicode_string const& s) const
    {
        const char* data = reinterpret_cast<const char*>(s.getBuffer());
        Py_ssize_t size = static_cast<Py_ssize_t>(s.length() * sizeof(s[0]));
        return ::PyUnicode_DecodeUTF16(data, size, nullptr, nullptr);
    }

    PyObject * operator() (mapnik::value_null const& /*s*/) const
    {
        Py_RETURN_NONE;
    }
};

} // namespace

struct mapnik_value_to_python
{
    static PyObject* convert(mapnik::value const& v)
    {
        return mapnik::util::apply_visitor(value_converter(),v);
    }
};

struct mapnik_param_to_python
{
    static PyObject* convert(mapnik::value_holder const& v)
    {
        return mapnik::util::apply_visitor(value_converter(),v);
    }
};



namespace PYBIND11_NAMESPACE { namespace detail {

template <>
struct type_caster<mapnik::value>
{
    mapnik::transcoder const tr_{"utf8"};
public:

    PYBIND11_TYPE_CASTER(mapnik::value, const_name("Value"));

    bool load(handle src, bool)
    {
        PyObject *source = src.ptr();
        if (PyUnicode_Check(source))
        {
            PyObject* tmp = PyUnicode_AsUTF8String(source);
            if (!tmp) return false;
            char* c_str = PyBytes_AsString(tmp);
            value = tr_.transcode(c_str);
            Py_DecRef(tmp);
            return !PyErr_Occurred();
        }
        else if (PyBool_Check(source))
        {
            value = (source == Py_True) ? true : false;
            return !PyErr_Occurred();
        }
        else if (PyFloat_Check(source))
        {
            PyObject *tmp = PyNumber_Float(source);
            if (!tmp) return false;
            value = PyFloat_AsDouble(tmp);
            Py_DecRef(tmp);
            return !PyErr_Occurred();
        }
        else if(PyLong_Check(source))
        {
            PyObject *tmp = PyNumber_Long(source);
            if (!tmp) return false;
            value = PyLong_AsLong(tmp);
            Py_DecRef(tmp);
            return !PyErr_Occurred();
        }
        else if (source == Py_None)
        {
            value = mapnik::value_null{};
            return true;
        }
        return false;
    }

    static handle cast(mapnik::value src, return_value_policy /*policy*/, handle /*parent*/)
    {
        return mapnik_value_to_python::convert(src);
    }
};

template <>
struct type_caster<mapnik::value_holder>
{
public:

    PYBIND11_TYPE_CASTER(mapnik::value_holder, const_name("ValueHolder"));

    bool load(handle src, bool)
    {
        PyObject *source = src.ptr();
        if (PyUnicode_Check(source))
        {
            PyObject* tmp = PyUnicode_AsUTF8String(source);
            if (!tmp) return false;
            char* c_str = PyBytes_AsString(tmp);
            value = std::string(c_str);
            Py_DecRef(tmp);
            return !PyErr_Occurred();
        }
        else if (PyBool_Check(source))
        {
            value = (source == Py_True) ? true : false;
            return !PyErr_Occurred();
        }
        else if (PyFloat_Check(source))
        {
            PyObject *tmp = PyNumber_Float(source);
            if (!tmp) return false;
            value = PyFloat_AsDouble(tmp);
            Py_DecRef(tmp);
            return !PyErr_Occurred();
        }
        else if(PyLong_Check(source))
        {
            PyObject *tmp = PyNumber_Long(source);
            if (!tmp) return false;
            value = PyLong_AsLongLong(tmp);
            Py_DecRef(tmp);
            return !PyErr_Occurred();
        }
        else if (source == Py_None)
        {
            value = mapnik::value_null{};
            return true;
        }
        return false;
    }

    static handle cast(mapnik::value_holder src, return_value_policy /*policy*/, handle /*parent*/)
    {
        return mapnik_param_to_python::convert(src);
    }
};

}} // namespace PYBIND11_NAMESPACE::detail


#endif // MAPNIK_PYTHON_BINDING_VALUE_CONVERTER_INCLUDED
