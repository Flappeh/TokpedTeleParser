from .database import db, PiAccount
from datetime import datetime
number = []

with open('./data/phone_number.txt','r') as f:
    lines = f.readlines()
    for i in lines:
        num = i.split(':')
        number.append(num[1].strip())

# with open('./data/phone_fixed.txt','w') as f:
#     for i in number:
#         f.write(f"{i}\n")
        

def import_phone_number():
    try:
        with db.atomic():
            for i in number:
                PiAccount.create(
                    phone = i,
                    last_used = datetime(1990, 1, 1),
                    password = "Goodgame00"
                )
    except:
        print("error inserting number")
        