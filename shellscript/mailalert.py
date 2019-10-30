#!/usr/bin/python3
import sys
import sendmail
from mailparm import send_from, e_passwd, send_to
try:
    vendor = sys.argv[1]
except:
    sys.exit('!!!!!!!!!! this script does not run without a parameter !!!!!!!!!!!!')
subject = '!!!!!!!!  Error processing jk' + vendor + ' inventory !!!!!!!!!' 
text = 'There is an error processing jk' + vendor + ' inventory, please check on var\log\cron the file jk' + vendor + '.log for details'
sendmail.send_mail(send_from, e_passwd, send_to, subject, text)
