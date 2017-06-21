#!/bin/bash

set -eu
set -o pipefail

# we pin the mason version to avoid changes in mason breaking builds
MASON_VERSION="1150c38"

function setup_mason() {
    mkdir -p ./mason
    curl -sSfL https://github.com/mapbox/mason/archive/${MASON_VERSION}.tar.gz | tar --gunzip --extract --strip-components=1 --exclude="*md" --exclude="test*" --directory=./mason
    export MASON_HOME=$(pwd)/mason_packages/.link
    export PATH=$(pwd)/mason:${PATH}
    export CXX=${CXX:-clang++}
    export CC=${CC:-clang}
}


setup_mason

set +eu
set +o pipefail