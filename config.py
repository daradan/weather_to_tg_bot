import os

from dotenv import load_dotenv, find_dotenv

load_dotenv(find_dotenv())

TG_TOKEN = os.getenv('TG_TOKEN')

URL_ONECALL = 'https://api.openweathermap.org/data/2.5/onecall'
URL_AIR_POLLUTION = 'http://api.openweathermap.org/data/2.5/air_pollution'
PARAMS_ONECALL = {'appid': os.getenv('API_ID'),
                  'units': 'metric',
                  'lang': 'ru',
                  'exclude': 'minutely,hourly'
                  }
PARAMS_AIR_POLLUTION = {'appid': os.getenv('API_ID')}