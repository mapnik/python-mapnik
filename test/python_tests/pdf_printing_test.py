import mapnik
import os

def make_map_from_xml(source_xml):
        m = mapnik.Map(100, 100)
        mapnik.load_map(m, source_xml, True)
        m.zoom_all()
        return m

def make_pdf(m, output_pdf, esri_wkt):
        # renders a PDF with a grid and a legend
        page = mapnik.printing.PDFPrinter(use_ocg_layers=True)

        page.render_map(m, output_pdf)
        page.render_grid_on_map(m)
        page.render_legend(m)

        page.finish()
        page.add_geospatial_pdf_header(m, output_pdf, wkt=esri_wkt)

if mapnik.has_pycairo():
        import mapnik.printing

        def test_pdf_printing():
                source_xml = './test/data/good_maps/marker-text-line.xml'.encode('utf-8')
                m = make_map_from_xml(source_xml)

                actual_pdf = "/tmp/pdf-printing-actual.pdf"
                esri_wkt = 'GEOGCS["GCS_WGS_1984",DATUM["D_WGS_1984",SPHEROID["WGS_1984",6378137,298.257223563]],PRIMEM["Greenwich",0],UNIT["Degree",0.017453292519943295]]'
                make_pdf(m, actual_pdf, esri_wkt)

                expected_pdf = './test/python_tests/images/pycairo/pdf-printing-expected.pdf'

                diff = abs(os.stat(expected_pdf).st_size - os.stat(actual_pdf).st_size)
                msg = 'diff in size (%s) between actual (%s) and expected(%s)' % (diff, actual_pdf, 'tests/python_tests/' + expected_pdf)
                assert diff < 1500, msg

# TODO: ideas for further testing on printing module
# - test with and without pangocairo
# - test legend with attribution
# - test graticule (bug at the moment)
