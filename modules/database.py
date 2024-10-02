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
    result = ForeignKeyField(TokpedItem, backref="search_result")

    class Meta:
        database = db

