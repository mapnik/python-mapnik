#!/usr/bin/env python

import os

from nose.tools import eq_
import PyPDF2

import mapnik
from .utilities import execution_path, run_all


def setup():
    # All of the paths used are relative, if we run the tests
    # from another directory we need to chdir()
    os.chdir(execution_path("."))

def make_map_from_xml(source_xml):
	m = mapnik.Map(210,297)
	mapnik.load_map(m, source_xml, True)
	m.zoom_all()

	return m

if mapnik.has_pycairo():
	def make_pdf(m, output_pdf, esri_wkt):
		page = mapnik.printing.PDFPrinter(
			margin=0, scale=mapnik.printing.any_scale,
			centering=mapnik.printing.centering.both,
			use_ocg_layers=True)
		page.render_map(m, output_pdf)
		page.finish()
		page.add_geospatial_pdf_header(m, output_pdf, wkt=esri_wkt)

	def test_pdf_bbox():
		source_xml = "../data/good_maps/marker-text-line.xml"
		m = make_map_from_xml(source_xml)

		output_pdf = "/tmp/pdf_printing_test-pdf_bbox.pdf"
		esri_wkt = """GEOGCS['GCS_WGS_1984',DATUM['D_WGS_1984',SPHEROID['WGS_1984',6378137,298.257223563]],
			PRIMEM['Greenwich',0],UNIT['Degree',0.017453292519943295]]"""
		make_pdf(m, output_pdf, esri_wkt)

		infile = file(output_pdf, 'rb')
		pdf_file_reader = PyPDF2.PdfFileReader(infile)
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


if __name__ == "__main__":
    setup()
    exit(run_all(eval(x) for x in dir() if x.startswith("test_")))
