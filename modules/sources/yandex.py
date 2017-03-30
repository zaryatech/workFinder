# -*- coding: utf-8 -*-
#!/usr/bin/env python

import re
from mako.template import Template

#
#
# модуль возвращающий данные из yandex
#
#

YANDEX_XML_TEMPLATE=Template(r"""<?xml version="1.0" encoding="utf-8"?>
<request>
<!--Группирующий тег-->
   <query>
   <!--Текст поискового запроса-->
   ${query}
   </query>
   <sortby>
   <!--Тип сортировки результатов поиска-->
   </sortby>
   <groupings>
   <!--Параметры группировки в дочерних тегах-->
      <groupby attr="d" mode="deep" groups-on-page="10" docs-in-group="1" />
   </groupings>
   <page>
   <!--Номер запрашиваемой страницы результатов поиска-->
   </page>
</request>""", input_encoding='utf-8',
        output_encoding='utf-8',
        default_filters=['decode.utf8'])


def createQuery(keyWords):
    # убираем точку с конца
    query=re.sub(r"\.\s*$",r"",keyWords)
    # заменяем последовательные пробелы на один
    query=re.sub(r"\s+",r" ",query)
    # заменяем пробелы перед и за запятой вместе с самой запятую на '|' 
    query=re.sub(r"\s?,\s?",r"|",query)
    return query 

def loadData(config):
    keyWords=config.get('KeyWords','keyWords')
    print(YANDEX_XML_TEMPLATE.render_unicode(query=createQuery(keyWords)))
    result = [{'header':'Услуги механической обработки металла на заказ...', 'reference':'http://presslit.ru/tooling/',
     'description':'Токарно-фрезерные, расточные, шлифовальные работы. Обработка давлением. ... «ПРЕССЛИТМАШ» изготавливает детали из металла по вашим образцам, эскизам или чертежам.'}]
    return result
