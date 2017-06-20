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
    install mapnik 3.0.15
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
    install boost 1.63.0
    install boost_libsystem 1.63.0
    install boost_libfilesystem 1.63.0
    install boost_libprogram_options 1.63.0
    install boost_libregex_icu57 1.63.0
    install freetype 2.7.1
    install harfbuzz 1.4.2-ft
    # deps needed by python-mapnik (not mapnik core)
    install boost_libthread 1.63.0
    install boost_libpython 1.63.0
    install postgis 2.3.2-1
}

function setup_runtime_settings() {
    local MASON_LINKED_ABS=$(pwd)/mason_packages/.link
    echo "export PROJ_LIB=${MASON_LINKED_ABS}/share/proj" > mason-config.env
    echo "export ICU_DATA=${MASON_LINKED_ABS}/share/icu/${ICU_VERSION}" >> mason-config.env
    echo "export GDAL_DATA=${MASON_LINKED_ABS}/share/gdal" >> mason-config.env
    echo "export PATH=$(pwd)/mason_packages/.link/bin:${PATH}" >> mason-config.env
    echo "export PGTEMP_DIR=$(pwd)/local-tmp" >> mason-config.env
    echo "export PGDATA=$(pwd)/local-postgres" >> mason-config.env
    echo "export PGHOST=$(pwd)/local-unix-socket" >> mason-config.env
    echo "export PGPORT=1111" >> mason-config.env

    source mason-config.env
    rm -rf ${PGHOST}
    mkdir -p ${PGHOST}
    rm -rf ${PGDATA}
    mkdir -p ${PGDATA}
    rm -rf ${PGTEMP_DIR}
    mkdir -p ${PGTEMP_DIR}
    ./mason_packages/.link/bin/initdb
    sleep 2
    ./mason_packages/.link/bin/postgres -k ${PGHOST} > postgres.log &
    sleep 2
    ./mason_packages/.link/bin/createdb template_postgis -T postgres
    ./mason_packages/.link/bin/psql template_postgis -c "CREATE TABLESPACE temp_disk LOCATION '${PGTEMP_DIR}';"
    ./mason_packages/.link/bin/psql template_postgis -c "SET temp_tablespaces TO 'temp_disk';"
    ./mason_packages/.link/bin/psql template_postgis -c "CREATE PROCEDURAL LANGUAGE 'plpythonu' HANDLER plpython_call_handler;"
    ./mason_packages/.link/bin/psql template_postgis -c "CREATE EXTENSION postgis;"
    ./mason_packages/.link/bin/psql template_postgis -c "SELECT PostGIS_Full_Version();"
    ./mason_packages/.link/bin/pg_ctl -w stop
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