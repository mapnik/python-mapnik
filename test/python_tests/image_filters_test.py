import re, os
import mapnik
import pytest
from .utilities import side_by_side_image, execution_path

@pytest.fixture(scope="module")
def setup():
    # All of the paths used are relative, if we run the tests
    # from another directory we need to chdir()
    os.chdir(execution_path('.'))
    yield

def replace_style(m, name, style):
    m.remove_style(name)
    m.append_style(name, style)

def test_append():
    s = mapnik.Style()
    assert s.image_filters ==  ''
    s.image_filters = 'gray'
    assert s.image_filters ==  'gray'
    s.image_filters = 'sharpen'
    assert s.image_filters ==  'sharpen'

if 'shape' in mapnik.DatasourceCache.plugin_names():
    def test_style_level_image_filter(setup):
        m = mapnik.Map(256, 256)
        mapnik.load_map(m, '../data/good_maps/style_level_image_filter.xml')
        m.zoom_all()
        successes = []
        fails = []
        for name in ("", "agg-stack-blur(2,2)", "blur",
                     "edge-detect", "emboss", "gray", "invert",
                     "sharpen", "sobel", "x-gradient", "y-gradient"):
            if name == "":
                filename = "none"
            else:
                filename = re.sub(r"[^-_a-z.0-9]", "", name)
            # find_style returns a copy of the style object
            style_markers = m.find_style("markers")
            style_markers.image_filters = name
            style_labels = m.find_style("labels")
            style_labels.image_filters = name
            # replace the original style with the modified one
            replace_style(m, "markers", style_markers)
            replace_style(m, "labels", style_labels)
            im = mapnik.Image(m.width, m.height)
            mapnik.render(m, im)
            actual = '/tmp/mapnik-style-image-filter-' + filename + '.png'
            expected = 'images/style-image-filter/' + filename + '.png'
            im.save(actual, "png32")
            if not os.path.exists(expected) or os.environ.get('UPDATE'):
                print('generating expected test image: %s' % expected)
                im.save(expected, 'png32')
            expected_im = mapnik.Image.open(expected)
            # compare them
            if im.to_string('png32') == expected_im.to_string('png32'):
                successes.append(name)
            else:
                fails.append(
                    'failed comparing actual (%s) and expected(%s)' %
                    (actual, expected))
                fail_im = side_by_side_image(expected_im, im)
                fail_im.save(
                    '/tmp/mapnik-style-image-filter-' +
                    filename +
                    '.fail.png',
                    'png32')
        assert len(fails) ==  0, '\n' + '\n'.join(fails)
