import urllib
import sqlite3
import json
import time
import ssl
import csv

# If you are in China use this URL:
# serviceurl = "http://maps.google.cn/maps/api/geocode/json?"
serviceurl = "https://maps.googleapis.com/maps/api/geocode/json?"
apikey = "&key=AIzaSyBZkXtmv9aAapicnQGx4su7mqb_jWIvMUg"

# Deal with SSL certificate anomalies Python > 2.7
# scontext = ssl.SSLContext(ssl.PROTOCOL_TLSv1)
scontext = None

conn = sqlite3.connect('geodata.sqlite')
cur = conn.cursor()

cur.execute('''
CREATE TABLE IF NOT EXISTS Locations (address TEXT, geodata TEXT, formtype TEXT, sticker TEXT, contractor TEXT, startdate DATE, enddate DATE, exportdate DATE)''')

#fh = open("where.data")
with open('where.csv', 'rb') as fh:
    reader = csv.reader(fh)
    projects = list(reader)
count = 0
for line in projects:
    if count > 1500 : break
    address = line[0].strip()
    formtype = line[1]
    sticker = line[2]
    contractor = line[3]
    startdate = line[4]
    enddate = line[5]
    exportdate = line[6]

    print ''
    #cur.execute("SELECT geodata FROM Locations WHERE address= ?", (buffer(address), ))
    cur.execute("SELECT sticker FROM Locations WHERE sticker LIKE ?", (buffer(sticker[0:9]) + '%', ))
    #print sticker[0:9]

    try:
        print sticker
        data = cur.fetchone()[0] #returns results of query above (sticker column) if it exists
        print data, "found in database"
        #continue
        #revision 1 (length of sticker in csv is greater than length of sticker in db)
        if (len(sticker) > len(data)):
            print "len(sticker) > len(data)"
            cur.execute("""UPDATE Locations SET sticker = ? , startdate = ?, enddate = ?, exportdate = ? WHERE sticker LIKE ? """, (buffer(sticker), buffer(startdate), buffer(enddate), buffer(exportdate), buffer(sticker[0:9]) + '%'))
            print "Updated ", data, " with ", sticker, "(first revision)"
            continue
        #all other revisions (last number of sticker in csv is greater than length of sticker in db)
        elif (len(sticker) == len(data) and sticker[-1] > data[-1]):
            print "len(sticker) == len(data) & sticker[-1] > data[-1]"
            cur.execute("""UPDATE Locations SET sticker = ? , startdate = ?, enddate = ?, exportdate = ? WHERE sticker LIKE ? """, (buffer(sticker), buffer(startdate), buffer(enddate), buffer(exportdate), buffer(sticker[0:9]) + '%'))
            print "Updated ", data, " with ", sticker, "(subsequent revision)"
            continue
        else:
            print "Not updated!"
            continue
    except:
        print sticker, "not found in database"
        pass

    print 'Resolving', address
    url = serviceurl + urllib.urlencode({"sensor":"false", "address": address}) + apikey
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

    cur.execute('''INSERT INTO Locations (address, geodata, formtype, sticker, contractor, startdate, enddate, exportdate)
            VALUES ( ?, ?, ?, ?, ?, ?, ?, ? )''', ( buffer(address), buffer(data), buffer(formtype), buffer(sticker), buffer(contractor), buffer(startdate), buffer(enddate), buffer(exportdate)) )
    conn.commit()
    time.sleep(1)

print "Run geodump_json.py to read the data from the database so you can visualize it on a map."
