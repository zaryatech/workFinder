#!/usr/bin/env python
# -*- coding: utf-8 -*-

from sqlalchemy import Column, Integer, DateTime

from sqlalchemy.dialects.postgresql import JSONB

from . import Base

class DirtyData(Base):
    """ Хранилище первоначальной информации """
    __tablename__='dirtydata'
    id=Column(Integer,primary_key=True)
    data=Column(JSONB)
    dateOfCreation=Column(DateTime)



    




