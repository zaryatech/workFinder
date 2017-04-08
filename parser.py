#!/usr/bin/env python
# -*- coding: utf-8 -*-


import imp,os
import ConfigParser
from datetime import datetime

def __load_all_sources(config,dir='modules/sources'):
    sources =[]
    list_modules=os.listdir(dir)
    list_modules.remove('__init__.py')
    for module_name in list_modules:
        if module_name.split('.')[-1]=='py':
            foo = imp.load_source(module_name.split('.')[0], dir+os.sep+module_name)
            sources.append(foo)
    return sources

if __name__=='__main__':
    print '[START] : ' + datetime.now().isoformat()
    config = ConfigParser.RawConfigParser()
    config.read('./parser.cfg')
    sources = __load_all_sources(config)

    # header reference description contacts
    result = []
    for source in sources:
        print (source)
        #result.extend(source.loadData(config))
        source.loadData(config)

    print '[END] : ' + datetime.now().isoformat()
    #print (result)



