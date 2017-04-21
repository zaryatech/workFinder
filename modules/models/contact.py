#! -*- coding: utf-8 -*-

from sqlalchemy import Column,Integer,Text,DateTime

from sqlalchemy.dialects.postgresql import ARRAY

from . import Base

class Contact(Base):
    """ Контакт """
    __tablename__='contact'
    id=Column(Integer,primary_key=True)
    mail=Column(ARRAY (Text))
    phone=Column(ARRAY(Text)),
    organization=Column(ARRAY(Text))
    refreshDate=Column(DateTime)
    lastSendDate=Column(DateTime)
        


    



