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
import sys, traceback
locale.setlocale(locale.LC_ALL,'ru_RU.utf-8')


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
        d = date_unit.get(date,None)
        if d is None:
            _=date.split()
            _[1]=month_unit[_[1].encode('utf-8')]
            d=datetime.strptime('{} {} {}'.format(_[0],_[1],datetime.today().year),'%d %B %Y')
            #d=datetime.strptime('06 Апрель 2017','%d %B %Y')
            if datetime.today()<d:
                d=datetime.strptime('{} {} {}'.format(_[0],_[1],datetime.today().year-1),'%d %B %Y')
        return d
    except:
        print "[ERROR]can't parse " + date


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
        # больше года назад
        return None
    else:
        return parseADate(dateStr)


def loadSallerInfo(href,vacancy, saller_dict):
    driver.get('https://www.avito.ru{}'.format(vacancy['href']))
    oref=driver.find_element(By.XPATH,'//div[@class="seller-info-name"]/a')
    org_code=re.sub(r'.*/(.*)/profile',r'\1',oref.get_attribute('href'))
    # грузим инфу
    if org_code not in saller_dict:
        button = driver.find_element(By.XPATH,'//button[span[@class="item-phone-button-sub-text"]]')
        button.click()
        WebDriverWait(driver, 1).until(EC.presence_of_element_located((By.XPATH,'//div[@class="item-phone-big-number js-item-phone-big-number"]/img')))        
        img = driver.find_element(By.XPATH,'//div[@class="item-phone-big-number js-item-phone-big-number"]/img')
        _,src = img.get_attribute('src').split('data:image/png;base64,')
        stream=io.BytesIO(base64.b64decode(src))
        img = Image.open(stream)
        with PyTessBaseAPI() as api:
            api.SetImage(img)    
            org_phone=api.GetUTF8Text().strip()
        org_name=oref.get_attribute('textContent').strip()
        item_phone_saller_info=driver.find_element(By.XPATH,'//div[@class="item-phone-seller-info"]')
        # 0 - "на Avito с ...", 1 - контакнтое лицо, 2-е адрес 
        values=[ item.get_attribute('textContent').strip() for item in item_phone_saller_info.find_elements(By.XPATH,'//div[@class="seller-info-value"]')]
        org_contact=values[1]
        org_address=values[2]
        saller_dict[org_code]={'code':org_code, 'name':org_name,'contact':org_contact, 'address':org_address, 'phone':org_phone}
    vacancy['ocode']=org_code


def createQuery(config):
    _=config.get('KeyWords','keyWords')
    # убираем точку с конца
    _=re.sub(r"\.\s*$",r"",_)
    # заменяем ' ,  ' на ','
    _=re.sub(r"\s*,\s*",r",",_)
    # заменяем последовательные пробелы на '+'
    _=re.sub(r"\s+",r"+",_)
    words=_.split(',')
    
    # заменяем пробелы перед и за запятой вместе с самой запятую на ',' 
    regions=re.sub(r"\s*,\s*",r",",config.get('Avito','regions')).split(',')
    urls_info_list=[]
    for word in words:
        for region in regions:
            uri=config.get('Avito','url_template').format(region,word)
            urls_info_list.append({'region':region,'word':word,'uri':uri}]
    return urls_info_list

def loadVacancy(driver,vacancy_dict, region,word):
    _=driver.find_elements(By.CSS_SELECTOR,'div[class*="item_table clearfix js-catalog-item-enum"]')
    if _ is None:
        return
    for div in _:
        id=div.get_attribute('id')
        if id in vacancy_dict:
            vacancy_dict[id]['words'].append(word)
            continue
        date=getADate(div.find_element(By.CSS_SELECTOR,'div[class*="date c-2"]').get_attribute('textContent').strip())
        if date is not None:
            uriRef=div.find_element(By.CSS_SELECTOR,'a[class*="item-description-title-link"]')
            href=uriRef.get_attribute('href')
            vacancy_dict[id]={'words':[word],'region':region,'href':href,'vacancy':uriRef.get_attribute('textContent').strip(),'date':date}



def loadData(config):
    driver=None
    try:
        driver=webdriver.PhantomJS(executable_path=config.get('Common','webdriver'))
        saller_dict={}
        vacancy_dict={}
        for url_info in createQuery(config):
            loadVacancy(driver,vacancy_dict,region,word)
        for vacancy in vacancy_dict:
            loadSallerInfo(driver,vacancy,saller_dict)
    except:
        if driver is not None:
            driver.close()
        traceback.print_exc(file=sys.stdout)
#    createQuery(config)
#    result = [{'source':'avito','header':'Услуги механической обработки металла на заказ...', 'reference':'http://presslit.ru/tooling/',
#     'description':'Токарно-фрезерные, расточные, шлифовальные работы. Обработка давлением. ... «ПРЕССЛИТМАШ» изготавливает детали из металла по вашим образцам, эскизам или чертежам.'}]
    return None




