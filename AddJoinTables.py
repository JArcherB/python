# -*- coding: utf-8 -*-
"""
Created on Mon Jan 28 16:32:43 2019

@author: jaburton
"""
import arcpy

arcpy.env.workspace = r'C:\Users\jaburton\Documents\ArcGIS\Projects\Oquirrh View\Oquirrh View.gdb'
arcpy.env.overwriteOutput = 'True'

polygons = r'C:\Users\jaburton\Documents\ArcGIS\Projects\Oquirrh View\Oquirrh View.gdb\AffordableHousing_Polygon'
tables = arcpy.ListTables()
for table in tables:
    print(table)
    arcpy.AddJoin_management(polygons,'NAME', table, 'NAME')
    print('Joins completed')
    
#arcpy.CopyFeatures_management(polygons, 'AffordableHousing_Data')