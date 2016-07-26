#!/usr/bin/env bash

set -eu
set -o pipefail

function install() {
    MASON_PLATFORM_ID=$(mason env MASON_PLATFORM_ID)
    if [[ ! -d ./mason_packages/${MASON_PLATFORM_ID}/${1}/ ]]; then
        mason install $1 $2
        mason link $1 $2
    fi
}

ICU_VERSION="55.1"

function install_mason_deps() {
    install mapnik latest &
    install ccache 3.2.4 &
    install jpeg_turbo 1.4.0 libjpeg &
    install libpng 1.6.20 libpng &
    install libtiff 4.0.4beta libtiff &
    install libpq 9.4.1 &
    install sqlite 3.8.8.3 libsqlite3 &
    install expat 2.1.0 libexpat &
    wait
    install icu ${ICU_VERSION} &
    install proj 4.8.0 libproj &
    install pixman 0.32.6 libpixman-1 &
    install cairo 1.14.2 libcairo &
    wait
    install webp 0.4.2 libwebp &
    install gdal 1.11.2 libgdal &
    install boost 1.61.0 &
    install boost_libthread 1.61.0 &
    install boost_libpython 1.61.0 &
    install boost_libsystem 1.61.0 &
    install boost_libfilesystem 1.61.0 &
    install boost_libprogram_options 1.61.0 &
    install boost_libregex 1.61.0 &
    install freetype 2.6 libfreetype &
    install harfbuzz 0.9.41 libharfbuzz &
    wait
}

function setup_runtime_settings() {
    local MASON_LINKED_ABS=$(pwd)/mason_packages/.link
    export PROJ_LIB=${MASON_LINKED_ABS}/share/proj
    export ICU_DATA=${MASON_LINKED_ABS}/share/icu/${ICU_VERSION}
    export GDAL_DATA=${MASON_LINKED_ABS}/share/gdal
    if [[ $(uname -s) == 'Darwin' ]]; then
        export DYLD_LIBRARY_PATH=$(pwd)/mason_packages/.link/lib:${DYLD_LIBRARY_PATH}
    else
        export LD_LIBRARY_PATH=$(pwd)/mason_packages/.link/lib:${LD_LIBRARY_PATH}
    fi
    export PATH=$(pwd)/mason_packages/.link/bin:${PATH}
}

function main() {
    source scripts/setup_mason.sh
    setup_mason
    install_mason_deps
    setup_runtime_settings
    echo "Ready, now run:"
    echo ""
    echo "    make test"
}

main

set +eu
set +o pipefail