#!/usr/bin/env python
# -*- coding: utf-8 -*-
from __future__ import absolute_import, print_function

import os

from nose.tools import assert_almost_equal, eq_

import mapnik

from .utilities import execution_path, run_all


def setup():
    # All of the paths used are relative, if we run the tests
    # from another directory we need to chdir()
    os.chdir(execution_path('.'))

if 'topojson' in mapnik.DatasourceCache.plugin_names():

    def test_topojson_init():
        # topojson tests/data/json/escaped.geojson -o tests/data/topojson/escaped.topojson --properties
        # topojson version 1.4.2
        ds = mapnik.Datasource(
            type='topojson',
            file='../data/topojson/escaped.topojson')
        e = ds.envelope()
        assert_almost_equal(e.minx, -81.705583, places=7)
        assert_almost_equal(e.miny, 41.480573, places=6)
        assert_almost_equal(e.maxx, -81.705583, places=5)
        assert_almost_equal(e.maxy, 41.480573, places=3)

    def test_topojson_properties():
        ds = mapnik.Datasource(
            type='topojson',
            file='../data/topojson/escaped.topojson')
        f = list(ds.features_at_point(ds.envelope().center()))[0]
        eq_(len(ds.fields()), 11)
        desc = ds.describe()
        eq_(desc['geometry_type'], mapnik.DataGeometryType.Point)

        eq_(f['name'], u'Test')
        eq_(f['int'], 1)
        eq_(f['description'], u'Test: \u005C')
        eq_(f['spaces'], u'this has spaces')
        eq_(f['double'], 1.1)
        eq_(f['boolean'], True)
        eq_(f['NOM_FR'], u'Qu\xe9bec')
        eq_(f['NOM_FR'], u'Québec')

        ds = mapnik.Datasource(
            type='topojson',
            file='../data/topojson/escaped.topojson')
        f = list(ds.all_features())[0]
        eq_(len(ds.fields()), 11)

        desc = ds.describe()
        eq_(desc['geometry_type'], mapnik.DataGeometryType.Point)

        eq_(f['name'], u'Test')
        eq_(f['int'], 1)
        eq_(f['description'], u'Test: \u005C')
        eq_(f['spaces'], u'this has spaces')
        eq_(f['double'], 1.1)
        eq_(f['boolean'], True)
        eq_(f['NOM_FR'], u'Qu\xe9bec')
        eq_(f['NOM_FR'], u'Québec')

    def test_geojson_from_in_memory_string():
        ds = mapnik.Datasource(
            type='topojson',
            inline=open(
                '../data/topojson/escaped.topojson',
                'r').read())
        f = list(ds.all_features())[0]
        eq_(len(ds.fields()), 11)

        desc = ds.describe()
        eq_(desc['geometry_type'], mapnik.DataGeometryType.Point)

        eq_(f['name'], u'Test')
        eq_(f['int'], 1)
        eq_(f['description'], u'Test: \u005C')
        eq_(f['spaces'], u'this has spaces')
        eq_(f['double'], 1.1)
        eq_(f['boolean'], True)
        eq_(f['NOM_FR'], u'Qu\xe9bec')
        eq_(f['NOM_FR'], u'Québec')

#    @raises(RuntimeError)
    def test_that_nonexistant_query_field_throws(**kwargs):
        ds = mapnik.Datasource(
            type='topojson',
            file='../data/topojson/escaped.topojson')
        eq_(len(ds.fields()), 11)
        # TODO - this sorting is messed up
        eq_(ds.fields(), ['name', 'int', 'description',
                          'spaces', 'double', 'boolean', 'NOM_FR',
                          'object', 'array', 'empty_array', 'empty_object'])
        eq_(ds.field_types(), ['str', 'int',
                               'str', 'str', 'float', 'bool', 'str',
                               'str', 'str', 'str', 'str'])
# TODO - should topojson plugin throw like others?
#        query = mapnik.Query(ds.envelope())
#        for fld in ds.fields():
#            query.add_property_name(fld)
#        # also add an invalid one, triggering throw
#        query.add_property_name('bogus')
#        fs = ds.features(query)

if __name__ == "__main__":
    setup()
    exit(run_all(eval(x) for x in dir() if x.startswith("test_")))
