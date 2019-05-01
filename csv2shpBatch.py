import arcpy
import os

csvWorkspace = r"C:\Users\JBurton_AOR\Documents\FLBGR\CSV"
arcpy.env.workspace = csvWorkspace
arcpy.env.overwriteOutput = True

gdb = r"C:\Users\JBurton_AOR\Documents\ArcGIS\Projects\FLBGR\FLBGR.gdb"
csvList = arcpy.ListFiles("*.csv")
x = "Easting"
y = "Northing"
#z = "Elevation"
sr = arcpy.SpatialReference(2232)


for csvFile in csvList:
    event = "exc_results_1"
    print csvFile
    arcpy.MakeXYEventLayer_management(csvFile,x,y,event,sr)
    shpfile = os.path.join(gdb, os.path.splitext(csvFile)[0])
    arcpy.CopyFeatures_management(event,shpfile)

    del event
