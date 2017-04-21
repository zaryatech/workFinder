#!/usr/bin/env python
# -*- coding: utf-8 -*-

from sqlalchemy import Column, Integer, DateTime, ForeignKey, Text
from sqlalchemy.dialects.postgresql import JSONB, ARRAY
from . import Base


class Vacancy(Base):
    """ Хранилище данных по вакансиям """
    __tablename__='vacancy'
    id=Column(Integer,primary_key=True)
    data=Column(JSONB)
    dateOfCreation=Column(DateTime)
    contact=Column('contact_id',Integer,ForeignKey('contact.id'))
    keyWords=Column(ARRAY(Text))




    




