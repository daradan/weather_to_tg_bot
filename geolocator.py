import json
import os
from dotenv import load_dotenv, find_dotenv
import certifi
import ssl
import geopy.geocoders
from geopy.geocoders import Nominatim

ctx = ssl.create_default_context(cafile=certifi.where())
geopy.geocoders.options.default_ssl_context = ctx

load_dotenv(find_dotenv())


def get_lat_long(city: str) -> dict:
    geolocator = Nominatim(user_agent='test@test.kz', scheme='http')
    location = geolocator.geocode(city)
    data = {
        city.lower(): {
            'latitude': location.latitude,
            'longitude': location.longitude,
            'address': location.address
        }
    }
    return data


def add_city(data_prev: dict, city: str) -> dict:
    city_with_geo = get_lat_long(city)
    data_prev.update(city_with_geo)
    with open('geolocator.json', 'w', encoding='utf-8') as file:
        json.dump(data_prev, file, ensure_ascii=False, indent=4)
    return city_with_geo[city.lower()]


def check_geolocator(city: str) -> dict:
    if not os.path.exists('geolocator.json'):
        return add_city({}, city)
    with open('geolocator.json', encoding='utf-8') as file:
        data = json.load(file)
        if city.lower() in data.keys():
            return data[city.lower()]
        return add_city(data, city)


if __name__ == '__main__':
    print(check_geolocator('astana'))
