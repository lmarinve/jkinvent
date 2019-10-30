#!/usr/bin/python3
import sys, os, shutil, datetime, zipfile
import pyodbc
from zipfile import ZipFile
from datetime import date
sys.path.append(os.path.abspath('/opt/jkinvent/python'))
import initconf
import dbparm
import dbaction
import sendmail, delmsg
from mailparm import send_from, send_to, e_passwd
from datetime import datetime
from dbparm import dsn, user, password, database, con_string
try:
    vendor = folder = sys.argv[1]
except:
    sys.exit('!!!!!!!!!! this script does not run without a parameter !!!!!!!!!!!!')
res_vendor = initconf.initvendor(vendor)
x_action = res_vendor['x_act']
x_code = res_vendor['x_code']
x_qty = res_vendor['x_qty']
txtlst = [0,1]
csvlst = [2,3,5]
exclst = [4,6]
filelst= []
applst = []
res_conf = initconf.initconf(vendor)
filelst = res_conf['filelst']
print(filelst)
if filelst:
    src1 = '/opt/jkinvent/' + vendor + '/'
    dest1 = '/opt/jkinvent/' + vendor + '/history/' + str(date.today()) + "/"
    try:
        os.makedirs(dest1)
    except OSError:
        pass
    os.chdir(src1)
    for zip_file in filelst:
        if zip_file is not None:
            if zip_file.endswith('.zip'):
                zip_file = src1 + zip_file
                with ZipFile(zip_file, 'r') as x_zip:
                    x_zip.extractall()
                    x_list = os.listdir(src1)
                    for x_file in x_list:
                        if not x_file.endswith('.zip'):
                            applst.append(x_file)
    if applst:
        filelst.extend(applst)

    db_file = False
    db_act = False
    for fileName in filelst:
        if fileName is not None:
            if x_action in txtlst:
                db_act = dbaction.dbaction(src1,fileName,vendor,x_code,x_qty, x_action)
            elif x_action in csvlst and fileName.endswith('.csv'):
                db_act = dbaction.dbaction(src1,fileName,vendor,x_code,x_qty, x_action)
            elif x_action in exclst and fileName.endswith('.xlsx'):
                db_act = dbaction.dbaction(src1,fileName,vendor,x_code,x_qty, x_action)
            elif x_action in exclst and fileName.endswith('.xls'):
                db_act = dbaction.dbaction(src1,fileName,vendor,x_code,x_qty, x_action)
            else:
                print ("File does not match config file...",x_action)
                continue
            print("file processed...",db_act)
            db_file = True
    if db_file and db_act:
        cnxn = pyodbc.connect(con_string)
        cursor = cnxn.cursor()
        x_now = datetime.now()
        x_day = x_now.strftime('%Y-%m-%d')
        final_query = "UPDATE [JKEATS].[dbo].[SUPPLIER] SET NOTE3 = '%s' \
                  WHERE CODE = '%s' " %(x_day, vendor)
        cursor.execute(final_query)
        cnxn.commit()
        imapSession = res_conf['imapSession']
        delmsg.delmsg(folder,imapSession,src1,dest1)
        imapSession.expunge() # close the mailbox
        imapSession.close() # close the mailbox
        imapSession.logout()# logout     imapSession.close()
    elif db_file:
        subject = '!!!!!!!!  Error processing jk' + vendor + ' inventory !!!!!!!!!'
        text = 'There is an error processing jk' + vendor + ' inventory, please check on var\log\cron the file jk' + vendor + '.log for details'
        sendmail.send_mail(send_from,e_passwd,send_to,subject,text)
else:
    print("no Email found...")
