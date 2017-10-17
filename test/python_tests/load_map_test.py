#!/usr/bin/env python

import glob
import os

from nose.tools import eq_

import mapnik

from .utilities import execution_path, run_all


default_logging_severity = mapnik.logger.get_severity()


def setup():
    # make the tests silent to suppress unsupported params from harfbuzz tests
    # TODO: remove this after harfbuzz branch merges
    mapnik.logger.set_severity(getattr(mapnik.severity_type, "None"))
    # All of the paths used are relative, if we run the tests
    # from another directory we need to chdir()
    os.chdir(execution_path('.'))


def teardown():
    mapnik.logger.set_severity(default_logging_severity)


def test_broken_files():
    default_logging_severity = mapnik.logger.get_severity()
    mapnik.logger.set_severity(getattr(mapnik.severity_type, "None"))
    broken_files = glob.glob("../data/broken_maps/*.xml")
    # Add a filename that doesn't exist
    broken_files.append("../data/broken/does_not_exist.xml")

    failures = []
    for filename in broken_files:
        try:
            m = mapnik.Map(512, 512)
            strict = True
            mapnik.load_map(m, filename, strict)
            failures.append(
                'Loading broken map (%s) did not raise RuntimeError!' %
                filename)
        except RuntimeError:
            pass
    eq_(len(failures), 0, '\n' + '\n'.join(failures))
    mapnik.logger.set_severity(default_logging_severity)


def test_can_parse_xml_with_deprecated_properties():
    default_logging_severity = mapnik.logger.get_severity()
    mapnik.logger.set_severity(getattr(mapnik.severity_type, "None"))
    files_with_deprecated_props = glob.glob("../data/deprecated_maps/*.xml")

    failures = []
    for filename in files_with_deprecated_props:
        try:
            m = mapnik.Map(512, 512)
            strict = True
            mapnik.load_map(m, filename, strict)
            base_path = os.path.dirname(filename)
            m = mapnik.Map(512, 512)
            mapnik.load_map_from_string(
                m,
                open(
                    filename,
                    'rb').read(),
                strict,
                base_path)
        except RuntimeError as e:
            # only test datasources that we have installed
            if not 'Could not create datasource' in str(e) \
               and not 'could not connect' in str(e):
                failures.append(
                    'Failed to load valid map %s (%s)' %
                    (filename, e))
    eq_(len(failures), 0, '\n' + '\n'.join(failures))
    mapnik.logger.set_severity(default_logging_severity)


def test_good_files():
    good_files = glob.glob("../data/good_maps/*.xml")
    good_files.extend(glob.glob("../visual_tests/styles/*.xml"))

    failures = []
    for filename in good_files:
        try:
            m = mapnik.Map(512, 512)
            strict = True
            mapnik.load_map(m, filename, strict)
            base_path = os.path.dirname(filename)
            with open(filename, 'rb') as f:
                m = mapnik.Map(512, 512)
                mapnik.load_map_from_string(m, f.read(), strict, base_path)
        except RuntimeError as e:
            # only test datasources that we have installed
            if not 'Could not create datasource' in str(e) \
               and not 'could not connect' in str(e):
                failures.append(
                    'Failed to load valid map %s (%s)' %
                    (filename, e))
    eq_(len(failures), 0, '\n' + '\n'.join(failures))

if __name__ == "__main__":
    setup()
    exit(run_all(eval(x) for x in dir() if x.startswith("test_")))
