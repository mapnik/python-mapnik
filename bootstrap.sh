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

ICU_VERSION="57.1"

function install_mason_deps() {
    install mapnik 333ef9f
    install jpeg_turbo 1.5.1 libjpeg
    install libpng 1.6.28 libpng
    install libtiff 4.0.7 libtiff
    install libpq 9.6.2
    install sqlite 3.17.0 libsqlite3
    install expat 2.2.0 libexpat
    install icu ${ICU_VERSION}
    install proj 4.9.3 libproj
    install pixman 0.34.0 libpixman-1
    install cairo 1.14.8 libcairo
    install webp 0.6.0 libwebp
    install libgdal 2.1.3 libgdal
    install boost 1.63.0
    install boost_libsystem 1.63.0
    install boost_libfilesystem 1.63.0
    install boost_libprogram_options 1.63.0
    install boost_libregex_icu57 1.63.0
    install freetype 2.7.1 libfreetype
    install harfbuzz 1.4.2-ft libharfbuzz
    # deps needed by python-mapnik (not mapnik core)
    install boost_libthread 1.63.0
    install boost_libpython 1.63.0
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
    echo "    python setup.py test"
}

main

set +eu
set +o pipefail
