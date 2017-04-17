#! -*- coding: utf-8 -*-

from sqlalchemy import {
    Column,
    Integer,
    Text
}

from sqlalchemy.dialects.postgresql import ARRAY

class Contact(Base):
    """ Контакт """
    __table__='contact'
    id=Column(Integer,primary_key=True)
    mail=Column(ARRAY (Text))
    phone=Column(ARRAY(Text)),
    organization=Column(ARRAY(Text))
    refreshDate=Column(DateTime)
    lastSendDate=Column(DateTime)
        


    



