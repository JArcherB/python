import arcpy
from arcpy import env
import os
from os.path import join
from arcpy.sa import *
arcpy.CheckOutExtension('spatial')

env.workspace = r'D:\VectorTiles\VectorTileTerrain.gdb'

                                        #30Meter   10000
def createPolyShades(inRaster, reclass, rasterRes, minPolyArea):

    for interval in remapDict:

        outPolyFGD = r'D:\VectorTiles\HillshadePolygons.gdb'

        outRasterName = '{}_Interval{}'.format(inRaster, interval)
        outPolys = join(outPolyFGD, 'PolyShade_{}_{}class'.format(rasterRes, interval))

        newRange = RemapRange(remapDict[interval])

        outRaster = Reclassify(inRaster, 'Value', newRange)
        outRaster.save(outRasterName)
        print outRasterName + ' Created'

        arcpy.RasterToPolygon_conversion(outRasterName, outPolys, 'SIMPLIFY')
        print outPolys + ' Created'

        sql_254 = """"{}" = {}""".format('gridcode', 254)
        outPolys_254FL = arcpy.MakeFeatureLayer_management(outPolys, 'outPolysFL', sql_254)
        arcpy.DeleteFeatures_management(outPolys_254FL)
        arcpy.Delete_management(outPolys_254FL)
        print 'Deleted gridcode 254'

        sql_MinPolyArea = """"{}" < {}""".format('Shape_Area', minPolyArea)
        outPolys_minPolysFL = arcpy.MakeFeatureLayer_management(outPolys, 'outPolys_minPolysFL', sql_MinPolyArea)
        arcpy.DeleteFeatures_management(outPolys_minPolysFL)
        arcpy.Delete_management(outPolys_minPolysFL)
        print 'Deleted polygons less than {} sq meters'.format(minPolyArea)

        if not arcpy.TestSchemaLock(outRasterName):
            print outRasterName + ' is LOCKED'
            print ''
            continue
        else:
            arcpy.Delete_management(outRasterName)
            print 'Deleted ' + outRasterName
            print ''

def deleteHillshades(wildcard):
    rasterList = arcpy.ListRasters()
    for r in rasterList:
        if wildcard in r:
            arcpy.Delete_management(r)
            print 'Deleted ' + r



remapDict = {45:[[0, 45, 45], [45.1, 254, 254]], \
             110:[[0, 110, 110], [110.1, 254, 254]], \
             160:[[0, 160, 160], [160.1, 254, 254]], \
             200:[[0, 200, 200], [200.1, 254, 254]]}


#inHillshade = 'HillShade_30Meter_foc10_z2'
inHillshade = 'HillShade_10Meter_foc10_z2reclass_foc7int_majfilter'
#outPolys = 'PolyShade_10Meter_254less'

createPolyShades(inHillshade, remapDict, '10Meter', 10000)
deleteHillshades('Interval')


