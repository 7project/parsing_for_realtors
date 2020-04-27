import logging
import random
import re
import time
from decimal import Decimal
import json
from pprint import pprint

import bs4
import requests


logging.basicConfig(level=logging.INFO)
logger = logging.getLogger('PARSING')


class DecimalEncoder(json.JSONEncoder):
    def default(self, o):
        if isinstance(o, Decimal):
            return float(o)
        return super(DecimalEncoder, self).default(o)


class Parser:
    """
    initialization
    """
    def __init__(self):
        self.session = requests.Session()
        self.session.headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 6.1; Win64; x64; rv:69.0) Gecko/20100101 Firefox/69.0',
            'Accept-Language': 'ru-RU,ru;q=0.8,en-US;q=0.5,en;q=0.3',

        }
        self.domain = 'https://www.wellton-towers.ru'
        self.data_for_record = []

    def loading(self, url):
        while True:
            try:
                time.sleep(random.randint(1, 3))
                result = self.session.get(url=url, verify=False)
                data = result.json()
                result = data['html'].strip().split('\n')
                return result
            except Exception as exp:
                logger.info(exp)

    def parser_result(self, result):

        url_page = re.search(r'[/]\w+[/]\w+[/]', result[0].strip()).group()
        url_page = self.domain + url_page

        article = re.search(r'[1-9][A-Я]', result[1].strip()).group()

        row_plan = result[11].strip()
        start_index = re.search(r'=\"', row_plan).end()
        end_index = re.search(r'\"\s', row_plan).start()
        plan = row_plan[start_index:end_index]
        plan = self.domain + plan

        area = re.search(r'[\d]{2,3}[,.]?[\d]?', result[19].strip()).group()
        area = float(area.replace(',', '.'))

        building = re.search(r'[\d]{2,}[.][\d]?', result[24].strip()).group()

        floor = re.search(r'[\d]{1,3}', result[29].strip()).group()
        floor = int(floor)

        discount_percent = re.search(r'[\d]', result[37].strip()).group()
        discount_percent = int(discount_percent)

        price_base = re.search(r'[\d]{1,3}\s?[\d]{1,3}\s?[\d]{1,3}', result[39].strip()).group()
        price_base = price_base.replace(' ', '')

        price_sale = re.search(r'[\d]{1,3}\s?[\d]{1,3}\s?[\d]{1,3}', result[40].strip()).group()
        price_sale = price_sale.replace(' ', '')

        logger.info('%s, %s, %s, %s, %s, %s, %s, %s, %s', url_page, article, plan, area, building, floor,
                    discount_percent, price_base, price_sale)

        self.data_for_record.append(
            {
                'complex': 'WELLTON TOWERS',
                'type': 'flat',
                'phase': None,
                'building': building,
                'section': None,
                'price_base': Decimal(price_base),
                'price_sale': Decimal(price_sale),
                'price_finished_sale': None,
                'area': area,
                'living_area': None,
                'number': None,
                'number_on_site': None,
                'rooms': None,
                'floor': floor,
                'in_sale': 1,
                'sale_status': 'в продаже',
                'finished': 'optional',
                'ceil': Decimal(3.1),
                'article': article,
                'finishing_name': 'White box',
                'furniture': None,
                'furniture_price': None,
                'plan': plan,
                'feature': None,
                'view': ['на Москву', 'на реку'],
                'euro_planning': 1,
                'sale': None,
                'discount_percent': discount_percent,
                'discount': None,
            }
        )

    def run(self):
        for i in range(238):
            url = f'https://www.wellton-towers.ru/filter/?limit=1&mode=cards&offset={i}'
            result = self.loading(url)
            if len(result) == 45:
                self.parser_result(result=result)
        self.save()

    def save(self):
        logger.info(f'Длинна списка - {len(self.data_for_record)}')
        pprint(self.data_for_record)
        data_file = json.dumps(self.data_for_record, cls=DecimalEncoder, indent=1, sort_keys=False,
                               ensure_ascii=False).encode('utf-8').decode('windows-1251')
        with open('date_json_2.json', 'w') as file_data:
            file_data.write(data_file)


if __name__ == '__main__':
    parser = Parser()
    parser.run()
