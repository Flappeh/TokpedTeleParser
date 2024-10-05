from .database import db,TokpedItem, ItemSearch, NotifyItem, RunningJob


db.connect()
db.create_tables([TokpedItem, ItemSearch, NotifyItem, RunningJob])