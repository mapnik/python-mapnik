#! /bin/bash

function setup_postgres_settings() {
    export PGDATA=$PWD/local-postgres
    export PGHOST=$PWD/local-unix-socket
    export PGPORT=1111
}

function setup_postgres() {
    rm -rf -- "$PGDATA" "$PGHOST"
    mkdir -p -- "$PGDATA" "$PGHOST"

    initdb -N
    postgres -k "$PGHOST" -c fsync=off > postgres.log &
    sleep 2
    createdb template_postgis -T postgres
    psql template_postgis -e -c "CREATE PROCEDURAL LANGUAGE 'plpythonu' HANDLER plpython_call_handler;"
    psql template_postgis -e -c "CREATE EXTENSION postgis;"
    psql template_postgis -e -c "SELECT PostGIS_Full_Version();"
}

setup_postgres_settings
setup_postgres
