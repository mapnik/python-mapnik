#!/bin/bash

# we pin the mason version to avoid changes in mason breaking builds
MASON_ARCHIVE_VERSION="v0.20.0"
MASON_ARCHIVE_BASE="https://github.com/mapbox/mason/archive"

function install() {
    local package_prefix=
    package_prefix=$(mason prefix $1 $2) || return
    if [ ! -d "$package_prefix/" ]; then
        mason install $1 $2 || return
    fi
    mason link $1 $2
}

function mason_packages() {
    printf '%s\n' "${MASON_ROOT:-"$PWD/mason_packages"}"
}

function setup_mason() {
    local cdup=
    if cdup=$(git rev-parse --show-cdup 2>/dev/null); then
        # we are inside *some* git repository (not necessarily python-mapnik)
        if git submodule status "${cdup}mason" >/dev/null 2>&1; then
            # there is submodule "mason" (assume we are in python-mapnik)
            # update the submodule, bail out on failure
            git submodule update --init "${cdup}mason" ||
                return
        else
            # there is no submodule named "mason"
            # proceed as if we were outside git repository
            cdup=
        fi
    fi
    if [ ! -d "${cdup}mason/" ]; then
        # the directory doesn't exist, and we are either outside any git
        # repository, or in a repository with no submodule named "mason"
        mkdir -p "${cdup}mason/"
        # download and unpack mason archive
        curl -sSfL "${MASON_ARCHIVE_BASE}/${MASON_ARCHIVE_VERSION}.tar.gz" |
            tar --extract --gunzip --directory="${cdup}mason/" \
                --strip-components=1 --exclude="test" ||
            return
    fi
    export PATH=$(cd "${cdup}mason" && pwd):${PATH}
    export CXX=${CXX:-clang++}
    export CC=${CC:-clang}
}


setup_mason
