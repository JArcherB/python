# -*- coding: utf-8 -*-
"""
Created on Wed Nov 21 14:28:47 2018

@author: JBorgione
"""

import arcpy
arcpy.env.overwriteOutput = True
inGDB = r'C:\Replicas\Replicas.gdb'
outGDB = r'J:\Replicas.gdb'
arcpy.Copy_management(inGDB, outGDB)