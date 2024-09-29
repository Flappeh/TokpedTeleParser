from peewee import *
import os
from datetime import datetime

DIRNAME = os.getcwd()

db = SqliteDatabase(DIRNAME + '/data/database.db')

class TeleUser(Model):
    name = CharField()
    phone = CharField()
    pasword = CharField()
    
    class Meta:
        database = db


class PiAccount(Model):
    phone = CharField()
    password = CharField()
    last_used =  DateTimeField(default=datetime.now())
    class Meta:
        database = db
    

class PiWallet(Model):
    public_key = CharField(null = True)
    pass_phrase = CharField(null = True)
    balance = CharField(null = True)
    last_update = DateTimeField(default=datetime.now())
    class Meta:
        database = db
    