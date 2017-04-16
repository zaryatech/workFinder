#!/usr/bin/env python
# -*- coding: utf-8 -*-
from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import base64
import re,unicodedata
from tesserocr import PyTessBaseAPI
from PIL import Image
from selenium.webdriver.chrome.options import Options
import io
from datetime import datetime, timedelta
import locale
import traceback
locale.setlocale(locale.LC_ALL,'ru_RU.utf-8')
import sys
reload(sys)
date_unit={
'Сегодня':datetime.today(),
'Вчера':datetime.today()-timedelta(days=1)
}

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


def parseADate(date):
    try:
	dateStr=unicodedata.normalize('NFKD', date)
        suff=re.search('(\d\d\d\d)$',dateStr)
        d=None
        if suff is None:
            dateStr=re.sub(r'\s*\d\d:\d\d$',r'',dateStr.encode('utf-8'))
            d = date_unit.get(dateStr,None)
            if d is None:
                _=date.split()
                _[1]=month_unit[_[1].encode('utf-8')]
                d=datetime.strptime('{} {} {}'.format(_[0],_[1],datetime.today().year),'%d %B %Y')
                if datetime.today()<d:
                    d=datetime.strptime('{} {} {}'.format(_[0],_[1],datetime.today().year-1),'%d %B %Y')
            else:
                # убираем время
                d=datetime(d.year,d.month,d.day)
        return d
    except:
        print '[ERROR]can\'t parse ' + date


def getADate(dateStr):
    """
        Сегодня 13:38
        Вчера 15:12
        5 апреля 08:33
        1 декабря 2015  
    """
    dateStr=unicodedata.normalize("NFKD", dateStr)
    suff=re.search('(\d\d\d\d)$',dateStr)
    if suff is not None:
        _=date.split()
        _[1]=month_unit[_[1]]
        d=datetime.strptime('{} {} {}'.format(_[0],_[1],datetime.today().year),'%d %B %Y')
        if datetime.today()<d:
           d=datetime.strptime('{} {} {}'.format(_[0],_[1],datetime.today().year-1),'%d %B %Y')
        return d
    else:
        return parseADate(dateStr)


def loadSallerInfo(config,driver,vacancy, saller_dict):
    print ('[DEBIG]loadSallerInfo {}'.format(vacancy['href']))
    driver.get(vacancy['href'])
    org_code=None
    try: 
        oref=driver.find_element(By.XPATH,'//div[@class="seller-info-name"]/a')
        org_code=re.sub(r'.*/(.*)/profile',r'\1',oref.get_attribute('href'))
    except:
        oref=driver.find_element(By.XPATH,'//div[@class="seller-info-name"]')
    # грузим инфу
    if org_code is None or org_code not in saller_dict:
        button = WebDriverWait(driver,20).until(EC.element_to_be_clickable((By.XPATH,'//button[span[@class="item-phone-button-sub-text"]]')))
        webdriver.ActionChains(driver).move_to_element_with_offset(button, 10, 10).click().perform()
        #button.click()
        WebDriverWait(driver, 20).until(EC.presence_of_element_located((By.XPATH,'//div[@class="item-phone-big-number js-item-phone-big-number"]/img')))        
        img = driver.find_element(By.XPATH,'//div[@class="item-phone-big-number js-item-phone-big-number"]/img')
        _,src = img.get_attribute('src').split('data:image/png;base64,')
        stream=io.BytesIO(base64.b64decode(src))
        img = Image.open(stream)
        with PyTessBaseAPI() as api:
            api.SetVariable("tessedit_char_whitelist", "0123456789 -")
            api.SetImage(img)    
            org_phone=api.GetUTF8Text().strip()
        org_name=oref.get_attribute('textContent').strip()
        item_phone_saller_info=driver.find_element(By.XPATH,'//div[@class="item-phone-seller-info"]')
        # 0 - "на Avito с ...", 1 - контакнтое лицо, 2-е адрес 
        values=[ item.get_attribute('textContent').strip() for item in item_phone_saller_info.find_elements(By.XPATH,'//div[@class="seller-info-value"]')]
        org_contact=values[1]
        org_address=values[2]
        if org_code is None:
            org_code=org_name 
        saller_dict[org_code]={'code':org_code, 'name':org_name,'contact':org_contact, 'address':org_address, 'phone':org_phone,'count':'1','mail':''}
    vacancy['companyId']=org_code


def createQuery(config):
    _=config.get('avito','keyWords')
    # убираем точку с конца
    _=re.sub(r'\.\s*$',r'',_)
    # заменяем ' ,  ' на ','
    _=re.sub(r'\s*,\s*',r',',_)
    # заменяем последовательные пробелы на '+'
    _=re.sub(r'\s+',r'+',_)
    words=_.split(',')

    # заменяем пробелы перед и за запятой вместе с самой запятую на ',' 
    regions=re.sub(r'\s*,\s*',r',',config.get('avito','regions')).split(',')
    urls_info_list=[]
    for word in words:
        for region in regions:
            uri=config.get('avito','url_template').format(region,word)
            urls_info_list.append({'region':region,'word':word,'uri':uri})
    return urls_info_list

def loadVacancy(config,driver,vacancy_dict, uri,region,word):
    print ('[DEBIG]loadVacancy {} {} {}'.format(uri,region,word))
    driver.get(uri) 
    _=driver.find_elements(By.CSS_SELECTOR,'div[class*="item_table clearfix js-catalog-item-enum"]')
    if _ is None or not _:
        return
    for div in _:
        id=div.get_attribute('id')
        if id in vacancy_dict:
            vacancy_dict[id]['words'].add(word)
            continue
        date=getADate(div.find_element(By.CSS_SELECTOR,'div[class*="date c-2"]').get_attribute('textContent').strip())
        if date is not None and date >= datetime.today()-timedelta(days=int(config.get('avito','not_older_than'))):
            uriRef=div.find_element(By.CSS_SELECTOR,'a[class*="item-description-title-link"]')
            href=uriRef.get_attribute('href').strip()
            vacancy=uriRef.get_attribute('textContent').strip()
            hot=0
            now=datetime.today()
            now=datetime(now.year,now.month,now.day)
            if date==now:
                hot=2
            if date==now-timedelta(days=1):
                hot=1
            vacancy_dict[id]={'id':id,'hot':hot,'words':set([word]),'region':region,'href':href,'vacancy':vacancy,'date':date.strftime('%Y-%m-%d')}



def loadData(config,driver):
    expenses=[]
    try:
        saller_dict={}
        vacancy_dict={}
        for url_info in createQuery(config):
            loadVacancy(config,driver,vacancy_dict,url_info['uri'],url_info['region'],url_info['word'])
        for key, vacancy in vacancy_dict.items():
            loadSallerInfo(config,driver,vacancy,saller_dict)
        
 
        for key, vacancy in vacancy_dict.items():
            expensy=dict(vacancy)
            expensy['words']=re.sub(r'\+',r' ',', '.join(vacancy['words']))
            saller=saller_dict[vacancy['companyId']]
            expensy.update(saller)
            expensy['source']=re.sub(r'.*\.(.*)$',r'\1',__name__)
            expenses.append(expensy)
    except:
        if driver is not None:
            driver.close()
        traceback.print_exc(file=sys.stdout)
    return expenses





