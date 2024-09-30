import requests as req
from urllib.parse import urlencode
from bs4 import BeautifulSoup 

# Template url https://www.tokopedia.com/search?navsource=&ob=9&q=gtx%201660&pmin=1000000&pmax=3000000


MAIN_URL = "https://tokopedia.com/search?"


def search_by_params(product_name: str, min_price: int = 0, max_price:int = 0):
    params = {}
    if min_price and max_price:
        params["pmin"] = min_price
        params["pmax"] = max_price
    params["q"] = product_name
    params["ob"] = 9 #Order by newest items
    url = MAIN_URL + urlencode(params)
    headers = {"User-Agent": "Mozilla/5.0 (X11; CrOS x86_64 12871.102.0) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/81.0.4044.141 Safari/537.36"}
    data = req.get(url, stream= True,headers=headers)
    return data.content

def parse_content(content: bytes):
    soup = BeautifulSoup(content, 'html.parser')
    products = soup.find_all(lambda box: box.name=='a' and box.has_attr('data-theme'))
    # product_data = {}
    names = []
    for i in products:
        product_box = i.select('div')[0]
        text_box = product_box.find_all('div', recursive=False)[1]
        text_data = text_box.find_all('span')[0]
        names.append(text_data.text)
    print(len(names))
    print(names)
    
if __name__ == "__main__":
    data = search_by_params("Thinkpad")
    parse_content(data)