#!/usr/bin/env python
import os
import sqlite3
import sys
import threading

from nose.tools import eq_
from nose.plugins.skip import SkipTest

import mapnik

from .utilities import execution_path, run_all

PYTHON3 = sys.version_info[0] == 3


def setup():
    # All of the paths used are relative, if we run the tests
    # from another directory we need to chdir()
    os.chdir(execution_path('.'))

NUM_THREADS = 10
TOTAL = 245


def create_ds(test_db, table):
    ds = mapnik.SQLite(file=test_db, table=table)
    ds.all_features()
    del ds

if 'sqlite' in mapnik.DatasourceCache.plugin_names():

    def test_rtree_creation():
        if not os.path.exists('../data/sqlite/world.sqlite'):
            raise SkipTest

        test_db = '../data/sqlite/world.sqlite'
        index = test_db + '.index'
        table = 'world_merc'

        if os.path.exists(index):
            os.unlink(index)

        threads = []
        for i in range(NUM_THREADS):
            t = threading.Thread(target=create_ds, args=(test_db, table))
            t.start()
            threads.append(t)

        for i in threads:
            i.join()

        eq_(os.path.exists(index), True)
        conn = sqlite3.connect(index)
        cur = conn.cursor()
        try:
            cur.execute(
                "Select count(*) from idx_%s_GEOMETRY" %
                table.replace(
                    "'", ""))
            conn.commit()
            eq_(cur.fetchone()[0], TOTAL)
        except sqlite3.OperationalError:
            # don't worry about testing # of index records if
            # python's sqlite module does not support rtree
            pass
        cur.close()
        conn.close()

        ds = mapnik.SQLite(file=test_db, table=table)
        fs = list(ds.all_features())
        del ds
        eq_(len(fs), TOTAL)
        os.unlink(index)
        ds = mapnik.SQLite(file=test_db, table=table, use_spatial_index=False)
        fs = list(ds.all_features())
        del ds
        eq_(len(fs), TOTAL)
        eq_(os.path.exists(index), False)

        ds = mapnik.SQLite(file=test_db, table=table, use_spatial_index=True)
        fs = list(ds.all_features())
        # TODO - this loop is not releasing something
        # because it causes the unlink below to fail on windows
        # as the file is still open
        # for feat in fs:
        #    query = mapnik.Query(feat.envelope())
        #    selected = ds.features(query)
        #    eq_(len(selected.features)>=1,True)
        del ds

        eq_(os.path.exists(index), True)
        os.unlink(index)

    test_rtree_creation.requires_data = True

    def test_geometry_round_trip():
        test_db = '/tmp/mapnik-sqlite-point.db'
        ogr_metadata = True

        # create test db
        conn = sqlite3.connect(test_db)
        cur = conn.cursor()
        cur.execute('''
             CREATE TABLE IF NOT EXISTS point_table
             (id INTEGER PRIMARY KEY AUTOINCREMENT, geometry BLOB, name varchar)
             ''')
        # optional: but nice if we want to read with ogr
        if ogr_metadata:
            cur.execute('''CREATE TABLE IF NOT EXISTS geometry_columns (
                        f_table_name VARCHAR,
                        f_geometry_column VARCHAR,
                        geometry_type INTEGER,
                        coord_dimension INTEGER,
                        srid INTEGER,
                        geometry_format VARCHAR )''')
            cur.execute('''INSERT INTO geometry_columns
                        (f_table_name, f_geometry_column, geometry_format,
                        geometry_type, coord_dimension, srid) VALUES
                        ('point_table','geometry','WKB', 1, 1, 4326)''')
        conn.commit()
        cur.close()

        # add a point as wkb (using mapnik) to match how an ogr created db
        # looks
        x = -122  # longitude
        y = 48  # latitude
        wkt = 'POINT(%s %s)' % (x, y)
        # little endian wkb (mapnik will auto-detect and ready either little or
        # big endian (XDR))
        wkb = mapnik.Geometry.from_wkt(wkt).to_wkb(mapnik.wkbByteOrder.NDR)
        values = (None, sqlite3.Binary(wkb), "test point")
        cur = conn.cursor()
        cur.execute(
            '''INSERT into "point_table" (id,geometry,name) values (?,?,?)''',
            values)
        conn.commit()
        cur.close()
        conn.close()

        def make_wkb_point(x, y):
            import struct
            byteorder = 1  # little endian
            endianess = ''
            if byteorder == 1:
                endianess = '<'
            else:
                endianess = '>'
            geom_type = 1  # for a point
            return struct.pack('%sbldd' % endianess,
                               byteorder, geom_type, x, y)

        # confirm the wkb matches a manually formed wkb
        wkb2 = make_wkb_point(x, y)
        eq_(wkb, wkb2)

        # ensure we can read this data back out properly with mapnik
        ds = mapnik.Datasource(
            **{'type': 'sqlite', 'file': test_db, 'table': 'point_table'})
        fs = ds.featureset()
        feat = fs.next()
        eq_(feat.id(), 1)
        eq_(feat['name'], 'test point')
        geom = feat.geometry
        eq_(geom.to_wkt(), 'POINT(-122 48)')
        del ds

        # ensure it matches data read with just sqlite
        conn = sqlite3.connect(test_db)
        cur = conn.cursor()
        cur.execute('''SELECT * from point_table''')
        conn.commit()
        result = cur.fetchone()
        cur.close()
        feat_id = result[0]
        eq_(feat_id, 1)
        name = result[2]
        eq_(name, 'test point')
        geom_wkb_blob = result[1]
        if not PYTHON3:
            geom_wkb_blob = str(geom_wkb_blob)
        eq_(geom_wkb_blob, geom.to_wkb(mapnik.wkbByteOrder.NDR))
        new_geom = mapnik.Geometry.from_wkb(geom_wkb_blob)
        eq_(new_geom.to_wkt(), geom.to_wkt())
        conn.close()
        os.unlink(test_db)

if __name__ == "__main__":
    setup()
    returncode = run_all(eval(x) for x in dir() if x.startswith("test_"))
    exit(returncode)
