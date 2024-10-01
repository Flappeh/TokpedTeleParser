from urllib.parse import urlencode
from bs4 import BeautifulSoup 
import json
from dotenv import load_dotenv
from selenium.webdriver import Chrome
from selenium.webdriver.chrome.options import Options
import multiprocessing
import os

load_dotenv()

# Template url https://www.tokopedia.com/search?navsource=&ob=9&q=gtx%201660&pmin=1000000&pmax=3000000


MAIN_URL = "https://tokopedia.com/search?"
chrome_options = Options()
chrome_options.add_argument("--headless")
chrome_options.add_argument("user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/87.0.4280.88 Safari/537.36")
def search_by_params(product_name: str, min_price: int = 0, max_price:int = 0):
    params = {}
    if min_price and max_price:
        params["pmin"] = min_price
        params["pmax"] = max_price
    params["q"] = product_name
    params["ob"] = 9 #Order by newest items
    url = MAIN_URL + urlencode(params)
    headers = {"User-Agent": "Mozilla/5.0 (X11; CrOS x86_64 12871.102.0) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/81.0.4044.141 Safari/537.36"}
    with Chrome(options=chrome_options) as browser:
        browser.get(url)
        data = browser.page_source
    return data

def parse_content(content: bytes):
    soup = BeautifulSoup(content, 'html.parser')
    products = soup.find_all(lambda box: box.name=='a' and box.has_attr('data-theme'))
    # product_data = {}
    result = []
    for i in products:
        item = {}
        product_box = i.select('div')[0]
        text_box = product_box.find_all('div', recursive=False)[1]
        product_name = text_box.find_all('span')[0]
        product_price = text_box.find_all('div', recursive=False)[1]
        product_link = i.get("href")
        
        item["product_name"] = product_name.text
        item["product_price"] = product_price.text.split("Rp")[1]
        item["product_link"] = product_link
        result.append(item)
    return result

def get_data(input: str):
    data = search_by_params(input)
    result = parse_content(data)
    print(json.dumps(result))

if __name__ == "__main__":
    # data_to_search = [
    #     'Lenovo Ideapad',
    #     'Iphone 11',
    #     'GTX 1060',
    #     'Ryzen 7800x',
    #     'Samsung S10'
    # ]
    # processes = []
    # for i in data_to_search:
    #     process = multiprocessing.Process(target=get_data, args=(i,))
    #     processes.append(process)
    #     process.start()
    
    # for i in processes:
    #     i.join()
    get_data('Lenovo Ideapad')
    print("Dones!")