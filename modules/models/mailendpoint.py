#!/usr/bin/env python
# -*- coding: utf-8 -*-

from sqlalchemy import Column, Integer, Text, DateTime, ForeignKey
    
from . import Base

class MailEndpoint(Base):
    """ Список адресов для рассылки """
    __tablename__='mailendpoint'
    id=Column(Integer,primary_key=True)
    mail=Column(Text,nullable=False)
    contact=Column('contact_id', Integer,ForeignKey('contact.id'))


