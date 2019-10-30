import email, getpass, imaplib
import os, sys, shutil
import datetime
from datetime import date

def delmsg(folder,imapSession,source,dest_dir):

    no_of_msgs = int(imapSession.select(folder)[1][0])  # required to perform search, m.list() for all lables, '[Gmail]/Sent Mail'
    print("- Found a total of {1} messages in '{0}'.".format(folder, no_of_msgs))
    typ, data = imapSession.search(None, 'ALL')
    if data != ['']:  # if not empty list means messages exist
        no_msgs_del = data[0]
        msgs_list = no_msgs_del.split()
        for msg in msgs_list:
            imapSession.store(msg,'+FLAGS', '\\Deleted')  # move to trash
    else:
        print("- Nothing to remove.")

    os.chdir(source)
    try:
        os.makedirs(dest_dir)
    except OSError:
        pass

    files = [f for f in os.listdir('.') if os.path.isfile(f)]

    print (source, dest_dir, files)

    for f in files:
        shutil.move(os.path.join(f), os.path.join(dest_dir,f))
