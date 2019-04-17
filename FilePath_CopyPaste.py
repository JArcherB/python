from shutil import copyfile
import os
outpath = r'J:\LAS_Millcreek'
inpath = r'Z:\LIDAR\2013_LiDAR\2013_LiDAR_Final\LAS_Final\LAS_StatePlaneFeet'
thefile = r'C:\Users\jaburton\Documents\LAS_FileList.txt'

f = open(thefile, 'r')


for line in f:
    newline = line.replace("\n","")
    infile = os.path.join(inpath,newline)
    outfile = os.path.join(outpath,newline)
    copyfile(infile,outfile)
