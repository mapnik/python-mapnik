#!/usr/bin/env python

import os

from nose.tools import eq_

from mapnik import printing, Map, load_map
from .utilities import execution_path, run_all

def setup():
    # All of the paths used are relative, if we run the tests
    # from another directory we need to chdir()
    os.chdir(execution_path('.'))

def make_map_from_xml(source_xml):
	m = Map(100, 100)
	load_map(m, source_xml, True)
	m.zoom_all()

	return m

def make_pdf(m, output_pdf, esri_wkt):
	page = printing.PDFPrinter(use_ocg_layers=True)
	page.render_map(m, output_pdf)
	page.render_on_map_scale(m)
	# page.render_on_map_lat_lon_grid(m) # FIXME. to be tested has a few problems
	page.render_legend(m)
	ctx = page.get_cairo_context()
	page.render_scale(m, ctx)
	page.finish()
	page.add_geospatial_pdf_header(m, output_pdf, wkt=esri_wkt)

def test_pdf_printing():
	# TODO: make this a proper test once refactoring is over
	source_xml = '../data/good_maps/marker-text-line.xml'.encode('utf-8')
	m = make_map_from_xml(source_xml)

	output_pdf = "/tmp/pdf_printing_test-test_pdf_printing.pdf"
	esri_wkt = 'GEOGCS["GCS_WGS_1984",DATUM["D_WGS_1984",SPHEROID["WGS_1984",6378137,298.257223563]],PRIMEM["Greenwich",0],UNIT["Degree",0.017453292519943295]]'
	make_pdf(m, output_pdf, esri_wkt)

	# TODO: compare against expected PDF once finished

if __name__ == "__main__":
    setup()
    exit(run_all(eval(x) for x in dir() if x.startswith("test_")))
