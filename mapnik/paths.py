import os

mapniklibpath = os.path.join(os.path.dirname(os.path.realpath(__file__)), '..', '..', '..')
inputpluginspath = os.path.join(mapniklibpath, 'mapnik', 'input')
fontscollectionpath = os.path.join(mapniklibpath, 'mapnik', 'fonts')

__all__ = [mapniklibpath,inputpluginspath,fontscollectionpath]
