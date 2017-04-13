#!/use/bin/env python
# -*- coding: utf-8 -*-

from datetime import datetime, timedelta
from selenium import webdriver
from selenium.webdriver.common.by import By
import traceback,sys
import re,unicodedata
import locale
locale.setlocale(locale.LC_ALL,'ru_RU.utf-8')
import sys
reload(sys)



def getSallerInfo(config,driver,href,expensy):
    driver.get(href)
    expensy['name']=driver.find_element(By.XPATH,'//div[@id="vacancy-company"]').get_attribute('textContent')\
        .encode('utf-8').strip()
    expensy['count']=driver.find_element(By.XPATH,'//div[@class="field"]/div[@class="field-value" and position()=2]')\
        .get_attribute('textContent').encode('utf-8').strip()
    expensy['org_address']=driver.find_element(By.XPATH,'//div[@class="vacancy-fields-group" and position()=2]/div[@class="field" and position()=1]/div[@class="field-value"]')\
        .get_attribute('textContent').encode('utf-8').strip()
    print(expensy['org_address'])
    #if companyId not in saller_dict:
    #    driver.get(config.get('mintrud18','company_template').format(companyId))
    #    elements=driver.find_elements(By.XPATH,'//div[@class="panel-body"]/div[@class="row"]/div[@class="col-sm-9"]')
    #    org_contact=elements[0].get_attribute('textContent').strip()
    #    org_address=elements[3].get_attribute('textContent').strip()
    #    org_phone=elements[4].get_attribute('textContent').strip()
    #    saller_dict[companyId]={'code':companyId, 'contact':org_contact, 'address':org_address, 'phone':org_phone} 
    #return saller_dict[companyId]


def createQuery(config,driver):
    _=config.get('bashzan','keyWords') 
    # убираем точку с конца
    _=re.sub(r'\.\s*$',r'',_)
    # заменяем ' ,  ' на ','
    _=re.sub(r'\s*,\s*',r',',_)
    # заменяем последовательные пробелы на '+'
    _=re.sub(r'\s+',r'%20',_)
    words=_.split(',')
    urls_info_list=[]
    notBefore=datetime.today()-timedelta(days=int(config.get('bashzan','not_older_than')))
    for word in words:
        page=1
        uri=config.get('bashzan','url_template').format(word,str(page))
        urls_info_list.append({'region':'bashkortostan','word':word,'uri':uri})
        driver.get(uri)
        nav_list=driver.find_elements(By.XPATH,'//nav[@class="pagination"]/span')
        if len(nav_list)>1:
            for i in range(2,len(nav_list)):
                uri=config.get('bashzan','url_template').format(word,str(i))
                urls_info_list.append({'region':'bashkortostan','word':word,'uri':uri})
                 
    return urls_info_list

   
month_unit={
    'января':'Январь',
    'февраля':'Февраль',
    'марта':'Март',
    'апреля':'Апрель',
    'мая':'Май',
    'июня':'Июнь',
    'июля':'Июль',
    'августа':'Август',
    'сентября':'Сентябрь',
    'октября':'Октябрь',
    'ноября':'Ноябрь',
    'декабря':'Декабрь'
}

def getDate(dateStr):
    _=dateStr.split()
    _[1]=month_unit[_[1].encode('utf-8')].encode('utf-8')
    d=datetime.strptime('{} {} {}'.format(_[0],_[1],datetime.today().year),'%d %B %Y')
    if datetime.today() < d:
        d=datetime.strptime('{} {} {}'.format(_[0],_[1],datetime.today().year-1),'%d %B %Y')
    return d
    
         
 
def loadData(config,driver):
    saller_dict={}
    vacancy_dict={}
    process_next_page=True
    for url_info in createQuery(config,driver):
        if not process_next_page:
            break
        driver.get(url_info['uri'])
        for row in driver.find_elements(By.CSS_SELECTOR,'div[class*="vacancy clearfix"]'):
            try:
                _=row.find_element(By.XPATH,'.//div[@class="vacancy-name"]/a')
                id=re.sub(r'.*/vacancies/(.*)$',r'\1',_.get_attribute('href'))
                if id not in vacancy_dict:
                     vacancy={}
                     vacancy['vacancy']=_.get_attribute('textContent')
                     vacancy['href']=_.get_attribute('href')
                     _=row.find_element(By.XPATH,'.//div[@class="vacancy-date"]').get_attribute('textContent').strip().encode('utf-8')
                     date=getDate(_)
                     notBefore=datetime.today()-timedelta(days=int(config.get('bashzan','not_older_than')))
                     if date<notBefore:
                        process_next_page=False
                        continue
                     hot=0
                     now=datetime.today()
                     now=datetime(now.year,now.month,now.day)
                     if date>=now-timedelta(days=1):
                         hot=2
                     if date<now-timedelta(days=1) and date>=now-timedelta(days=3):
                         hot=1
                     vacancy['hot']=hot
                     vacancy['date']=date.strftime('%Y-%m-%d')
                     vacancy['words']=set([url_info['word']])
                     vacancy['region']=url_info['region']
                     vacancy_dict[id]=vacancy
                else:
                     vacancy_dict[id]['words'].add(word)

            except:
                traceback.print_exc(file=sys.stdout)
                #pass

       
    expenses=[]    
    for key,vacancy in vacancy_dict.items():
        expensy=dict(vacancy)
        expensy['words']=re.sub(r'\+',r' ',', '.join(vacancy['words']))
        getSallerInfo(config,driver,vacancy['href'],expensy)
        #expenses.append(expensy)
    return expenses

