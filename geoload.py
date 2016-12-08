import urllib
import sqlite3
import json
import time
import ssl
import csv

# If you are in China use this URL:
# serviceurl = "http://maps.google.cn/maps/api/geocode/json?"
serviceurl = "http://maps.googleapis.com/maps/api/geocode/json?"

# Deal with SSL certificate anomalies Python > 2.7
# scontext = ssl.SSLContext(ssl.PROTOCOL_TLSv1)
scontext = None

conn = sqlite3.connect('geodata.sqlite')
cur = conn.cursor()

cur.execute('''
CREATE TABLE IF NOT EXISTS Locations (address TEXT, geodata TEXT, formtype TEXT, sticker TEXT, contractor TEXT)''')

#fh = open("where.data")
with open('where.csv', 'rb') as fh:
    reader = csv.reader(fh)
    projects = list(reader)
count = 0
for line in projects:
    if count > 2000 : break
    address = line[0].strip()
    formtype = line[1]
    sticker = line[2]
    contractor = line[3]
    print ''
    cur.execute("SELECT geodata FROM Locations WHERE address= ?", (buffer(address), ))

    try:
        data = cur.fetchone()[0]
        print "Found in database ",address
        continue
    except:
        pass

    print 'Resolving', address
    url = serviceurl + urllib.urlencode({"sensor":"false", "address": address})
    print 'Retrieving', url
    uh = urllib.urlopen(url, context=scontext)
    data = uh.read()
    print 'Retrieved',len(data),'characters',data[:20].replace('\n',' ')
    count = count + 1
    try:
        js = json.loads(str(data))
        # print js  # We print in case unicode causes an error
    except:
        continue

    if 'status' not in js or (js['status'] != 'OK' and js['status'] != 'ZERO_RESULTS') :
        print '==== Failure To Retrieve ===='
        print data
        break

    cur.execute('''INSERT INTO Locations (address, geodata, formtype, sticker, contractor)
            VALUES ( ?, ?, ?, ?, ? )''', ( buffer(address), buffer(data), buffer(formtype), buffer(sticker), buffer(contractor) ) )
    conn.commit()
    time.sleep(1)

print "Run geodump.py to read the data from the database so you can visualize it on a map."
