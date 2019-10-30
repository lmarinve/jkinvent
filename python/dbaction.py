import os, sys, datetime, csv, xlrd, chardet
from datetime import datetime
import pandas as pd
import pyodbc
sys.path.append(os.path.abspath('/opt/jkinvent/python'))
from dbparm import dsn, user, password, database, con_string 
import isnum


def init_qty(x_vendor):
    print("init_qty: ",x_vendor)
    cnxn = pyodbc.connect(con_string)
    cursor = cnxn.cursor()
    if x_vendor != "BOCCHI":
        x_init = 6666
    else:
        x_init = 0
    init_query = "UPDATE [JKEATS].[dbo].[BIN] \
SET UNITS = '%s' WHERE WAREHOUSE = '%s' AND DROPSHIP = 1" %(x_init, x_vendor)
    cursor.execute(init_query)
    cnxn.commit()
    return True


def dbquery(x_vendor, x_code, y_code, x_qty, x_act, cnxn, cursor):
    x_qty = int(float(x_qty))
    if x_qty < 1:
        x_qty = 0
    #
    if x_vendor == "BOCCHI":
        x_split = x_code.split()
        x_code = str(x_split[0])
    #
    fst_query = "SELECT NUMBER, BUYDESC FROM [JKEATS].[dbo].[BUYPRICE] \
                where SUPPLIER = '%s' and BUYDESC = '%s' and DROPSHIP = 1" %(x_vendor, x_code)
    cursor.execute(fst_query)
    rows = cursor.fetchall()
    #
    if rows == None and x_vendor == "STOCK":
        print ("second query for: ", x_code)
        fst_query = "SELECT NUMBER, BUYDESC FROM [JKEATS].[dbo].[BUYPRICE] \
                    where SUPPLIER = '%s' and BUYDESC = '%s' and DROPSHIP = 1" %(x_vendor, y_code)
        cursor.execute(fst_query)
    else:
        print ("row: ",rows)
        print ("x_code: ", x_code)
    for row in rows:
        x_number = row.NUMBER
        print ("number", x_number)
        print ("qty:", x_qty)
        snd_query = "UPDATE [JKEATS].[dbo].[BIN] \
                    SET UNITS = '%s' WHERE  WAREHOUSE = '%s' AND \
                    NUMBER = '%s' AND DROPSHIP = 1" %(x_qty, x_vendor,x_number)
        cursor.execute(snd_query)
    cnxn.commit()
    return True


def txt_action(x_dir, x_file, x_vendor, sku, qty, x_act):
    print('TXT_ACTION: x_dir:', x_dir, 'x_file:', x_file, 'x_vendor:', x_vendor, 'sku:', sku, 'qty:', qty, 'x_act:', x_act)
    cnxn = pyodbc.connect(con_string)
    cursor = cnxn.cursor()
    os.chdir(x_dir)
    csv_file = x_vendor + '.csv'
    qty_ok = False
    if x_act % 2 == 0:
        x_delim = '\t'
        x_action = 2
    else:
        x_delim = ','
    x_action = 3
    with open(x_file, 'rb') as f:
        result = chardet.detect(f.read())
    x_encode = result['encoding']
    print ('x_file:',x_file,'csv_file:',csv_file,'encode:',x_encode)
    df1 = pd.read_table(x_file, sep=x_delim, encoding=x_encode, engine='python')
    print(df1)
    df1.to_csv(csv_file)
    x_success = csv_action(x_dir, csv_file, x_vendor, sku, qty, x_action)
    if x_success:
        init_qty(x_vendor)
        x_action = 33
        x_success = csv_action(x_dir, csv_file, x_vendor, sku, qty, x_action)
    return x_success    


#2
def csv_action(x_dir, x_file, x_vendor, sku, qty, x_act):
    print('CSV_ACTION: x_dir:', x_dir, 'x_file:', x_file, 'x_vendor:', x_vendor, 'sku:', sku, 'qty:', qty, 'x_act:', x_act)
    x_sku = sku
    if x_act % 2 == 0:
        x_delim = '\t'
    else:
        x_delim = ','
    cnxn = pyodbc.connect(con_string)
    cursor = cnxn.cursor()
    os.chdir(x_dir)
    with open(x_file, 'rb') as f:
        result = chardet.detect(f.read())
    x_encode = result['encoding']
    print("Encode:",x_encode,"Delimiter:",x_delim)
    fi = open(x_file, 'rb')
    data = csv.reader((line.replace('\0', '') for line in fi), delimiter=x_delim)
    fi.close()
    qty_ok = False
    with open(x_file, encoding=x_encode, errors='ignore') as fp:
        rfp = csv.reader((line.replace('\0', '') for line in fp), delimiter=x_delim)
        print ('x_act:',x_act,'delimiter:',x_delim)
        for cnt, line in enumerate(rfp):
            if cnt > 0 and line:
                try:
                    print("line:",line)
                    x_code = str(line[x_sku])
                    y_code = x_code
                    x_qty =  line[qty]
                    x_num = isnum.is_number(x_qty)
                    if x_num:
                        if float(x_qty) > 0:
                            x_qty = int(float(x_qty))
                        else:
                            x_qty = 0
                        if x_act >= 22:
                            dbquery(x_vendor, x_code, y_code, x_qty, x_act, cnxn, cursor) 
                        if x_qty > 0:
                            qty_ok = True
                except:
                    print("except cnt: ",cnt)
                    print("except line: ",line)
                    print("except len line: ",len(line))
                    print("except sku,qty,act: ", x_sku, qty, x_act)
                    print("****************************************************************")
            else:
                print("ELSE cnt == 0: ",cnt)
                print("Current Line",line[0])
                print("sku,qty,act: ", x_sku, qty, x_act)
                print("****************************************************************")
    if qty_ok:
        return True
    else:
        return False


def xlrd_action(x_dir, x_file, x_vendor, sku, qty, x_act):
    print("xlrd_action: ", x_dir, x_file, x_vendor, sku, qty, x_act)
    cnxn = pyodbc.connect(con_string)
    cursor = cnxn.cursor()
    os.chdir(x_dir)
    wkb = xlrd.open_workbook(x_file)
    rsheet = wkb.sheet_by_index(0)
    qty_ok = False
    for rowx in range(rsheet.nrows):
        x_code = y_code = str(rsheet.cell_value(rowx,sku))
        x_qty = rsheet.cell_value(rowx,qty)
        x_num = isnum.is_number(x_qty)
        if x_num:
            if float(x_num) > 0:
                x_qty = int(float(x_qty))
            else:
                x_qty = 0
            if x_act == 44:
                dbquery(x_vendor, x_code, y_code, x_qty, x_act, cnxn, cursor) 
            if x_qty > 0:
                qty_ok = True
    if qty_ok:
        return True
    else:
        return False

def yesno_action(x_dir, x_file, x_vendor, sku, qty, x_act):
    print("yesno_action: ", x_dir, x_file, x_vendor, sku, qty, x_act)
    cnxn = pyodbc.connect(con_string)
    cursor = cnxn.cursor()
    os.chdir(x_dir)
    fi = open(x_file, 'rb')
    data = csv.reader((line.replace('\0', '') for line in fi), delimiter=',')
    fi.close()
    qty_ok = False
    with open(x_file, encoding="utf8", errors='ignore') as fp:
        rfp = csv.reader((line.replace('\0', '') for line in fp), delimiter=',')
        for cnt, line in enumerate(rfp):
            if cnt > 0:
                x_code = y_code = str(line[sku])
                x_qty =  line[qty]
                if x_qty == 'yes' or x_qty == "Y" or x_qty == 'In Stock' :
                    x_qty = 10
                    qty_ok = True
                elif x_qty == 'no' or x_qty == 'N' or x_qty == 'Out of Stock':
                    x_qty = 0
                    qty_ok = True
                elif x_qty == 'Low Stock':
                    x_qty = 3
                    qty_ok = True
                else:
                    x_qty = 6666
                if x_act == 55:
                    print(x_vendor, "code: ",x_code, y_code, "x_qty: ",x_qty, "act:", x_act)
                    dbquery(x_vendor, x_code, y_code, x_qty, x_act, cnxn, cursor) 
    if qty_ok:
        return True
    else:
        return False


def xlyn_action(x_dir, x_file, x_vendor, sku, qty, x_act):
    print("xlyn_action: ", x_dir, x_file, x_vendor, sku, qty, x_act)
    x_sku = sku
    y_sku = x_sku + 1
    cnxn = pyodbc.connect(con_string)
    cursor = cnxn.cursor()
    os.chdir(x_dir)
    wkb = xlrd.open_workbook(x_file)
    rsheet = wkb.sheet_by_index(0)
    for rowx in range(rsheet.nrows):
        x_code = y_code = str(rsheet.cell_value(rowx,sku))
        x_qty = rsheet.cell_value(rowx,qty)
        if x_qty == 'yes' or x_qty == "Y" or x_qty == 'In Stock' :
            x_qty = 10
        elif x_qty == 'no' or x_qty == 'N' or x_qty == 'Out of Stock':
            x_qty = 0
        elif x_qty == 'Low Stock':
            x_qty = 3
        else:
            x_qty = 6666
        dbquery(x_vendor, x_code, y_code, x_qty, x_act, cnxn, cursor) 
    return True

def dbaction(src1,fileName,vendor,sku,qty, x_action):
    x_success = False
    if fileName != '':
        x_dir = src1
        x_file = fileName
        x_vendor = vendor
        if x_vendor == 'topkn':
            x_vendor = 'top kn'
        #
        if x_action <= 1:
            print('DBACTION: x_dir:', x_dir, 'x_file:', x_file, 'x_vendor:', x_vendor, 'sku:', sku, 'qty:', qty, 'x_action:', x_action)
            x_success = txt_action(x_dir, x_file, x_vendor, sku, qty, x_action)
        elif x_action == 2 or x_action == 3:
            print('DBACTION: x_dir:', x_dir, 'x_file:', x_file, 'x_vendor:', x_vendor, 'sku:', sku, 'qty:', qty, 'x_action:', x_action)
            x_success = csv_action(x_dir, x_file, x_vendor, sku, qty, x_action)
            if x_success:
                init_qty(x_vendor)
                if x_action == 2:  
                    x_action = 22
                elif x_action == 3:
                    x_action = 33
                print('DBACTION: x_dir:', x_dir, 'x_file:', x_file, 'x_vendor:', x_vendor, 'sku:', sku, 'qty:', qty, 'x_action:', x_action)
                x_success = csv_action(x_dir, x_file, x_vendor, sku, qty, x_action)
        elif x_action == 4:
            print('DBACTION: x_dir:', x_dir, 'x_file:', x_file, 'x_vendor:', x_vendor, 'sku:', sku, 'qty:', qty, 'x_action:', x_action)
            x_success = xlrd_action(x_dir, x_file, x_vendor, sku, qty, x_action)
            if x_success:
                init_qty(x_vendor)
                x_action = 44
                print('DBACTION: x_dir:', x_dir, 'x_file:', x_file, 'x_vendor:', x_vendor, 'sku:', sku, 'qty:', qty, 'x_action:', x_action)
                x_success = xlrd_action(x_dir, x_file, x_vendor, sku, qty, x_action)
        elif x_action == 5:
            print('DBACTION: x_dir:', x_dir, 'x_file:', x_file, 'x_vendor:', x_vendor, 'sku:', sku, 'qty:', qty, 'x_action:', x_action)
            x_success = yesno_action(x_dir, x_file, x_vendor, sku, qty, x_action)
            if x_success:
                init_qty(x_vendor)
                x_action = 55
                print('DBACTION: x_dir:', x_dir, 'x_file:', x_file, 'x_vendor:', x_vendor, 'sku:', sku, 'qty:', qty, 'x_action:', x_action)
                x_success = yesno_action(x_dir, x_file, x_vendor, sku, qty, x_action)
            elif x_vendor == "DEV":
                x_action = 3
                print('DBACTION: x_dir:', x_dir, 'x_file:', x_file, 'x_vendor:', x_vendor, 'sku:', sku, 'qty:', qty, 'x_action:', x_action)
                x_success = csv_action(x_dir, x_file, x_vendor, sku, qty, x_action)
                if x_success:
                    init_qty(x_vendor)
                    x_action = 33
                    print('DBACTION: x_dir:', x_dir, 'x_file:', x_file, 'x_vendor:', x_vendor, 'sku:', sku, 'qty:', qty, 'x_action:', x_action)
                    x_success = csv_action(x_dir, x_file, x_vendor, sku, qty, x_action)
        elif x_action == 6:
            print('DBACTION: x_dir:', x_dir, 'x_file:', x_file, 'x_vendor:', x_vendor, 'sku:', sku, 'qty:', qty, 'x_action:', x_action)
            x_success = xlyn_action(x_dir, x_file, x_vendor, sku, qty, x_action)
    if x_success:
        return True
    else:
        return False
