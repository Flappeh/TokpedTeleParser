from .database import db,TokpedItem, ItemSearch


db.connect()
db.create_tables([TokpedItem, ItemSearch])