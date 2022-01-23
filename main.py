import time
from datetime import datetime
import requests
from bs4 import BeautifulSoup as bs
import random
from math import ceil
import json
import re
import csv


def json_to_csv():
    with open('output.json') as json_file:
        jsondata = json.load(json_file)

    data_file = open('output.csv', 'w', newline='')
    csv_writer = csv.writer(data_file)

    count = 0
    for data in jsondata:
        if count == 0:
            header = data.keys()
            csv_writer.writerow(header)
            count += 1
        csv_writer.writerow(data.values())

    data_file.close()


def write_json(new_data, filename):
    with open(filename, 'r+') as file:
        # First we load existing data into a dict.
        file_data = json.load(file)
        # Join new_data with file_data inside emp_details
        file_data.append(new_data)
        # Sets file's current position at offset.
        file.seek(0)
        # convert back to json.
        json.dump(file_data, file, indent=4)


def get_categories():
    categories = []
    sitemap = requests.get('https://www.target.com/sitemap_index.xml.gz')
    soup = bs(sitemap.content, 'html.parser')
    urls = soup.find_all('loc')
    for url in urls:
        if 'https://www.target.com/p/' in url.text:
            categories.append(url.text)
    return categories


def get_products(categories):
    products = []
    m = ceil(2500 / len(categories))
    for categorie in categories:
        sitemap = requests.get(categorie)
        soup = bs(sitemap.content, 'html.parser')
        urls = soup.find_all('loc')
        urls = random.sample(urls, m)
        for url in urls:
            url = url.text.split('/-/')
            products.append(f'https://www.target.com/p/-/{url[1]}')
    return products


def part1(product):
    content = requests.get(product)
    content = bs(content.content, 'html.parser').find('script', {"type": "application/ld+json"}).text
    data = json.loads(content)
    data1 = data['@graph'][1]['itemListElement']
    RootCate = data1[1]['item']['name']
    SubCate = data1[-1]['item']['name']
    return RootCate, SubCate


def part2(product):
    tcin = int(re.findall(r'(\d+)', product)[0])
    content = requests.get(
        f'https://redsky.target.com/redsky_aggregations/v1/web/pdp_client_v1?key=ff457966e64d5e877fdbad070f276d18ecec4a'
        f'01&tcin={tcin}&pricing_store_id=3991&has_financing_options=true&visitor_id=017E81FBB48602019CD3D0445A1D2994'
        f'&has_size_context=true&latitude=36.170&longitude=8.710&state=33&zip=07100').json()
    price = content['data']['product']['price']['current_retail']
    title = content['data']['product']['item']['product_description']['title']
    return title, price


if __name__ == '__main__':
    categories = get_categories()
    products = get_products(categories)
    count = 0
    for product in products:
        try:
            RootCate, SubCate = part1(product)
            time.sleep(0.3)
            title, price = part2(product)
            now = datetime.now()
            dt_string = now.strftime("%d/%m/%Y %H:%M:%S")
            data = {'ProductURL': product,
                    'ProductName': title,
                    "RootCate": RootCate,
                    "SubCate": SubCate,
                    "CurrentPrice": price,
                    "TimeStamp": dt_string}
            write_json(data, 'output.json')
            time.sleep(0.3)
            count += 1
        except:
            pass
        if count >= 2000:
            json_to_csv()
            break
