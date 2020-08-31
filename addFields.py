# -*- coding: utf-8 -*-
"""
Created on Wed May 15 12:56:34 2019

@author: JBurton_AOR
"""
import arcpy 

arcpy.env.workspace = r'C:\Users\JBurton_AOR\Documents\ArcGIS\Projects\LakeShasta\TrackLogs.gdb'
arcpy.env.overwriteOutput = 'True'

def addFields():
    """
    Makes a list of the feature classes, adds fields, populates data
    
    Returns: Modified feature classes
    """
    
    logs = arcpy.ListFeatureClasses()
    print (logs)
    #Variable for Calculate Geometry
    field = 'ACRES'
    
    #for loop to add fields and calculate acreage
    for fc in logs:    
        print ('processing' + " " + fc)
        
        #add FILE field
        arcpy.AddField_management(fc, 'FILE', 'TEXT')
        
        #add ACRES field
        arcpy.AddField_management(fc, 'ACRES', 'FLOAT')
        print ('added fields')
        
        #Calculate geometry - acres
        arcpy.CalculateGeometryAttributes_management(fc, [[field, 'AREA']], area_unit='Acres')
        
        #define field name and expression
        fieldName = 'FILE'
        expression = str(fc) #populates field
        
        #Calculate FILE name
        arcpy.CalculateField_management(fc, fieldName, '"'+expression+'"', "PYTHON")
        print ('calculated fields')
    return

if __name__=='__main__':
    addFields()