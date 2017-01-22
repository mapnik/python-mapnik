#!/usr/bin/env python

import os

from nose.tools import eq_
from PyPDF2 import PdfFileReader

from mapnik import Map, has_pycairo, load_map
from .utilities import execution_path, run_all


def setup():
    # All of the paths used are relative, if we run the tests
    # from another directory we need to chdir()
    os.chdir(execution_path("."))

def make_map_from_xml(source_xml):
	m = Map(100, 100)
	load_map(m, source_xml, True)
	m.zoom_all()

	return m

def make_pdf(m, output_pdf, esri_wkt, render_grid_on_map=False, render_legend=False):
	page = PDFPrinter(use_ocg_layers=True)
	page.render_map(m, output_pdf)

	if render_grid_on_map:
		page.render_grid_on_map(m)

	if render_legend:
		page.render_legend(m)

	page.finish()
	page.add_geospatial_pdf_header(m, output_pdf, wkt=esri_wkt)

if has_pycairo():
  from mapnik.printing import PDFPrinter

	def test_pdf_printing():
		source_xml = "../data/good_maps/marker-text-line.xml"
		m = make_map_from_xml(source_xml)

		actual_pdf = "/tmp/pdf-printing-actual.pdf"
		esri_wkt = "GEOGCS['GCS_WGS_1984',DATUM['D_WGS_1984',SPHEROID['WGS_1984',6378137,298.257223563]],PRIMEM['Greenwich',0],UNIT['Degree',0.017453292519943295]]"
		make_pdf(m, actual_pdf, esri_wkt, render_grid_on_map=True, render_legend=True)

		expected_pdf = "images/pycairo/pdf-printing-expected.pdf"

		diff = abs(os.stat(expected_pdf).st_size - os.stat(actual_pdf).st_size)
		msg = "diff in size (%s) between actual (%s) and expected(%s)" % (diff, actual_pdf, "tests/python_tests/" + expected_pdf)
		eq_(diff < 1500, True, msg)

	def test_pdf_bbox():
		source_xml = "../data/good_maps/marker-text-line.xml"
		m = make_map_from_xml(source_xml)

		output_pdf = "/tmp/pdf_printing_test-pdf_bbox.pdf"
		esri_wkt = """GEOGCS['GCS_WGS_1984',DATUM['D_WGS_1984',SPHEROID['WGS_1984',6378137,298.257223563]],
			PRIMEM['Greenwich',0],UNIT['Degree',0.017453292519943295]]"""
		make_pdf(m, output_pdf, esri_wkt)

		infile = file(output_pdf, "rb")
		pdf_file_reader = PdfFileReader(infile)
		pdf_page = pdf_file_reader.getPage(0)
		bbox = pdf_page.bleedBox
		actual_bbox = [float(bbox[x]) for x in range(0,4)]

		# A4 format has a width of 21cm (8.26772in) and a height of 29.7cm (11.69291in)
		# => width in PDF points (1/72in) is 8.26772*72 ~= 595.3 and 11.69291*72 ~= 841.9
		expected_bbox = [0, 0, 595.3, 841.9]

		for actual, expected in zip(actual_bbox, expected_bbox):
			diff = abs(actual - expected)
			eq_(diff < 10, True, "diff in bbox dimension ({0}) between actual ({1}) and expected({2})".format(
				diff, actual, expected))


# TODO: ideas for further testing on printing module
# - test with and without pangocairo
# - test legend with attribution
# - test graticule (bug at the moment)


if __name__ == "__main__":
    setup()
    exit(run_all(eval(x) for x in dir() if x.startswith("test_")))
