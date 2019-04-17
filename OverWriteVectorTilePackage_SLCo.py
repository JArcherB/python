# -*- coding: utf-8 -*-
#  Name: OverWriteVectorTilePackage_SLCo.py
#
#
#  Purpose:Create a vector tile package and overwrite a Vector Tile Service from a local vector tile package
#
# Requirements: Have a vector tile package uploaded to ArcGIS Online and published as a
#               Service. This script must be run as the user who owns the service
#               Input Username, and password for user who owns vectortilepackage and service
#               Input item ID of uploaded vectortilepackage
#               Input Service Name of service to be overwritten
#
# Author:      Kelly Gerrow
#Contact:      kgerrow@esri.com
#
# Created:     10/3/2016

# Updated by Patrick Demer, 2/2/2017 for vector tiles packages

#-------------------------------------------------------------------------------


#import variables
import json, arcpy, time, requests
import urllib3
import logging

#disable insecure request warning
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

#Set the environment
arcpy.env.workspace = r"C:\Users\jaburton\Documents\ArcGIS\Projects"
#Allow environment to be overwritten
arcpy.env.overwriteOutput = True

#config logger
logging.basicConfig(filename=r'C:\Logs\LogFile',level=logging.DEBUG)

#Create time variable for logging
beginTime = time.strftime('%H:%M:%S')
day = time.strftime('%A, %m-%d-%Y')

#Create log variable and output file
#logOutput = open(r'C:\Logs\LogFile','w+')


#Create variable for Vector tile index
tileIndex = r"C:\Users\jaburton\Documents\ArcGIS\Projects\VectorBasemap\VectorBasemap.gdb\VectorTileIndex1"

#Create vector tile package locally
p = arcpy.mp.ArcGISProject(r'C:\Users\jaburton\Documents\ArcGIS\Projects\VectorBasemap\VectorBasemap.aprx')
outputPath = r'C:\Users\jaburton\Documents\ArcGIS\Projects\VectorBasemap'
#log start time
logging.debug("Process began" + ' ' + day + ' ' + 'at' + ' ' + beginTime + "\n")
#logOutput.write("Process began" + ' ' + day + ' ' + 'at' + ' ' + beginTime + "\n")
for m in p.listMaps("VectorTile"):
    print("Packaging " + m.name)
    arcpy.CreateVectorTilePackage_management(m, outputPath + m.name + '.vtpk', "ONLINE", "", "INDEXED", 295828763.795777, 564.248588)
    print("Vector Tile Created")
   

#returns ssl value and user token
def getToken(adminUser, pw):
        data = {'username': adminUser,
            'password': pw,
            'referer' : 'https://www.arcgis.com',
            'f': 'json'}
        url  = 'https://www.arcgis.com/sharing/rest/generateToken'
        jres = requests.post(url, data=data, verify=False).json()
        return jres['token'],jres['ssl']

#RETURNS UNIQUE ORGANIZATION URL and OrgID
def GetAccount(pref, token):
    URL= pref+'www.arcgis.com/sharing/rest/portals/self?f=json&token=' + token
    response = requests.get(URL, verify=False)
    jres = json.loads(response.text)
    return jres['urlKey'], jres['id']

def uploadItem(userName, portalUrl, TPK, itemID, layerName, extent, token):
    #Upload the input TPK, this is using a post request through the requests module,
    #returns a response of success or failure of the uploaded TPK. This can then be used to update the tiles
    #in the tile service

    #update Item URL
    updateUrl = '{}.maps.arcgis.com/sharing/rest/content/users/{}/items/{}/update'.format(portalUrl,userName,itemID)
    #opens Tile Package
    filesUp = {"file": open(TPK, 'rb')}

    #data for request. as this is updated an existing item, the value of overwrite is set to true
    data = {'f':'json',
        'token':token,
        'name':layerName,
        'title': layerName,
        'itemId':itemID,
        'filetype': 'Tile Package',
        'overwrite': 'true',
        'async':'true',
        'extent':extent}
    #submit requst
    response = requests.post(updateUrl, data=data, files=filesUp, verify=False).json()

    return response

def updateTiles(orgID, layerName, extent, lods,token):
   #Build each tile of the tiled service.
   url = "https://tiles.arcgis.com/tiles/{}/arcgis/rest/admin/services/{}/VectorTileServer/update".format(orgID, layerName)
   data = {'mergeBundle': 'false', "token":token, 'f':'json'}
   jres = requests.post(url, data).json()
    #returns jobID
   return jres



#Enter Username and Password
user= 'SLCoVector' #raw_input('What is the ArcGIS Online Username?')
pw = 'bw#r%X1%fBr2'#raw_input('What is the ArcGIS Online Password?')
inItemID= '6abb83f03e6e4b0788d37e858df8475a'#raw_input('What is the Item ID of the uploaded VTPK?')
layerName ='Salt_Lake_County_Base_Map'#raw_input('What is the Service Name of the service to overwrite ?')
tpk = r'C:\Users\jaburton\Documents\ArcGIS\Projects\VectorBasemapVectorTile.vtpk'#location of VTPK
#extent = 'extent'# example'{"xmin":-1.84761407196E7,"ymin":1995253.5241999999,"xmax":-7185123.9953000005,"ymax":1.1525580625400003E7,"spatialReference":{"wkid":102100}}'
#lods = '0-19' #enter levels in format outlined http://resources.arcgis.com/en/help/arcgis-rest-api/index.html#/Update_Tiles/02r30000022v000000/
extent = '{"xmin":-114.24,"ymin":36.97,"xmax":-108.86,"ymax":42.02,"spatialReference":{"wkid":102100}}'
lods = '4-23'


#get account information
token= getToken(user, pw)
if token[1] == False:
           pref='http://'
else:
           pref='https://'

#Create Portal URL and assign variables

t=GetAccount(pref,token[0])
urlKey=t[0]
orgID=t[1]
portalUrl=pref+urlKey


#upload updated TPK
update = uploadItem(user,portalUrl,tpk,inItemID,layerName, extent, token[0])
print (update)

if update['success'] ==True:
    unpack = updateTiles(orgID, layerName, extent, lods,token[0])
print (unpack)
#check publishing status until status is complete
statusURL ='{}.maps.arcgis.com/sharing/rest/content/users/{}/items/{}/status?jobId={}&f=json&token={}'.format(portalUrl,user,unpack['itemId'],unpack['jobId'],token[0])
requestStatus = requests.get(statusURL)
status=requestStatus.json()
while status['status']=='processing':
    time.sleep(10)
    print (status['status'])
    statusURL ='{}.maps.arcgis.com/sharing/rest/content/users/{}/items/{}/status?jobId={}&f=json&token={}'.format(portalUrl,user,unpack['itemId'],unpack['jobId'],token[0])
    requestStatus = requests.get(statusURL)
    status=requestStatus.json()
logging.debug("Ended at # " + time.strftime('%H:%M:%S') + "\n")
logging.debug("Vector tiles were created and updated successfully.")
#logOutput.write("Ended at # " + time.strftime('%H:%M:%S') + "\n")
#logOutput.write("Vector tiles were created and updated successfully.")
 
#print completed status
print (status['status'])

