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

//pybind11
#include <pybind11/pybind11.h>
#include <pybind11/stl.h>
#include <mapnik/util/variant.hpp>

namespace PYBIND11_NAMESPACE { namespace detail {
    template <typename... Ts>
    struct type_caster<mapnik::util::variant<Ts...>> : variant_caster<mapnik::util::variant<Ts...>> {};

    // Specifies the function used to visit the variant -- `apply_visitor` instead of `visit`
    template <>
    struct visit_helper<mapnik::util::variant> {
        template <typename... Args>
        static auto call(Args &&...args) -> decltype(mapnik::util::apply_visitor(args...)) {
            return mapnik::util::apply_visitor(args...);
        }
    };
}} // namespace PYBIND11_NAMESPACE::detail
