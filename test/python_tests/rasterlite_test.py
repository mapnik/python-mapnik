import os
import mapnik
import pytest

from .utilities import execution_path

@pytest.fixture
def setup():
    # All of the paths used are relative, if we run the tests
    # from another directory we need to chdir()
    os.chdir(execution_path('.'))
    yield

if 'rasterlite' in mapnik.DatasourceCache.plugin_names():

    def test_rasterlite():
        ds = mapnik.Rasterlite(
            file='../data/rasterlite/globe.sqlite',
            table='globe'
        )
        e = ds.envelope()

        assert e.minx == pytest.approx(-180,abs=1e-5)
        assert e.miny == pytest.approx(-90, abs=1e-5)
        assert e.maxx == pytest.approx(180, abs=1e-5)
        assert e.maxy == pytest.approx( 90, abs=1e-5)
        assert len(ds.fields()) == 0
        query = mapnik.Query(ds.envelope())
        for fld in ds.fields():
            query.add_property_name(fld)
        fs = ds.features(query)
        feat = fs.next()
        assert feat.id() == 1
        assert feat.attributes == {}
