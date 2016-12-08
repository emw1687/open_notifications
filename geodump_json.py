import sqlite3
import json
import codecs

conn = sqlite3.connect('geodata.sqlite')
cur = conn.cursor()

cur.execute('SELECT * FROM Locations')
fhand = codecs.open('where.json','w', "utf-8")
#fhand.write("myData = [\n")

myData = {}
myData["type"] = "FeatureCollection"
myData["features"] = []

count = 0
for row in cur :
    data = str(row[1])
    try: js = json.loads(str(data))
    except: continue

    if not('status' in js and js['status'] == 'OK') : continue

    lat = js["results"][0]["geometry"]["location"]["lat"]
    lng = js["results"][0]["geometry"]["location"]["lng"]
    if lat == 0 or lng == 0 : continue
    where = js['results'][0]['formatted_address']
    where = where.replace("'","")

    try :
        #print where, lat, lng

        count = count + 1
        #if count > 1 : fhand.write(",\n")
        #output = "["+str(lat)+","+str(lng)+", '"+where+"', '"+str(row[2])+"', '"+str(row[3])+"', '"+str(row[4])+"']"
        output = {}
        output["type"] = "Feature"
        output["geometry"] = {}
        output["properties"] = {}
        output["geometry"]["type"] = "Point"
        output["geometry"]["coordinates"] = []
        output["geometry"]["coordinates"].append(lng)
        output["geometry"]["coordinates"].append(lat)
        output["properties"]["sticker"] = str(row[3])
        output["properties"]["address"] = str(where)
        output["properties"]["contractor"] = str(row[4])
        output["properties"]["startdate"] = str(row[5])
        output["properties"]["enddate"] = str(row[6])
        output["properties"]["exportdate"] = str(row[7])
        formtype = str(row[2])
        if "06" in formtype:
            output["properties"]["formtype"] = "aq06"
        elif "001" in formtype:
            output["properties"]["formtype"] = "anf001"
        if count > 1 : myData["features"].append(output)
        #output = "["+str(lat)+","+str(lng)+", '"+where+"', '"+str(row[2])+"', '"+str(row[3])+"', '"+str(row[4])+"']"
    except:
        continue

#fhand.write("\n);\n")
json.dump(myData, fhand)
cur.close()
fhand.close()
print count, "records written to where.json"
print "Open where.html to view the data in a browser"
