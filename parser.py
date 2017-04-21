#!/usr/bin/env python
# -*- coding: utf-8 -*-


import imp,os
import ConfigParser
from datetime import datetime
import sys,traceback
reload(sys)
sys.setdefaultencoding('utf-8')
import xlsxwriter
from selenium import webdriver

column_keys=['source','id','vacancy','region','words','date','name','address','contact','phone','mail','count']
headers_map={
#            'source':'Источник',
#            'id':'Идентификатор',
            'vacancy':'Описание',
            'region':'Регион',
#            'words':'Ключевые слова',
            'date':'Дата размещения',
            'name':'Компания',
            'address':'Адрес',
            'contact':'Контактное лицо',
            'phone':'Телефон',
            'mail':'E-mail контактного лица',
            'count':'Количество вакантных мест'
}
region_unit={
    'udmurtiya':'Удмуртия',
    'bashkortostan':'Башкортостан',
    'tatarstan':'Татарстан',
    'kirovskaya_oblast':'Кировская область',
    'permskiy_kray':'Пермский край',
}


def generateExel(module,file_template,expenses):
    if len(expenses)==0:
        return
    workbook = xlsxwriter.Workbook(file_template.format(datetime.today().strftime('%Y_%m_%d')))
    worksheet = workbook.add_worksheet()
    hot_map={
        2: workbook.add_format({'fg_color': '#3eff0f'}),
        1: workbook.add_format({'fg_color': '#f3dc40'}),
        0: workbook.add_format()
    }
  
    row=0
    col=0
    for key in column_keys:
        worksheet.write(row, col,headers_map.get(key).decode('utf-8'),workbook.add_format({'bold': True}))
        col+=1
    for expensy in expenses:
        row+=1
        col=0
        hot=expensy['hot']
        for key in column_keys:    
            try:
                value= expensy[key].encode('utf-8')
            except:
                value = expensy[key]
            if key=='region':
                value=region_unit[value]
            worksheet.write(row, col,value,hot_map[hot])
            col+=1
    workbook.close() 
 


def __load_all_sources(config,dir='modules/sources'):
    sources = {}
    list_modules=os.listdir(dir)
    list_modules.remove('__init__.py')
    for module_name in list_modules:
        if module_name.split('.')[-1]=='py':
            foo = imp.load_source(module_name.split('.')[0],
                                  dir+os.sep+module_name)
            sources[module_name.split('.')[0]]=foo
    return sources



def loadData(config):
    print ('[START] : ' , datetime.now().isoformat())
    sources = __load_all_sources(config)

    # header reference description contacts
    if config.get('common','webdrivertype')=='PhantomJS':
        driver=webdriver.PhantomJS(executable_path=config.get('common','webdriver'))
    if config.get('common','webdrivertype')=='Chrome':
        driver=webdriver.Chrome(executable_path=config.get('common','webdriver'))
    driver.implicitly_wait(10)
    result=[]
    try:
        if len(sys.argv)==1: 
            for module,source in sources.items():
                print ('[INFO] processing ', module)
                expenses=source.loadData(config,driver)
                result.append([module,expenses])
        else:
            module_list=sys.argv[1:]
            for module,source in sources.items():
                if module in module_list:
                    print ('[INFO] processing ', module)
                    expenses=source.loadData(config,driver)
                    result.append([module,expenses])

    except:
        traceback.print_exc(file=sys.stdout)
    finally:
        if driver is not None:
            driver.close()

    print ('[END] : ' , datetime.now().isoformat())
    return result



 
if __name__=='__main__':
    config = ConfigParser.RawConfigParser()
    config.read('./parser.cfg')
    sources = __load_all_sources(config)
    for module,expenses in loadData(config):
        generateExel(module,config.get(module,'exel_file_template_name'),expenses)




