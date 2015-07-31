#!/usr/bin/env python
# -*- coding: utf-8 -*-

import time
from nose.tools import eq_,assert_almost_equal
import atexit
from utilities import execution_path, run_all
from subprocess import Popen
import errno, threading
import os, mapnik

GEOWAVE_DEMO_APP = 'mil.nga.giat.geowave.datastore.accumulo.app.GeoWaveDemoApp'
GEOWAVE_CLI_MAIN = 'mil.nga.giat.geowave.core.cli.GeoWaveMain'
SHAPEFILE = os.path.join(execution_path('.'),'../data/shp/world_merc.shp')

ZOOKEEPER_URL = 'localhost:2181'
INSTANCE_NAME = 'geowave'
USERNAME = 'root'
PASSWORD = 'password'
TABLE_NAMESPACE = 'mapnik'
ADAPTER_TYPE = 'geotools-vector'
ADAPTER_ID = "world_merc"

DEMO_APP_LOG = 'GeoWaveDemoApp.log'
DEMO_APP_PID = 'geowave-pid.txt'
INGEST_LOG = 'ingest.log'

DEBUG_OUTPUT = True 

def log(msg):
    if DEBUG_OUTPUT:
      print msg

class Command(object):
    def __init__(self, cmd):
        self.cmd = cmd
        self.process = None

    def run(self, timeout=5):
        def target():
            self.process = Popen(self.cmd, shell=True)
            self.process.communicate()

        thread = threading.Thread(target=target)
        thread.start()

        thread.join(timeout)
        if thread.is_alive():
            log('Thread timed out!')
            self.process.terminate()
            thread.join()
            return None
        return self.process.returncode

def setup():
    # All of the paths used are relative, if we run the tests
    # from another directory we need to chdir()
    os.chdir(execution_path('.'))

def geowave_initialize():
    try:
        os.environ['GEOWAVE_RUNTIME_JAR']
    except KeyError:
        print 'GeoWave Initialization Failed!  GEOWAVE_RUNTIME_JAR undefined'
        return False
    
    try:
        os.environ['GEOWAVE_INGEST_JAR']
    except KeyError:
        print 'GeoWave Initialization Failed!  GEOWAVE_INGEST_JAR undefined'
        return False

    log('Starting Mini Accumulo with GeoWave...')
    start_accumulo = Command('nohup java -Dinteractive=false -cp %s %s > %s 2>&1 & echo $! > %s' % (os.environ['GEOWAVE_RUNTIME_JAR'],GEOWAVE_DEMO_APP,DEMO_APP_LOG,DEMO_APP_PID))
    start_accumulo.run()

    log('Sleeping for 15 seconds...')
    time.sleep(15)

    log('Ingesting shapefile...')
    ingest_shapefile = Command('java -cp %s %s -localingest -z %s -u %s -p %s -i %s -n %s -f %s -b %s > %s 2>&1' % (os.environ['GEOWAVE_INGEST_JAR'],GEOWAVE_CLI_MAIN,ZOOKEEPER_URL,USERNAME,PASSWORD,INSTANCE_NAME,TABLE_NAMESPACE,ADAPTER_TYPE,SHAPEFILE,INGEST_LOG))
    ret_val = ingest_shapefile.run(timeout=60)

    if ret_val == 0:
        log('GeoWave Initialization Successful!')
        return True

    log('GeoWave Initialization Failed!')
    return False

def silentremove(filename):
    try:
        os.remove(filename)
    except OSError as e:
        if e.errno != errno.ENOENT:
            raise

def geowave_takedown():
    log('Shutting down Mini Accumulo with Geowave...')
    Command('kill `cat %s` >> %s 2>&1' % (DEMO_APP_PID,DEMO_APP_LOG)).run()
    silentremove(DEMO_APP_PID)
    silentremove(DEMO_APP_LOG)
    silentremove(INGEST_LOG)

if 'geowave' in mapnik.DatasourceCache.plugin_names() \
        and geowave_initialize():
    
    def test_envelope():
        ds = mapnik.GeoWave(zookeeper_url=ZOOKEEPER_URL,
                            instance_name=INSTANCE_NAME,
                            username=USERNAME,
                            password=PASSWORD,
                            table_namespace=TABLE_NAMESPACE,
                            adapter_id=ADAPTER_ID)
        env = ds.envelope()
        assert_almost_equal(env.minx, -180.0, places=1)
        assert_almost_equal(env.miny, -59.641, places=3)
        assert_almost_equal(env.maxx, 180.0, places=1)
        assert_almost_equal(env.maxy, 83.613, places=3)
    
    def test_combined_envelope():
        ds = mapnik.GeoWave(zookeeper_url=ZOOKEEPER_URL,
                            instance_name=INSTANCE_NAME,
                            username=USERNAME,
                            password=PASSWORD,
                            table_namespace=TABLE_NAMESPACE,
                            adapter_id=ADAPTER_ID,
                            cql_filter='BBOX(the_geom, -180.0, 0.0, 180.0, 83.613)')
        env = ds.envelope()
        assert_almost_equal(env.minx, -180.0, places=1)
        assert_almost_equal(env.miny, 0.0, places=1)
        assert_almost_equal(env.maxx, 180.0, places=1)
        assert_almost_equal(env.maxy, 83.613, places=3)

    def test_features():
        ds = mapnik.GeoWave(zookeeper_url=ZOOKEEPER_URL,
                            instance_name=INSTANCE_NAME,
                            username=USERNAME,
                            password=PASSWORD,
                            table_namespace=TABLE_NAMESPACE,
                            adapter_id=ADAPTER_ID)
        fs = ds.featureset()
        feature = fs.next()
        eq_(feature is not None,True)
    
    def test_features_at_point():
        ds = mapnik.GeoWave(zookeeper_url=ZOOKEEPER_URL,
                            instance_name=INSTANCE_NAME,
                            username=USERNAME,
                            password=PASSWORD,
                            table_namespace=TABLE_NAMESPACE,
                            adapter_id=ADAPTER_ID)
        fs = ds.features_at_point(mapnik.Coord(-77.0164, 38.9047), 0.5)
        feature = fs.next()
        eq_(feature['FIPS'],'US')
        eq_(feature['ISO2'],'US')
        eq_(feature['ISO3'],'USA')
        eq_(feature['UN'],840)
        eq_(feature['NAME'],'United States')
        eq_(feature['AREA'],915896)
        eq_(feature['POP2005'],299846449)
        eq_(feature['REGION'],19)
        eq_(feature['SUBREGION'],21)
        eq_(feature['LON'],-98.606000)
        eq_(feature['LAT'],39.622000)

    def test_cql_query_filter():
        ds = mapnik.GeoWave(zookeeper_url=ZOOKEEPER_URL,
                            instance_name=INSTANCE_NAME,
                            username=USERNAME,
                            password=PASSWORD,
                            table_namespace=TABLE_NAMESPACE,
                            adapter_id=ADAPTER_ID,
                            cql_filter='BBOX(the_geom, -6.7597, 52.8478, -5.7597, 53.8478)')
        fs = ds.featureset()
        
        env = ds.envelope()
        eq_(env.minx,-6.7597)
        eq_(env.miny,52.8478)
        eq_(env.maxx,-5.7597)
        eq_(env.maxy,53.8478)

        feature = fs.next()
        eq_(feature['FIPS'],'EI')
        eq_(feature['ISO2'],'IE')
        eq_(feature['ISO3'],'IRL')
        eq_(feature['UN'],372)
        eq_(feature['NAME'],'Ireland')
        eq_(feature['AREA'],6889)
        eq_(feature['POP2005'],4143294)
        eq_(feature['REGION'],150)
        eq_(feature['SUBREGION'],154)
        eq_(feature['LON'],-8.152000)
        eq_(feature['LAT'],53.177000)

    def test_fields_and_types():
        ds = mapnik.GeoWave(zookeeper_url=ZOOKEEPER_URL,
                            instance_name=INSTANCE_NAME,
                            username=USERNAME,
                            password=PASSWORD,
                            table_namespace=TABLE_NAMESPACE,
                            adapter_id=ADAPTER_ID)
        eq_(ds.fields(),['FIPS','ISO2','ISO3','UN','NAME','AREA','POP2005','REGION','SUBREGION','LON','LAT'])
        eq_(ds.field_types(),['str','str','str','int','str','int','int','int','int','float','float'])

    def test_geometry_detection():
        ds = mapnik.GeoWave(zookeeper_url=ZOOKEEPER_URL,
                            instance_name=INSTANCE_NAME,
                            username=USERNAME,
                            password=PASSWORD,
                            table_namespace=TABLE_NAMESPACE,
                            adapter_id=ADAPTER_ID)
        meta = ds.describe()
        eq_('Collection' in str(meta['geometry_type']), True)
    
    atexit.register(geowave_takedown)

if __name__ == "__main__":
    setup()
    exit(run_all(eval(x) for x in dir() if x.startswith("test_")))
