#!/usr/bin/env python
# -*- coding: utf-8 -*-


from wsgiref.simple_server import make_server
from pyramid.config import Configurator
from pyramid.response import Response
from sqlalchemy import engine_from_config
from modules.models import initialize_sql

import ConfigParser
import sys,traceback
reload(sys)
sys.setdefaultencoding('utf-8')

def hello_world(request):
    return Response('привет!')


def main(global_config, **settings):
    config = Configurator()
    config.add_route('hello', '/hello/{name}')
    config.add_view(hello_world, route_name='hello')
    
    config.scan('modules.models')
    engine=engine_from_config(settings,prefix='sqlalchemy.')
    initialize_sql(engine)

    app = config.make_wsgi_app()
   


#def main(global_config, **settings):
#    config=Configurator(settings=settings)
#    config.scan('modules.models')
#    engine=engine_from_config(settings,prefix='sqlalchemy.')
#    config.add_view(hello_world)
#    app=config.make_wsgi_app()
#    return app
#
#
#if __name__=='__main__':
#    app=main()
#    config = ConfigParser.ConfigParser()
#    config.read('development.ini')
#    db_url = config.get('app:main', 'sqlalchemy.url')
#    server=make_server('0.0.0.0',8081,app)
#    server.serve_forever()
#    
#      
