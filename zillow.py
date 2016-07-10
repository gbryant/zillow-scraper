from webpage import webpage
import re
import random
from time import sleep
from datetime import date, timedelta
import pycurl
from StringIO import StringIO
import os



class ZillowResultsPage(webpage):
    def __init__(self,url=""):
        webpage.__init__(self,url)
        self.pageCount=0
        self.currPage=0

    def process(self):
        webpage.process(self)
        self.pageCount = re.findall('numPages\":(\\d+)',self.data)[0]
        self.currPage = re.findall('.*&p=(\\d+)&.*',self.url)[0]
        return self

    def getlistingurls(self):
        listings=[]
        results = re.findall('homedetails.*?zpid/', self.data)
        for i in set(results):
            listings.append("http://www.zillow.com/"+i)
        return listings

    def nextpage(self):
        if int(self.currPage) < int(self.pageCount):
            results = re.match("(.*&p=)(\\d+)(&.*)",self.url).groups()
            newURL = results[0]+str(int(self.currPage)+1)+results[2]
            self.url = newURL
            self.fetch().process()
            return True
        else:
            return False

class ZillowListingPage(webpage):
    def __init__(self,url=""):
        webpage.__init__(self,url)
        self.status=''
        self.listdate=''
        self.mls=''
        self.address=''
        self.price=''
        self.beds=''
        self.baths=''
        self.homesize=''
        self.lotsize=''
        self.description=''
        self.imageurls=[]

    def process(self):
        webpage.process(self)
        #***************Get listing status
        self.status = self.doc.xpath("normalize-space(//span[contains(@id,'listing-icon')]/following-sibling::text())")
        if self.status == "":
            self.status = self.doc.xpath("normalize-space(//span[contains(@id,'listing-icon')]/following-sibling::span)")
        print self.status
        #***************Get listing date
        try:
            daysOld = self.doc.xpath("//li[contains(text(),'on Zillow')]/text()")[0].split()[0]
            d = date.today() - timedelta(int(daysOld))
            self.listdate = d.isoformat()
        except:
            pass
        #***************Get MLS number
        try:
            self.mls = self.doc.xpath("//li[contains(text(),'MLS')]/text()")[0].split()[2]
        except:
            pass
        #***************Get address
        try:
            self.address = self.doc.xpath("//meta[contains(@property,'address')]/@content")[0]
        except:
            pass
        #***************Get price
        try:
            self.price = self.doc.xpath("normalize-space(//div[contains(@class,'main-row  home-summary-row')])")
        except:
            pass
        #***************Get beds
        try:
            for item in self.doc.iterfind(".//span"):
                if item.text != None and 'bed' in item.text:
                    self.beds = item.text
        except:
            pass
        #***************Get baths
        try:
            for item in self.doc.iterfind(".//span"):
                if item.text != None and 'bath' in item.text:
                    self.baths = item.text
        except:
            pass
        #***************Get home size
        try:
            for item in self.doc.iterfind(".//span"):
                if item.text != None and 'sqft' in item.text:
                    self.homesize = item.text
        except:
            pass
        #***************Get lot size
        try:
            for item in self.doc.iterfind(".//li"):
                if item.text != None and 'Lot:' in item.text:
                    self.lotsize = item.text
        except:
            pass
        #***************Get description
        try:
            self.description = self.doc.xpath("//div[contains(@class,'hdp-header-description')]//div[contains(@class,'notranslate')]['text()']")[0].text
        except:
            pass
        #***************Get image urls
        try:
            for item in self.doc.iterfind(".//img"):
                if item.get('class') == 'hip-photo':
                    if item.get('href') != None:
                        self.imageurls.append(item.get('href').replace("p_h","p_f"))
        except:
            pass
        return self


    def getdict(self):
        return {"url":self.url,"status":self.status,"listdate":self.listdate,"mls":self.mls,"address":self.address,"price":self.price,\
                "beds":self.beds,"baths":self.baths,"homesize":self.homesize,"lotsize":self.lotsize,"description":self.description,\
                "images":self.imageurls}

    def saveimages(self):
        for i in self.imageurls:
            self.saveimage(i,self.url)
            sleep(random.uniform(2.2,8.7))

    def __str__(self):
        return \
            (self.url+'\n'+\
         self.status+'\n'+\
         self.listdate+'\n'+\
         self.mls+'\n'+\
         self.address+'\n'+\
         self.price+'\n'+\
         self.beds+'\n'+\
         self.baths+'\n'+\
         self.homesize+'\n'+\
         self.lotsize+'\n'+\
         self.description+'\n'+\
         str(self.imageurls)).encode('utf8','ignore')