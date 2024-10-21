from urllib.parse import urlencode
from bs4 import BeautifulSoup 
import json
from dotenv import load_dotenv
from selenium.webdriver import Firefox, FirefoxOptions, Chrome, ChromeOptions
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.by import By
import multiprocessing
from time import sleep
import random
from selenium.webdriver.firefox.service import Service
from .utils import store_item, store_search, update_search, store_notify_item, get_logger
from .environment import SEARCH_INTERVAL
# Template url https://www.tokopedia.com/search?navsource=&ob=9&q=gtx%201660&pmin=1000000&pmax=3000000


MAIN_URL = "https://tokopedia.com/search?"

logger = get_logger()

def get_user_agent():
    with open('data/user-agents.txt', 'r') as f:
        data = [line.rstrip() for line in f]
    agent = random.choice(data)
    return agent

class TokpedParser(Chrome):
# class TokpedParser(Firefox):
    
    def __init__(self, options: ChromeOptions = None, service: Service = None, keep_alive: bool = True) -> None:
        options = ChromeOptions()
        # options.add_argument(f"user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/119.0.0.0 Safari/537.36")
        options.add_argument(f"user-agent={get_user_agent()}")
        options.add_argument("--headless=new")
        super().__init__(options, service, keep_alive)
        # self.driver = Chrome(options=options)
        # self.driver = Firefox(options=options)
        self.set_page_load_timeout(SEARCH_INTERVAL * 2 / 3 )
        
    def browser_get_data(self, url):
        try:
            self.get(url)
            for _ in range(3):
                body = self.find_element(by=By.CSS_SELECTOR, value="body")
                body.send_keys(Keys.PAGE_DOWN)
                sleep(0.2)
            return self.page_source
        except:
            logger.error(f"Error opening browser for url : {url}")
            return None
        
    def build_search_url(self, product_name: str, min_price: int = 0, max_price:int = 0):
        try:
            params = {}
            if min_price and max_price:
                params["pmin"] = min_price
                params["pmax"] = max_price
            params["q"] = product_name
            params["ob"] = 9 #Order by newest items
            params["condition"] = 2 # Filter only used
            url = MAIN_URL + urlencode(params)
            return url
        except:
            logger.error(f"Error building search url for {product_name}")
            return None
        
        
    def parse_content(self, content: bytes):
        try:
            soup = BeautifulSoup(content, 'html.parser')
            products = soup.find_all(lambda box: box.name=='a' and box.has_attr('data-theme'))
            result = []
            for i in products:
                product_link = i.get("href")
                if "topads" in product_link:
                    continue 
                item = {}
                product_box = i.select('div')[0]
                text_box = product_box.find_all('div', recursive=False)[1]
                product_name = text_box.find_all('span')[0]
                product_price = text_box.find_all('div', recursive=False)[1]
                
                item["product_name"] = product_name.text
                item["product_price"] = int(product_price.text.split("Rp")[1].replace('.',''))
                item["product_link"] = product_link
                result.append(item)
            return result
        except:
            logger.error("Error parsing html content")
            return []
        
    def get_data(self, input_data):
        try:
            query = input_data["product_name"]
            url = self.build_search_url(input_data['product_name'], input_data['min_price'], input_data['max_price'])
            data = self.browser_get_data(url)
            new_search = store_search(query, input_data["min_price"],input_data["max_price"], url)
            result = self.parse_content(data)
            items = []
            new_items = []
            for i in result:
                item_id, is_new = store_item(i)
                if item_id in items:
                    continue
                if is_new:
                    new_items.append(item_id)
                items.append(item_id)
            if not new_search:
                # new_data = check_difference(old_items, items)
                if len(new_items) > 0:
                    logger.info("New data found!")
                    update_search(query, items)
                    store_notify_item(
                        query_string = query, 
                        item_ids = new_items,
                        chat_id = int(input_data["chat_id"]))
                else:
                    logger.debug("Data masih sama")
        except Exception as e:
            logger.error(e)
            logger.error("Error getting data for current query")
                
def start_search_process(args):
    parser = TokpedParser()
    parser.get_data(args)
    parser.quit()

def start_item_search(data):
    logger.info(f"Starting search :  {data['product_name']}")
    # get_data(data)
    process = multiprocessing.Process(target=start_search_process, args=(data,))
    process.start()

