from urllib.parse import urlencode
from bs4 import BeautifulSoup 
import json
from dotenv import load_dotenv
from selenium.webdriver import Firefox, FirefoxOptions, Chrome, ChromeOptions
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.by import By
import multiprocessing
from time import sleep
from .utils import store_item

# Template url https://www.tokopedia.com/search?navsource=&ob=9&q=gtx%201660&pmin=1000000&pmax=3000000


MAIN_URL = "https://tokopedia.com/search?"



def browser_get_data(url):
    options = FirefoxOptions()
    # options.add_argument("--headless=new")
    options.headless = True
    options.add_argument("user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/87.0.4280.88 Safari/537.36")
    # driver = Chrome(options=options)
    driver = Firefox(options=options)
    driver.get(url)
    for _ in range(3):
        body = driver.find_element(by=By.CSS_SELECTOR, value="body")
        body.send_keys(Keys.PAGE_DOWN)
        sleep(0.2)
    return driver.page_source

def search_by_params(product_name: str, min_price: int = 0, max_price:int = 0):
    params = {}
    if min_price and max_price:
        params["pmin"] = min_price
        params["pmax"] = max_price
    params["q"] = product_name
    params["ob"] = 9 #Order by newest items
    url = MAIN_URL + urlencode(params)
    data = browser_get_data(url)
    return data

def parse_content(content: bytes):
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

def get_data(data):
    data = search_by_params(data['product_name'], data['min_price'], data['max_price'])
    result = parse_content(data)
    print("Got result")
    print(len(result))
    for i in result:
        store_item(i)

def start_item_search(data):
    print(f"Entered user data {data}")
    # get_data(data)
    process = multiprocessing.Process(target=get_data, args=(data,))
    process.start()
    process.join()

# if __name__ == "__main__":
#     # data_to_search = [
#     #     'Lenovo Ideapad',
#     #     'Iphone 11',
#     #     'GTX 1060',
#     #     'Ryzen 7800x',
#     #     'Samsung S10'
#     # ]
#     # processes = []
#     # for i in data_to_search:
#     #     process = multiprocessing.Process(target=get_data, args=(i,))
#     #     processes.append(process)
#     #     process.start()
    
#     # for i in processes:
#     #     i.join()
#     get_data(
#         {
#             "product_name": "Lenovo Ideapad",
#             "min_price": 3000000,
#             "max_price": 9000000
#         }
#     )
#     print("Dones!")