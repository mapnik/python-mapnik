import glob,os
import sys
import threading
import mapnik
import pytest

from .utilities import execution_path

default_logging_severity = mapnik.logger.get_severity()


@pytest.mark.parametrize('from_string', [False, True])
def test_load_map_releases_gil(tmp_path, from_string):
    xml = '<Map>' + ''.join(
        '<Layer name="layer_%s"/>' % i for i in range(2000)
    ) + '</Map>'
    filename = tmp_path / 'map.xml'
    filename.write_text(xml)
    load = mapnik.load_map_from_string if from_string else mapnik.load_map
    source = xml if from_string else str(filename)
    m = mapnik.Map(256, 256)
    start = threading.Event()
    progressed = threading.Event()

    def other_thread():
        start.wait()
        progressed.set()

    thread = threading.Thread(target=other_thread)
    thread.start()
    interval = sys.getswitchinterval()
    try:
        # Only native map loading should let the other thread run here.
        sys.setswitchinterval(60)
        start.set()
        load(m, source, True)
        ran_during_loading = progressed.is_set()
    finally:
        sys.setswitchinterval(interval)
        start.set()
        thread.join()

    assert ran_during_loading
    assert len(m.layers) == 2000


@pytest.fixture(scope="module")
def setup_and_teardown():
    # All of the paths used are relative, if we run the tests
    # from another directory we need to chdir()
    os.chdir(execution_path('.'))
    # make the tests silent to suppress unsupported params from harfbuzz tests
    # TODO: remove this after harfbuzz branch merges
    mapnik.logger.set_severity(getattr(mapnik.severity_type, "None"))
    yield
    mapnik.logger.set_severity(default_logging_severity)

def test_broken_files(setup_and_teardown):
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
    assert len(failures) ==  0, '\n' + '\n'.join(failures)
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
            m = mapnik.Map(512, 512)
            base_path = os.path.dirname(filename)
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
    assert len(failures) == 0, '\n' + '\n'.join(failures)
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
            m = mapnik.Map(512, 512)
            base_path = os.path.dirname(filename)
            with open(filename, 'rb') as f:
                mapnik.load_map_from_string(m, f.read(), strict, base_path)
        except RuntimeError as e:
            # only test datasources that we have installed
            if not 'Could not create datasource' in str(e) \
               and not 'could not connect' in str(e):
                failures.append(
                    'Failed to load valid map %s (%s)' %
                    (filename, e))
    assert len(failures) == 0, '\n' + '\n'.join(failures)
