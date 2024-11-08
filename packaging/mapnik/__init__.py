#
# This file is part of Mapnik (c++ mapping toolkit)
# Copyright (C) 2024 Artem Pavlenko
#
# This library is free software; you can redistribute it and/or
# modify it under the terms of the GNU Lesser General Public
# License as published by the Free Software Foundation; either
# version 2.1 of the License, or (at your option) any later version.
#
# This library is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the GNU
# Lesser General Public License for more details.
#
# You should have received a copy of the GNU Lesser General Public
# License along with this library; if not, write to the Free Software
# Foundation, Inc., 51 Franklin St, Fifth Floor, Boston, MA  02110-1301  USA
#

"""Mapnik Python module.

Python bindings to the Mapnik C++ shared library.

Several things happen when you do:

    >>> import mapnik

 1) Mapnik C++ objects are imported via the '__init__.py' from the '_mapnik.so' shared object
    (_mapnik.pyd on win) which references libmapnik.so (linux), libmapnik.dylib (mac), or
    mapnik.dll (win32).

 2) The paths to the input plugins and font directories are imported from the 'paths.py'
    file which was constructed and installed during SCons installation.

 3) All available input plugins and TrueType fonts are automatically registered.

"""

import itertools
import os
import warnings

def bootstrap_env():
    """
    If an optional settings file exists, inherit its
    environment settings before loading the mapnik library.

    This feature is intended for customized packages of mapnik.

    The settings file should be a python file with an 'env' variable
    that declares a dictionary of key:value pairs to push into the
    global process environment, if not already set, like:

        env = {'ICU_DATA':'/usr/local/share/icu/'}
    """
    if os.path.exists(os.path.join(
            os.path.dirname(__file__), 'mapnik_settings.py')):
        from .mapnik_settings import env
        process_keys = os.environ.keys()
        for key, value in env.items():
            if key not in process_keys:
                os.environ[key] = value

bootstrap_env()

from ._mapnik import *

def Shapefile(**keywords):
    """Create a Shapefile Datasource.

     Required keyword arguments:
       file -- path to shapefile without extension

     Optional keyword arguments:
       base -- path prefix (default None)
       encoding -- file encoding (default 'utf-8')

     >>> from mapnik import Shapefile, Layer
     >>> shp = Shapefile(base='/home/mapnik/data',file='world_borders')
     >>> lyr = Layer('Shapefile Layer')
     >>> lyr.datasource = shp

    """
    return CreateDatasource(type='shape', **keywords)

def CSV(**keywords):
    """Create a CSV Datasource.

    Required keyword arguments:
      file -- path to csv

    Optional keyword arguments:
      inline -- inline CSV string (if provided 'file' argument will be ignored and non-needed)
      base -- path prefix (default None)
      encoding -- file encoding (default 'utf-8')
      row_limit -- integer limit of rows to return (default: 0)
      strict -- throw an error if an invalid row is encountered
      escape -- The escape character to use for parsing data
      quote -- The quote character to use for parsing data
      separator -- The separator character to use for parsing data
      headers -- A comma separated list of header names that can be set to add headers to data that lacks them
      filesize_max -- The maximum filesize in MB that will be accepted

    >>> from mapnik import CSV
    >>> csv = CSV(file='test.csv')

    >>> from mapnik import CSV
    >>> csv = CSV(inline='''wkt,Name\n"POINT (120.15 48.47)","Winthrop, WA"''')

    For more information see https://github.com/mapnik/mapnik/wiki/CSV-Plugin

    """
    return CreateDatasource(type='csv', **keywords)


def GeoJSON(**keywords):
    """Create a GeoJSON Datasource.

    Required keyword arguments:
      file -- path to json

    Optional keyword arguments:
      encoding -- file encoding (default 'utf-8')
      base -- path prefix (default None)

    >>> from mapnik import GeoJSON
    >>> geojson = GeoJSON(file='test.json')

    """
    return CreateDatasource(type='geojson', **keywords)


def PostGIS(**keywords):
    """Create a PostGIS Datasource.

    Required keyword arguments:
      dbname -- database name to connect to
      table -- table name or subselect query

      *Note: if using subselects for the 'table' value consider also
       passing the 'geometry_field' and 'srid' and 'extent_from_subquery'
       options and/or specifying the 'geometry_table' option.

    Optional db connection keyword arguments:
      user -- database user to connect as (default: see postgres docs)
      password -- password for database user (default: see postgres docs)
      host -- postgres hostname (default: see postgres docs)
      port -- postgres port (default: see postgres docs)
      initial_size -- integer size of connection pool (default: 1)
      max_size -- integer max of connection pool (default: 10)
      persist_connection -- keep connection open (default: True)

    Optional table-level keyword arguments:
      extent -- manually specified data extent (comma delimited string, default: None)
      estimate_extent -- boolean, direct PostGIS to use the faster, less accurate `estimate_extent` over `extent` (default: False)
      extent_from_subquery -- boolean, direct Mapnik to query Postgis for the extent of the raw 'table' value (default: uses 'geometry_table')
      geometry_table -- specify geometry table to use to look up metadata (default: automatically parsed from 'table' value)
      geometry_field -- specify geometry field to use (default: first entry in geometry_columns)
      srid -- specify srid to use (default: auto-detected from geometry_field)
      row_limit -- integer limit of rows to return (default: 0)
      cursor_size -- integer size of binary cursor to use (default: 0, no binary cursor is used)

    >>> from mapnik import PostGIS, Layer
    >>> params = dict(dbname=env['MAPNIK_NAME'],table='osm',user='postgres',password='gis')
    >>> params['estimate_extent'] = False
    >>> params['extent'] = '-20037508,-19929239,20037508,19929239'
    >>> postgis = PostGIS(**params)
    >>> lyr = Layer('PostGIS Layer')
    >>> lyr.datasource = postgis

    """
    return CreateDatasource(type='postgis', **keywords)


def PgRaster(**keywords):
    """Create a PgRaster Datasource.

    Required keyword arguments:
      dbname -- database name to connect to
      table -- table name or subselect query

      *Note: if using subselects for the 'table' value consider also
       passing the 'raster_field' and 'srid' and 'extent_from_subquery'
       options and/or specifying the 'raster_table' option.

    Optional db connection keyword arguments:
      user -- database user to connect as (default: see postgres docs)
      password -- password for database user (default: see postgres docs)
      host -- postgres hostname (default: see postgres docs)
      port -- postgres port (default: see postgres docs)
      initial_size -- integer size of connection pool (default: 1)
      max_size -- integer max of connection pool (default: 10)
      persist_connection -- keep connection open (default: True)

    Optional table-level keyword arguments:
      extent -- manually specified data extent (comma delimited string, default: None)
      estimate_extent -- boolean, direct PostGIS to use the faster, less accurate `estimate_extent` over `extent` (default: False)
      extent_from_subquery -- boolean, direct Mapnik to query Postgis for the extent of the raw 'table' value (default: uses 'geometry_table')
      raster_table -- specify geometry table to use to look up metadata (default: automatically parsed from 'table' value)
      raster_field -- specify geometry field to use (default: first entry in raster_columns)
      srid -- specify srid to use (default: auto-detected from geometry_field)
      row_limit -- integer limit of rows to return (default: 0)
      cursor_size -- integer size of binary cursor to use (default: 0, no binary cursor is used)
      use_overviews -- boolean, use overviews when available (default: false)
      prescale_rasters -- boolean, scale rasters on the db side (default: false)
      clip_rasters -- boolean, clip rasters on the db side (default: false)
      band -- integer, if non-zero interprets the given band (1-based offset) as a data raster (default: 0)

    >>> from mapnik import PgRaster, Layer
    >>> params = dict(dbname='mapnik',table='osm',user='postgres',password='gis')
    >>> params['estimate_extent'] = False
    >>> params['extent'] = '-20037508,-19929239,20037508,19929239'
    >>> pgraster = PgRaster(**params)
    >>> lyr = Layer('PgRaster Layer')
    >>> lyr.datasource = pgraster

    """
    return CreateDatasource(type = 'pgraster', **keywords)


def Raster(**keywords):
    """Create a Raster (Tiff) Datasource.

    Required keyword arguments:
      file -- path to stripped or tiled tiff
      lox -- lowest (min) x/longitude of tiff extent
      loy -- lowest (min) y/latitude of tiff extent
      hix -- highest (max) x/longitude of tiff extent
      hiy -- highest (max) y/latitude of tiff extent

    Hint: lox,loy,hix,hiy make a Mapnik Box2d

    Optional keyword arguments:
      base -- path prefix (default None)
      multi -- whether the image is in tiles on disk (default False)

    Multi-tiled keyword arguments:
      x_width -- virtual image number of tiles in X direction (required)
      y_width -- virtual image number of tiles in Y direction (required)
      tile_size -- if an image is in tiles, how large are the tiles (default 256)
      tile_stride -- if an image is in tiles, what's the increment between rows/cols (default 1)

    >>> from mapnik import Raster, Layer
    >>> raster = Raster(base='/home/mapnik/data',file='elevation.tif',lox=-122.8,loy=48.5,hix=-122.7,hiy=48.6)
    >>> lyr = Layer('Tiff Layer')
    >>> lyr.datasource = raster

    """
    return CreateDatasource(type='raster', **keywords)


def Gdal(**keywords):
    """Create a GDAL Raster Datasource.

    Required keyword arguments:
      file -- path to GDAL supported dataset

    Optional keyword arguments:
      base -- path prefix (default None)
      shared -- boolean, open GdalDataset in shared mode (default: False)
      bbox -- tuple (minx, miny, maxx, maxy). If specified, overrides the bbox detected by GDAL.

    >>> from mapnik import Gdal, Layer
    >>> dataset = Gdal(base='/home/mapnik/data',file='elevation.tif')
    >>> lyr = Layer('GDAL Layer from TIFF file')
    >>> lyr.datasource = dataset

    """
    keywords['type'] = 'gdal'
    if 'bbox' in keywords:
        if isinstance(keywords['bbox'], (tuple, list)):
            keywords['bbox'] = ','.join([str(item)
                                         for item in keywords['bbox']])
    return CreateDatasource(**keywords)


def Occi(**keywords):
    """Create a Oracle Spatial (10g) Vector Datasource.

    Required keyword arguments:
      user -- database user to connect as
      password -- password for database user
      host -- oracle host to connect to (does not refer to SID in tsnames.ora)
      table -- table name or subselect query

    Optional keyword arguments:
      initial_size -- integer size of connection pool (default 1)
      max_size -- integer max of connection pool (default 10)
      extent -- manually specified data extent (comma delimited string, default None)
      estimate_extent -- boolean, direct Oracle to use the faster, less accurate estimate_extent() over extent() (default False)
      encoding -- file encoding (default 'utf-8')
      geometry_field -- specify geometry field (default 'GEOLOC')
      use_spatial_index -- boolean, force the use of the spatial index (default True)

    >>> from mapnik import Occi, Layer
    >>> params = dict(host='myoracle',user='scott',password='tiger',table='test')
    >>> params['estimate_extent'] = False
    >>> params['extent'] = '-20037508,-19929239,20037508,19929239'
    >>> oracle = Occi(**params)
    >>> lyr = Layer('Oracle Spatial Layer')
    >>> lyr.datasource = oracle
    """
    keywords['type'] = 'occi'
    return CreateDatasource(**keywords)


def Ogr(**keywords):
    """Create a OGR Vector Datasource.

    Required keyword arguments:
      file -- path to OGR supported dataset
      layer -- name of layer to use within datasource (optional if layer_by_index or layer_by_sql is used)

    Optional keyword arguments:
      layer_by_index -- choose layer by index number instead of by layer name or sql.
      layer_by_sql -- choose layer by sql query number instead of by layer name or index.
      base -- path prefix (default None)
      encoding -- file encoding (default 'utf-8')

    >>> from mapnik import Ogr, Layer
    >>> datasource = Ogr(base='/home/mapnik/data',file='rivers.geojson',layer='OGRGeoJSON')
    >>> lyr = Layer('OGR Layer from GeoJSON file')
    >>> lyr.datasource = datasource

    """
    keywords['type'] = 'ogr'
    return CreateDatasource(**keywords)


def SQLite(**keywords):
    """Create a SQLite Datasource.

    Required keyword arguments:
      file -- path to SQLite database file
      table -- table name or subselect query

    Optional keyword arguments:
      base -- path prefix (default None)
      encoding -- file encoding (default 'utf-8')
      extent -- manually specified data extent (comma delimited string, default None)
      metadata -- name of auxiliary table containing record for table with xmin, ymin, xmax, ymax, and f_table_name
      geometry_field -- name of geometry field (default 'the_geom')
      key_field -- name of primary key field (default 'OGC_FID')
      row_offset -- specify a custom integer row offset (default 0)
      row_limit -- specify a custom integer row limit (default 0)
      wkb_format -- specify a wkb type of 'spatialite' (default None)
      use_spatial_index -- boolean, instruct sqlite plugin to use Rtree spatial index (default True)

    >>> from mapnik import SQLite, Layer
    >>> sqlite = SQLite(base='/home/mapnik/data',file='osm.db',table='osm',extent='-20037508,-19929239,20037508,19929239')
    >>> lyr = Layer('SQLite Layer')
    >>> lyr.datasource = sqlite

    """
    keywords['type'] = 'sqlite'
    return CreateDatasource(**keywords)


def Rasterlite(**keywords):
    """Create a Rasterlite Datasource.

    Required keyword arguments:
      file -- path to Rasterlite database file
      table -- table name or subselect query

    Optional keyword arguments:
      base -- path prefix (default None)
      extent -- manually specified data extent (comma delimited string, default None)

    >>> from mapnik import Rasterlite, Layer
    >>> rasterlite = Rasterlite(base='/home/mapnik/data',file='osm.db',table='osm',extent='-20037508,-19929239,20037508,19929239')
    >>> lyr = Layer('Rasterlite Layer')
    >>> lyr.datasource = rasterlite

    """
    keywords['type'] = 'rasterlite'
    return CreateDatasource(**keywords)

def register_plugins(path=None):
    """Register plugins located by specified path"""
    if not path:
        if 'MAPNIK_INPUT_PLUGINS_DIRECTORY' in os.environ:
            path = os.environ.get('MAPNIK_INPUT_PLUGINS_DIRECTORY')
        else:
            from .paths import inputpluginspath
            path = inputpluginspath
    DatasourceCache.register_datasources(path, False)


def register_fonts(path=None, valid_extensions=[
                   '.ttf', '.otf', '.ttc', '.pfa', '.pfb', '.ttc', '.dfont', '.woff']):
    """Recursively register fonts using path argument as base directory"""
    if not path:
        if 'MAPNIK_FONT_DIRECTORY' in os.environ:
            path = os.environ.get('MAPNIK_FONT_DIRECTORY')
        else:
            from .paths import fontscollectionpath
            path = fontscollectionpath
    for dirpath, _, filenames in os.walk(path):
        for filename in filenames:
            if os.path.splitext(filename.lower())[1] in valid_extensions:
                FontEngine.register_font(os.path.join(dirpath, filename))

# # auto-register known plugins and fonts
register_plugins()
register_fonts()
