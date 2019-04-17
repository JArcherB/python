# -*- coding: utf-8 -*-
"""
Created on Mon Nov 19 13:32:23 2018

@author: jaburton
"""
import arcpy
import shutil

##This is run in ArcGIS Pro to create a list from a selection
#gridlist = []  #create an empty list
#with arcpy.da.SearchCursor('LAS_FileNames_Polygon','FileName') as cursor:
#	for row in cursor:
#		gridlist.append(row[0])


indir = r'\\Slcsufile\suapad\LIDAR\2013_LiDAR\2013_LiDAR_Final\LAS_Final\LAS'
outdir = r'C:\LAS_Data\Millcreek'
for g in gridlist:
    infile = '{}\{}'.format(indir,g)
    outfile = '{}\{}'.format(outdir,g)
    shutil.copy(infile,outfile)
