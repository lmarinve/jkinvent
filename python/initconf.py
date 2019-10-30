import email, getpass, imaplib, uuid
import os, sys
import pyodbc
import datetime

def initvendor(vendor):
    choices = {'AMBA': (3, 0, 2), 'ATL': (3, 0, 1), 'AVA': (4, 0, 1), 
               'BEL': (6, 1, 2), 'BOCCHI':(4, 2, 3), 'BOSC':(3, 0, 1),
               'DEV': (5, 0, 1), 'FOR': (3, 0, 2), 'FRE': (4, 0, 1),
               'HAF':(1, 1, 2), 'HMW': (3, 2, 6), 'HUD': (3,0,4),
               'JAM': (4, 0 ,2), 'KRS': (3, 1, 3), 'NAT': (3, 0, 2),
               'STOCK' : (0, 2, 8), 'tdp': (4, 0, 1),
               'TRY': (3,0,1), 'stu': (3, 0, 1)
              }
    (rst1, rst2, rst3) = choices.get(vendor, (0,0,0))
    return { 'x_act' : rst1, 'x_code' : rst2, 'x_qty' : rst3 }

def initconf(vendor):

    userName = '****'
    passwd = '****'
    detach_dir = '/opt/jkinvent'
    fileName = ''
    filelst  = []
    x_vendor = vendor
    imapSession = imaplib.IMAP4_SSL('imap.gmail.com')
    typ, accountDetails = imapSession.login(userName, passwd)
    try:
        if typ != 'OK':
            print ('Not able to sign in!')
            raise
        else:    
            print ('sign in ok!')
        imapSession.select(x_vendor)
        typ, data = imapSession.search(None, 'ALL')
        if typ != 'OK':
            print ('Error searching Inbox.')
            raise
        else:    
            print ('searching Inbox ok!', data)
    
        # Iterating over all emails
        for msgId in data[0].split():
            typ, messageParts = imapSession.fetch(msgId, '(RFC822)')
            if typ != 'OK':
                print ('Error fetching mail.')
                raise

            emailBody = messageParts[0][1]
            mail = email.message_from_bytes(emailBody)
            for part in mail.walk():
                if part.get_content_maintype() == 'multipart':
                    continue
                if part.get('Content-Disposition') is None:
                    continue
                fileName = part.get_filename()
                print ("fileName:",fileName)
                if fileName is not None:
                    print ("Appending fileName to list:",fileName)
                    filelst.append(fileName)
                    filePath = os.path.join(detach_dir, x_vendor, fileName)
                    if not os.path.isfile(filePath) :
                        print ("Creating:",fileName, 'in:', filePath)
                        fp = open(filePath, 'wb')
                        fp.write(part.get_payload(decode=True))
                        fp.close()
    except :
        print ('Not able to download all attachments.')
    return {
        'filelst': filelst,
        'imapSession': imapSession,
    }

