# from requests_html import AsyncHTMLSession
import requests as req
from modules.exceptions import InvalidWalletKeyError
from modules.environment import BLOCKCHAIN_URI
import json
BLOCKCHAIN_URI = BLOCKCHAIN_URI + '/accounts/'

def get_balance_from_public_key(key: str) -> str:
    try:
        res = req.get(BLOCKCHAIN_URI + key) 
        data = res.json()
        balance = data['balances']
        response = ("\n".join([i['balance'] for i in balance]))
        if "status" in data and data["status"] == 400:
            return f"Invalid wallet: {key}"
        return f"Wallet key : {key}\n Balances: {response} Coin"
    except Exception as e:
        print("Error encountered on retrieving public key balance")