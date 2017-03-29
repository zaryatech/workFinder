#!/usr/bin/env python

import imp,os

sources=[]

def __load_all_sources(dir="modules/sources"):
    list_modules=os.listdir(dir)
    list_modules.remove('__init__.py')
    for module_name in list_modules:
        if module_name.split('.')[-1]=='py':
            foo = imp.load_source('module', dir+os.sep+module_name)
            sources.append(foo)

if __name__=='__main__':
    __load_all_sources()
    result = []
    for source in sources:
        result.extend(source.loadData())

    print (result)
    


