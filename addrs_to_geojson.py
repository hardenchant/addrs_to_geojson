import json
import logging
import os

import requests

YANDEX_API_KEY = os.getenv('YANDEX_API_KEY')
addresses = []


def get_coords_with_sputnik(addr: str):
    """
    Free geocoder service
    Gets first result from sputnik geocoder response
    :param addr: addr like "Москва, ул. Тверская, 1"
    :return: longitude and latitude
    """
    resp = requests.get(f"http://search.maps.sputnik.ru/search/addr?q={addr}").json()
    return resp['result']['address'][0]['features'][0]['geometry']['geometries'][0]['coordinates']


def get_coords_with_yandex_geocoder(addr):
    """
    25000 free requests per day for one api key
    Gets first result from yandex geocoder response
    :param addr: addr like "Москва, ул. Тверская, 1"
    :return: longitude and latitude
    """
    resp = requests.get(
        f"https://geocode-maps.yandex.ru/1.x/?apikey={YANDEX_API_KEY}&geocode={addr}&format=json"
    ).json()
    return resp['response']['GeoObjectCollection']['featureMember'][0]['GeoObject']['Point']['pos'].split(' ')


def gen_geojson_from_addrs_and_lats(addrs_lats: dict):
    geojson = {
        "type": "FeatureCollection",
        "features": []
    }
    color_purple = "#b51eff"
    for addr, lats in addrs_lats.items():
        geojson['features'].append({
            "type": "Feature",
            "geometry": {
                "type": "Point",
                "coordinates": [*lats]
            },
            "properties": {
                "description": addr,
                "iconCaption": addr,
                "marker-color": color_purple
            }
        })
    return geojson


if __name__ == '__main__':
    all_coords = {}
    for addr in addresses:
        try:
            coords = get_coords_with_yandex_geocoder(addr)
        except Exception as e:
            logging.error(f"Error caused when call yandex API for {addr}")
            logging.error(e)
            continue
        all_coords[addr] = coords
    geojson = gen_geojson_from_addrs_and_lats(all_coords)

    with open('coords2.geojson', 'w', newline='') as geojson_file:
        geojson_file.write(json.dumps(geojson, indent=4, sort_keys=True))
