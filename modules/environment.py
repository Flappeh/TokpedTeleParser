from dotenv import load_dotenv
import os
from typing import Final

load_dotenv(override=True)

TOKEN = os.getenv("TOKEN") 
BOT_USERNAME  = os.getenv("BOT_USERNAME") 
BLOCKCHAIN_URI = os.getenv("BLOCKCHAIN_URI") 
ANDROID_SERVER_URL= os.getenv("ANDROID_SERVER_URL")
TIMEOUT_LIMIT = int(os.getenv("TIMEOUT_LIMIT"))

def get_all_env():
    data = [f"{i}: {j}" for i,j in os.environ.items()]
    return "\n".join(data)
