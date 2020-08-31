# -*- coding: utf-8 -*-
"""
Created on Fri May 10 13:28:00 2019

@author: JBurton_AOR
"""

import arcpy, os
#import Shapefiles_toGDB

#set global environment
arcpy.env.workspace = r'C:\Users\JBurton_AOR\Documents\ArcGIS\Projects\Oahu\Oahu.gdb'
arcpy.env.overwriteOutput = 'True'


def excelToTable():
    """
    Creates a table from excel

    Returns: Table
    """

    in_excel= r'C:\Users\JBurton_AOR\Documents\ArcGIS\Projects\Oahu\Oahu_Attribute_Table.xlsx'
    out_table= r'C:\Users\JBurton_AOR\Documents\ArcGIS\Projects\Oahu\Oahu.gdb\Oahu_Attribute_Table'

    #excel to table using local variables
    arcpy.ExcelToTable_conversion(in_excel, out_table)
    print ('Oahu attribute table completed')
    return


def shpToGDB():
    """
    Takes shapefiles from a folder and copies them to a GDB

    Returns: Feature classes
    """
    #set local environment for this function
    arcpy.env.workspace = r'C:\Users\JBurton_AOR\Documents\ArcGIS\Projects\Oahu\daily_shapefiles'
    arcpy.env.overwriteOutput = 'True'

    #create list to use in for loop
    shpList = arcpy.ListFeatureClasses()
    print (shpList)
    
    out_GDB = r'C:\Users\JBurton_AOR\Documents\ArcGIS\Projects\Oahu\Daily_Coverage.gdb'
    
    arcpy.Delete_management(out_GDB)
    print('Daily_Coverage.gdb deleted')
    
    path = r'C:\Users\JBurton_AOR\Documents\ArcGIS\Projects\Oahu'
    name = r'Daily_Coverage.gdb'
    arcpy.CreateFileGDB_management(path, name)
    print ('Daily_Coverage.gdb created')
    
    #for loop runs tool on each shapefile in the folder
    for sf in shpList:
        arcpy.FeatureClassToGeodatabase_conversion(sf, out_GDB)
        print (sf + ' ' + 'was exported')
    print('Shapefiles were exported to the GDB')
    return 


def addFields():
    """
    Makes a list of the feature classes, adds fields, populates data

    Returns: Modified feature classes
    """

    arcpy.env.workspace = r'C:\Users\JBurton_AOR\Documents\ArcGIS\Projects\Oahu\Daily_Coverage.gdb'
    arcpy.env.overwriteOutput = 'True'

    logs = arcpy.ListFeatureClasses()
    print (logs)
    #Variable for Calculate Geometry
    field = 'ACRES'
    
    
    #for loop to add fields and calculate acreage
    for fc in logs:
        print ('processing' + " " + fc)

        #add FILE field
        arcpy.AddField_management(fc, 'FILE_NAME', 'TEXT')

        #add ACRES field
        arcpy.AddField_management(fc, 'ACRES', 'FLOAT')

        #add CULM_ACRES field
        arcpy.AddField_management(fc, 'CULM_ACRES', 'FLOAT')
        print ('added fields')

        #Calculate geometry - acres
        arcpy.CalculateGeometryAttributes_management(fc, [[field, 'AREA']], area_unit='Acres')

        #define field name and expression
        fieldName = 'FILE_NAME'
        expression = str(fc) #populates field

        #Calculate FILE name
        arcpy.CalculateField_management(fc, fieldName, '"'+expression+'"', "PYTHON")
        print ('calculated fields')
    return

def append():
    """
    Appends all the feature classes in Daily_Coverage.gdb

    Returns: New feature class ready for join
    """
    
    arcpy.env.workspace = r'C:\Users\JBurton_AOR\Documents\ArcGIS\Projects\Oahu\Daily_Coverage.gdb'
    arcpy.env.overwriteOutput = 'True'
    
    print ('appending feature classes')
    #set local variables
    outLocation = r'C:\Users\JBurton_AOR\Documents\ArcGIS\Projects\Oahu\Oahu.gdb'
    outName = 'DailyCoverage_Append'
    template = 'clean_hydroBuffer_06242019'
    schemaType = 'NO_TEST'
    fieldMappings = ""
    subtype = ""

    fcList = arcpy.ListFeatureClasses()
    print (fcList)
   
    emptyFC = arcpy.CreateFeatureclass_management(outLocation, outName, 'POLYGON', template)
    print ('created empty feature class' + " " + str(outName))
   
    #append into one feature class
    arcpy.Append_management(fcList, emptyFC, 'TEST')
    print ('Append Complete')
    return 

def joinTable():
    """
    Joins appended feature class to excel table

    Returns: New feature class ready for union
    """
    arcpy.env.workspace = r'C:\Users\JBurton_AOR\Documents\ArcGIS\Projects\Oahu\Oahu.gdb'
    arcpy.env.overwriteOutput = 'True'
    
    #local variables for AddJoin
    in_layer = 'DailyCoverage_Append'
    in_field = 'FILE_NAME'
    join_table = 'Oahu_Attribute_Table'
    join_field = 'FILE'

    joinedTable = arcpy.management.AddJoin(in_layer, in_field, join_table, join_field, "KEEP_ALL")
    print ('Join complete')
    #variables for Copy Features
    outFC = r'C:\Users\JBurton_AOR\Documents\ArcGIS\Projects\Oahu\Oahu.gdb\DailyCoverage_AddJoin'
    
    arcpy.CopyFeatures_management(joinedTable, outFC)
    print ('New feature class created')
    
    in_dataset = r'C:\Users\JBurton_AOR\Documents\ArcGIS\Projects\Oahu\Oahu.gdb\DailyCoverage_AddJoin'
    out_dataset = r'C:\Users\JBurton_AOR\Documents\ArcGIS\Projects\Oahu\Oahu.gdb\DailyCoverage_Projected'
    spatial_ref = arcpy.Describe(r'C:\Users\JBurton_AOR\Documents\ArcGIS\Projects\Oahu\daily_shapefiles\clean_hydroBuffer_06242019.shp').spatialReference
    print ('Spatial Reference described')
    arcpy.Project_management(in_dataset, out_dataset, out_coor_system = spatial_ref, in_coor_system = spatial_ref)
    print('DailyCoverage_Projected was created')
    
    inGDB = r'C:\Users\JBurton_AOR\Documents\ArcGIS\Projects\Oahu\Oahu_Dashboard.gdb\DailyCoverage_Projected'
    arcpy.CopyFeatures_management(out_dataset, inGDB)
    print ('Daily Log Projected was copied to Dashboard GDB')
#    import zipfile
#
#    #Creates the empty zip file and opens it for writing
#    myzipfile = zipfile.ZipFile(r"C:\Users\JBurton_AOR\Documents\LakeShasta\Dashboard.zip", 'w', zipfile.ZIP_DEFLATED)
#    for root, dirs, files in os.walk(r"C:\Users\JBurton_AOR\Documents\LakeShasta"):
#        if root == r"C:\Users\JBurton_AOR\Documents\LakeShasta\Dashboard_LakeShasta.gdb":
#            for f in files:
#                myzipfile.write(os.path.join(root, f))
    
    return

def searchCursor():
    """
    iterates through table adding acreage for each day

    Returns:CULM_ACRES populated
    """
    arcpy.env.workspace = r'C:\Users\JBurton_AOR\Documents\ArcGIS\Projects\Oahu\Oahu_Dashboard.gdb'
    arcpy.env.overwriteOutput = 'True'
    counter = 0
    fc = r'C:\Users\JBurton_AOR\Documents\ArcGIS\Projects\Oahu\Oahu_Dashboard.gdb\DailyCoverage_Projected'
    field1 = 'DailyCoverage_Append_ACRES'
    field2 = 'DailyCoverage_Append_CULM_ACRES'
    
    with arcpy.da.UpdateCursor(fc, [field1, field2]) as cursor:
        for row in cursor:
            counter = counter + row[0]
            row[1] = counter
            cursor.updateRow(row)
    del cursor
    print ('CULM_ACRES was populated')
    
    return
            
    

def union():
    """
    Unions the result from joinTable

    Returns: New feature class ready for dissolve
    """
    arcpy.env.workspace = r'C:\Users\JBurton_AOR\Documents\ArcGIS\Projects\Oahu\Oahu.gdb'
    arcpy.env.overwriteOutput = 'True'
    
    #local variable for Union
    in_features = r'C:\Users\JBurton_AOR\Documents\ArcGIS\Projects\Oahu\Oahu_Dashboard.gdb\DailyCoverage_Projected'
    out_features = r'C:\Users\JBurton_AOR\Documents\ArcGIS\Projects\Oahu\Oahu.gdb\DailyCoverage_Union'
    
    arcpy.Union_analysis(in_features, out_features)
    print ('Union feature class created')
    
    return

def dissolve():
    """
    Dissolves Union into one polyogn

    Returns: Polygon
    """
    arcpy.env.workspace = r'C:\Users\JBurton_AOR\Documents\ArcGIS\Projects\Oahu\Oahu.gdb'
    arcpy.env.overwriteOutput = 'True'
    
    #local variable for Dissolve
    in_features = r'C:\Users\JBurton_AOR\Documents\ArcGIS\Projects\Oahu\Oahu.gdb\DailyCoverage_Union'
    out_features = r'C:\Users\JBurton_AOR\Documents\ArcGIS\Projects\Oahu\Oahu.gdb\Total_Coverage'
    
    arcpy.Dissolve_management(in_features, out_features)
    print ('Total Coverage created')


##    #add ACRES field
##    arcpy.AddField_management(out_features, 'ACRES', 'FLOAT')
##    print ('added fields')
##
##    outGDB = r'C:\Users\JBurton_AOR\Documents\ArcGIS\Projects\Oahu\Oahu_Dashboard.gdb\Oahu_Total_Coverage'
##    field = 'ACRES'
##
##    
##    #Calculate geometry - acres
##    arcpy.CalculateGeometryAttributes_management(out_features, [[field, 'AREA']], area_unit='Acres')
##    print ('calculated acreage')
##
##    arcpy.CopyFeatures_management(out_features, outGDB)
##    print ('Total Coverage was copied to Oahu Dashboard GDB')

    return

def intersect():
    """
    Intersects dissolve wiht MRS boundary

    Returns: Polygon
    """
    arcpy.env.workspace = r'C:\Users\JBurton_AOR\Documents\ArcGIS\Projects\Oahu\Oahu.gdb'
    arcpy.env.overwriteOutput = 'True'

    
    #variables for intersect analysis
    MRS = r'C:\Users\JBurton_AOR\Documents\ArcGIS\Projects\Oahu\Oahu.gdb\MRS_WGS84_UTM4N'
    Coverage = r'C:\Users\JBurton_AOR\Documents\ArcGIS\Projects\Oahu\Oahu.gdb\Total_Coverage'
    outGDB = r'C:\Users\JBurton_AOR\Documents\ArcGIS\Projects\Oahu\Oahu.gdb\Oahu_Total_Coverage'

    arcpy.Delete_management(outGDB)
    print('Oahu Total Coverage deleted')
    
    inFeatures = ['MRS_WGS84_UTM4N','Total_Coverage']
    intersectOutput = 'Oahu_Total_Coverage'
    arcpy.Intersect_analysis(inFeatures, outGDB)
    print ('intersect complete')
    
    #add ACRES field
    arcpy.AddField_management(outGDB, 'ACRES', 'FLOAT')
    print ('added fields')

    field = 'ACRES'

    #Calculate geometry - acres
    arcpy.CalculateGeometryAttributes_management(outGDB, [[field, 'AREA']], area_unit='Acres')
    print ('calculated acreage')

    #arcpy.CopyFeatures_management(intersectOutput, outGDB)
    print ('Total Coverage was copied to Oahu_Dashboard.gdb')

if __name__=='__main__':
    excelToTable()
    shpToGDB()
    addFields()
    append()
    joinTable()
    searchCursor()
    union()
    dissolve()
    intersect()
    
    
