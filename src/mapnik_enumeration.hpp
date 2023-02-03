/*****************************************************************************
 *
 * This file is part of Mapnik (c++ mapping toolkit)
 *
 * Copyright (C) 2015 Artem Pavlenko, Jean-Francois Doyon
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
#ifndef MAPNIK_PYTHON_BINDING_ENUMERATION_INCLUDED
#define MAPNIK_PYTHON_BINDING_ENUMERATION_INCLUDED

#pragma GCC diagnostic push
#include <mapnik/warning_ignore.hpp>
#include <boost/python/converter/registered.hpp>  // for registered
#include <boost/python/enum.hpp>        // for enum_
#include <boost/python/implicit.hpp>    // for implicitly_convertible
#include <boost/python/to_python_converter.hpp>
#pragma GCC diagnostic pop

namespace mapnik {

template <typename EnumWrapper>
class enumeration_ :
        public boost::python::enum_<typename EnumWrapper::native_type>
{
    // some short cuts
    using base_type = boost::python::enum_<typename EnumWrapper::native_type>;
    using native_type = typename EnumWrapper::native_type;
public:
    enumeration_() :
        base_type( EnumWrapper::get_name().c_str() )
    {
        init();
    }
    enumeration_(const char * python_alias) :
        base_type( python_alias )
    {
        init();
    }
    enumeration_(const char * python_alias, const char * doc) :
        base_type( python_alias, doc )
    {
        init();
    }

private:
    struct converter
    {
        static PyObject* convert(EnumWrapper const& v)
        {
            // Redirect conversion to a static method of our base class's
            // base class. A free template converter will not work because
            // the base_type::base typedef is protected.
            // Lets hope MSVC agrees that this is legal C++
            using namespace boost::python::converter;
            return base_type::base::to_python(
                registered<native_type>::converters.m_class_object
                ,  static_cast<long>(native_type(v)));

        }
    };

    void init() {
        boost::python::implicitly_convertible<native_type, EnumWrapper>();
        boost::python::to_python_converter<EnumWrapper, converter >();
        for (auto const& kv : EnumWrapper::lookupMap())
        {
            base_type::value(kv.second.c_str(), kv.first);
        }
    }

};

} // end of namespace mapnik

#endif // MAPNIK_PYTHON_BINDING_ENUMERATION_INCLUDED
