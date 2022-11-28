import os

from dotenv import load_dotenv, find_dotenv

load_dotenv(find_dotenv())

TG_TOKEN = os.getenv('TG_TOKEN')
