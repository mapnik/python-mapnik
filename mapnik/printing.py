# -*- coding: utf-8 -*-

"""Mapnik classes to assist in creating printable maps."""

from __future__ import absolute_import, print_function

import math
import os
import tempfile

import mapnik
from mapnik import Box2d, Coord, Geometry, Layer, Map, Projection, Style, render
from mapnik.conversions import m2pt, m2px
from mapnik.formats import pagesizes
from mapnik.scales import any_scale, default_scale, deg_min_sec_scale, sequence_scale

try:
    import cairo
    HAS_PYCAIRO_MODULE = True
except ImportError:
    HAS_PYCAIRO_MODULE = False

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


class centering:

    """
    Style of centering to use with the map.

    none: map will be placed in the top left corner
    constrained_axis: map will be centered on the most constrained axis (e.g. vertical for a portrait page); a square
        map will be constrained horizontally
    unconstrained_axis: map will be centered on the unconstrained axis
    vertical: map will be centered vertically
    horizontal: map will be centered horizontally
    both: map will be centered vertically and horizontally
    """

    none = 0
    constrained_axis = 1
    unconstrained_axis = 2
    vertical = 3
    horizontal = 4
    both = 5


class resolutions:

    """Some predefined resolutions in DPI"""

    dpi72 = 72
    dpi150 = 150
    dpi300 = 300
    dpi600 = 600


class PDFPrinter:

    """
    Main class for creating PDF print outs. Basic usage is along the lines of

    import mapnik

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
                 resolution=resolutions.dpi72,
                 preserve_aspect=True,
                 centering=centering.constrained_axis,
                 is_latlon=False,
                 use_ocg_layers=False):
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

        if not HAS_PYCAIRO_MODULE:
            raise Exception(
                "PDF rendering only available when pycairo is available")

        self.font_name = "DejaVu Sans"

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

        if (self._centering == centering.both or
                self._centering == centering.horizontal or
                (self._centering == centering.constrained_axis and is_map_size_constrained) or
                (self._centering == centering.unconstrained_axis and not is_map_size_constrained)):
            return True
        else:
            return False

    def _has_vertical_centering(self, m):
        """Returns whether the map has a vertical centering or not."""
        is_map_size_constrained = self._is_map_size_constrained(m)

        if (self._centering == centering.both or
                self._centering == centering.vertical or
                (self._centering == centering.constrained_axis and not is_map_size_constrained) or
                (self._centering == centering.unconstrained_axis and is_map_size_constrained)):
            return True
        else:
            return False

    def _is_map_size_constrained(self, m):
        """Tests whether the map's size is constrained on the horizontal or vertical axes."""
        available_area = self._get_render_area_size()
        map_aspect = m.envelope().width() / m.envelope().height()
        page_aspect = available_area[0] / available_area[1]

        return map_aspect > page_aspect

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

        self.scale = rounded_mapscale
        self.map_box = Box2d(tx, ty, tx + mapw, ty + maph)

    def render_on_map_lat_lon_grid(self, m, dec_degrees=True):
        # don't render lat_lon grid if we are already in latlon
        if self._is_latlon:
            return
        p2 = Projection(m.srs)

        latlon_bounds = p2.inverse(m.envelope())
        if p2.inverse(m.envelope().center()).x > latlon_bounds.maxx:
            latlon_bounds = Box2d(
                latlon_bounds.maxx,
                latlon_bounds.miny,
                latlon_bounds.minx + 360,
                latlon_bounds.maxy)

        if p2.inverse(m.envelope().center()).y > latlon_bounds.maxy:
            latlon_bounds = Box2d(
                latlon_bounds.miny,
                latlon_bounds.maxy,
                latlon_bounds.maxx,
                latlon_bounds.miny + 360)

        latlon_mapwidth = latlon_bounds.width()
        # render an extra 20% so we generally won't miss the ends of lines
        latlon_buffer = 0.2 * latlon_mapwidth
        if dec_degrees:
            latlon_divsize = default_scale(latlon_mapwidth / 7.0)
        else:
            latlon_divsize = deg_min_sec_scale(latlon_mapwidth / 7.0)
        latlon_interpsize = latlon_mapwidth / m.width

        self._render_lat_lon_axis(
            m,
            p2,
            latlon_bounds.minx,
            latlon_bounds.maxx,
            latlon_bounds.miny,
            latlon_bounds.maxy,
            latlon_buffer,
            latlon_interpsize,
            latlon_divsize,
            dec_degrees,
            True)
        self._render_lat_lon_axis(
            m,
            p2,
            latlon_bounds.miny,
            latlon_bounds.maxy,
            latlon_bounds.minx,
            latlon_bounds.maxx,
            latlon_buffer,
            latlon_interpsize,
            latlon_divsize,
            dec_degrees,
            False)

    def _render_lat_lon_axis(self, m, p2, x1, x2, y1, y2, latlon_buffer,
                             latlon_interpsize, latlon_divsize, dec_degrees, is_x_axis):
        ctx = cairo.Context(self._s)
        ctx.set_source_rgb(1, 0, 0)
        ctx.set_line_width(1)
        latlon_labelsize = 6

        ctx.translate(m2pt(self.map_box.minx), m2pt(self.map_box.miny))
        ctx.rectangle(
            0, 0, m2pt(
                self.map_box.width()), m2pt(
                self.map_box.height()))
        ctx.clip()

        ctx.select_font_face(
            "DejaVu",
            cairo.FONT_SLANT_NORMAL,
            cairo.FONT_WEIGHT_NORMAL)
        ctx.set_font_size(latlon_labelsize)

        box_top = self.map_box.height()
        if not is_x_axis:
            ctx.translate(m2pt(self.map_box.width() / 2),
                          m2pt(self.map_box.height() / 2))
            ctx.rotate(-math.pi / 2)
            ctx.translate(-m2pt(self.map_box.height() / 2), -
                          m2pt(self.map_box.width() / 2))
            box_top = self.map_box.width()

        for xvalue in round_grid_generator(
                x1 - latlon_buffer, x2 + latlon_buffer, latlon_divsize):
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

                ctx.move_to(start.x, start.y)
                ctx.line_to(end.x, end.y)
                ctx.stroke()

                if cmp(start.y, 0) != cmp(end.y, 0):
                    start_cross = end.x
                if cmp(start.y, m2pt(self.map_box.height())) != cmp(
                        end.y, m2pt(self.map_box.height())):
                    end_cross = end.x

            if dec_degrees:
                line_text = "%g" % (xvalue)
            else:
                line_text = format_deg_min_sec(xvalue)
            if start_cross:
                ctx.move_to(start_cross + 2, latlon_labelsize)
                ctx.show_text(line_text)
            if end_cross:
                ctx.move_to(end_cross + 2, m2pt(box_top) - 2)
                ctx.show_text(line_text)

    def render_on_map_scale(self, m):
        (div_size, page_div_size) = self._get_sensible_scalebar_size(m)

        first_value_x = (
            math.floor(
                m.envelope().minx / div_size) + 1) * div_size
        first_value_x_percent = (
            first_value_x - m.envelope().minx) / m.envelope().width()
        self._render_scale_axis(
            first_value_x,
            first_value_x_percent,
            self.map_box.minx,
            self.map_box.maxx,
            page_div_size,
            div_size,
            self.map_box.miny,
            self.map_box.maxy,
            True)

        first_value_y = (
            math.floor(
                m.envelope().miny / div_size) + 1) * div_size
        first_value_y_percent = (
            first_value_y - m.envelope().miny) / m.envelope().height()
        self._render_scale_axis(
            first_value_y,
            first_value_y_percent,
            self.map_box.miny,
            self.map_box.maxy,
            page_div_size,
            div_size,
            self.map_box.minx,
            self.map_box.maxx,
            False)

        if self._use_ocg_layers:
            self._s.show_page()
            self._layer_names.append("Coordinate Grid Overlay")

    def _get_sensible_scalebar_size(self, m, width=-1):
        # aim for about 8 divisions across the map
        # also make sure we can fit the bar with in page area width if
        # specified
        div_size = sequence_scale(m.envelope().width() / 8, [1, 2, 5])
        page_div_size = self.map_box.width() * div_size / m.envelope().width()
        while width > 0 and page_div_size > width:
            div_size /= 2
            page_div_size /= 2
        return (div_size, page_div_size)

    def _render_box(self, ctx, x, y, w, h, text=None,
                    stroke_color=(0, 0, 0), fill_color=(0, 0, 0)):
        ctx.set_line_width(1)
        ctx.set_source_rgb(*fill_color)
        ctx.rectangle(x, y, w, h)
        ctx.fill()

        ctx.set_source_rgb(*stroke_color)
        ctx.rectangle(x, y, w, h)
        ctx.stroke()

        if text:
            ctx.move_to(x + 1, y)
            self.write_text(
                ctx, text, fill_color=[
                    1 - z for z in fill_color], size=h - 2)

    def _render_scale_axis(self, first, first_percent, start, end,
                           page_div_size, div_size, boundary_start, boundary_end, is_x_axis):
        prev = start
        text = None
        fill = (0, 0, 0)
        border_size = 8
        value = first_percent * (end - start) + start
        label_value = first - div_size
        if self._is_latlon and label_value < -180:
            label_value += 360

        ctx = cairo.Context(self._s)

        if not is_x_axis:
            ctx.translate(
                m2pt(
                    self.map_box.center().x), m2pt(
                    self.map_box.center().y))
            ctx.rotate(-math.pi / 2)
            ctx.translate(-m2pt(self.map_box.center().y), -
                          m2pt(self.map_box.center().x))

        while value < end:
            ctx.move_to(m2pt(value), m2pt(boundary_start))
            ctx.line_to(m2pt(value), m2pt(boundary_end))
            ctx.set_source_rgb(0.5, 0.5, 0.5)
            ctx.set_line_width(1)
            ctx.stroke()

            for bar in (m2pt(boundary_start) - border_size,
                        m2pt(boundary_end)):
                self._render_box(
                    ctx,
                    m2pt(prev),
                    bar,
                    m2pt(
                        value -
                        prev),
                    border_size,
                    text,
                    fill_color=fill)

            prev = value
            value += page_div_size
            fill = [1 - z for z in fill]
            label_value += div_size
            if self._is_latlon and label_value > 180:
                label_value -= 360
            text = "%d" % label_value
        else:
            for bar in (m2pt(boundary_start) - border_size,
                        m2pt(boundary_end)):
                self._render_box(
                    ctx, m2pt(prev), bar, m2pt(
                        end - prev), border_size, fill_color=fill)

    def render_scale(self, m, ctx=None, width=0.05):
        """ m: map to render scale for
        ctx: A cairo context to render the scale to. If this is None (the default) then
            automatically create a context and choose the best location for the scale bar.
        width: Width of area available to render scale bar in (in m)

        will return the size of the rendered scale block in pts
        """

        (w, h) = (0, 0)

        # don't render scale if we are lat lon
        # dont report scale if we have warped the aspect ratio
        if self._preserve_aspect and not self._is_latlon:
            bar_size = 8.0
            box_count = 3
            if ctx is None:
                ctx = cairo.Context(self._s)
                (tx, ty) = self._get_meta_info_corner(
                    (self.map_box.width(), self.map_box.height()), m)
                ctx.translate(tx, ty)

            (div_size, page_div_size) = self._get_sensible_scalebar_size(
                m, width / box_count)

            div_unit = "m"
            if div_size > 1000:
                div_size /= 1000
                div_unit = "km"

            text = "0%s" % div_unit
            ctx.save()
            if width > 0:
                ctx.translate(m2pt(width - box_count * page_div_size) / 2, 0)
            for ii in range(box_count):
                fill = (ii % 2,) * 3
                self._render_box(
                    ctx,
                    m2pt(
                        ii *
                        page_div_size),
                    h,
                    m2pt(page_div_size),
                    bar_size,
                    text,
                    fill_color=fill)
                fill = [1 - z for z in fill]
                text = "%g%s" % ((ii + 1) * div_size, div_unit)
            # else:
            #    self._render_box(ctx, m2pt(box_count*page_div_size), h, m2pt(page_div_size), bar_size, text, fill_color=(1,1,1), stroke_color=(1,1,1))
            w = (box_count) * page_div_size
            h += bar_size
            ctx.restore()

            if width > 0:
                box_width = m2pt(width)
            else:
                box_width = None

            font_size = 6
            ctx.move_to(0, h)
            if HAS_PANGOCAIRO_MODULE:
                alignment = pango.ALIGN_CENTER
            else:
                alignment = None

            text_ext = self.write_text(
                ctx,
                "Scale 1:%d" %
                self.scale,
                box_width=box_width,
                size=font_size,
                alignment=alignment)
            h += text_ext[3] + 2

        return (w, h)

    def render_legend(self, m, page_break=False, ctx=None, collumns=1, width=None, height=None,
                      item_per_rule=False, attribution={}, legend_item_box_size=(0.015, 0.0075)):
        """ m: map to render legend for
        ctx: A cairo context to render the legend to. If this is None (the default) then
            automatically create a context and choose the best location for the legend.
        width: Width of area available to render legend in (in m)
        page_break: move to next page if legend overflows this one
        collumns: number of columns available in legend box
        attribution: additional text that will be rendered in gray under the layer name. keyed by layer name
        legend_item_box_size:  two tuple with width and height of legend item box size in meters

        will return the size of the rendered block in pts
        """

        (w, h) = (0, 0)
        if self._s:
            if ctx is None:
                ctx = cairo.Context(self._s)
                (tx, ty) = self._get_meta_info_corner(
                    (self.map_box.width(), self.map_box.height()), m)
                ctx.translate(m2pt(tx), m2pt(ty))
                width = self._pagesize[0] - 2 * tx
                height = self._pagesize[1] - self._margin - ty

            x = 0
            y = 0
            if width:
                cwidth = width / collumns
                w = m2pt(width)
            else:
                cwidth = None
            current_collumn = 0

            processed_layers = []
            for l in reversed(m.layers):
                have_layer_header = False
                added_styles = {}
                layer_title = l.name
                if layer_title in processed_layers:
                    continue
                processed_layers.append(layer_title)

                # check through the features to find which combinations of styles are active
                # for each unique combination add a legend entry
                for f in l.datasource.all_features():
                    if f.num_geometries() > 0:
                        active_rules = []
                        rule_text = ""
                        for s in l.styles:
                            st = m.find_style(s)
                            for r in st.rules:
                                # we need to do the scale test here as well so we don't
                                # add unused scale rules to the legend
                                # description
                                if ((not r.filter) or r.filter.evaluate(f) == '1') and \
                                        r.min_scale <= m.scale_denominator() and m.scale_denominator() < r.max_scale:
                                    active_rules.append((s, r.name))
                                    if r.filter and str(r.filter) != "true":
                                        if len(rule_text) > 0:
                                            rule_text += " AND "
                                        if r.name:
                                            rule_text += r.name
                                        else:
                                            rule_text += str(r.filter)
                        active_rules = tuple(active_rules)
                        if active_rules in added_styles:
                            continue

                        added_styles[active_rules] = (f, rule_text)
                        if not item_per_rule:
                            break
                    else:
                        added_styles[l] = (None, None)

                legend_items = sorted(added_styles.keys())
                for li in legend_items:
                    if True:
                        (f, rule_text) = added_styles[li]

                        legend_map_size = (int(m2pt(legend_item_box_size[0])), int(
                            m2pt(legend_item_box_size[1])))
                        lemap = Map(
                            legend_map_size[0],
                            legend_map_size[1],
                            srs=m.srs)
                        if m.background:
                            lemap.background = m.background
                        # the buffer is needed to ensure that text labels that overflow the edge of the
                        # map still render for the legend
                        lemap.buffer_size = 1000
                        for s in l.styles:
                            sty = m.find_style(s)
                            lestyle = Style()
                            for r in sty.rules:
                                for sym in r.symbols:
                                    try:
                                        sym.avoid_edges = False
                                    except:
                                        print(
                                            "**** Cant set avoid edges for rule", r.name)
                                if r.min_scale <= m.scale_denominator() and m.scale_denominator() < r.max_scale:
                                    lerule = r
                                    lerule.min_scale = 0
                                    lerule.max_scale = float("inf")
                                    lestyle.rules.append(lerule)
                            lemap.append_style(s, lestyle)

                        ds = MemoryDatasource()
                        if f is None:
                            ds = l.datasource
                            layer_srs = l.srs
                        elif f.envelope().width() == 0:
                            ds.add_feature(
                                Feature(
                                    f.id(),
                                    Geometry2d.from_wkt("POINT(0 0)"),
                                    **f.attributes))
                            lemap.zoom_to_box(Box2d(-1, -1, 1, 1))
                            layer_srs = m.srs
                        else:
                            ds.add_feature(f)
                            layer_srs = l.srs

                        lelayer = Layer("LegendLayer", layer_srs)
                        lelayer.datasource = ds
                        for s in l.styles:
                            lelayer.styles.append(s)
                        lemap.layers.append(lelayer)

                        if f is None or f.envelope().width() != 0:
                            lemap.zoom_all()
                            lemap.zoom(1.1)

                        item_size = legend_map_size[1]
                        if not have_layer_header:
                            item_size += 8

                        if y + item_size > m2pt(height):
                            current_collumn += 1
                            y = 0
                            if current_collumn >= collumns:
                                if page_break:
                                    self._s.show_page()
                                    x = 0
                                    current_collumn = 0
                                else:
                                    break

                        if not have_layer_header and item_per_rule:
                            ctx.move_to(x + m2pt(current_collumn * cwidth), y)
                            e = self.write_text(ctx, l.name, m2pt(cwidth), 8)
                            y += e[3] + 2
                            have_layer_header = True
                        ctx.save()
                        ctx.translate(x + m2pt(current_collumn * cwidth), y)
                        # extra save around map render as it sets up a clip box
                        # and doesn't clear it
                        ctx.save()
                        render(lemap, ctx)
                        ctx.restore()

                        ctx.rectangle(0, 0, *legend_map_size)
                        ctx.set_source_rgb(0.5, 0.5, 0.5)
                        ctx.set_line_width(1)
                        ctx.stroke()
                        ctx.restore()

                        ctx.move_to(
                            x +
                            legend_map_size[0] +
                            m2pt(
                                current_collumn *
                                cwidth) +
                            2,
                            y)
                        legend_entry_size = legend_map_size[1]
                        legend_text_size = 0
                        if not item_per_rule:
                            rule_text = layer_title
                        if rule_text:
                            e = self.write_text(
                                ctx, rule_text, m2pt(
                                    cwidth - legend_item_box_size[0] - 0.005), 6)
                            legend_text_size += e[3]
                            ctx.rel_move_to(0, e[3])
                        if layer_title in attribution:
                            e = self.write_text(
                                ctx,
                                attribution[layer_title],
                                m2pt(
                                    cwidth -
                                    legend_item_box_size[0] -
                                    0.005),
                                6,
                                fill_color=(
                                    0.5,
                                    0.5,
                                    0.5))
                            legend_text_size += e[3]

                        if legend_text_size > legend_entry_size:
                            legend_entry_size = legend_text_size

                        y += legend_entry_size + 2
                        if y > h:
                            h = y
        return (w, h)
