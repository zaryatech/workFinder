#!/usr/bin/env python
# -*- coding: utf-8 -*-

from HTMLParser import HTMLParser
import requests
import time
import random

class ListParser(HTMLParser):
    def __init__(self):
        HTMLParser.__init__(self)
        self.info=[]
        self.readData=False
        self.currentRecord=None

    def handle_starttag(self, tag, attrs):
        if tag==u'a':
            self.currentRecord={}
            self.readData=False
            for (attr, value) in attrs:
                if attr==u'title':
                    self.currentRecord['title']=value
                if attr==u'href':
                    self.currentRecord['href']=value
                if attr==u'class' and value=='description-title-link':
                    self.readData=True
    def handle_endtag(self, tag):
        pass
    def handle_data(self, data):
        if self.readData:
            self.currentRecord['data']=data    
            self.info.append(self.currentRecord)
            self.readData=False




if __name__== '__main__':
    #response = requests.get("http://bbc.com/")    
    with open('list.html') as f:
        html=f.read()

    parser=ListParser()
    parser.feed(html.decode('utf-8'))
    parser.close()

    print('parsing list ok')

    print (parser.info)

    # отдыхаем
    for record in parser.info:
#        sleepSec =5+random.randrange(5)
#        print(u'sleep before parsing ' + record['title'] + ' sec: ' + str(sleepSec))

        print ('https://www.avito.ru'+record['href'])
#        response=requests.get("www.avito.ru"+record['href'])
        time.sleep(sleepSec)
        print(u'continue processing ' + record['title'])



    #file='list.html'
    #class="description-title-link"




