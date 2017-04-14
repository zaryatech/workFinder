#!/usr/bin/env python
# -*- coding: utf-8 -*-

from datetime import datetime, timedelta
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import traceback,sys
import re,unicodedata
import locale
locale.setlocale(locale.LC_ALL,'ru_RU.utf-8')
import sys
reload(sys)


region_dict={
'udmurtiya':'1800000000000',
'bashkortostan':'0200000000000',
'tatarstan':'1600000000000',
'kirovskaya_oblast':'4300000000000',
'permskiy_kray':'5900000000000'
}

def createQuery(config):
    _=config.get('trudvsem','keyWords')
    # убираем точку с конца
    _=re.sub(r'\.\s*$',r'',_)
    # заменяем ' ,  ' на ','
    _=re.sub(r'\s*,\s*',r',',_)
    words=_.split(',')
    urls_info_dict={}
    for word in words:
        urls_info_dict[word]=[]
        regions='bashkortostan'.split(',')
        for region in regions:
            url=config.get('trudvsem','url_template').format(word,region_dict[region])
            urls_info_dict[word].append({'region':region,'url':url})
    return urls_info_dict


def getVacancy(config,driver,href,expensy):
    try:
        driver.get(href)
        address=driver.find_element(By.XPATH,'//div/b[contains(text(), "Дополнительная информация по адресу")]/following-sibling::span')
        expensy['address']=address.get_attribute('textContent').strip()
        count=driver.find_element(By.XPATH,'//div/b[contains(text(), "Количество рабочих мест")]/following-sibling::span')
        expensy['count']=count.get_attribute('textContent').strip()
        name=driver.find_element(By.XPATH,'//div[@class="company"]/a')
        expensy['name']=name.get_attribute('textContent').strip()
        contact=driver.find_element(By.XPATH,'//div/b[contains(text(), "Контактное лицо")]/following-sibling::span')
        expensy['contact']=contact.get_attribute('textContent').strip()
        _=contact.find_element(By.XPATH,'./../following-sibling::div')
        phone=_.find_element(By.XPATH,'./div/span')
        expensy['phone']=phone.get_attribute('textContent').strip()
        _=_.find_element(By.XPATH,'./following-sibling::div')
        try:
            mail=_.find_element(By.XPATH,'./div/a')
            expensy['mail']=mail.get_attribute('textContent').strip()
        except:
            expensy['mail']=''
    except:
        print("[DEBUG]error on {}".format(href))
        raise

    


def loadData(config,driver):
    vacancy_dict={}
    notBefore=datetime.today()-timedelta(days=int(10))
    for word,value in createQuery(config).items():
        for reg_url in value:
            next_page=True
            region=reg_url['region']
            url=reg_url['url']
            driver.get(url)
            while next_page:
                try:
                    try:
                        WebDriverWait(driver,5).until(EC.presence_of_element_located((By.CSS_SELECTOR,'div[class*="item row"]')))
                    except:
                        WebDriverWait(driver,5).until(EC.presence_of_element_located((By.CSS_SELECTOR,'p[class*="no-data"]')))
 
                    item_rows=driver.find_elements(By.CSS_SELECTOR,'div[class*="item row"]:not([class*="mobility-panel-search"])')
                    for item in item_rows:
                        try:
                            date=item.find_element(By.XPATH,'.//span[@class="date"]/time').get_attribute('textContent').strip()
                            date=datetime.strptime(date,'%d.%m.%Y')
                            if date < notBefore:
                                next_page=False
                                break
                            _=item.find_element(By.XPATH,'.//a[@class="vacancy"]')
                            href=_.get_attribute('href')
                            id=re.sub(r'.*/card/.*/(.*)\?.*',r'\1',href)
                            if id not in vacancy_dict:
                                vacancy={}
                                _=_.find_element(By.XPATH,'./span')
                                vacancy['vacancy']=_.get_attribute('textContent').strip()
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
                                vacancy['region']=region
                                vacancy['href']=href
                                vacancy_dict[id]=vacancy
                            else:
                                vacancy_dict[id]['words'].add(word)
                        except:
                            traceback.print_exc(file=sys.stdout)
                            pass

                    if next_page:
                        nextButton=driver.find_elements(By.XPATH,'//a[@class="next"]')
                        if len(nextButton)>0:
                            if nextButton[0].is_enabled():
                                nextButton[0].click()
                        else:
                            next_page=0
                except:
                    traceback.print_exc(file=sys.stdout)
                    next_page=False

    expenses=[]
    for id,vacancy in vacancy_dict.items():
        expensy=dict(vacancy)
        expensy['words']=', '.join(vacancy['words'])
        getVacancy(config,driver,vacancy['href'],expensy)
        print(expensy)
        expenses.append(expensy)
    return expenses




