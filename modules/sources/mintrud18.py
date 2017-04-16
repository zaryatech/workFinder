#!/use/bin/env python
# -*- coding: utf-8 -*-

from datetime import datetime, timedelta
from selenium import webdriver
from selenium.webdriver.common.by import By
import traceback,sys
import re
import locale
locale.setlocale(locale.LC_ALL,'ru_RU.utf-8')
import sys
reload(sys)



def getSaller(config,driver,saller_dict,companyId):
    if companyId not in saller_dict:
        driver.get(config.get('mintrud18','company_template').format(companyId))
        elements=driver.find_elements(By.XPATH,'//div[@class="panel-body"]/div[@class="row"]/div[@class="col-sm-9"]')
        org_contact=elements[0].get_attribute('textContent').strip()
        org_address=elements[3].get_attribute('textContent').strip()
        org_phone=elements[4].get_attribute('textContent').strip()
        org_mail=elements[2].get_attribute('textContent').strip()
        saller_dict[companyId]={'code':companyId, 'contact':org_contact, 'address':org_address, 'phone':org_phone,'mail':org_mail} 
    return saller_dict[companyId]


def createQuery(config):
    _=config.get('mintrud18','keyWords') 
    # убираем точку с конца
    _=re.sub(r'\.\s*$',r'',_)
    # заменяем ' ,  ' на ','
    _=re.sub(r'\s*,\s*',r',',_)
    # заменяем последовательные пробелы на '+'
    _=re.sub(r'\s+',r'%20',_)
    words=_.split(',')
    urls_info_list=[]
    notBefore=datetime.today()-timedelta(days=int(config.get('mintrud18','not_older_than')))
    for word in words:
        uri=config.get('mintrud18','url_template').format(word,notBefore.strftime('%d.%m.%Y'))
        urls_info_list.append({'region':'udmurtiya','word':word,'uri':uri})
    return urls_info_list




def loadData(config,driver):
    saller_dict={}
    vacancy_dict={}
    
    for url_info in createQuery(config):
        driver.get(url_info['uri'])
        for row in driver.find_elements(By.XPATH,'//tbody[@role="rowgroup"]/tr'):
            try:
                _=row.find_element(By.XPATH,'.//td[position()=1]/a')
                id=re.sub(r'.*/vacancy/detail/(.*)/\?.*',r'\1',_.get_attribute('href'))
                if id not in vacancy_dict:
                     vacancy={}
                     vacancy['vacancy']=_.get_attribute('textContent')
                     _=row.find_element(By.XPATH,'//td[position()=4]/a')
                     vacancy['companyId']=re.sub(r'.*companyId=(.*)',r'\1',_.get_attribute('href'))
                     vacancy['name']=_.get_attribute('textContent').strip() 
                     _=row.find_element(By.XPATH,'//td[position()=5]')
                     date=datetime.strptime(_.get_attribute('textContent').strip(),'%d.%m.%Y')
                     hot=0
                     now=datetime.today()
                     now=datetime(now.year,now.month,now.day)
                     if date>=now-timedelta(days=1):
                         hot=2
                     if date<now-timedelta(days=1) and date>=now-timedelta(days=3):
                         hot=1
                     vacancy['hot']=hot
                     vacancy['date']=date.strftime('%Y-%m-%d')
                     _=row.find_element(By.XPATH,'//td[position()=6]')
                     vacancy['count']=_.get_attribute('textContent')
                     vacancy['words']=set([url_info['word']])
                     vacancy_dict[id]=vacancy
                     vacancy['region']=url_info['region']
                     vacancy_dict[id]=vacancy
                     vacancy['id']=id
                else:
                     vacancy_dict[id]['words'].add(word)

            except:
                traceback.print_exc(file=sys.stdout)
                #pass

       
    expenses=[]    
    for key,vacancy in vacancy_dict.items():
        expensy=dict(vacancy)
        expensy['words']=re.sub(r'\+',r' ',', '.join(vacancy['words']))
        saller=getSaller(config,driver,saller_dict,vacancy['companyId'])
        expensy.update(saller)
        expensy['source']=re.sub(r'.*\.(.*)$',r'\1',__name__)
        expenses.append(expensy)
    return expenses

