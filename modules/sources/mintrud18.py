#!/use/bin/env python
# -*- coding: utf-8 -*-

from datetime import datetime, timedelta
from selenium import webdriver
from selenium.webdriver.common.by import By
import traceback,sys
import re

KEY_WORDS=['Токарь', 'Фрезеровщик']

url_template="http://szan.mintrud18.ru/vacancy/?ActivityScopeNoStandart=True&SearchType=1&Profession={}&Region=18&HideWithEmptySalary=False&ShowOnlyWithEmployerInfo=True&ShowOnlyWithHousing=False&StartDate={}&Sort=4&PageSize=0&SpecialCategories=False"


def getSaller(driver,saller_dict,companyId):
    if companyId not in saller_dict:
        driver.get('http://szan.mintrud18.ru/employer/detailvacancy/?companyId={}'.format(companyId))
        elements=driver.find_elements(By.XPATH,'//div[@class="panel-body"]/div[@class="row"]/div[@class="col-sm-9"]')
        org_contact=elements[0].get_attribute('textContent').strip()
        org_address=elements[3].get_attribute('textContent').strip()
        org_phone=elements[4].get_attribute('textContent').strip()
        saller_dict[companyId]={'code':companyId, 'contact':org_contact, 'address':org_address, 'phone':org_phone} 
    return saller_dict[companyId]

 
if __name__=="__main__":
    chromedriver_path='../chromedriver'
    driver = webdriver.Chrome(executable_path=chromedriver_path)

    vacancy_dict={}
    saller_dict={}

    for word in KEY_WORDS:
        url=url_template.format(word,datetime.today().strftime('%d.%m.%Y'))
        driver.get(url)
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
                    vacancy['date']=date 
                    hot=0
                    now=datetime.today()
                    now=datetime(now.year,now.month,now.day)
                    if date==now:
                        hot=2
                    if date==now-timedelta(days=1):
                        hot=1
                    vacancy['hot']=hot
                    _=row.find_element(By.XPATH,'//td[position()=6]')
                    vacancy['count']=_.get_attribute('textContent')
                    vacancy['words']=set([word])
                    vacancy_dict[id]=vacancy
                    vacancy['region']='udmurtiya'
                    vacancy_dict[id]=vacancy
                else:
                    vacancy_dict[id]['words'].add(word)

            except:
                traceback.print_exc(file=sys.stdout)
                #pass

        
    expenses=[]    
    for key,vacancy  in vacancy_dict.items():

        expensy=dict(vacancy)
        saller=getSaller(driver,saller_dict,vacancy['companyId'])
        expensy.update(saller)
        expenses.append(expensy)


    column_keys=['vacancy','region','words','date','name','address','contact','phone']
    headers_map={'vacancy':'Описание',
                'region':'Регион',
                'words':'Ключевые слова',
                'date':'Дата размещения',
                'name':'Компания',
                'address':'Адрес',
                'contact':'Контактное лицо',
                'phone':'Телефон'
    }
   
 
    for expensy in expenses:
        print('---------------------------')
        for key in column_keys:
            print(headers_map[key])
            print( expensy[key])

        
    driver.close()


