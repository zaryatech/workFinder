#!/usr/bin/env python
# -*- coding: utf-8 -*-


import imp,os
import ConfigParser


def __load_all_sources(config,dir='modules/sources'):
    sources =[]
    list_modules=os.listdir(dir)
    list_modules.remove('__init__.py')
    for module_name in list_modules:
        if module_name.split('.')[-1]=='py':
            foo = imp.load_source('module', dir+os.sep+module_name)
            sources.append(foo)
    return sources

if __name__=='__main__':
    config = ConfigParser.RawConfigParser()
    config.read('./parser.cfg')
    sources = __load_all_sources(config)

    # header reference description contacts
    result = []
    for source in sources:
        result.extend(source.loadData(config))

    print (result)
    


