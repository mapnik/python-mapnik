import os
import shutil
import mapnik
import pytest
from .utilities import execution_path

@pytest.fixture(scope="module")
def setup():
    # All of the paths used are relative, if we run the tests
    # from another directory we need to chdir()
    os.chdir(execution_path('.'))
    yield


def make_tmp_map():
    m = mapnik.Map(512, 512)
    m.background_color = mapnik.Color('steelblue')
    ds = mapnik.MemoryDatasource()
    context = mapnik.Context()
    context.push('Name')
    f = mapnik.Feature(context, 1)
    f['Name'] = 'Hello'
    f.geometry = mapnik.Geometry.from_wkt('POINT (0 0)')
    ds.add_feature(f)
    s = mapnik.Style()
    r = mapnik.Rule()
    sym = mapnik.MarkersSymbolizer()
    sym.allow_overlap = True
    r.symbols.append(sym)
    s.rules.append(r)
    lyr = mapnik.Layer('Layer')
    lyr.datasource = ds
    lyr.styles.append('style')
    m.append_style('style', s)
    m.layers.append(lyr)
    return m

def draw_title(m, ctx, text, size=10, color=mapnik.Color('black')):
    """ Draw a Map Title near the top of a page."""
    middle = m.width / 2.0
    ctx.set_source_rgba(*cairo_color(color))
    ctx.select_font_face(
        "Helvetica",
        cairo.FONT_SLANT_NORMAL,
        cairo.FONT_WEIGHT_NORMAL)
    ctx.set_font_size(size)
    x_bearing, y_bearing, width, height = ctx.text_extents(text)[:4]
    ctx.move_to(middle - width / 2 - x_bearing, 20.0 - height / 2 - y_bearing)
    ctx.show_text(text)


def draw_neatline(m, ctx):
    w, h = m.width, m.height
    ctx.set_source_rgba(*cairo_color(mapnik.Color('black')))
    outline = [
        [0, 0], [w, 0], [w, h], [0, h]
    ]
    ctx.set_line_width(1)
    for idx, pt in enumerate(outline):
        if (idx == 0):
            ctx.move_to(*pt)
        else:
            ctx.line_to(*pt)
    ctx.close_path()
    inset = 6
    inline = [
        [inset, inset], [w - inset, inset], [w -
                                             inset, h - inset], [inset, h - inset]
    ]
    ctx.set_line_width(inset / 2)
    for idx, pt in enumerate(inline):
        if (idx == 0):
            ctx.move_to(*pt)
        else:
            ctx.line_to(*pt)
    ctx.close_path()
    ctx.stroke()


def cairo_color(c):
    """ Return a Cairo color tuple from a Mapnik Color."""
    ctx_c = (c.r / 255.0, c.g / 255.0, c.b / 255.0, c.a / 255.0)
    return ctx_c

if mapnik.has_pycairo():
    import cairo

    def test_passing_pycairo_context_svg(setup):
        m = make_tmp_map()
        m.zoom_to_box(mapnik.Box2d(-180, -90, 180, 90))
        test_cairo_file = '/tmp/mapnik-cairo-context-test.svg'
        surface = cairo.SVGSurface(test_cairo_file, m.width, m.height)
        expected_cairo_file = 'images/pycairo/cairo-cairo-expected.svg'
        context = cairo.Context(surface)
        mapnik.render(m, context)
        draw_title(m, context, "Hello Map", size=20)
        draw_neatline(m, context)
        surface.finish()
        if not os.path.exists(expected_cairo_file) or os.environ.get('UPDATE'):
            print('generated expected cairo surface file', expected_cairo_file)
            shutil.copy(test_cairo_file, expected_cairo_file)
        diff = abs(
            os.stat(expected_cairo_file).st_size -
            os.stat(test_cairo_file).st_size)
        msg = 'diff in size (%s) between actual (%s) and expected(%s)' % (
            diff, test_cairo_file, 'tests/python_tests/' + expected_cairo_file)
        assert diff < 1500,  msg
        os.remove(test_cairo_file)

    def test_passing_pycairo_context_pdf():
        m = make_tmp_map()
        m.zoom_to_box(mapnik.Box2d(-180, -90, 180, 90))
        test_cairo_file = '/tmp/mapnik-cairo-context-test.pdf'
        surface = cairo.PDFSurface(test_cairo_file, m.width, m.height)
        expected_cairo_file = 'images/pycairo/cairo-cairo-expected.pdf'
        context = cairo.Context(surface)
        mapnik.render(m, context)
        draw_title(m, context, "Hello Map", size=20)
        draw_neatline(m, context)
        surface.finish()
        if not os.path.exists(expected_cairo_file) or os.environ.get('UPDATE'):
            print('generated expected cairo surface file', expected_cairo_file)
            shutil.copy(test_cairo_file, expected_cairo_file)
        diff = abs(
            os.stat(expected_cairo_file).st_size -
            os.stat(test_cairo_file).st_size)
        msg = 'diff in size (%s) between actual (%s) and expected(%s)' % (
            diff, test_cairo_file, 'tests/python_tests/' + expected_cairo_file)
        assert diff < 1500, msg
        os.remove(test_cairo_file)

    def test_passing_pycairo_context_png():
        m = make_tmp_map()
        m.zoom_to_box(mapnik.Box2d(-180, -90, 180, 90))
        test_cairo_file = '/tmp/mapnik-cairo-context-test.png'
        surface = cairo.ImageSurface(cairo.FORMAT_ARGB32, m.width, m.height)
        expected_cairo_file = 'images/pycairo/cairo-cairo-expected.png'
        expected_cairo_file2 = 'images/pycairo/cairo-cairo-expected-reduced.png'
        context = cairo.Context(surface)
        mapnik.render(m, context)
        draw_title(m, context, "Hello Map", size=20)
        draw_neatline(m, context)
        surface.write_to_png(test_cairo_file)
        reduced_color_image = test_cairo_file.replace('png', '-mapnik.png')
        im = mapnik.Image.from_cairo(surface)
        im.save(reduced_color_image, 'png8')
        surface.finish()
        if not os.path.exists(expected_cairo_file) or os.environ.get('UPDATE'):
            print('generated expected cairo surface file', expected_cairo_file)
            shutil.copy(test_cairo_file, expected_cairo_file)
        diff = abs(
            os.stat(expected_cairo_file).st_size -
            os.stat(test_cairo_file).st_size)
        msg = 'diff in size (%s) between actual (%s) and expected(%s)' % (
            diff, test_cairo_file, 'tests/python_tests/' + expected_cairo_file)
        assert diff < 500, msg
        os.remove(test_cairo_file)
        if not os.path.exists(
                expected_cairo_file2) or os.environ.get('UPDATE'):
            print(
                'generated expected cairo surface file',
                expected_cairo_file2)
            shutil.copy(reduced_color_image, expected_cairo_file2)
        diff = abs(
            os.stat(expected_cairo_file2).st_size -
            os.stat(reduced_color_image).st_size)
        msg = 'diff in size (%s) between actual (%s) and expected(%s)' % (
            diff, reduced_color_image, 'tests/python_tests/' + expected_cairo_file2)
        assert diff < 500,  msg
        os.remove(reduced_color_image)

    if 'sqlite' in mapnik.DatasourceCache.plugin_names():
        def _pycairo_surface(type, sym):
            test_cairo_file = '/tmp/mapnik-cairo-surface-test.%s.%s' % (
                sym, type)
            expected_cairo_file = 'images/pycairo/cairo-surface-expected.%s.%s' % (
                sym, type)
            m = mapnik.Map(256, 256)
            mapnik.load_map(m, '../data/good_maps/%s_symbolizer.xml' % sym)
            m.zoom_all()
            if hasattr(cairo, '%sSurface' % type.upper()):
                surface = getattr(
                    cairo,
                    '%sSurface' %
                    type.upper())(
                    test_cairo_file,
                    m.width,
                    m.height)
                mapnik.render(m, surface)
                surface.finish()
                if not os.path.exists(
                        expected_cairo_file) or os.environ.get('UPDATE'):
                    print(
                        'generated expected cairo surface file',
                        expected_cairo_file)
                    shutil.copy(test_cairo_file, expected_cairo_file)
                diff = abs(
                    os.stat(expected_cairo_file).st_size -
                    os.stat(test_cairo_file).st_size)
                msg = 'diff in size (%s) between actual (%s) and expected(%s)' % (
                    diff, test_cairo_file, 'tests/python_tests/' + expected_cairo_file)
                if os.uname()[0] == 'Darwin':
                    assert diff < 2100, msg
                else:
                    assert diff < 23000, msg
                os.remove(test_cairo_file)
                return True
            else:
                print(
                    'skipping cairo.%s test since surface is not available' %
                    type.upper())
                return True

        def test_pycairo_svg_surface1():
            assert _pycairo_surface('svg', 'point')

        def test_pycairo_svg_surface2():
            assert _pycairo_surface('svg', 'building')

        def test_pycairo_svg_surface3():
            assert _pycairo_surface('svg', 'polygon')

        def test_pycairo_pdf_surface1():
            assert _pycairo_surface('pdf', 'point')

        def test_pycairo_pdf_surface2():
            assert _pycairo_surface('pdf', 'building')

        def test_pycairo_pdf_surface3():
            assert _pycairo_surface('pdf', 'polygon')
