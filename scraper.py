from pymongo import MongoClient
import datetime
from time import sleep
from webpage import webpage
from zillow import ZillowResultsPage
from zillow import ZillowListingPage

client = MongoClient()
db = client.RealEstate
collection = db.Zillow


url = "http://www.zillow.com/search/GetResults.htm?spt=savedhomes&status=111011&lt=111101&ht=111111&pr=,&mp=,&bd=0%2C&ba=0%2C&sf=,&lot=,&yr=,&pho=0&pets=0&parking=0&laundry=0&pnd=1&red=0&zso=0&days=any&ds=all&pmf=1&pf=1&zoom=6&rect=-127359009,42573309,-113076783,48983822&p=1&sort=saved&search=maplist&disp=1&listright=true&isMapSearch=1&zoom=6"

z = ZillowResultsPage(url)
z.fetch().process()


newUrls=[]
for i in z.getlistingurls():
    cursor = collection.find({"url": i})
    if cursor.count() == 0:
        newUrls.append(i)

print 'adding',len(newUrls),'new urls to the database'


for i in newUrls:
    listing = ZillowListingPage(i)
    print listing.fetch().process()
    collection.insert_one(listing.getdict())
    listing.saveimages()
    sleep(5)

while z.nextpage():
    newUrls=[]
    for i in z.getlistingurls():
        cursor = collection.find({"url": i})
        if cursor.count() == 0:
            newUrls.append(i)
    print 'adding',len(newUrls),'new urls to the database'
    for i in newUrls:
        listing = ZillowListingPage(i)
        print listing.fetch().process()
        collection.insert_one(listing.getdict())
        listing.saveimages()
        sleep(5)
