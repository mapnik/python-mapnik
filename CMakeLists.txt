cmake_minimum_required(VERSION 3.15)
# include(cmake/vcpkg_setup.cmake)
project(${SKBUILD_PROJECT_NAME} LANGUAGES CXX VERSION ${SKBUILD_PROJECT_VERSION})

find_package(Python COMPONENTS Interpreter Development.Module)
find_package(mapnik CONFIG REQUIRED)
find_package(Boost REQUIRED COMPONENTS thread python${Python_VERSION_MAJOR}${Python_VERSION_MINOR})

#set(Python_SOABI ${SKBUILD_SOABI})
Python_add_library(_mapnik MODULE)
target_link_libraries(_mapnik PRIVATE
    mapnik::mapnik 
    mapnik::json
    mapnik::wkt
    # even though boost_thread is no longer used in mapnik core
    # we need to link in for boost_python to avoid missing symbol: _ZN5boost6detail12get_tss_dataEPKv / boost::detail::get_tss_data
    Boost::thread
    Boost::python${Python_VERSION_MAJOR}${Python_VERSION_MINOR}
    ICU::data ICU::i18n ICU::uc
)
target_sources(_mapnik PRIVATE
    src/boost_std_shared_shim.hpp
    src/mapnik_color.cpp
    src/mapnik_coord.cpp
    src/mapnik_datasource_cache.cpp
    src/mapnik_datasource.cpp
    src/mapnik_enumeration_wrapper_converter.hpp
    src/mapnik_enumeration.hpp
    src/mapnik_envelope.cpp
    src/mapnik_expression.cpp
    src/mapnik_feature.cpp
    src/mapnik_featureset.cpp
    src/mapnik_font_engine.cpp
    src/mapnik_fontset.cpp
    src/mapnik_gamma_method.cpp
    src/mapnik_geometry.cpp
    src/mapnik_grid_view.cpp
    src/mapnik_grid.cpp
    src/mapnik_image_view.cpp
    src/mapnik_image.cpp
    src/mapnik_label_collision_detector.cpp
    src/mapnik_layer.cpp
    src/mapnik_logger.cpp
    src/mapnik_map.cpp
    src/mapnik_palette.cpp
    src/mapnik_parameters.cpp
    src/mapnik_proj_transform.cpp
    src/mapnik_projection.cpp
    src/mapnik_python.cpp
    src/mapnik_query.cpp
    src/mapnik_raster_colorizer.cpp
    src/mapnik_rule.cpp
    src/mapnik_scaling_method.cpp
    src/mapnik_style.cpp
    src/mapnik_svg.hpp
    src/mapnik_symbolizer.cpp
    src/mapnik_threads.hpp
    src/mapnik_value_converter.hpp
    src/mapnik_view_transform.cpp
    src/python_grid_utils.cpp
    src/python_grid_utils.hpp
    src/python_optional.hpp
    src/python_to_value.hpp
)

install(TARGETS _mapnik LIBRARY DESTINATION ${SKBUILD_PROJECT_NAME})
