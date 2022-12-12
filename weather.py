import requests
import config
from models import Location


def get_weather(location: Location, lang: str) -> str:
    response = get_response(location.latitude, location.longitude, lang)
    data_parsed = parse_data(response)
    text_to_tg = make_text_to_tg(data_parsed, location.city)
    return text_to_tg


def get_response(latitude: str, longitude: str, lang: str) -> dict:
    params_onecall = config.PARAMS_ONECALL
    params_onecall['lat'] = latitude
    params_onecall['lon'] = longitude
    params_onecall['lang'] = lang
    response_onecall = requests.get(config.URL_ONECALL, params=params_onecall).json()

    params_air_population = config.PARAMS_AIR_POLLUTION
    params_air_population['lat'] = latitude
    params_air_population['lon'] = longitude
    response_air_population = requests.get(config.URL_AIR_POLLUTION, params=params_air_population).json()

    merged_responses = merge_responses(response_onecall, response_air_population)

    return merged_responses


def merge_responses(onecall: dict, air_population: dict) -> dict:
    merged_responses = onecall.copy()
    merged_responses.update(air_population)
    return merged_responses


def parse_data(response: dict) -> dict:
    data_parsed = {
        'temp_current': round(response['current']['temp']),
        'temp_feels_like': round(response['current']['feels_like']),
        'temp_max': round(response['daily'][0]['temp']['max']),
        'temp_next_day_max': round(response['daily'][1]['temp']['max']),
        'humidity': response['current']['humidity'],
        'wind_speed': round(response['current']['wind_speed']),
        'wind_speed_next': round(response['daily'][1]['wind_speed']),
        'wind_deg': deg_to_compass(response['current']['wind_deg']),
        'sunrise': response['current']['sunrise'],
        'sunset': response['current']['sunset'],
        'description': response['current']['weather'][0]['description'],
        'description_next': response['daily'][1]['weather'][0]['description'],
        'icon': make_emojies(response['current']['weather'][0]['icon']),
        'icon_next': make_emojies(response['daily'][1]['weather'][0]['icon']),
        'aqi': round(response['list'][0]['main']['aqi']),
        'co': round(response['list'][0]['components']['co']),
        'no': round(response['list'][0]['components']['no']),
        'no2': round(response['list'][0]['components']['no2']),
        'o3': round(response['list'][0]['components']['o3']),
        'so2': round(response['list'][0]['components']['so2']),
        'pm2_5': round(response['list'][0]['components']['pm2_5']),
        'pm10': round(response['list'][0]['components']['pm10']),
        'nh3': round(response['list'][0]['components']['nh3']),
    }
    return data_parsed


def deg_to_compass(wind_deg) -> list[str]:
    val = int((wind_deg / 22.5) + 0.5)
    text_compass = ['С', 'ССВ', 'СВ', 'ВСВ', 'В', 'ВЮВ', 'ЮВ', 'ЮЮВ', 'Ю', 'ЮЮЗ', 'ЮЗ', 'ЗЮЗ', 'З', 'ЗСЗ', 'СЗ', 'ССЗ']
    return text_compass[(val % 16)]


def make_emojies(icon: str) -> str:
    if '01' in icon:
        return '☀️'
    if '02' in icon:
        return '🌤️'
    if '03' in icon or '04' in icon:
        return '☁️'
    if '09' in icon:
        return '🌧️'
    if '10' in icon:
        return '🌦️'
    if '11' in icon:
        return '🌩️'
    if '13' in icon:
        return '🌨️'
    if '50' in icon:
        return '🌫️'
    else:
        return ''


def make_text_to_tg(data: dict, city: str) -> str:
    text_to_tg = f"🌡 {data['temp_current']}° ({data['temp_feels_like']}°), " \
                 f"{data['icon']} {data['description']}, " \
                 f"🌬️ {data['wind_speed']}м/с - {data['wind_deg']}, " \
                 f"💧{data['humidity']}%\n" \
                 f"<b>AQI:</b> {data['aqi']}, " \
                 f"<b>SO2:</b> {data['so2']}, " \
                 f"<b>O3:</b> {data['o3']}, " \
                 f"<b>PM2.5:</b> {data['pm2_5']}, " \
                 f"<b>PM10:</b> {data['pm10']}\n" \
                 f"<b><u>{city}</u></b>"
    return text_to_tg
