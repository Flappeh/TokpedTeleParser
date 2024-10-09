from time import time
import os
import logging
import sys
from .database import ItemSearch, TokpedItem, NotifyItem, RunningJob
from datetime import datetime, timedelta
from typing import List


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

def store_search(query_string: str, item_list: list[str], min_price: int, max_price: int):
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
            query_string = query_string,
            min_price = min_price,
            max_price = max_price
        )
        return True, []

def store_notify_item(query_string: str, item_ids: list[str], chat_id : int):
    message = "New item found\n"
    for i in item_ids:
        item = get_tokped_item(i)
        message += f"""

<b>Judul</b> : {item.name}
<b>Price</b> : Rp {item.price:,}
Url : <a href="{item.url}">url</a>
"""
    try:
        NotifyItem.create(
            query_string = query_string,
            message = message,
            chat_id = chat_id
        )
    except:
        logger.error("Error occured. Unable to create notification item")
    
def import_all_notif() -> List[NotifyItem]:
    try:
        notifications  = NotifyItem.select()
        return notifications
    except:
        logger.error("Error unable to retrieve notifications")

def get_last_notif_chat_id() -> int | None:
    try:
        return NotifyItem.select().order_by(NotifyItem.created_date.desc()).limit(1).chat_id
    except:
        logger.error("Error retrieving last notification chat id")
        return None

def remove_notif_from_id(id:int):
    try:
        NotifyItem.delete_by_id(id)
    except:
        logger.error(f"Unable to remove notification with id : {id}")

def get_all_job() -> List[RunningJob]:
    try:
        jobs = RunningJob.select()
        return jobs
    except:
        logger.error("Error retrieving list of jobs")

def check_job_data(query:str):
    try:
        RunningJob.get(RunningJob.query == query)
        return True
    except:
        return False

def store_job_data(query: str, chat_id: int, job_name:str):
    try:
        logger.info(f"Storing job for query : {query}")
        RunningJob.create(
            query=query,
            chat_id = chat_id,
            job_name = job_name
        )
    except:
        logger.error("Error on storing job data")

def get_search_from_query(query) -> ItemSearch:
    try:
        data = ItemSearch.get(
            ItemSearch.query_string == query
        )
        return data
    except:
        logger.error(f"Errr getting query data for item : {query}")
        raise

def delete_job_data(job_name:str):
    try:
        logger.info(f"Deleting job : {job_name}")
        job = RunningJob.get(RunningJob.job_name == job_name)
        job.delete_instance()
    except:
        logger.error(f"Error deleting job with name : {job_name}" )
        
def get_all_job_data():
    try:
        logger.info("Getting job data stored in database")
        jobs = RunningJob.select()
        data = []
        if len(jobs) < 1:
            return data
        for i in jobs:
            searchItem = get_search_from_query(i.query)
            data.append(
                {
                    "chat_id": i.chat_id,
                    "job_name": i.job_name,
                    "product_name": i.query,
                    "min_price": searchItem.min_price,
                    "max_price": searchItem.max_price
                }
            )
        return data
    except:
        logger.error("Error getting job data")