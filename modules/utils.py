from time import time
import os
import logging
import sys
from .database import ItemSearch, TokpedItem, NotifyItem
from datetime import datetime, timedelta

dir_path = os.path.dirname(os.path.realpath(__file__))
loggers = {}

def get_logger(name=None):
    global loggers
    if not name:
        name = __name__
    if loggers.get(name):
        return loggers.get(name)
    logger = logging.getLogger(name)
    logger.setLevel(logging.DEBUG)
    stream_handler = logging.StreamHandler(sys.stdout)
    log_formatter = logging.Formatter("%(asctime)s [%(levelname)s] %(name)s: %(message)s")
    stream_handler.setFormatter(log_formatter)
    logger.addHandler(stream_handler)
    logger.propagate = False
    return logger

logger = get_logger()

def check_difference(old_items: list, new_items: list):
    try:
        new_list = []
        print(f"""
OLD ITEMS = {old_items}


NEW ITEMS = {new_items}              
              
              
""")
        for i in new_items:
            if i in old_items:
                continue
            else:
                new_list.append(i)
        return new_list
    except:
        logger.error("Error checking for similarities between list")
        return []
    
def get_tokped_item(id: str):
    try:
        item = TokpedItem.get_by_id(int(id))
        return item
    except:
        logger.error(f"Error, unable to find tokped item with id : {id}")

def store_item(data):
    try:
        item = TokpedItem.get(
            TokpedItem.name == data['product_name']
        )
        item.price = data["product_price"]
        item.url = data["product_link"]
        item.save()
        return str(item.id)
    except:
        new_item = TokpedItem.create(
            name = data['product_name'],
            price = data['product_price'],
            url = data['product_link']
        )
        return str(new_item.id)

def store_search(query_string: str, item_list: list[str]):
    try:
        item_ids = ','.join(item_list)
        
        search = ItemSearch.get(
            ItemSearch.query_string == query_string
        )
        old_items = search.result.split(',')
        
        search.last_update = datetime.now()
        search.result = item_ids
        search.save()
        return False, old_items
    except:
        ItemSearch.create(
            result = item_ids,
            query_string = query_string
        )
        return True, []


def store_notify_item(query_string: str, item_id: list[str]):
    message = "New item found\n"
    for i in item_id:
        item = get_tokped_item(i)
        message += f"""

Judul : {item.name}
Price : {item.price}
Url : {item.url}
"""
    try:
        NotifyItem.create(
            query_string = query_string,
            message = message
        )
    except:
        logger.error("Error occured. Unable to create notification item")
    

# def store_phrase(phrase:str, balance: str):
#     try:
#         wallet = PiWallet.get(
#             PiWallet.pass_phrase == phrase
#         )
#         wallet.balance = balance
#         wallet.last_update = datetime.now()
#         wallet.save()
#     except:
#         logger.info("Wallet doesn't exist, creating one")
#         PiWallet.create(
#             balance = balance,
#             pass_phrase = phrase
#         )
        
        
# def get_wallet_account() -> PiAccount:
#     account  = PiAccount.select().where(PiAccount.last_used < datetime.now() - timedelta(days=1)).get()
#     account.last_used = datetime.now()
#     account.save()
#     print(f"Account : {account}")
#     return account

# def delete_wallet_account(account: PiAccount):
#     PiAccount.delete(account)

