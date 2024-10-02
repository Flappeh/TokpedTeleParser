from time import time
import os
import logging
import sys
from .database import ItemSearch, TokpedItem
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

def store_item(data):
    try:
        item = TokpedItem.get(
            TokpedItem.name == data['product_name']
        )
        item.price = data["product_price"]
        item.url = data["product_link"]
        item.save()
        return item
    except:
        new_item = TokpedItem.create(
            name = data['product_name'],
            price = data['product_price'],
            url = data['product_link']
        )
        return new_item

def store_phrase(query_string, items: list[TokpedItem]):
    pass

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

