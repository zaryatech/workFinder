#!/usr/bin/env python
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
    print(href)
    driver.get(href)
    expensy['name']=driver.find_element(By.XPATH,'//div[@id="vacancy-company"]').get_attribute('textContent')\
        .encode('utf-8').strip()
    vacancy_groups=driver.find_elements(By.XPATH,'//div[@class="vacancy-fields-group"]')
    expensy['count']=vacancy_groups[0].find_elements(By.XPATH,'.//div[@class="field-value"]')[1].get_attribute('textContent').strip()
    contact_group=vacancy_groups[1]
    address=contact_group.find_element(By.XPATH,'.//div[@class="field-label" and contains(text(), "Адрес")]/following-sibling::div')
    expensy['address']=address.get_attribute('textContent').strip()
    contact=contact_group.find_element(By.XPATH,'.//div[@class="field-label" and contains(text(), "Имя контактного лица")]/following-sibling::div')
    expensy['contact']=contact.get_attribute('textContent').strip()
    phone=contact_group.find_element(By.XPATH,'.//div[@class="field-label" and contains(text(), "Телефон контактного лица")]/following-sibling::div')
    expensy['phone']=phone.get_attribute('textContent').strip()
    try: 
        mail=contact_group.find_element(By.XPATH,'.//div[@class="field-label" and contains(text(), "E-mail контактного лица")]/following-sibling::div')
        expensy['mail']=mail.get_attribute('textContent').strip()
    except:
        expensy['mail']=''  

        

def createQuery(config,driver):
    _=config.get('bashzan','keyWords') 
    # убираем точку с конца
    _=re.sub(r'\.\s*$',r'',_)
    # заменяем ' ,  ' на ','
    _=re.sub(r'\s*,\s*',r',',_)
    words=_.split(',')
    urls_info_dict={}
    notBefore=datetime.today()-timedelta(days=int(config.get('bashzan','not_older_than')))
    for word in words:
        page=1
        uri=config.get('bashzan','url_template').format(word,str(page))
        urls_info_dict[word]=[]
        urls_info_dict[word].append(uri)
        driver.set_page_load_timeout(10)
        try:
            driver.get(uri)
        except:
            print('[WARNING] Timeout exception')
            driver.get(uri)
        nav_list=driver.find_elements(By.XPATH,'//nav[@class="pagination" and position()=1]/span')
        if len(nav_list)>1:
            for i in range(2,len(nav_list)+1):
                uri=config.get('bashzan','url_template').format(word,str(i))
                urls_info_dict[word].append(uri)
                 
    return urls_info_dict

   
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
    for word, value in createQuery(config,driver).items():
        next_word=False
        for uri in value:
            driver.get(uri)
            if next_word==True:
                break
            for row in driver.find_elements(By.CSS_SELECTOR,'div[class*="vacancy clearfix"]'):
                try:
                    _=row.find_element(By.XPATH,'.//div[@class="vacancy-name"]/a')
                    id=re.sub(r'.*/vacancies/(.*)$',r'\1',_.get_attribute('href'))
                    vDate=row.find_element(By.XPATH,'.//div[@class="vacancy-date"]').get_attribute('textContent').strip().encode('utf-8')
                    date=getDate(vDate)
                    notBefore=datetime.today()-timedelta(days=int(config.get('bashzan','not_older_than')))
                    if date<notBefore:
                        next_word=True
                        break
                    if id not in vacancy_dict:
                        vacancy={}
                        vacancy['vacancy']=_.get_attribute('textContent')
                        vacancy['href']=_.get_attribute('href')
                        hot=0
                        now=datetime.today()
                        now=datetime(now.year,now.month,now.day)
                        if date>=now-timedelta(days=1):
                            hot=2
                        if date<now-timedelta(days=1) and date>=now-timedelta(days=3):
                            hot=1
                        vacancy['hot']=hot
                        vacancy['date']=date.strftime('%Y-%m-%d')
                        vacancy['words']=set([word])
                        vacancy['region']='bashkortostan'
                        vacancy_dict[id]=vacancy
                    else:
                         vacancy_dict[id]['words'].add(word)

                except:
                    traceback.print_exc(file=sys.stdout)

       
    expenses=[]    
    for key,vacancy in vacancy_dict.items():
        try:
            expensy=dict(vacancy)
            expensy['words']=re.sub(r'\+',r' ',', '.join(vacancy['words']))
            getSallerInfo(config,driver,vacancy['href'],expensy)
            expenses.append(expensy)
        except:
            print('[ERROR] href: {}'.format(vacancy['href']))
            traceback.print_exc(file=sys.stdout)
 
        
    return expenses

