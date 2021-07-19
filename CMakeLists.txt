cmake_minimum_required(VERSION 3.15)
if(NOT DEFINED CMAKE_TOOLCHAIN_FILE)
    set(CMAKE_TOOLCHAIN_FILE "${CMAKE_CURRENT_LIST_DIR}/vcpkg/scripts/buildsystems/vcpkg.cmake")
endif()
project(python-mapnik)

find_package(Python COMPONENTS Development REQUIRED)
find_package(Boost COMPONENTS log python${Python_VERSION_MAJOR}${Python_VERSION_MINOR} REQUIRED)
find_package(mapnik CONFIG REQUIRED)
find_path(MAPBOX_GEOMETRY_INCLUDE_DIRS "mapbox/geometry.hpp" REQUIRED)

Python_add_library(python-mapnik MODULE 
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


target_link_libraries(python-mapnik PRIVATE
    Boost::boost 
    Boost::log 
    Boost::python${Python_VERSION_MAJOR}${Python_VERSION_MINOR}
    mapnik::core    
    mapnik::json
    mapnik::wkt
    mapnik::mapnik
)
target_include_directories(python-mapnik PRIVATE 
    ${MAPBOX_GEOMETRY_INCLUDE_DIRS}
)

set_target_properties(python-mapnik PROPERTIES OUTPUT_NAME "mapnik")
