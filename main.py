import requests
from requests import request
from bs4 import BeautifulSoup
import urllib.parse
import re
import threading


urls_to_city_pages = [
    "https://pl.wikipedia.org/wiki/Kategoria:Miasta_w_wojew%C3%B3dztwie_dolno%C5%9Bl%C4%85skim",
    "https://pl.wikipedia.org/wiki/Kategoria:Miasta_w_wojew%C3%B3dztwie_kujawsko-pomorskim",
    "https://pl.wikipedia.org/wiki/Kategoria:Miasta_w_wojew%C3%B3dztwie_lubelskim",
    "https://pl.wikipedia.org/wiki/Kategoria:Miasta_w_wojew%C3%B3dztwie_lubuskim",
    "https://pl.wikipedia.org/wiki/Kategoria:Miasta_w_wojew%C3%B3dztwie_%C5%82%C3%B3dzkim",
    "https://pl.wikipedia.org/wiki/Kategoria:Miasta_w_wojew%C3%B3dztwie_ma%C5%82opolskim",
    "https://pl.wikipedia.org/wiki/Kategoria:Miasta_w_wojew%C3%B3dztwie_mazowieckim",
    "https://pl.wikipedia.org/wiki/Kategoria:Miasta_w_wojew%C3%B3dztwie_opolskim",
    "https://pl.wikipedia.org/wiki/Kategoria:Miasta_w_wojew%C3%B3dztwie_podkarpackim",
    "https://pl.wikipedia.org/wiki/Kategoria:Miasta_w_wojew%C3%B3dztwie_podlaskim",
    "https://pl.wikipedia.org/wiki/Kategoria:Miasta_w_wojew%C3%B3dztwie_pomorskim",
    "https://pl.wikipedia.org/wiki/Kategoria:Miasta_w_wojew%C3%B3dztwie_%C5%9Bl%C4%85skim",
    "https://pl.wikipedia.org/wiki/Kategoria:Miasta_w_wojew%C3%B3dztwie_%C5%9Bwi%C4%99tokrzyskim",
    "https://pl.wikipedia.org/wiki/Kategoria:Miasta_w_wojew%C3%B3dztwie_warmi%C5%84sko-mazurskim",
    "https://pl.wikipedia.org/wiki/Kategoria:Miasta_w_wojew%C3%B3dztwie_wielkopolskim",
    "https://pl.wikipedia.org/wiki/Kategoria:Miasta_w_wojew%C3%B3dztwie_zachodniopomorskim",
]


# print(len(urls_to_city_pages))

class City:
    def __init__(self, url, province, city_name, **kwargs):
        self.url = f"https://pl.wikipedia.org/{url}"
        self.province = province
        self.city_name = city_name
        self.latitude, self.longitude = self.convert_coordinates(kwargs['latitude'], kwargs['longitude'])

    def __str__(self):
        return f"{self.city_name} {self.province} {self.latitude} {self.longitude}"

    def print_data_to_csv(self):
        return f"{self.city_name};{self.province};{self.latitude};{self.longitude}"

    def dms_to_dd(self, degrees, minutes, seconds, direction):
        # Calculate decimal degrees

        dd = degrees + (minutes / 60) + (seconds / 3600)
        # Check direction (N/S for latitude, E/W for longitude)
        if direction in ['S', 'W']:
            dd = -dd

        return dd

    def convert_coordinates(self, dms_lat, dms_lon):
        # Split the DMS strings into degrees, minutes, seconds, and direction
        lat_parts = dms_lat.split('°')
        lat_deg = float(lat_parts[0])
        lat_parts = lat_parts[1].split('′')
        lat_min = float(lat_parts[0])
        lat_parts = lat_parts[1].split('″')
        lat_sec = float(lat_parts[0].replace(',', '.')) if len(lat_parts) > 1 else 0.0
        lat_dir = dms_lat[-1]

        lon_parts = dms_lon.split('°')
        lon_deg = float(lon_parts[0])
        lon_parts = lon_parts[1].split('′')
        lon_min = float(lon_parts[0])
        lon_parts = lon_parts[1].split('″')
        lon_sec = float(lon_parts[0].replace(',', '.')) if len(lon_parts) > 1 else 0.0
        lon_dir = dms_lon[-1]

        # Convert to decimal degrees
        latitude = self.dms_to_dd(lat_deg, lat_min, lat_sec, lat_dir)
        longitude = self.dms_to_dd(lon_deg, lon_min, lon_sec, lon_dir)

        return latitude, longitude




def find_data(url):
    response = requests.get(url=url)

    bs = BeautifulSoup(response.text, 'html.parser')

    div_with_url = bs.find_all('div', class_='mw-category-group')


    city_list = []
    a_tags_list = []
    province = ''

    for div_index, div in enumerate(start=1, iterable=div_with_url):
        a_tags = div.find_all('a')
        for index, a in enumerate(start=1, iterable=a_tags):
            if index == 1 and div_index == 1:
                pattern = r'/wiki/.*'
                decoded_text = re.sub(pattern, "", urllib.parse.unquote(a.get('href')).encode('utf-8').decode('utf-8'))
                province = decoded_text
                continue

            #
            city_url = a.get('href')
            city_name = a.text
            # print(city_url, city_name)

            city_response = requests.get(url=f'https://pl.wikipedia.org/{city_url}')
            city_soup = BeautifulSoup(city_response.text, 'html.parser')

            city_province = ''
            a_tag_province = city_soup.find('a', title='Podział administracyjny Polski', string='Województwo')
            if a_tag_province:
                tr_element = a_tag_province.find_parent('tr')
                td_element = tr_element.find('td')
                a_name = td_element.find('a')
                city_province = a_name.text

            latitude = city_soup.find('span', class_='latitude').text
            longitude = city_soup.find('span', class_='longitude').text

            city = City(url=city_url, province=city_province, city_name=city_name, latitude=latitude, longitude=longitude)
            city_list.append(city)

    for city in city_list:
        print(city.print_data_to_csv())


threads = []

for page_url in urls_to_city_pages:
    thread = threading.Thread(target=find_data, args=(page_url, ))
    threads.append(thread)
    thread.start()


# find_data(urls_to_city_pages[0])


