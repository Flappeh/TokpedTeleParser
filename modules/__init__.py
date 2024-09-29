from .database import db,TeleUser,PiAccount,PiWallet


db.connect()
db.create_tables([TeleUser,PiAccount,PiWallet])