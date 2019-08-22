#!/usr/bin/env bash

BOOST_VERSION="1.66.0"
ICU_VERSION="57.1"
MAPNIK_VERSION="a0ea7db1a"

function install_mason_deps() (
    # subshell
    set -eu
    install_mapnik_deps
    install mapnik ${MAPNIK_VERSION}
)

function install_mapnik_deps() (
    # subshell
    set -eu
    install jpeg_turbo 1.5.1
    install libpng 1.6.28
    install libtiff 4.0.7
    install libpq 9.6.2
    install sqlite 3.17.0
    install expat 2.2.0
    install icu ${ICU_VERSION}
    install proj 4.9.3
    install pixman 0.34.0
    install cairo 1.14.8
    install webp 0.6.0
    install libgdal 2.1.3
    install boost ${BOOST_VERSION}
    install boost_libsystem ${BOOST_VERSION}
    install boost_libfilesystem ${BOOST_VERSION}
    install boost_libprogram_options ${BOOST_VERSION}
    install boost_libregex_icu${ICU_VERSION%%.*} ${BOOST_VERSION}
    install freetype 2.7.1
    install harfbuzz 1.4.2-ft
    # deps needed by python-mapnik (not mapnik core)
    install boost_libthread ${BOOST_VERSION}
    install boost_libpython ${BOOST_VERSION}
)

function setup_runtime_settings() {
    # PWD and ICU_VERSION are expanded here, but MASON_ROOT and PATH
    # expansion must be deferred to the generated script, so that it
    # can be used later
    printf 'export %s=${MASON_ROOT:-%q}\n'          \
            MASON_ROOT  "$PWD/mason_packages"       \
        > ./mason-config.env
    printf 'export %s=$%s\n'                                            \
            MASON_BIN   "{MASON_ROOT}/.link/bin"                        \
            PROJ_LIB    "{MASON_ROOT}/.link/share/proj"                 \
            ICU_DATA    "{MASON_ROOT}/.link/share/icu/${ICU_VERSION}"   \
            GDAL_DATA   "{MASON_ROOT}/.link/share/gdal"                 \
            PATH    '{MASON_BIN}:${PATH}'                               \
            PATH    '{PATH//":${MASON_BIN}:"/:}  # remove duplicates'   \
        >> ./mason-config.env
    source ./mason-config.env
}

function main() {
    source scripts/setup_mason.sh
    [ $? = 0 ] && install_mason_deps
    [ $? = 0 ] && setup_runtime_settings
    [ $? = 0 ] || return
    echo "Ready, now run:"
    echo ""
    echo "    make test"
}

main
