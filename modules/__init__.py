from .database import db,TokpedItem, ItemSearch, NotifyItem


db.connect()
db.create_tables([TokpedItem, ItemSearch, NotifyItem])