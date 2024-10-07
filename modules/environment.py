from dotenv import load_dotenv
import os
from typing import Final
import yaml


load_dotenv(override=True)
yaml_config = {}
with open('./data/config.yaml', 'r') as f:
    yaml_config = yaml.safe_load(f)
    
TOKEN = os.getenv("TOKEN") 
BOT_USERNAME  = os.getenv("BOT_USERNAME") 
SEARCH_INTERVAL = yaml_config["SEARCH_INTERVAL"]

def get_all_env():
    data = [f"{i}: {j}" for i,j in os.environ.items()]
    return "\n".join(data)
