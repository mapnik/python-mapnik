# -*- coding: utf-8 -*-

"""Mapnik classes to assist in creating printable maps."""

from __future__ import absolute_import, print_function

import logging
import math

from mapnik import Box2d, Coord, Geometry, Layer, Map, Projection, Style, render
from mapnik.printing.conversions import m2pt, m2px
from mapnik.printing.formats import pagesizes
from mapnik.printing.scales import any_scale, default_scale, deg_min_sec_scale, sequence_scale

try:
    import cairo
except ImportError:
    raise ImportError("Could not import pycairo; PDF rendering only available when pycairo is available")

try:
    import pangocairo
    import pango
    HAS_PANGOCAIRO_MODULE = True
except ImportError:
    HAS_PANGOCAIRO_MODULE = False

try:
    from PyPDF2 import PdfFileReader, PdfFileWriter
    from PyPDF2.generic import (ArrayObject, DecodedStreamObject, DictionaryObject, FloatObject, NameObject,
        NumberObject, TextStringObject)
    HAS_PYPDF2 = True
except ImportError:
    HAS_PYPDF2 = False

"""
Style of centering to use with the map.

CENTERING_NONE: map will be placed in the top left corner
CENTERING_CONSTRAINED_AXIS: map will be centered on the most constrained axis (e.g. vertical for a portrait page); a square
    map will be constrained horizontally
CENTERING_UNCONSTRAINED_AXIS: map will be centered on the unconstrained axis
CENTERING_VERTICAL: map will be centered vertically
CENTERING_HORIZONTAL: map will be centered horizontally
CENTERING_BOTH: map will be centered vertically and horizontally
"""
CENTERING_NONE = 0
CENTERING_CONSTRAINED_AXIS = 1
CENTERING_UNCONSTRAINED_AXIS = 2
CENTERING_VERTICAL = 3
CENTERING_HORIZONTAL = 4
CENTERING_BOTH = 5

# some predefined resolutions in DPI
DPI_72 = 72
DPI_150 = 150
DPI_300 = 300
DPI_600 = 600

L = logging.getLogger("mapnik.printing")


class PDFPrinter(object):

    """
    Main class for creating PDF print outs. Basic usage is along the lines of

    import mapnik
    import mapnik.printing

    page = mapnik.printing.PDFPrinter()
    m = mapnik.Map(100,100)
    mapnik.load_map(m, "my_xml_map_description", True)
    m.zoom_all()
    page.render_map(m, "my_output_file.pdf")
    """

    def __init__(self,
                 pagesize=pagesizes["a4"],
                 margin=0.005,
                 box=None,
                 percent_box=None,
                 scale_function=default_scale,
                 resolution=DPI_72,
                 preserve_aspect=True,
                 centering=CENTERING_CONSTRAINED_AXIS,
                 is_latlon=False,
                 use_ocg_layers=False,
                 font_name="DejaVu Sans"):
        """
        Args:
            pagesize: tuple of page size in meters, see predefined sizes in mapnik.formats module
            margin: page margin in meters
            box: the box to render the map into. Must be within page area, margin excluded. 
                This should be a Mapnik Box2d object. Default is the full page without margin.
            percent_box: similar to box argument but specified as a percent (0->1) of the full page size.
                If both box and percent_box are specified percent_box will be used.
            scale: scale helper to use when rounding the map scale. This should be a function that takes a single
                float and returns a float which is at least as large as the value passed in. This is a 1:x scale.
            resolution: the resolution used to render non vector elements (in DPI).
            preserve_aspect: whether to preserve map aspect ratio or not. This defaults to True and it is recommended
                you do not change it unless you know what you are doing: scales and so on will not work if it is
                set to False.
            centering: centering rules for maps where the scale rounding has reduced the map size. This should
                be a value from the mapnik.utils.centering class. The default is to center on the maps constrained
                axis. Typically this will be horizontal for portrait pages and vertical for landscape pages.
            is_latlon: whether the map is in lat lon degrees or not.
            use_ocg_layers: create OCG layers in the PDF, requires PyPDF2
            font_name: the font name used each time text is written (e.g., legend titles, representative fraction, etc.)
        """
        self._pagesize = pagesize
        self._margin = margin
        self._box = box
        self._resolution = resolution
        self._centering = centering
        self._is_latlon = is_latlon
        self._use_ocg_layers = use_ocg_layers

        self._surface = None
        self._layer_names = []
        self._filename = None

        self.map_box = None

        self.rounded_mapscale = None
        self._scale_function = scale_function
        self._preserve_aspect = preserve_aspect
        if not preserve_aspect:
            self._scale_function = any_scale

        if percent_box:
            self._box = Box2d(percent_box[0] * pagesize[0], percent_box[1] * pagesize[1],
                              percent_box[2] * pagesize[0], percent_box[3] * pagesize[1])

        self.font_name = font_name

    def render_map(self, m, filename):
        """Renders the given map to filename."""
        self._surface = cairo.PDFSurface(filename, m2pt(self._pagesize[0]), m2pt(self._pagesize[1]))
        ctx = cairo.Context(self._surface)

        # store the output filename so that we can post-process the PDF
        self._filename = filename

        (eff_width, eff_height) = self._get_render_area_size()
        (mapw, maph) = self._get_map_render_area_size(m, eff_width, eff_height)

        # set the map pixel size so that raster elements render at specified resolution
        m.resize(*self._get_map_pixel_size(mapw, maph))

        (tx, ty) = self._get_render_corner((mapw, maph), m)

        self._render_map_background(m, ctx, tx, ty)
        self._render_layers_maps(m, ctx, tx, ty)

        self.map_box = Box2d(tx, ty, tx + mapw, ty + maph)

    def _get_render_area_size(self):
        """Returns the width and height in meters of the page's render area."""
        render_area = self._get_render_area()
        return (render_area.width(), render_area.height())

    def _get_render_area(self):
        """Returns the page's area available for rendering. All dimensions are in meters."""
        render_area = Box2d(
            self._margin,
            self._margin,
            self._pagesize[0] -
            self._margin,
            self._pagesize[1] -
            self._margin)

        # if the user specified a box to render to, we take the intersection
        # of that box with the page area available
        if self._box:
            return render_area.intersect(self._box)

        return render_area

    def _get_map_render_area_size(self, m, eff_width, eff_height):
        """
        Returns the render area for the map, i.e., a width and height in meters.
        Preserves the map aspect by default.
        """
        scalefactor = self._get_map_scalefactor(m, eff_width, eff_height)
        mapw = eff_width * scalefactor
        maph = eff_height * scalefactor

        page_aspect = eff_width / eff_height
        map_aspect = m.envelope().width() / m.envelope().height()
        if self._preserve_aspect:
            if map_aspect > page_aspect:
                maph = mapw * (1 / map_aspect)
            else:
                mapw = maph * map_aspect

        return (mapw, maph)

    def _get_map_scalefactor(self, m ,eff_width, eff_height):
        """Returns the map scale factor based on effective render area size in meters."""
        scalex = m.envelope().width() / eff_width
        scaley = m.envelope().height() / eff_height
        scale = max(scalex, scaley)
        rounded_mapscale = self._scale_function(scale)
        self.rounded_mapscale = rounded_mapscale
        scalefactor = scale / rounded_mapscale

        return scalefactor

    def _get_map_pixel_size(self, width_page_m, height_page_m):
        """
        For a given map size in page coordinates, returns a tuple of the map
        'pixel' size based on the defined resolution.
        """
        return (int(m2px(width_page_m, self._resolution)),
                int(m2px(height_page_m, self._resolution)))

    def _get_render_corner(self, render_size, m):
        """Returns the top left corner of the box we should render our map into."""
        available_area = self._get_render_area()

        x = available_area[0]
        y = available_area[1]

        if self._has_horizontal_centering(m):
            x += (available_area.width() - render_size[0]) / 2

        if self._has_vertical_centering(m):
            y += (available_area.height() - render_size[1]) / 2
        return (x, y)

    def _has_horizontal_centering(self, m):
        """Returns whether the map has an horizontal centering or not."""
        is_map_size_constrained = self._is_map_size_constrained(m)

        if (self._centering == CENTERING_BOTH or
                self._centering == CENTERING_HORIZONTAL or
                (self._centering == CENTERING_CONSTRAINED_AXIS and is_map_size_constrained) or
                (self._centering == CENTERING_UNCONSTRAINED_AXIS and not is_map_size_constrained)):
            return True
        else:
            return False

    def _has_vertical_centering(self, m):
        """Returns whether the map has a vertical centering or not."""
        is_map_size_constrained = self._is_map_size_constrained(m)

        if (self._centering == CENTERING_BOTH or
                self._centering == CENTERING_VERTICAL or
                (self._centering == CENTERING_CONSTRAINED_AXIS and not is_map_size_constrained) or
                (self._centering == CENTERING_UNCONSTRAINED_AXIS and is_map_size_constrained)):
            return True
        else:
            return False

    def _is_map_size_constrained(self, m):
        """Tests whether the map's size is constrained on the horizontal or vertical axes."""
        available_area = self._get_render_area_size()
        map_aspect = m.envelope().width() / m.envelope().height()
        page_aspect = available_area[0] / available_area[1]

        return map_aspect > page_aspect

    def _render_map_background(self, m, ctx, tx, ty):
        """
        Renders the map background if there is one. If the user set use_ocg_layers to True, we put
        the background in a separate layer.
        """
        if m.background or m.background_image or m.background_color:
            background_map = Map(m.width,m.height,m.srs)
            if m.background:
                background_map.background = m.background
            if m.background_image:
                background_map.background_image = m.background_image
            if m.background_color:
                background_map.background_color = m.background_color

            background_map.zoom_to_box(m.envelope())
            self._render_layer_map(background_map, ctx, tx, ty)

            if self._use_ocg_layers:
                self._surface.show_page()
                self._layer_names.append("Map Background")

    def _render_layers_maps(self, m, ctx, tx, ty):
        """Renders a layer as an individual map within a parent Map object."""
        for layer in m.layers:
            self._layer_names.append(layer.name)

            layer_map = self._create_layer_map(m, layer)
            self._render_layer_map(layer_map, ctx, tx, ty)

            if self.map_spans_antimeridian(m):
                old_env = m.envelope()
                if m.envelope().minx < -180:
                    delta = 360
                else:
                    delta = -360
                m.zoom_to_box(
                    Box2d(
                        old_env.minx + delta,
                        old_env.miny,
                        old_env.maxx + delta,
                        old_env.maxy))
                self._render_layer_map(layer_map, ctx, tx, ty)
                # restore the original env
                m.zoom_to_box(old_env)

            if self._use_ocg_layers:
                self._surface.show_page()

    def _create_layer_map(self, m, layer):
        """
        Instantiates and returns a Map object for the layer.
        The layer Map has the parent Map dimensions.
        """
        layer_map = Map(m.width, m.height, m.srs)
        layer_map.layers.append(layer)

        for s in layer.styles:
            layer_map.append_style(s, m.find_style(s))

        layer_map.zoom_to_box(m.envelope())

        return layer_map

    def _render_layer_map(self, layer_map, ctx, tx, ty):
        """Renders the layer map. Scales the cairo context to the specified resolution."""
        ctx.save()
        ctx.translate(m2pt(tx), m2pt(ty))
        # cairo defaults to 72dpi
        ctx.scale(72.0 / self._resolution, 72.0 / self._resolution)

        # we clip the context to the map rectangle in order to restrict the background to that area
        ctx.rectangle(0, 0, layer_map.width , layer_map.height)
        ctx.clip()

        render(layer_map, ctx)
        ctx.restore()

    def map_spans_antimeridian(self, m):
        """Returns whether the map spans the antimeridian or not."""
        if self._is_latlon and (m.envelope().minx < -180 or m.envelope().maxx > 180):
            return True
        else:
            return False

    def render_grid_on_map(self, m, grid_layer_name="Coordinates Grid Overlay"):
        """
        Adds a grid overlay on the map, i.e., horizontal and vertical axes plus boxes around the map.

        Axes are drawn as 0.5px gray lines.
        Boxes alternate between black fill / white stroke and white fill / black stroke. Font is DejaVu Sans.
        """
        (div_size, page_div_size) = self._get_sensible_scalebar_size(m)

        # render horizontal axes
        (first_value_x, first_value_x_percent) = self._get_scale_axes_first_values(
            div_size,
            m.envelope().minx,
            m.envelope().width())
        self._render_grid_axes_and_boxes_on_map(
            first_value_x,
            first_value_x_percent,
            page_div_size,
            div_size,
            True)

        # render vertical axes
        (first_value_y, first_value_y_percent) = self._get_scale_axes_first_values(
            div_size,
            m.envelope().miny,
            m.envelope().height())
        self._render_grid_axes_and_boxes_on_map(
            first_value_y,
            first_value_y_percent,
            page_div_size,
            div_size,
            False)

        if self._use_ocg_layers:
            self._surface.show_page()
            self._layer_names.append(grid_layer_name)

    def _get_sensible_scalebar_size(self, m, num_divisions=8, width=-1):
        """
        Returns a sensible scalebar size based on the map envelope, the number of divisions expected
        in the scalebar, and optionally the width of the containing box.
        """
        div_size = sequence_scale(m.envelope().width() / num_divisions, [1, 2, 5])

        # ensures we can fit the bar within page area width if specified
        page_div_size = self.map_box.width() * div_size / m.envelope().width()
        while width > 0 and page_div_size > width:
            div_size /= 2.0
            page_div_size /= 2.0

        return (div_size, page_div_size)

    def _get_scale_axes_first_values(self, div_size, map_envelope_start, map_envelope_side_length):
        """
        Returns the first value and the first value percent - how far is that value on the map side length -
        for the scale axes.
        """
        first_value = (math.floor(map_envelope_start / div_size) + 1) * div_size
        first_value_percent = (first_value - map_envelope_start) / map_envelope_side_length

        return (first_value, first_value_percent)

    def _render_grid_axes_and_boxes_on_map(self, first, first_percent, page_div_size, div_size, is_x_axis):
        """
        Renders the horizontal or vertical axes and corresponding boxes on the map depending on the is_x_axis
        parameter.

        Axes are drawn as 0.5px gray lines.
        Boxes alternate between black fill / white stroke and white fill / black stroke. Font is DejaVu Sans.
        """
        ctx = cairo.Context(self._surface)

        if is_x_axis:
            (start, end, boundary_start, boundary_end) = self.map_box.minx, self.map_box.maxx, self.map_box.miny, self.map_box.maxy
        else:
            (start, end, boundary_start, boundary_end) = self.map_box.miny, self.map_box.maxy, self.map_box.minx, self.map_box.maxx

            ctx.translate(m2pt(self.map_box.center().x), m2pt(self.map_box.center().y))
            ctx.rotate(-math.pi / 2)
            ctx.translate(-m2pt(self.map_box.center().y), -m2pt(self.map_box.center().x))

        label_value = first - div_size
        if self._is_latlon and label_value < -180:
            label_value += 360

        prev = start
        text = None
        black_rgb = (0.0, 0.0, 0.0)
        fill_color = black_rgb
        value = first_percent * (end - start) + start

        while value < end:
            self._draw_line(ctx, m2pt(value), m2pt(boundary_start), m2pt(value), m2pt(boundary_end), line_width=0.5)
            self._render_grid_boxes(ctx, boundary_start, boundary_end, prev, value, text=text, fill_color=fill_color)

            prev = value
            value += page_div_size
            fill_color = [1.0 - z for z in fill_color]
            label_value += div_size
            if self._is_latlon and label_value > 180:
                label_value -= 360
            text = "%d" % label_value
        else:
            # ensure that the last box gets drawn
            self._render_grid_boxes(ctx, boundary_start, boundary_end, prev, end, fill_color=fill_color)

    def _draw_line(self, ctx, start_x, start_y, end_x, end_y, line_width=1, stroke_color=(0.5, 0.5, 0.5)):
        """
        Draws a line from (start_x, start_y) to (end_x, end_y) on the specified cairo context.
        By default, the line drawn is 1px wide and gray.
        """
        ctx.save()

        ctx.move_to(start_x, start_y)
        ctx.line_to(end_x, end_y)
        ctx.set_source_rgb(*stroke_color)
        ctx.set_line_width(line_width)
        ctx.stroke()

        ctx.restore()

    def _render_grid_boxes(self, ctx, boundary_start, boundary_end, prev, value, text=None, border_size=8, fill_color=(0.0, 0.0, 0.0)):
        """Renders the scale boxes at each end of the grid overlay."""
        for bar in (m2pt(boundary_start) - border_size, m2pt(boundary_end)):
            rectangle = Rectangle(m2pt(prev), bar, m2pt(value - prev), border_size)
            self._render_box(ctx, rectangle, text, fill_color=fill_color)

    def _render_box(self, ctx, rectangle, text=None, stroke_color=(0.0, 0.0, 0.0), fill_color=(1.0, 1.0, 1.0)):
        """
        Renders a box with top left corner positioned at (x,y).
        Default design is white fill and black stroke.
        """
        ctx.save()

        line_width = 1

        ctx.set_line_width(line_width)
        ctx.set_source_rgb(*fill_color)
        ctx.rectangle(rectangle.x, rectangle.y, rectangle.width, rectangle.height)
        ctx.fill()

        ctx.set_source_rgb(*stroke_color)
        ctx.rectangle(rectangle.x, rectangle.y, rectangle.width, rectangle.height)
        ctx.stroke()

        if text:
            ctx.move_to(rectangle.x + 1, rectangle.y)
            self.write_text(ctx, text, size=rectangle.height - 2, stroke_color=[1 - z for z in fill_color])

        ctx.restore()

    def write_text(self, ctx, text, box_width=None, size=10, stroke_color=(0.0, 0.0, 0.0), alignment=None):
        """
        Writes the text to the specified context.

        Returns:
            A rectangle (x, y, width, height) representing the extents of the text drawn
        """
        if HAS_PANGOCAIRO_MODULE:
            return self._write_text_pangocairo(ctx, text, box_width=box_width, size=size, stroke_color=stroke_color, alignment=alignment)
        else:
            return self._write_text_cairo(ctx, text, size=size, stroke_color=stroke_color)

    def _write_text_pangocairo(self, ctx, text, box_width=None, size=10, stroke_color=(0.0, 0.0, 0.0), alignment=None):
        """
        Use a pango.Layout object to write text to the cairo Context specified as a parameter.

        Returns:
            A rectangle (x, y, width, height) representing the extents of the pango layout as drawn
        """
        (attr, t, accel) = pango.parse_markup(text)
        pctx = pangocairo.CairoContext(ctx)

        pango_layout = pctx.create_layout()
        pango_layout.set_attributes(attr)

        fd = pango.FontDescription("%s %d" % (self.font_name, size))
        pango_layout.set_font_description(fd)

        if box_width:
            pango_layout.set_width(int(box_width * pango.SCALE))
        if alignment:
            pango_layout.set_alignment(alignment)
        pctx.update_layout(pango_layout)

        pango_layout.set_text(t)
        pctx.set_source_rgb(*stroke_color)
        pctx.show_layout(pango_layout)

        return pango_layout.get_pixel_extents()[0]

    def _write_text_cairo(self, ctx, text, size=10, stroke_color=(0.0, 0.0, 0.0)):
        """
        Writes text to the cairo Context specified as a parameter.

        Returns:
            A rectangle (x, y, width, height) representing the extents of the text drawn
        """
        ctx.rel_move_to(0, size)
        ctx.select_font_face(
            self.font_name,
            cairo.FONT_SLANT_NORMAL,
            cairo.FONT_WEIGHT_NORMAL)
        ctx.set_font_size(size)
        ctx.set_source_rgb(*stroke_color)
        ctx.show_text(text)

        ctx.rel_move_to(0, size)

        return (0, 0, len(text) * size, size)

    def render_scale(self, m, ctx=None, width=0.05, num_divisions=3, bar_size=8.0, with_representative_fraction=True):
        """
        Renders two things:
            - a scale bar
            - a scale representative fraction just below it

        Args:
            m: the Map object to render the scale for
            ctx: A cairo context to render the scale into. If this is None, we create a context and find out 
                the best location for the scale bar
            width: the width of area available for rendering the scale bar (in meters)
            num_divisions: the number of divisions for the scale bar
            bar_size: the size of the scale bar in points
            with_representative_fraction: whether we should render the representative fraction or not

        Returns:
            The size of the rendered scale block in points. (0, 0) if nothing is rendered.

        Notes:
            Does not render if lat lon maps or if the aspect ratio is not preserved.
            The scale bar divisions alternate between black fill / white stroke and white fill / black stroke.
        """
        (w, h) = (0, 0)

        # don't render scale text if we are in lat lon
        # dont render scale text if we have warped the aspect ratio
        if self._preserve_aspect and not self._is_latlon:

            if ctx is None:
                ctx = cairo.Context(self._surface)
                (tx, ty) = self._get_meta_info_corner((self.map_box.width(), self.map_box.height()), m)
                ctx.translate(m2pt(tx), m2pt(ty))

            (w, h) = self._render_scale_bar(m, ctx, width, w, h, num_divisions, bar_size)

            # renders the scale representative fraction text
            if with_representative_fraction:
                bar_to_fraction_space = 2
                ctx.move_to(0, h + bar_to_fraction_space)

                box_width = None
                if width > 0:
                    box_width = m2pt(width)
                h += self._render_scale_representative_fraction(ctx, box_width)

        return (w, h)

    def _render_scale_bar(self, m, ctx, width=0.05, w=0, h=0, num_divisions=3, bar_size=8.0):
        """
        Renders a graphic scale bar.

        Returns:
            The width and height of the scale bar rendered
        """
        # FIXME: bug. the scale bar divisions does not scale properly when the map envelope is huge
        # to reproduce render python-mapnik/test/data/good_maps/agg_poly_gamma_map.xml and call render_scale

        scale_bar_extra_space_factor = 1.2
        div_width = width / num_divisions * scale_bar_extra_space_factor
        (div_size, page_div_size) = self._get_sensible_scalebar_size(m, num_divisions=num_divisions, width=div_width)

        div_unit = self.get_div_unit(div_size)

        text = "0{}".format(div_unit)

        ctx.save()
        if width > 0:
            ctx.translate(m2pt(width - num_divisions * page_div_size) / 2, 0)
        for ii in range(num_divisions):
            fill = (ii % 2,) * 3
            rectangle = Rectangle(m2pt(ii*page_div_size), h, m2pt(page_div_size), bar_size)
            self._render_box(ctx, rectangle, text, fill_color=fill)
            fill = [1 - z for z in fill]
            text = "{0}{1}".format((ii + 1) * div_size, div_unit)

        w = (num_divisions) * page_div_size
        h += bar_size
        ctx.restore()

        return (w, h)

    def get_div_unit(self, div_size, div_unit_short="m", div_unit_long="km", div_unit_divisor=1000.0):
        """
        Returns the appropriate division unit based on the division size.

        Args:
            div_size: the size of the division
            div_unit_short: the default string for the division unit
            div_unit_long: the string for the division unit if div_size is large enough to be converted
                from div_unit_short to div_unit_long while keeping div_size greater than 1
            div_unit_divisor: the divisor applied to convert from div_unit_short to div_unit_long

        Note:
            Default values use the metric system
        """
        div_unit = div_unit_short
        if div_size > div_unit_divisor:
            div_size /= div_unit_divisor
            div_unit = div_unit_long

        return div_unit

    def _render_scale_representative_fraction(self, ctx, box_width, box_width_padding=2, font_size=6):
        """
        Renders the scale text, i.e.

        Returns:
            The text extent width including padding.
        """
        if HAS_PANGOCAIRO_MODULE:
            alignment = pango.ALIGN_CENTER
        else:
            alignment = None

        text = "Scale 1:{}".format(int(self.rounded_mapscale))
        text_extent = self.write_text(ctx, text, box_width=box_width, size=font_size, alignment=alignment)

        text_extent_width = text_extent[3]

        return text_extent_width + box_width_padding

    def _get_meta_info_corner(self, render_size, m):
        """
        Returns the corner (in page coordinates) of a possibly
        sensible place to render metadata such as a legend or scale.
        """
        (x, y) = self._get_render_corner(render_size, m)

        render_box_padding_in_meters = 0.005
        if self._is_map_size_constrained(m):
            y += render_size[1] + render_box_padding_in_meters
            x = self._margin
        else:
            x += render_size[0] + render_box_padding_in_meters
            y = self._margin

        return (x, y)

    def render_graticule_on_map(self, m, dec_degrees=True, grid_layer_name="Graticule"):
        # FIXME: buggy. does not get the top and right lines and other issues. see _render_graticule_axes_and_text also

        """
        Renders the graticule on the map.

        Lines are drawn as 0.5px wide and gray.
        Text font is DejaVu Sans and gray.
        """

        # don't render lat_lon grid if we are already in latlon
        if self._is_latlon:
            return

        p2 = Projection(m.srs)
        latlon_bounds = p2.inverse(m.envelope())

        # ensure that the projected map envelope is within the lat lon bounds and shift if necessary
        latlon_bounds = self._adjust_latlon_bounds(m, p2, latlon_bounds)

        latlon_mapwidth = latlon_bounds.width()
        # render an extra 20% so we generally won't miss the ends of lines
        latlon_buffer = 0.2 * latlon_mapwidth
        if dec_degrees:
            # FIXME: what is the 7.0 magic number about?
            latlon_divsize = default_scale(latlon_mapwidth / 7.0)
        else:
            # FIXME: what is the 7.0 magic number about?
            latlon_divsize = deg_min_sec_scale(latlon_mapwidth / 7.0)
        latlon_interpsize = latlon_mapwidth / m.width

        # renders the horizontal graticule axes
        self._render_graticule_axes_and_text(
            m,
            p2,
            latlon_bounds,
            latlon_buffer,
            latlon_interpsize,
            latlon_divsize,
            dec_degrees,
            True)

        # renders the vertical graticule axes
        self._render_graticule_axes_and_text(
            m, 
            p2,
            latlon_bounds,
            latlon_buffer,
            latlon_interpsize,
            latlon_divsize,
            dec_degrees,
            False)

        if self._use_ocg_layers:
            self._surface.show_page()
            self._layer_names.append(grid_layer_name)

    def _adjust_latlon_bounds(self, m, proj, latlon_bounds):
        """
        Ensures that the projected map envelope is within the lat lon bounds.
        If it's not, it shifts the lat lon bounds in the right direction by 360 degrees.

        Returns:
            The adjusted lat lon bounds box
        """
        if proj.inverse(m.envelope().center()).x > latlon_bounds.maxx:
            latlon_bounds = Box2d(
                latlon_bounds.maxx,
                latlon_bounds.miny,
                latlon_bounds.minx + 360,
                latlon_bounds.maxy)
        if proj.inverse(m.envelope().center()).y > latlon_bounds.maxy:
            latlon_bounds = Box2d(
                latlon_bounds.miny,
                latlon_bounds.maxy,
                latlon_bounds.maxx,
                latlon_bounds.miny + 360)

        return latlon_bounds

    def _render_graticule_axes_and_text(self, m, p2, latlon_bounds, latlon_buffer,
                             latlon_interpsize, latlon_divsize, dec_degrees, is_x_axis, stroke_color=(0.5, 0.5, 0.5)):
        # FIXME: buggy. does not get the top and right lines and other issues. see render_graticule_on_map also
        """
        Renders the horizontal or vertical axes on the map - depending on the is_x_axis parameter - along with
        the latitude or longitude text.

        Lines are drawn as 0.5px gray.
        Text font is DejaVu Sans gray.
        """

        ctx = cairo.Context(self._surface)
        ctx.set_source_rgb(*stroke_color)
        ctx.set_line_width(1)
        latlon_labelsize = 6

        ctx.translate(m2pt(self.map_box.minx), m2pt(self.map_box.miny))
        ctx.rectangle(0, 0, m2pt(self.map_box.width()), m2pt(self.map_box.height()))
        ctx.clip()

        ctx.select_font_face(self.font_name, cairo.FONT_SLANT_NORMAL, cairo.FONT_WEIGHT_NORMAL)
        ctx.set_font_size(latlon_labelsize)

        if is_x_axis:
            (x1, x2, y1, y2) = latlon_bounds.minx, latlon_bounds.maxx, latlon_bounds.miny, latlon_bounds.maxy
            box_top = self.map_box.height()
        else:
            (x1, x2, y1, y2) = latlon_bounds.miny, latlon_bounds.maxy, latlon_bounds.minx, latlon_bounds.maxx
            ctx.translate(m2pt(self.map_box.width() / 2), m2pt(self.map_box.height() / 2))
            ctx.rotate(-math.pi / 2)
            ctx.translate(-m2pt(self.map_box.height() / 2), -m2pt(self.map_box.width() / 2))
            box_top = self.map_box.width()

        for xvalue in self.round_grid_generator(x1 - latlon_buffer, x2 + latlon_buffer, latlon_divsize):
            yvalue = y1 - latlon_buffer
            start_cross = None
            end_cross = None
            while yvalue < y2 + latlon_buffer:
                if is_x_axis:
                    start = m.view_transform().forward(p2.forward(Coord(xvalue, yvalue)))
                else:
                    temp = m.view_transform().forward(p2.forward(Coord(yvalue, xvalue)))
                    start = Coord(m2pt(self.map_box.height()) - temp.y, temp.x)
                yvalue += latlon_interpsize
                if is_x_axis:
                    end = m.view_transform().forward(p2.forward(Coord(xvalue, yvalue)))
                else:
                    temp = m.view_transform().forward(p2.forward(Coord(yvalue, xvalue)))
                    end = Coord(m2pt(self.map_box.height()) - temp.y, temp.x)

                self._draw_line(ctx, start.x, start.y, end.x, end.y, line_width=0.5)

                if cmp(start.y, 0) != cmp(end.y, 0):
                    start_cross = end.x
                if cmp(start.y, m2pt(self.map_box.height())) != cmp(end.y, m2pt(self.map_box.height())):
                    end_cross = end.x

            if dec_degrees:
                line_text = "%g" % (xvalue)
            else:
                line_text = self.format_deg_min_sec(xvalue)

            if start_cross:
                ctx.move_to(start_cross + 2, latlon_labelsize)
                ctx.show_text(line_text)
            if end_cross:
                ctx.move_to(end_cross + 2, m2pt(box_top) - 2)
                ctx.show_text(line_text)

    def round_grid_generator(self, first, last, step):
        """Generator for lat lon grid values."""
        val = (math.floor(first / step) + 1) * step
        yield val
        while val < last:
            val += step
            yield val

    def format_deg_min_sec(self, value):
        """Converts decimal degrees value to a degrees/minutes/seconds string."""
        deg = math.floor(value)
        min = math.floor((value - deg) / (1.0 / 60))
        sec = int((value - deg * 1.0 / 60) / 1.0 / 3600)
        return "%d°%d'%d\"" % (deg, min, sec)

    def render_legend(self, m, ctx=None, columns=2, width=None, height=None, attribution=None, legend_item_box_size=(0.015, 0.0075)):
        """
        Renders a legend for the Map object. A legend is a collection of legend items, i.e., a minified
        representation of the layer's map along with the layer's title.

        Args:
            m: a Map object to render the legend for
            ctx: a cairo context to render the legend to. If this is None then automatically create a context
                and choose the best location for the legend.
            width: width of area available to render legend in (in meters)
            columns: number of columns available in legend box
            attribution: additional text that will be rendered in gray under the layer name. keyed by layer name
            legend_item_box_size:  two tuple with width and height of legend item box size in meters

        Returns:
            The size of the rendered block in points.
        """
        render_box = Rectangle()
        if self._surface:
            if ctx is None:
                ctx = cairo.Context(self._surface)
                (tx, ty) = self._get_meta_info_corner((self.map_box.width(), self.map_box.height()), m)
                ctx.translate(m2pt(tx), m2pt(ty))
                width = self._pagesize[0] - 2 * tx
                height = self._pagesize[1] - self._margin - ty

            column_width = None
            if width:
                column_width = width / columns
                render_box.width = m2pt(width)

            (render_box.width, render_box.height) = self._render_legend_items(m, ctx, render_box, column_width, height,
                                                                              columns=columns, attribution=attribution, legend_item_box_size=legend_item_box_size)

        return (render_box.width, render_box.height)

    def _render_legend_items(self, m, ctx, render_box, column_width, height, columns=2, attribution=None, legend_item_box_size=(0.015, 0.0075)):
        """Renders the legend items for the map."""
        current_column = 0
        processed_layers = []
        for layer in reversed(m.layers):
            have_layer_header = False
            layer_title = layer.name
            if layer_title in processed_layers:
                continue
            processed_layers.append(layer_title)

            added_styles = self._get_unique_added_styles(m, layer)
            legend_items = sorted(added_styles.keys())
            for li in legend_items:
                (f, rule_text) = added_styles[li]

                legend_map_size = (int(m2pt(legend_item_box_size[0])), int(m2pt(legend_item_box_size[1])))
                lemap = self._create_legend_item_map(m, layer, f, legend_map_size)

                item_size = legend_map_size[1]
                if not have_layer_header:
                    item_size += 8

                # if we get to the bottom of the page, start a new column
                # if we get to the max number of columns, start a new page
                if render_box.y + item_size > m2pt(height):
                    current_column += 1
                    render_box.y = 0
                    if current_column >= columns:
                        self._surface.show_page()
                        render_box.x = 0
                        current_column = 0

                self._render_legend_item_map(
                    lemap, legend_map_size, ctx, render_box.x, render_box.y, current_column, column_width)

                ctx.move_to(
                    render_box.x + legend_map_size[0] + m2pt(current_column * column_width) + 2, render_box.y)

                legend_entry_size = self._render_legend_item_text(
                    ctx, legend_map_size, legend_item_box_size, column_width, layer_title, attribution)

                vertical_spacing = 5
                render_box.y += legend_entry_size + vertical_spacing
                if render_box.y > render_box.height:
                    render_box.height = render_box.y

        return (render_box.width, render_box.height)

    def _get_unique_added_styles(self, m, layer):
        """
        Go through the features to find which combinations of styles are active.
        For each unique combination add a legend entry.
        """
        added_styles = {}
        for f in layer.datasource.all_features():
            if f.geometry:
                active_rules = []
                rule_text = ""
                for s in layer.styles:
                    st = m.find_style(s)
                    for r in st.rules:
                        if self._is_rule_within_map_scale_limits(m, f, r):
                            active_rules.append((s, r.name))
                            rule_text = self._get_rule_text(r, rule_text)

                active_rules = tuple(active_rules)
                if active_rules in added_styles:
                    continue

                added_styles[active_rules] = (f, rule_text)
                break
            else:
                added_styles[layer] = (None, None)

        return added_styles

    def _is_rule_within_map_scale_limits(self, m, feature, rule):
        """Returns whether the rule is within the map scale limits or not."""
        if ((not rule.filter) or rule.filter.evaluate(feature) == '1') and \
            rule.min_scale <= m.scale_denominator() and m.scale_denominator() < rule.max_scale:
            return True
        else:
            return False

    def _create_legend_item_map(self, m, layer, f, legend_map_size):
        """Creates the legend map, i.e., a minified version of the layer map, and returns it."""
        from mapnik import MemoryDatasource

        legend_map = Map(legend_map_size[0], legend_map_size[1], srs=m.srs)

        # the buffer is needed to ensure that text labels that overflow the edge of the
        # map still render for the legend
        legend_map.buffer_size = 1000
        for layer_style in layer.styles:
            lestyle = self._get_layer_style_valid_rules(m, layer_style)
            legend_map.append_style(layer_style, lestyle)

        ds = MemoryDatasource()
        if f is None:
            ds = layer.datasource
            layer_srs = layer.srs
        elif f.envelope().width() == 0:
            f.geometry = Geometry.from_wkt('POINT (0 0)')
            ds.add_feature(f)
            legend_map.zoom_to_box(Box2d(-1, -1, 1, 1))
            layer_srs = m.srs
        else:
            ds.add_feature(f)
            layer_srs = layer.srs

        lelayer = Layer("LegendLayer", layer_srs)
        lelayer.datasource = ds
        for layer_style in layer.styles:
            lelayer.styles.append(layer_style)
        legend_map.layers.append(lelayer)

        if f is None or f.envelope().width() != 0:
            legend_map.zoom_all()
            legend_map.zoom(1.1)

        return legend_map

    def _get_layer_style_valid_rules(self, m, layer_style):
        """Filters out the layer style rules that are not valid for the Map and returns the style."""
        style = m.find_style(layer_style)
        legend_style = Style()
        for r in style.rules:
            for sym in r.symbols:
                try:
                    sym.avoid_edges = False
                except AttributeError:
                    L.warning("Could not set avoid_edges for rule %s", r.name)
            if r.min_scale <= m.scale_denominator() and m.scale_denominator() < r.max_scale:
                legend_rule = r
                legend_rule.min_scale = 0
                legend_rule.max_scale = float("inf")
                legend_style.rules.append(legend_rule)

        return legend_style

    def _render_legend_item_map(self, lemap, legend_map_size, ctx, x, y, current_column, column_width, stroke_color=(0.5, 0.5, 0.5), line_width=1):
        """Renders the legend item map."""
        ctx.save()
        ctx.translate(x + m2pt(current_column * column_width), y)

        # extra save around map render as it sets up a clip box and doesn't clear it
        ctx.save()
        render(lemap, ctx)
        ctx.restore()

        ctx.rectangle(0, 0, *legend_map_size)
        ctx.set_source_rgb(*stroke_color)
        ctx.set_line_width(line_width)
        ctx.stroke()
        ctx.restore()

    def _render_legend_item_text(self, ctx, legend_map_size, legend_item_box_size, column_width, layer_title, attribution=None):
        """
        Renders the legend item text next to the legend item box.

        Returns:
            The size of the legend entry size, i.e., the legend box height or
            the legend text height depending on which one takes more vertical
            space.
        """
        gray_rgb = (0.5, 0.5, 0.5)
        legend_box_padding_in_meters = 0.005
        legend_box_width = m2pt(column_width - legend_item_box_size[0] - legend_box_padding_in_meters)

        legend_entry_size = legend_map_size[1]
        legend_text_size = 0

        rule_text = layer_title
        if rule_text:
            e = self.write_text(ctx, rule_text, box_width=legend_box_width, size=6)
            legend_text_size += e[3]
            ctx.rel_move_to(0, e[3])
        if attribution:
            if layer_title in attribution:
                e = self.write_text(
                        ctx,
                        attribution[layer_title],
                        box_width=legend_box_width,
                        size=6,
                        stroke_color=gray_rgb)
                legend_text_size += e[3]

        if legend_text_size > legend_entry_size:
            legend_entry_size = legend_text_size

        return legend_entry_size

    def _get_rule_text(self, rule, rule_text):
        """Returns the rule text."""
        if rule.filter and str(rule.filter) != "true":
            if len(rule_text) > 0:
                rule_text += " AND "
            if rule.name:
                rule_text += rule.name
            else:
                rule_text += str(rule.filter)

        return rule_text

    def finish(self):
        """
        Finishes the cairo surface and converts PDF pages to PDF layers if
        _use_ocg_layers was set to True.
        """
        if self._surface:
            self._surface.finish()
            self._surface = None

        if self._use_ocg_layers:
            self.convert_pdf_pages_to_layers(
                self._filename,
                layer_names=self._layer_names +
                ["Legend and Information"],
                reverse_all_but_last=True)

    def convert_pdf_pages_to_layers(self, filename, layer_names=None, reverse_all_but_last=True):
        """
        Takes a multi pages PDF as input and converts each page to a layer in a single page PDF.

        Note:
            requires PyPDF2 to be available

        Args:
            layer_names should be a sequence of the user visible names of the layers, if not given
            or if shorter than num pages generic names will be given to the unnamed layers

            if output_name is not provided a temporary file will be used for the conversion which
            will then be copied back over the source file.
        """
        if not HAS_PYPDF2:
            raise RuntimeError("PyPDF2 not available; PyPDF2 required to convert pdf pages to layers")

        with open(filename, "rb+") as f:
            file_reader = PdfFileReader(f)
            file_writer = PdfFileWriter()

            template_page_size = file_reader.pages[0].mediaBox
            output_pdf = file_writer.addBlankPage(
                width=template_page_size.getWidth(),
                height=template_page_size.getHeight())

            content_key = NameObject('/Contents')
            output_pdf[content_key] = ArrayObject()

            resource_key = NameObject('/Resources')
            output_pdf[resource_key] = DictionaryObject()

            (properties, ocgs) = self._make_ocg_layers(file_reader, file_writer, output_pdf, layer_names)

            properties_key = NameObject('/Properties')
            output_pdf[resource_key][properties_key] = file_writer._addObject(properties)

            ocproperties = DictionaryObject()
            ocproperties[NameObject('/OCGs')] = ocgs

            default_view = self._get_pdf_default_view(ocgs, reverse_all_but_last)
            ocproperties[NameObject('/D')] = file_writer._addObject(default_view)

            file_writer._root_object[NameObject('/OCProperties')] = file_writer._addObject(ocproperties)

            f.seek(0)
            file_writer.write(f)
            f.truncate()

    def _make_ocg_layers(self, file_reader, file_writer, output_pdf, layer_names=None):
        """
        Makes the OCGs layers.

        Returns:
            properties: a dictionary mapping the OCG layer name and the OCG layer property list
            ocgs: an array containing the OCG layers
        """
        properties = DictionaryObject()
        ocgs = ArrayObject()

        for (idx, page) in enumerate(file_reader.pages):
            # first start an OCG for the layer
            ocg_name = NameObject('/oc%d' % idx)
            ocgs_start = DecodedStreamObject()
            ocgs_start._data = "/OC %s BDC\n" % ocg_name
            ocg_end = DecodedStreamObject()
            ocg_end._data = "EMC\n"

            if isinstance(page['/Contents'], ArrayObject):
                page[NameObject('/Contents')].insert(0, ocgs_start)
                page[NameObject('/Contents')].append(ocg_end)
            else:
                page[NameObject(
                    '/Contents')] = ArrayObject((ocgs_start, page['/Contents'], ocg_end))

            output_pdf.mergePage(page)

            ocg = DictionaryObject()
            ocg[NameObject('/Type')] = NameObject('/OCG')

            if layer_names and len(layer_names) > idx:
                ocg[NameObject('/Name')] = TextStringObject(layer_names[idx])
            else:
                ocg[NameObject('/Name')] = TextStringObject('Layer %d' % (idx + 1))

            indirect_ocg = file_writer._addObject(ocg)
            properties[ocg_name] = indirect_ocg
            ocgs.append(indirect_ocg)

        return (properties, ocgs)

    def _get_pdf_default_view(self, ocgs, reverse_all_but_last=True):
        """
        Returns the D configuration dictionary of the PDF.

        The D configuration dictionary specifies the initial state of the optional content
        groups when a PDF is first opened.
        """
        default_view = DictionaryObject()
        default_view[NameObject('/Name')] = TextStringObject('Default')
        default_view[NameObject('/BaseState ')] = NameObject('/ON ')
        default_view[NameObject('/ON')] = ocgs
        default_view[NameObject('/OFF')] = ArrayObject()

        if reverse_all_but_last:
            default_view[NameObject('/Order')] = ArrayObject(reversed(ocgs[:-1]))
            default_view[NameObject('/Order')].append(ocgs[-1])
        else:
            default_view[NameObject('/Order')] = ArrayObject(reversed(ocgs))

        return default_view

    def add_geospatial_pdf_header(self, m, filename, epsg=None, wkt=None):
        """
        Adds geospatial PDF information to the PDF file as per:
            Adobe® Supplement to the ISO 32000 PDF specification
            BaseVersion: 1.7
            ExtensionLevel: 3
            (June 2008)

        Notes:
            The epsg code or the wkt text of the projection must be provided.
            Must be called *after* the page has had .finish() called.
        """
        if not HAS_PYPDF2:
            raise RuntimeError("PyPDF2 not available; PyPDF2 required to add geospatial header to PDF")

        if not any((epsg,wkt)):
            raise RuntimeError("EPSG or WKT required to add geospatial header to PDF")

        with open(filename, "rb+") as f:
            file_reader = PdfFileReader(f)
            file_writer = PdfFileWriter()

            # preserve OCProperties at document root if we have one
            if NameObject('/OCProperties') in file_reader.trailer['/Root']:
                file_writer._root_object[NameObject('/OCProperties')] = file_reader.trailer[
                    '/Root'].getObject()[NameObject('/OCProperties')]

            for page in file_reader.pages:
                gcs = DictionaryObject()
                gcs[NameObject('/Type')] = NameObject('/PROJCS')

                if epsg:
                    gcs[NameObject('/EPSG')] = NumberObject(int(epsg))
                if wkt:
                    gcs[NameObject('/WKT')] = TextStringObject(wkt)

                measure = self._get_pdf_measure(m, gcs)
                page[NameObject('/VP')] = self._get_pdf_vp(measure)

                file_writer.addPage(page)

            f.seek(0)
            file_writer.write(f)
            f.truncate()

    def _get_pdf_measure(self, m, gcs):
        """
        Returns the PDF Measure dictionary.

        The Measure dictionary is used in the viewport array
        and specifies the scale and units that apply to the output map.
        """
        measure = DictionaryObject()
        measure[NameObject('/Type')] = NameObject('/Measure')
        measure[NameObject('/Subtype')] = NameObject('/GEO')
        measure[NameObject('/GCS')] = gcs

        bounds = self._get_pdf_bounds()
        measure[NameObject('/Bounds')] = bounds
        measure[NameObject('/LPTS')] = bounds

        measure[NameObject('/GPTS')] = self._get_pdf_gpts(m)

        return measure

    def _get_pdf_bounds(self):
        """
        Returns the PDF BOUNDS array.

        The PDF's bounds array is equivalent to the map's neatline, i.e.,
        the border delineating the extent of geographic data on the output map.
        """
        bounds = ArrayObject()

        # PDF specification's default for bounds (full unit square)
        bounds_default = (0.0, 0.0, 0.0, 1.0, 1.0, 1.0, 1.0, 0.0)

        for x in bounds_default:
            bounds.append(FloatObject(str(x)))

        return bounds

    def _get_pdf_gpts(self, m):
        """
        Returns the GPTS array object containing the four corners of the
        map envelope in map projection.

        The GPTS entry is an array of numbers, taken pairwise, defining
        points as latitude and longitude.
        """
        gpts = ArrayObject()

        proj = Projection(m.srs)
        env = m.envelope()
        for x in ((env.minx, env.miny), (env.minx, env.maxy),
                  (env.maxx, env.maxy), (env.maxx, env.miny)):
            latlon_corner = proj.inverse(Coord(*x))
            # these are in lat,lon order according to the specification
            gpts.append(FloatObject(str(latlon_corner.y)))
            gpts.append(FloatObject(str(latlon_corner.x)))

        return gpts

    def _get_pdf_vp(self, measure):
        """
        Returns the PDF's VP array.

        The VP entry is an array of viewport dictionaries. A viewport is basiscally
        a rectangular region on the PDF page. The only required entry is the BBox which
        specifies the location of the viewport on the page.
        """
        viewport = DictionaryObject()
        viewport[NameObject('/Type')] = NameObject('/Viewport')

        bbox = ArrayObject()
        for x in self.map_box:
            # this should be converted from meters to points
            # fix submitted in https://github.com/mapnik/python-mapnik/pull/115
            bbox.append(FloatObject(str(x)))

        viewport[NameObject('/BBox')] = bbox
        viewport[NameObject('/Measure')] = measure

        vp_array = ArrayObject()
        vp_array.append(viewport)

        return vp_array

    def get_width(self):
        """Returns page's width."""
        return self._pagesize[0]

    def get_height(self):
        """Returns page's height."""
        return self._pagesize[1]

    def get_margin(self):
        """Returns page's margin."""
        return self._margin

    def get_cairo_context(self):
        """
        Allows access to the cairo Context so that extra 'bits'
        can be rendered to the page directly.
        """
        return cairo.Context(self._surface)


class Rectangle(object):

    def __init__(self, x=0, y=0, width=0, height=0):
        self.x = x
        self.y = y
        self.width = width
        self.height = height

    def __repr__(self):
        return "({}, {}, {}, {})".format(self.x, self.y, self.width, self.height)

    def origin(self):
        """Returns the top left corner coordinates in pdf points."""
        return (self.x, self.y)
