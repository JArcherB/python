# create parcels, source: cadastral plat data, process cadastral lines, transfer data for countywide use
# mborden Sep 2018

# sample imports
import arcpy
import sys
import os
import smtplib
import time
import string
from email.MIMEMultipart import MIMEMultipart
from email.MIMEBase import MIMEBase
from email.MIMEText import MIMEText
from email.Utils import COMMASPACE, formatdate
from email import Encoders

# init
arcpy.env.overwriteOutput = True

# functions
def sendEmail(errMessage):   
    from_addr = "errors@slco.org"
    to_addr = "IS-GISDL@slco.org"  
    subject = "Errors: Recorder Cadastral Parcel Creation"   
    msg_text = errMessage
    msg = "From: %s\nTo: %s\nSubject: %s\n\n%s" % (from_addr, to_addr, subject, msg_text)
    server = "SLCMail.slcounty.org"
    server = smtplib.SMTP(server)
    server.sendmail(from_addr, to_addr, msg)
    server.quit()
    print ("Error: Email Sent" + errMessage)

def sendFinishEmail():   
    
    msg = MIMEMultipart()
    msg['From'] = "noreply@slco.org"
    msg['To'] = "Salt Lake County Parcel Users" 
    msg['Date'] = formatdate(localtime=True)
    msg['Subject'] = "Success: PSdraft Parcel Creation Complete" 
    msg.attach(MIMEText("PSdraft - Updated in Maintenance105.gdb"))
    
    f = r"//slcisgisetl/e$/scripts/recorder/logs/PSdraft_create.log"
    attachment = MIMEBase('application', "octet-stream")
    attachment.set_payload( open(f,"rb").read() )
    Encoders.encode_base64(attachment)
    attachment.add_header('Content-Disposition',  'attachment; filename="%s"' % os.path.basename(f))
    msg.attach(attachment)

    server = "SLCMail.slcounty.org"
    server = smtplib.SMTP(server)
    server.sendmail("noreply@slco.org", ["IS-GISDL@slco.org", "bjeter@slco.org", "brollins@slco.org", "tcurtis@slco.org", "jzenger@slco.org", "BLeCheminant@slco.org", "TBain@slco.org"], msg.as_string())
    server.quit()
    
def deleteData(delPath, dataType):
    try:
        if arcpy.Exists(delPath):
            arcpy.Delete_management(in_data=delPath, data_type=dataType)
            print "Success: deleted " + delPath 
    except Exception as err:
        print err
        sendEmail(err)

def copyData(fromPath, toPath):
    try:
        arcpy.CopyFeatures_management(fromPath, toPath, "", "0", "0", "0")
        print "Success: copied from " + fromPath + " to " + toPath 
    except Exception as err:
        print err
        sendEmail(err)
        
def makeLayer(inFeats, outLayer, whereClause, wspace, fldInfo):
    try:
        arcpy.MakeFeatureLayer_management(in_features=inFeats, out_layer=outLayer, where_clause=whereClause, workspace=wspace, field_info=fldInfo) 
        print "Success: created in memory layer " + outLayer 
    except Exception as err:
        print err
        sendEmail(err)

def makePoly(inFeats, outFC, clusTol, atts, labFeats):
    try:
        arcpy.FeatureToPolygon_management(in_features=inFeats, out_feature_class=outFC, cluster_tolerance=clusTol, attributes=atts, label_features=labFeats)
        print "Success: created polygon layer " + outFC
    except Exception as err:
        print err
        sendEmail(err)

def dissolveData(inFeats, outFC, dissField, statsFields, multiPart, unLines):
    try:
        arcpy.Dissolve_management(in_features=inFeats, out_feature_class=outFC, dissolve_field=dissField, statistics_fields=statsFields, multi_part=multiPart, unsplit_lines=unLines)
        print "Success: dissolved " + outFC
    except Exception as err:
        print err
        sendEmail(err)

def compactGDB(wspace):
    try:
        arcpy.Compact_management (in_workspace=wspace)
        print "Success: compacted " + wspace
    except Exception as err:
        print err
        sendEmail(err)

def clipAnalysis(inFeats, clipFeats, outFC, clusTol):
    try:
        arcpy.Clip_analysis(in_features=inFeats, clip_features=clipFeats, out_feature_class=outFC, cluster_tolerance=clusTol)
        print "Success: clipped to " + outFC
    except Exception as err:
        print err
        sendEmail(err)

def spatialIndex(inFeats, sgOne, sgTwo, sgThree):
    try:
        arcpy.AddSpatialIndex_management (in_features=inFeats, spatial_grid_1=sgOne, spatial_grid_2=sgTwo, spatial_grid_3=sgThree)
        print "Success: spatial index on " + inFeats
    except Exception as err:
        print err
        sendEmail(err)

def appendData(inData, targetData, schemaType, fldMapping, sType):
    try:
        arcpy.Append_management (inputs=inData, target=targetData, schema_type=schemaType, field_mapping=fldMapping, subtype=sType)
        print "Success: append to " + targetData
    except Exception as err:
        print err
        sendEmail(err)

def spatialJoin(targetFeats,
                joinFeats,
                outFeats,
                joinOper,
                joinType,
                fldMapping,
                matchOption,
                searchRadius,
                distanceFldName):
    try:
        arcpy.SpatialJoin_analysis (target_features=targetFeats,
                                    join_features=joinFeats,
                                    out_feature_class=outFeats,
                                    join_operation=joinOper,
                                    join_type=joinType,
                                    field_mapping=fldMapping,
                                    match_option=matchOption,
                                    search_radius=searchRadius,
                                    distance_field_name=distanceFldName)
        print "Success: join output to " + outFeats
    except Exception as err:
        print err
        sendEmail(err)

def main():

    # log file
    Build = r"//RE-GOLD-16S/GISDATA$/ParcelBuild"
    logFile = r"//slcisgisetl/e$/scripts/recorder/logs/PSdraft_create.log"
    logoutput = open(logFile,'w')
    beginTime = time.strftime('%Y-%m-%d %H:%M:%S')
    logoutput.write("Began at # " + beginTime + "\n")
    sys.stdout = logoutput  

    # vars
    Build_gdb = Build + r"/BuildDB.gdb"
    CadastralLine = Build + r"/RVecPBasRecVecData.sde/RVecPB.REC_VEC_DATA.Cadastral/RVecPB.REC_VEC_DATA.Cadastral_Line"
    CadastralPoint = Build + r"/RVecPBasRecVecData.sde/RVecPB.REC_VEC_DATA.Cadastral/RVecPB.REC_VEC_DATA.ParcelPoint"
    CadLine = Build_gdb + r"/CadastralLine"
    CadPoint = Build_gdb + r"/CadastralPoint"
    ParcelPoly = Build_gdb + r"/ParcelPoly"
    ParcelPolyJoin = Build_gdb + r"/ParcelPolyJoin"
    ParcelDissolve = Build_gdb + r"/ParcelDissolve"
    Parcels = Build_gdb + r"/Parcels"
    AGRCParcels = Build_gdb + r"/AGRCParcels"
    Clipper = Build_gdb + r"/Clipper"
    Maint_gdb = r"//re-gisvr3-w8s/FGDShare/PolyMgmt/Maintenance105.gdb"
    MaintPSD = r"//re-gisvr3-w8s/FGDShare/PolyMgmt/Maintenance105.gdb/PSdraft"
    MaintDSS = r"//re-gisvr3-w8s/FGDShare/PolyMgmt/Maintenance105.gdb/ParcelDissolve" 
    MaintPPJ = r"//re-gisvr3-w8s/FGDShare/PolyMgmt/Maintenance105.gdb/ParcelPolyJoin"
    
    # prep process, delete old data, copy new source data from recorder cadastral data
    deleteData(CadLine,'')
    deleteData(CadPoint,'')
    deleteData(ParcelPoly,'')
    deleteData(ParcelPolyJoin,'')
    deleteData(ParcelDissolve,'')
    deleteData(Parcels,'')
    deleteData(AGRCParcels,'')
    copyData(CadastralLine, CadLine)      
    copyData(CadastralPoint, CadPoint)

    # create polygons from cadastral line data
    makePoly(CadLine, ParcelPoly, '', "NO_ATTRIBUTES", '') # problems with feat layer in memory as input

    # link cadastral parcel point data to newly created polygons, so Parcel ID can be used in atts
    spatialJoin(ParcelPoly,
               CadPoint,
               ParcelPolyJoin,
               "JOIN_ONE_TO_ONE",
               "KEEP_ALL",
               "PIN \"PIN\" true true false 14 Text 0 0 , First,#,//RE-GOLD-16S/GISDATA$/ParcelBuild/BuildDB.gdb/CadastralPoint,PIN,-1,-1",
               "INTERSECT",
               "",
               "")

    # process data    
    makeLayer(ParcelPolyJoin, "Parcel_NotNull", '"PIN" IS NOT NULL', '', '')
    dissolveData("Parcel_NotNull", ParcelDissolve, "PIN", "", "MULTI_PART", "DISSOLVE_LINES")
    deleteData("in_memory",'')
   
    makeLayer(ParcelPolyJoin, "Parcel_Null", '"PIN" IS NULL', '', '')
    appendData("Parcel_Null", ParcelDissolve, "NO_TEST", '', '')
    deleteData("in_memory",'')
   
    makeLayer(ParcelDissolve, "Parcel_Dissolve", '', '', '')
    makeLayer(Clipper, "Parcel_Clipper", '', '', '')
    clipAnalysis("Parcel_Dissolve", "Parcel_Clipper", Parcels, '')
    
    makeLayer(ParcelPolyJoin, "Parcel_PolyJoin", '', '', '')
    clipAnalysis("Parcel_PolyJoin", "Parcel_Clipper", AGRCParcels, '')
    deleteData("in_memory",'')
   
    spatialIndex(Parcels, "1300", "115700", "0")
    spatialIndex(AGRCParcels, "1300", "115700", "0")

    # del copy data from BuildDB.gdb to Maint105.gdb    
    deleteData(MaintPSD,'')
    deleteData(MaintDSS,'')
    deleteData(MaintPPJ,'')    
    copyData(Parcels, MaintPSD)
    copyData(ParcelDissolve, MaintDSS)
    copyData(ParcelPolyJoin, MaintPPJ)
    compactGDB(Maint_gdb)
    compactGDB(Build_gdb)

    # close log / send finish notice 
    logoutput.write("Ended at # " + time.strftime('%Y-%m-%d %H:%M:%S') + "\n")
    logoutput.close()
    sendFinishEmail()

    # end main
    

# start 
if __name__ == '__main__':  
    main()   
