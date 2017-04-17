#!/usr/bin/env python
# -*- coding: utf-8 -*-


from wsgiref.simple_server import make_server
from pyramid.config import Configurator
from pyramid.response import Response


import ConfigParser
import sys,traceback
reload(sys)
sys.setdefaultencoding('utf-8')

def hello_world(request):
    return Response('привет!')

def main():
    config=Configurator()
    config.add_view(hello_world)
    app=config.make_wsgi_app()
    return app


if __name__=='__main__':
    app=main()
    server=make_server('0.0.0.0',8081,app)
    server.serve_forever()
    
      
