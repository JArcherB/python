# -*- coding: utf-8 -*-
"""
Created on Mon Jan 28 12:56:16 2019

@author: jaburton
"""
import arcpy
import xlrd
import os
#script to create tables from excel in ArcGIS Pro. Then capitalize the Name field in each table.

#set workspace
arcpy.env.workspace = r'C:\Users\jaburton\Documents\ArcGIS\Projects\Oquirrh View\Oquirrh View.gdb'
arcpy.env.overwriteOutput = 'True'
#set variables
outGDB = r'C:\Users\jaburton\Documents\ArcGIS\Projects\Oquirrh View\Oquirrh View.gdb'
in_excel = r'C:\Users\jaburton\Documents\Excel for ArcGIS\OquirrhViewExistingConditions-Data_JAMESCOPY.xlsx'

#create a funtion to import all excel sheets
def importallsheets(in_excel,outGDB):
    workbook = xlrd.open_workbook(in_excel)
    sheets = [sheet.name for sheet in workbook.sheets()]
    
    print('{} sheets found: {}'.format(len(sheets), ','.join(sheets)))
    for sheet in sheets:
        out_table = os.path.join(
                outGDB,
                arcpy.ValidateTableName(
                        '{0}_{1}'.format(os.path.basename(in_excel), sheet),
                        outGDB))
        print('Converting {} to {}'.format(sheet, out_table))
        
        arcpy.ExcelToTable_conversion(in_excel, out_table, sheet)

if __name__ == '__main__':
    importallsheets(r'C:\Users\jaburton\Documents\Excel for ArcGIS\OquirrhViewExistingConditions-Data_JAMESCOPY.xlsx',
                    r'C:\Users\jaburton\Documents\ArcGIS\Projects\Oquirrh View\Oquirrh View.gdb')

tables = arcpy.ListTables()
for table in tables:
    print(table)
    arcpy.CalculateField_management(table, 'NAME', '!NAME!.upper()','PYTHON3')
    print('NAME field is now uppercase.')

