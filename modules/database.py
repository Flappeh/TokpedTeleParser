from peewee import *
import os
from datetime import datetime

DIRNAME = os.getcwd()

db = SqliteDatabase(DIRNAME + '/data/database.db')

class TokpedItem(Model):
    name = CharField()
    price = IntegerField()
    url = CharField()
    
    class Meta:
        database = db
        
class ItemSearch(Model):
    query_string = CharField()
    last_update = DateTimeField(default = datetime.now())
    min_price = IntegerField()
    max_price = IntegerField()
    result = CharField()
    url = CharField()

    class Meta:
        database = db

class NotifyItem(Model):
    chat_id = IntegerField(null = True)
    query_string = CharField()
    message = CharField(max_length=10000)
    created_date = DateTimeField(default = datetime.now())
    class Meta:
        database = db

class RunningJob(Model):
    chat_id = IntegerField(null=True)
    job_name = CharField()
    query = CharField()
    
    class Meta:
        database = db
        