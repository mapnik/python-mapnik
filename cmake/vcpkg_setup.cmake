if(WIN32)
    set(VCPKG_TARGET_TRIPLET x64-windows-static)
endif()
set(CMAKE_TOOLCHAIN_FILE "~/vcpkg/scripts/buildsystems/vcpkg.cmake")
